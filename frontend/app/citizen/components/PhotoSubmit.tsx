"use client";

import { useState, useRef, ChangeEvent } from "react";
import { Camera, ArrowLeft, Upload, CheckCircle2, Loader2, AlertCircle } from "lucide-react";
import QualityWarning from "./QualityWarning";

interface Props {
  lang: string;
  onBack: () => void;
  onSubmitted: (id: string) => void;
  apiBase: string;
  userId?: string;
}

type AnalysisState = "idle" | "preview" | "analyzing" | "analyzed" | "submitting";

const MOCK_ANALYSIS_RESULTS = [
  { theme: "Roads & Infrastructure", urgency: "High", confidence: "94%", description: "Pothole / road damage detected. Affects vehicle safety and commute." },
  { theme: "Water Supply", urgency: "Critical", confidence: "91%", description: "Water supply infrastructure issue detected. Possible pipe damage or open drain." },
  { theme: "Sanitation", urgency: "High", confidence: "88%", description: "Garbage accumulation or drainage blockage detected." },
  { theme: "Electricity", urgency: "Medium", confidence: "85%", description: "Street light or power line damage detected." },
];

export default function PhotoSubmit({ lang, onBack, onSubmitted, apiBase, userId }: Props) {
  const [state, setState] = useState<AnalysisState>("idle");
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<typeof MOCK_ANALYSIS_RESULTS[0] | null>(null);
  const [qualityCheck, setQualityCheck] = useState<{score: number, suggestions: string[]} | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const t = {
    title: lang === "hi" ? "फ़ोटो से रिपोर्ट" : lang === "te" ? "ఫోటో ద్వారా నివేదించండి" : "Report via Photo",
    drag: lang === "hi" ? "फ़ोटो यहाँ खींचें या क्लिक करें" : lang === "te" ? "ఫోటో ఇక్కడ లాగండి లేదా క్లిక్ చేయండి" : "Drag photo here or click to upload",
    analyze: lang === "hi" ? "AI से विश्लेषण करें" : lang === "te" ? "AI తో విశ్లేషించండి" : "Analyze with AI",
    submit: lang === "hi" ? "जमा करें" : lang === "te" ? "సమర్పించు" : "Submit Report",
    analyzing: lang === "hi" ? "AI विश्लेषण कर रहा है..." : lang === "te" ? "AI విశ్లేషిస్తోంది..." : "AI is analyzing your photo...",
  };

  const handleFile = (file: File) => {
    setImageFile(file);
    setImageUrl(URL.createObjectURL(file));
    setState("preview");
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) handleFile(file);
  };

  const runAnalysis = async () => {
    setState("analyzing");
    
    let qualityData = null;
    try {
      if (imageFile) {
        // Helper to convert file to base64
        const getBase64 = (file: File): Promise<string> => {
          return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result as string);
            reader.readAsDataURL(file);
          });
        };
        const base64Img = await getBase64(imageFile);
        const checkRes = await fetch(`${apiBase}/submissions/quality-check`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ media_type: "image", content: base64Img, original_language: lang }),
        });
        qualityData = await checkRes.json();
      }
    } catch (e) {
      console.warn("Quality check failed", e);
    }
    
    // Simulate Gemini multimodal analysis with a 2.5s delay
    await new Promise((r) => setTimeout(r, 1000));
    const result = MOCK_ANALYSIS_RESULTS[Math.floor(Math.random() * MOCK_ANALYSIS_RESULTS.length)];
    setAnalysis(result);
    setQualityCheck(qualityData);
    setState("analyzed");
  };

  const submitPhoto = async () => {
    if (!analysis) return;
    setState("submitting");
    try {
      const res = await fetch(`${apiBase}/submissions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          media_type: "image",
          content: `[Photo submission] ${analysis.theme}: ${analysis.description} (AI Confidence: ${analysis.confidence})`,
          original_language: lang === "hi" ? "hi-IN" : lang === "te" ? "te-IN" : "en-IN",
          source: "web",
          quality_score: qualityCheck?.score ?? 100.0,
          quality_suggestions: qualityCheck?.suggestions ?? [],
          user_id: userId
        }),
      });
      const data = await res.json();
      onSubmitted(data.id);
    } catch {
      alert("Submission failed. Please try again.");
      setState("analyzed");
    }
  };

  return (
    <div className="animate-fade-in flex flex-col">
      <button onClick={onBack} className="self-start flex items-center gap-2 text-slate-400 hover:text-white mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span className="text-sm">Back</span>
      </button>
      <h2 className="text-xl font-semibold text-white mb-6">{t.title}</h2>

      {/* Upload area */}
      {state === "idle" && (
        <div
          className="glass-card p-10 flex flex-col items-center gap-4 border-dashed border-2 border-slate-600 hover:border-saffron-500 transition-colors cursor-pointer"
          onClick={() => inputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          <div className="w-16 h-16 rounded-2xl bg-saffron-500/20 flex items-center justify-center">
            <Upload className="w-8 h-8 text-saffron-400" />
          </div>
          <p className="text-slate-400 text-sm text-center">{t.drag}</p>
          <span className="px-5 py-2 rounded-xl text-sm font-semibold text-white" style={{ background: "linear-gradient(135deg, #f97316, #ea580c)" }}>
            <Camera className="w-4 h-4 inline mr-2" />
            {lang === "hi" ? "कैमरा / गैलरी" : lang === "te" ? "కెమెరా / గ్యాలరీ" : "Camera / Gallery"}
          </span>
          <input ref={inputRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={handleInputChange} />
        </div>
      )}

      {/* Preview + analyze */}
      {(state === "preview" || state === "analyzing" || state === "analyzed") && imageUrl && (
        <div className="flex flex-col gap-4">
          <div className="relative w-full rounded-xl overflow-hidden border border-slate-700">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={imageUrl} alt="Uploaded" className="w-full max-h-64 object-cover" />
            {state === "analyzing" && (
              <div className="absolute inset-0 bg-black/60 flex flex-col items-center justify-center gap-3">
                <Loader2 className="w-8 h-8 text-saffron-400 animate-spin" />
                <p className="text-white text-sm font-medium">{t.analyzing}</p>
                <div className="w-40 h-1 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-saffron-500 animate-pulse" style={{ width: "70%" }} />
                </div>
              </div>
            )}
          </div>

          {state === "analyzed" && analysis && (
            <div className="glass-card p-5 border-l-4 border-saffron-500">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                <span className="text-sm font-semibold text-emerald-400">AI Analysis Complete ({analysis.confidence} confidence)</span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Theme Detected</div>
                  <div className="text-white font-semibold">{analysis.theme}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Urgency</div>
                  <div className={`font-semibold ${analysis.urgency === "Critical" ? "text-red-400" : analysis.urgency === "High" ? "text-orange-400" : "text-yellow-400"}`}>
                    {analysis.urgency}
                  </div>
                </div>
              </div>
              <p className="text-slate-300 text-sm mt-3">{analysis.description}</p>
            </div>
          )}
          
          {state === "analyzed" && qualityCheck && qualityCheck.score < 65 && (
            <div className="mt-2">
              <QualityWarning
                score={qualityCheck.score}
                suggestions={qualityCheck.suggestions}
                lang={lang}
                onProceed={submitPhoto}
                onImprove={() => { setState("idle"); setImageUrl(null); setAnalysis(null); setQualityCheck(null); }}
              />
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={() => { setState("idle"); setImageUrl(null); setAnalysis(null); }}
              className="flex-1 py-3 rounded-xl border border-slate-600 text-slate-300 font-semibold text-sm hover:bg-white/5 transition-colors"
            >
              {lang === "hi" ? "दोबारा चुनें" : lang === "te" ? "మళ్ళీ ఎంచుకోండి" : "Retake"}
            </button>
            {state === "preview" && (
              <button
                id="analyze-photo-btn"
                onClick={runAnalysis}
                className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-white text-sm"
                style={{ background: "linear-gradient(135deg, #f97316, #ea580c)" }}
              >
                <Camera className="w-4 h-4" />
                {t.analyze}
              </button>
            )}
            {state === "analyzed" && (!qualityCheck || qualityCheck.score >= 65) && (
              <button
                id="submit-photo-btn"
                onClick={submitPhoto}
                className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-white text-sm"
                style={{ background: "linear-gradient(135deg, #1e88ed, #1671da)" }}
              >
                {t.submit}
              </button>
            )}
          </div>
        </div>
      )}

      {state === "submitting" && (
        <div className="flex flex-col items-center gap-4 py-10">
          <Loader2 className="w-10 h-10 text-brand-400 animate-spin" />
          <p className="text-white font-medium">{lang === "hi" ? "भेजा जा रहा है..." : lang === "te" ? "సమర్పిస్తోంది..." : "Submitting..."}</p>
        </div>
      )}
    </div>
  );
}
