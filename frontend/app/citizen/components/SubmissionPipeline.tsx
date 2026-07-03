"use client";

import { useEffect, useState } from "react";
import { Mic, Globe2, BrainCircuit, MapPin, CheckCircle2 } from "lucide-react";

interface Props {
  onComplete: () => void;
}

const STEPS = [
  { id: "ingest", label: "Receiving Input", icon: Mic },
  { id: "translate", label: "Translating to English", icon: Globe2 },
  { id: "classify", label: "AI Classification", icon: BrainCircuit },
  { id: "geotag", label: "Geotagging Location", icon: MapPin },
  { id: "logged", label: "Logged & Routed", icon: CheckCircle2 },
];

export default function SubmissionPipeline({ onComplete }: Props) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    // Animate through the steps to simulate processing
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < STEPS.length - 1) return prev + 1;
        clearInterval(interval);
        setTimeout(onComplete, 1500); // Wait a bit on the final step
        return prev;
      });
    }, 1200); // 1.2s per step

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-surface-900 rounded-2xl border border-slate-800 shadow-xl relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-brand-500/20" />
      <div 
        className="absolute top-0 left-0 h-1 bg-brand-500 transition-all duration-1000 ease-out"
        style={{ width: `${((currentStep + 1) / STEPS.length) * 100}%` }}
      />

      <div className="text-center mb-8">
        <h2 className="text-xl font-bold text-white mb-2">Processing Submission</h2>
        <p className="text-slate-400 text-sm">Our AI is analyzing your input...</p>
      </div>

      <div className="space-y-4">
        {STEPS.map((step, index) => {
          const Icon = step.icon;
          const isActive = index === currentStep;
          const isPast = index < currentStep;

          return (
            <div 
              key={step.id} 
              className={`flex items-center gap-4 p-4 rounded-xl border transition-all duration-500 ${
                isActive 
                  ? "bg-brand-900/30 border-brand-500/50 transform scale-105 shadow-lg shadow-brand-500/10" 
                  : isPast
                  ? "bg-emerald-900/10 border-emerald-500/20"
                  : "bg-surface-800 border-slate-700/50 opacity-50"
              }`}
            >
              <div className={`p-2 rounded-lg transition-colors duration-500 ${
                isActive ? "bg-brand-500 text-white animate-pulse" :
                isPast ? "bg-emerald-500 text-white" :
                "bg-slate-700 text-slate-400"
              }`}>
                <Icon className="w-5 h-5" />
              </div>
              
              <div className="flex-1 font-medium">
                <span className={
                  isActive ? "text-brand-300" :
                  isPast ? "text-emerald-400" :
                  "text-slate-400"
                }>
                  {step.label}
                </span>
              </div>

              {isPast && (
                <div className="text-emerald-400 animate-fade-in">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
              )}
              {isActive && (
                <div className="w-5 h-5 border-2 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
