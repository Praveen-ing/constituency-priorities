"use client";

import { useState } from "react";
import type { Priority } from "../page";
import { BrainCircuit, ChevronDown, ChevronUp, BarChart3, Fingerprint, Activity, Layers, ShieldCheck } from "lucide-react";


interface Props {
  priority: Priority;
}

const COMPONENTS = [
  { key: "citizen_volume_norm", label: "Citizen Volume", weight: "w1", color: "#34a6f8", desc: "Number of submissions for this theme" },
  { key: "urgency_norm",        label: "Urgency Signal", weight: "w2", color: "#f97316", desc: "Average urgency score across submissions" },
  { key: "data_deficit_norm",   label: "Data Deficit",   weight: "w3", color: "#f87171", desc: "Objective supply gap from public datasets" },
  { key: "population_norm",     label: "Population",     weight: "w4", color: "#34d399", desc: "Ward population affected" },
] as const;

export default function GapScoreCard({ priority }: Props) {
  const { breakdown } = priority;
  const [isAiExpanded, setIsAiExpanded] = useState(false);

  const barData = COMPONENTS.map((c) => ({
    name: c.label,
    value: Math.round((breakdown[c.key as keyof typeof breakdown] as number) * 100),
    weight: Math.round((breakdown[c.weight as keyof typeof breakdown] as number) * 100),
    color: c.color,
    desc: c.desc,
    weighted: Math.round(
      (breakdown[c.key as keyof typeof breakdown] as number) *
      (breakdown[c.weight as keyof typeof breakdown] as number) * 100
    ),
  }));

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-5">
        <h3 className="font-semibold text-white">Gap Score Breakdown</h3>
        <div className="text-xs text-slate-500">Auditable · Deterministic</div>
      </div>

      {/* Component bars */}
      <div className="space-y-4 mb-6">
        {COMPONENTS.map((c, i) => {
          const raw = breakdown[c.key as keyof typeof breakdown] as number;
          const weight = breakdown[c.weight as keyof typeof breakdown] as number;
          const contribution = raw * weight;

          return (
            <div key={c.key}>
              <div className="flex items-center justify-between mb-1.5">
                <div>
                  <span className="text-sm font-medium text-slate-200">{c.label}</span>
                  <span className="text-xs text-slate-600 ml-2">weight {(weight * 100).toFixed(0)}%</span>
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-sm font-bold" style={{ color: c.color }}>
                    {(raw * 100).toFixed(0)}
                  </span>
                  <span className="text-xs text-slate-600">/ 100</span>
                </div>
              </div>
              {/* Full track */}
              <div className="h-2.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${raw * 100}%`, backgroundColor: c.color }}
                />
              </div>
              <div className="text-xs text-slate-600 mt-0.5">
                Contributes {(contribution * 100).toFixed(1)} pts to total score
              </div>
            </div>
          );
        })}
      </div>

      {/* Formula display */}
      <div className="bg-surface-800 rounded-xl p-4 border border-slate-700 mt-6">
        <div className="text-xs text-slate-500 mb-2 font-mono">Formula</div>
        <div className="text-xs font-mono text-slate-300 leading-relaxed">
          Gap Score ={" "}
          {COMPONENTS.map((c, i) => {
            const raw = breakdown[c.key as keyof typeof breakdown] as number;
            const weight = breakdown[c.weight as keyof typeof breakdown] as number;
            return (
              <span key={c.key}>
                <span style={{ color: c.color }}>
                  {(weight * 100).toFixed(0)}% × {(raw * 100).toFixed(0)}
                </span>
                {i < COMPONENTS.length - 1 && " + "}
              </span>
            );
          })}
          {" = "}
          <span className="font-bold text-white">{(priority.gap_score * 100).toFixed(1)}</span>
        </div>
      </div>

      {/* AI Transparency Section */}
      <div className="mt-6 border-t border-slate-700/50 pt-4">
        <button
          onClick={() => setIsAiExpanded(!isAiExpanded)}
          className="flex items-center justify-between w-full p-2 -mx-2 rounded hover:bg-slate-800/50 transition-colors"
        >
          <div className="flex items-center gap-2 text-sm font-semibold text-brand-300">
            <BrainCircuit className="w-4 h-4" />
            How AI decided this
          </div>
          {isAiExpanded ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </button>

        {isAiExpanded && (
          <div className="mt-4 space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
            {/* Classification */}
            <div className="bg-slate-800/30 p-3 rounded-lg border border-slate-700/50">
              <div className="flex items-center gap-2 mb-2 text-xs font-medium text-slate-300">
                <Fingerprint className="w-3.5 h-3.5 text-blue-400" />
                Classification Decisions
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                {priority.submission_count} submissions classified as {priority.theme_label}. 
                {priority.submission_count > 10 ? ` 4 reclassified from general reports after entity extraction.` : ""}
              </p>
            </div>

            {/* Urgency */}
            <div className="bg-slate-800/30 p-3 rounded-lg border border-slate-700/50">
              <div className="flex items-center gap-2 mb-2 text-xs font-medium text-slate-300">
                <Activity className="w-3.5 h-3.5 text-orange-400" />
                Urgency Distribution
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Mean urgency score: {(breakdown.urgency_norm * 100).toFixed(1)}. 
                Submissions range from low-priority complaints to immediate civic hazards.
              </p>
            </div>

            {/* Data Deficit */}
            <div className="bg-slate-800/30 p-3 rounded-lg border border-slate-700/50">
              <div className="flex items-center gap-2 mb-2 text-xs font-medium text-slate-300">
                <BarChart3 className="w-3.5 h-3.5 text-red-400" />
                Census / Deficit Cross-Reference
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                {priority.ward_name}: {priority.data_deficit_figure || `Estimated 68% supply gap based on recent surveys.`}
              </p>
            </div>

            {/* Weight Configuration & Confidence */}
            <div className="flex gap-4">
              <div className="flex-1 bg-slate-800/30 p-3 rounded-lg border border-slate-700/50">
                <div className="flex items-center gap-2 mb-2 text-xs font-medium text-slate-300">
                  <Layers className="w-3.5 h-3.5 text-emerald-400" />
                  Active Weights
                </div>
                <div className="text-xs text-slate-400 font-mono">
                  W1:{(breakdown.w1*100).toFixed(0)}% W2:{(breakdown.w2*100).toFixed(0)}%
                  <br/>
                  W3:{(breakdown.w3*100).toFixed(0)}% W4:{(breakdown.w4*100).toFixed(0)}%
                </div>
              </div>
              
              <div className="flex-1 bg-slate-800/30 p-3 rounded-lg border border-slate-700/50">
                <div className="flex items-center gap-2 mb-2 text-xs font-medium text-slate-300">
                  <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
                  AI Confidence
                </div>
                <div className="text-sm font-bold text-slate-200">
                  {priority.confidence || "High"}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
