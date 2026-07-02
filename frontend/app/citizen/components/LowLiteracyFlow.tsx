"use client";

import { useState } from "react";
import { ArrowLeft, Check } from "lucide-react";

interface Props {
  lang: string;
  onBack: () => void;
  onSubmitted: (id: string) => void;
}

const ISSUES = [
  { id: "school", emoji: "🏫", en: "School", hi: "स्कूल", te: "పాఠశాల", theme: "education" },
  { id: "water", emoji: "💧", en: "Water", hi: "पानी", te: "నీరు", theme: "water" },
  { id: "road", emoji: "🛣️", en: "Road", hi: "सड़क", te: "రోడ్డు", theme: "roads" },
  { id: "hospital", emoji: "🏥", en: "Hospital", hi: "अस्पताल", te: "ఆసుపత్రి", theme: "health" },
  { id: "toilet", emoji: "🚽", en: "Toilet", hi: "शौचालय", te: "మరుగుదొడ్డి", theme: "sanitation" },
  { id: "light", emoji: "💡", en: "Electricity", hi: "बिजली", te: "విద్యుత్", theme: "electricity" },
  { id: "house", emoji: "🏠", en: "Housing", hi: "घर", te: "ఇల్లు", theme: "housing" },
  { id: "jobs", emoji: "💼", en: "Jobs", hi: "रोज़गार", te: "ఉద్యోగాలు", theme: "employment" },
] as const;

const URGENCY_OPTIONS = [
  { id: "low", emoji: "🟡", en: "Minor", hi: "थोड़ा", te: "కొంచెం", value: 0.3 },
  { id: "medium", emoji: "🟠", en: "Moderate", hi: "मध्यम", te: "మధ్యస్థ", value: 0.6 },
  { id: "high", emoji: "🔴", en: "Urgent!", hi: "तत्काल!", te: "అత్యవసరం!", value: 0.9 },
] as const;

type Step = "issue" | "urgency" | "confirm";

export default function LowLiteracyFlow({ lang, onBack, onSubmitted }: Props) {
  const [step, setStep] = useState<Step>("issue");
  const [selectedIssue, setSelectedIssue] = useState<(typeof ISSUES)[number] | null>(null);
  const [selectedUrgency, setSelectedUrgency] = useState<(typeof URGENCY_OPTIONS)[number] | null>(null);
  const [loading, setLoading] = useState(false);

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const label = (item: { en: string; hi: string; te: string }) =>
    lang === "hi" ? item.hi : lang === "te" ? item.te : item.en;

  const submit = async () => {
    if (!selectedIssue || !selectedUrgency) return;
    setLoading(true);
    const text = `Icon submission: ${selectedIssue.en} issue, urgency: ${selectedUrgency.en}`;
    try {
      const res = await fetch(`${apiBase}/submissions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          media_type: "text",
          content: text,
          original_language: lang === "hi" ? "hi-IN" : lang === "te" ? "te-IN" : "en-IN",
          source: "web",
        }),
      });
      const data = await res.json();
      onSubmitted(data.id);
    } catch {
      alert("Submission failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <button onClick={step === "issue" ? onBack : () => setStep("issue")} className="flex items-center gap-2 text-slate-400 hover:text-white mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span className="text-sm">{step === "issue" ? "Back" : "Change issue"}</span>
      </button>

      {/* Progress dots */}
      <div className="flex justify-center gap-2 mb-8">
        {(["issue", "urgency", "confirm"] as Step[]).map((s) => (
          <div key={s} className={`h-2 rounded-full transition-all duration-300 ${step === s ? "w-8 bg-brand-500" : "w-2 bg-slate-700"}`} />
        ))}
      </div>

      {step === "issue" && (
        <>
          <h2 className="text-xl font-semibold text-white text-center mb-8">
            {lang === "hi" ? "क्या समस्या है?" : lang === "te" ? "సమస్య ఏమిటి?" : "What is the issue?"}
          </h2>
          <div className="grid grid-cols-2 gap-4">
            {ISSUES.map((issue) => (
              <button
                key={issue.id}
                id={`icon-${issue.id}`}
                onClick={() => { setSelectedIssue(issue); setStep("urgency"); }}
                className="glass-card p-5 flex flex-col items-center gap-3 hover:border-brand-500/50 hover:scale-105 transition-all duration-200"
              >
                <span className="text-4xl">{issue.emoji}</span>
                <span className="text-sm font-semibold text-slate-200">{label(issue)}</span>
              </button>
            ))}
          </div>
        </>
      )}

      {step === "urgency" && selectedIssue && (
        <>
          <div className="flex flex-col items-center mb-8">
            <span className="text-6xl mb-3">{selectedIssue.emoji}</span>
            <h2 className="text-xl font-semibold text-white text-center">
              {lang === "hi" ? "कितनी जरूरी है?" : lang === "te" ? "ఎంత అత్యవసరం?" : "How urgent?"}
            </h2>
          </div>
          <div className="flex flex-col gap-4">
            {URGENCY_OPTIONS.map((u) => (
              <button
                key={u.id}
                id={`urgency-${u.id}`}
                onClick={() => { setSelectedUrgency(u); setStep("confirm"); }}
                className="glass-card p-5 flex items-center gap-4 hover:border-slate-500 hover:scale-[1.02] transition-all duration-200 text-left"
              >
                <span className="text-3xl">{u.emoji}</span>
                <span className="text-lg font-semibold text-white">{label(u)}</span>
              </button>
            ))}
          </div>
        </>
      )}

      {step === "confirm" && selectedIssue && selectedUrgency && (
        <>
          <h2 className="text-xl font-semibold text-white text-center mb-8">
            {lang === "hi" ? "क्या यह सही है?" : lang === "te" ? "ఇది సరైనదా?" : "Confirm your submission"}
          </h2>
          <div className="glass-card p-6 mb-6 flex flex-col items-center gap-4">
            <span className="text-5xl">{selectedIssue.emoji}</span>
            <div className="text-center">
              <div className="text-xl font-bold text-white">{label(selectedIssue)}</div>
              <div className="text-slate-400 mt-1">{selectedUrgency.emoji} {label(selectedUrgency)}</div>
            </div>
          </div>
          <button
            id="confirm-icon-submit"
            onClick={submit}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-4 rounded-xl font-semibold text-white transition-all hover:scale-[1.02] disabled:opacity-40"
            style={{ background: "linear-gradient(135deg, #1e88ed, #1671da)" }}
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Check className="w-5 h-5" />
            )}
            {lang === "hi" ? "जमा करें" : lang === "te" ? "సమర్పించు" : "Submit"}
          </button>
        </>
      )}
    </div>
  );
}
