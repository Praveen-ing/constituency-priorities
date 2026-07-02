"use client";

import type { Weights } from "../page";

interface Props {
  weights: Weights;
  onChange: (w: Weights) => void;
}

const SLIDERS = [
  { key: "w1" as keyof Weights, label: "Citizen Volume",  color: "#34a6f8", desc: "Weight given to # of submissions" },
  { key: "w2" as keyof Weights, label: "Urgency Signal",  color: "#f97316", desc: "Weight given to urgency score" },
  { key: "w3" as keyof Weights, label: "Data Deficit",    color: "#f87171", desc: "Weight given to public data gap" },
  { key: "w4" as keyof Weights, label: "Population",      color: "#34d399", desc: "Weight given to population affected" },
];

export default function WeightSliders({ weights, onChange }: Props) {
  const total = weights.w1 + weights.w2 + weights.w3 + weights.w4;

  const handleChange = (key: keyof Weights, value: number) => {
    onChange({ ...weights, [key]: value });
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">Adjust Priority Weights</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${Math.abs(total - 1) < 0.01 ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"}`}>
          {Math.abs(total - 1) < 0.01 ? "✓ Weights sum to 100%" : `Weights sum to ${(total * 100).toFixed(0)}%`}
        </span>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        {SLIDERS.map(({ key, label, color, desc }) => (
          <div key={key}>
            <div className="flex items-center justify-between mb-1.5">
              <div>
                <span className="text-sm font-medium text-slate-200">{label}</span>
                <p className="text-xs text-slate-600">{desc}</p>
              </div>
              <span className="text-sm font-mono font-bold" style={{ color }}>
                {(weights[key] * 100).toFixed(0)}%
              </span>
            </div>
            <input
              id={`slider-${key}`}
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={weights[key]}
              onChange={(e) => handleChange(key, parseFloat(e.target.value))}
              className="w-full h-2 rounded-full appearance-none cursor-pointer"
              style={{
                background: `linear-gradient(to right, ${color} 0%, ${color} ${weights[key] * 100}%, #1e2d47 ${weights[key] * 100}%, #1e2d47 100%)`,
              }}
            />
          </div>
        ))}
      </div>

      <p className="text-xs text-slate-600 mt-3">
        Click <strong className="text-slate-400">Recompute</strong> to see rankings update with these weights.
        The formula remains deterministic — only the emphasis shifts.
      </p>
    </div>
  );
}
