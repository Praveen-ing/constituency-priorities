"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Mic, Camera, MessageSquare, Grid3X3,
  ArrowLeft, ArrowRight, CheckCircle,
} from "lucide-react";
import VoiceRecorder from "./components/VoiceRecorder";
import LowLiteracyFlow from "./components/LowLiteracyFlow";
import LanguageSelector from "./components/LanguageSelector";
import SubmissionPipeline from "./components/SubmissionPipeline";
import PhotoSubmit from "./components/PhotoSubmit";

type Mode = "choose" | "voice" | "photo" | "text" | "icon" | "pipeline" | "done";

const MODES = [
  { id: "voice", label: "Voice", labelHi: "आवाज़", labelTe: "వాయిస్", icon: Mic, color: "from-brand-600 to-brand-700", desc: "Speak your concern" },
  { id: "photo", label: "Photo", labelHi: "फ़ोटो", labelTe: "ఫోటో", icon: Camera, color: "from-saffron-500 to-saffron-600", desc: "Photograph an issue" },
  { id: "text", label: "Text", labelHi: "टेक्स्ट", labelTe: "టెక్స్ట్", icon: MessageSquare, color: "from-emerald-500 to-emerald-600", desc: "Type your concern" },
  { id: "icon", label: "Icons", labelHi: "चित्र", labelTe: "చిత్రాలు", icon: Grid3X3, color: "from-purple-500 to-purple-600", desc: "Tap pictures (no reading needed)" },
] as const;

export default function CitizenPage() {
  const [mode, setMode] = useState<Mode>("choose");
  const [lang, setLang] = useState("en");
  const [submittedId, setSubmittedId] = useState<string | null>(null);
  const [textInput, setTextInput] = useState("");
  const [loading, setLoading] = useState(false);

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const submitText = async () => {
    if (!textInput.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/submissions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ media_type: "text", content: textInput, original_language: lang, source: "web" }),
      });
      const data = await res.json();
      setSubmittedId(data.id);
      setMode("pipeline");
    } catch {
      alert("Submission failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const labelFor = (m: typeof MODES[number]) =>
    lang === "hi" ? m.labelHi : lang === "te" ? m.labelTe : m.label;

  if (mode === "done") {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-6 text-center">
        <div className="w-20 h-20 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center mb-6 animate-fade-in">
          <CheckCircle className="w-10 h-10 text-emerald-400" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">
          {lang === "hi" ? "धन्यवाद!" : lang === "te" ? "ధన్యవాదాలు!" : "Thank you!"}
        </h2>
        <p className="text-slate-400 mb-2">
          {lang === "hi"
            ? "आपकी बात दर्ज हो गई है।"
            : lang === "te"
            ? "మీ అభ్యర్థన నమోదైంది."
            : "Your submission has been recorded."}
        </p>
        {submittedId && <p className="text-xs text-slate-600 font-mono mb-8">ID: {submittedId}</p>}
        <Link href="/" className="flex items-center gap-2 text-brand-400 hover:text-brand-300 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          {lang === "hi" ? "वापस जाएं" : lang === "te" ? "వెనుకకు" : "Back to home"}
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-5 border-b border-slate-800">
        <Link href="/" className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">Home</span>
        </Link>
        <h1 className="text-lg font-semibold text-white">Submit a Priority</h1>
        <LanguageSelector lang={lang} onLangChange={setLang} />
      </header>

      <div className="flex-1 max-w-2xl mx-auto w-full px-6 py-8 flex flex-col justify-center">
        {mode === "pipeline" && (
          <SubmissionPipeline onComplete={() => setMode("done")} />
        )}

        {mode === "choose" && (
          <div className="animate-fade-in">
            <p className="text-slate-400 text-center mb-8 text-lg">
              {lang === "hi"
                ? "आप कैसे बताना चाहते हैं?"
                : lang === "te"
                ? "మీరు ఎలా చెప్పాలనుకుంటున్నారు?"
                : "How would you like to share?"}
            </p>
            <div className="grid grid-cols-2 gap-4">
              {MODES.map((m) => {
                const Icon = m.icon;
                return (
                  <button
                    key={m.id}
                    id={`mode-${m.id}`}
                    onClick={() => setMode(m.id as Mode)}
                    className="glass-card p-6 flex flex-col items-center gap-3 hover:border-slate-500 hover:scale-105 transition-all duration-200 group"
                  >
                    <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${m.color} flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow`}>
                      <Icon className="w-7 h-7 text-white" />
                    </div>
                    <span className="text-lg font-bold text-white">{labelFor(m)}</span>
                    <span className="text-xs text-slate-400 text-center">{m.desc}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {mode === "voice" && (
          <VoiceRecorder
            lang={lang}
            onBack={() => setMode("choose")}
            onSubmitted={(id) => { setSubmittedId(id); setMode("pipeline"); }}
          />
        )}

        {mode === "icon" && (
          <LowLiteracyFlow
            lang={lang}
            onBack={() => setMode("choose")}
            onSubmitted={(id) => { setSubmittedId(id); setMode("pipeline"); }}
          />
        )}

        {mode === "text" && (
          <div className="animate-fade-in">
            <button onClick={() => setMode("choose")} className="flex items-center gap-2 text-slate-400 hover:text-white mb-6 transition-colors">
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">Back</span>
            </button>
            <h2 className="text-xl font-semibold text-white mb-6">
              {lang === "hi" ? "अपनी बात लिखें" : lang === "te" ? "మీ సమస్య వ్రాయండి" : "Describe your concern"}
            </h2>
            <textarea
              id="text-submission"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder={
                lang === "hi"
                  ? "उदाहरण: हमारे वार्ड में पानी की बहुत समस्या है..."
                  : lang === "te"
                  ? "ఉదాహరణ: మా వార్డులో నీటి సమస్య తీవ్రంగా ఉంది..."
                  : "Example: Our ward has a severe water shortage problem..."
              }
              rows={6}
              className="w-full bg-surface-700 border border-slate-600 rounded-xl p-4 text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 resize-none transition-colors text-sm leading-relaxed"
            />
            <button
              id="submit-text-btn"
              onClick={submitText}
              disabled={loading || !textInput.trim()}
              className="mt-4 w-full flex items-center justify-center gap-2 py-4 rounded-xl font-semibold text-white transition-all duration-200 hover:scale-[1.02] disabled:opacity-40 disabled:cursor-not-allowed disabled:scale-100"
              style={{ background: "linear-gradient(135deg, #1e88ed, #1671da)" }}
            >
              {loading ? "Submitting..." : lang === "hi" ? "जमा करें" : lang === "te" ? "సమర్పించు" : "Submit"}
              {!loading && <ArrowRight className="w-4 h-4" />}
            </button>
          </div>
        )}

        {mode === "photo" && (
          <PhotoSubmit
            lang={lang}
            onBack={() => setMode("choose")}
            onSubmitted={(id) => { setSubmittedId(id); setMode("pipeline"); }}
            apiBase={apiBase}
          />
        )}
      </div>
    </div>
  );
}
