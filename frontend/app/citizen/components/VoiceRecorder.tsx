"use client";

import { useState, useRef } from "react";
import { Mic, Square, Send, ArrowLeft, Volume2 } from "lucide-react";
import QualityWarning from "./QualityWarning";

interface Props {
  lang: string;
  onBack: () => void;
  onSubmitted: (id: string) => void;
  userId?: string;
}

type RecordState = "idle" | "recording" | "recorded" | "submitting";

export default function VoiceRecorder({ lang, onBack, onSubmitted, userId }: Props) {
  const [state, setState] = useState<RecordState>("idle");
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [qualityCheck, setQualityCheck] = useState<{score: number, suggestions: string[]} | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const t = {
    title: lang === "hi" ? "अपनी बात बोलें" : lang === "te" ? "మీ సమస్య చెప్పండి" : "Speak your concern",
    tapToRecord: lang === "hi" ? "रिकॉर्ड करने के लिए दबाएं" : lang === "te" ? "రికార్డ్ చేయడానికి నొక్కండి" : "Tap to start recording",
    tapToStop: lang === "hi" ? "रोकने के लिए दबाएं" : lang === "te" ? "ఆపడానికి నొక్కండి" : "Tap to stop",
    submit: lang === "hi" ? "जमा करें" : lang === "te" ? "సమర్పించు" : "Submit",
    rerecord: lang === "hi" ? "फिर से रिकॉर्ड करें" : lang === "te" ? "మళ్ళీ రికార్డ్ చేయండి" : "Re-record",
    submitting: lang === "hi" ? "भेजा जा रहा है..." : lang === "te" ? "సమర్పిస్తోంది..." : "Submitting...",
    hint:
      lang === "hi"
        ? "उदाहरण: 'हमारे स्कूल में पर्याप्त कमरे नहीं हैं। बच्चे बाहर बैठते हैं।'"
        : lang === "te"
        ? "ఉదాహరణ: 'మా పాఠశాలలో తగినన్ని గదులు లేవు. పిల్లలు బయట కూర్చుంటున్నారు.'"
        : "Example: 'Our school doesn't have enough classrooms. Children sit outside.'",
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRef.current = mr;
      chunksRef.current = [];

      mr.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      mr.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        setState("recorded");
        stream.getTracks().forEach((t) => t.stop());
      };

      mr.start(250);
      setState("recording");
      setDuration(0);
      timerRef.current = setInterval(() => setDuration((d) => d + 1), 1000);
    } catch {
      alert("Microphone access denied. Please enable it in your browser settings.");
    }
  };

  const stopRecording = () => {
    mediaRef.current?.stop();
    if (timerRef.current) clearInterval(timerRef.current);
  };

  const submitAudio = async (skipQualityCheck = false) => {
    if (!audioBlob) return;
    setState("submitting");

    try {
      // Helper to convert blob to base64 data URI
      const getBase64 = (blob: Blob): Promise<string> => {
        return new Promise((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result as string);
          reader.readAsDataURL(blob);
        });
      };
      
      const audioData = await getBase64(audioBlob);

      if (!skipQualityCheck && !qualityCheck) {
        const checkRes = await fetch(`${apiBase}/submissions/quality-check`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            media_type: "audio", 
            content: audioData, 
            original_language: lang === "hi" ? "hi-IN" : lang === "te" ? "te-IN" : "en-IN" 
          }),
        });
        const qualityData = await checkRes.json();
        
        if (qualityData.score < 65) {
          setQualityCheck(qualityData);
          setState("recorded");
          return;
        }
        setQualityCheck(qualityData);
      }

      const payloadScore = qualityCheck?.score ?? 100.0;
      const payloadSuggestions = qualityCheck?.suggestions ?? [];

      const res = await fetch(`${apiBase}/submissions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          media_type: "audio",
          content: audioData,
          original_language: lang === "hi" ? "hi-IN" : lang === "te" ? "te-IN" : "en-IN",
          source: "web",
          quality_score: payloadScore,
          quality_suggestions: payloadSuggestions,
          user_id: userId
        }),
      });
      const data = await res.json();
      onSubmitted(data.id);
    } catch {
      alert("Submission failed. Please try again.");
      setState("recorded");
    }
  };

  const fmt = (s: number) => `${Math.floor(s / 60).toString().padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")}`;

  return (
    <div className="animate-fade-in flex flex-col items-center">
      <button onClick={onBack} className="self-start flex items-center gap-2 text-slate-400 hover:text-white mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span className="text-sm">Back</span>
      </button>

      <h2 className="text-xl font-semibold text-white mb-2 text-center">{t.title}</h2>
      <p className="text-sm text-slate-500 text-center mb-8 max-w-sm">{t.hint}</p>

      {/* Waveform / recording indicator */}
      <div className="relative w-40 h-40 mb-8">
        {state === "recording" && (
          <div className="absolute inset-0 rounded-full bg-red-500/10 animate-ping" />
        )}
        <button
          id="voice-record-btn"
          onClick={state === "idle" ? startRecording : state === "recording" ? stopRecording : undefined}
          disabled={state === "submitting"}
          className={`relative w-full h-full rounded-full flex flex-col items-center justify-center gap-2 text-white font-semibold transition-all duration-200 hover:scale-105 shadow-2xl ${
            state === "recording"
              ? "bg-red-600 hover:bg-red-700"
              : "hover:opacity-90"
          }`}
          style={state !== "recording" ? { background: "linear-gradient(135deg, #1e88ed, #1671da)" } : undefined}
        >
          {state === "idle" && <Mic className="w-10 h-10" />}
          {state === "recording" && <Square className="w-8 h-8" />}
          {state === "recorded" && <Volume2 className="w-10 h-10" />}
          {state === "submitting" && (
            <div className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          )}
          {state === "recording" && (
            <span className="text-lg font-mono">{fmt(duration)}</span>
          )}
        </button>
      </div>

      <p className="text-sm text-slate-400 mb-6">
        {state === "idle" && t.tapToRecord}
        {state === "recording" && t.tapToStop}
        {state === "recorded" && "Recording ready — play back or submit"}
        {state === "submitting" && t.submitting}
      </p>

      {state === "recorded" && audioUrl && (
        <div className="w-full flex flex-col gap-3">
          <audio controls src={audioUrl} className="w-full rounded-lg mb-2" />
          
          {qualityCheck && (
            <QualityWarning
              score={qualityCheck.score}
              suggestions={qualityCheck.suggestions}
              lang={lang}
              onProceed={() => submitAudio(true)}
              onImprove={() => { setAudioBlob(null); setAudioUrl(null); setState("idle"); setQualityCheck(null); }}
            />
          )}

          {!qualityCheck && (
            <div className="flex gap-3">
              <button
                onClick={() => { setAudioBlob(null); setAudioUrl(null); setState("idle"); }}
              className="flex-1 py-3 rounded-xl border border-slate-600 text-slate-300 font-semibold text-sm hover:bg-white/5 transition-colors"
            >
              {t.rerecord}
            </button>
              <button
                id="submit-voice-btn"
                onClick={() => submitAudio(false)}
                className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-white text-sm transition-all hover:scale-[1.02]"
                style={{ background: "linear-gradient(135deg, #1e88ed, #1671da)" }}
              >
                <Send className="w-4 h-4" />
                {t.submit}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
