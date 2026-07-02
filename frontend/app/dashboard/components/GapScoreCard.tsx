"use client";

import type { Priority } from "../page";


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
      <div className="bg-surface-800 rounded-xl p-4 border border-slate-700">
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
    </div>
  );
}
