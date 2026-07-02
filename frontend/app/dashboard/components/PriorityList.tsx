"use client";

import type { Priority } from "../page";

interface Props {
  priorities: Priority[];
  selected: Priority | null;
  onSelect: (p: Priority) => void;
}

const THEME_EMOJI: Record<string, string> = {
  education: "🏫",
  water: "💧",
  roads: "🛣️",
  health: "🏥",
  sanitation: "🚽",
  electricity: "💡",
  housing: "🏠",
  employment: "💼",
  other: "📋",
};

function GapBar({ score }: { score: number }) {
  const color =
    score > 0.7 ? "#f87171" : score > 0.5 ? "#fb923c" : "#34d399";
  return (
    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mt-2">
      <div
        className="h-full rounded-full transition-all duration-700"
        style={{ width: `${score * 100}%`, backgroundColor: color }}
      />
    </div>
  );
}

export default function PriorityList({ priorities, selected, onSelect }: Props) {
  return (
    <div className="divide-y divide-slate-800">
      {priorities.map((p) => {
        const isSelected = selected?.priority_id === p.priority_id;
        const color = p.gap_score > 0.7 ? "#f87171" : p.gap_score > 0.5 ? "#fb923c" : "#34d399";

        return (
          <button
            key={p.priority_id}
            id={`priority-${p.priority_id}`}
            onClick={() => onSelect(p)}
            className={`w-full text-left px-4 py-4 transition-all duration-150 ${
              isSelected
                ? "bg-brand-900/40 border-l-2 border-brand-500"
                : "hover:bg-white/3 border-l-2 border-transparent"
            }`}
          >
            <div className="flex items-start gap-3">
              {/* Rank badge */}
              <div
                className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-black shrink-0 mt-0.5"
                style={{
                  backgroundColor: p.rank === 1 ? "rgba(248,113,113,0.2)" : "rgba(100,116,139,0.2)",
                  color: p.rank === 1 ? "#f87171" : "#94a3b8",
                }}
              >
                {p.rank}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span>{THEME_EMOJI[p.theme_id] ?? "📋"}</span>
                  <span className="font-semibold text-white text-sm truncate">{p.theme_label}</span>
                </div>
                <div className="text-xs text-slate-500 truncate mb-1">{p.ward_name}</div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-600">{p.submission_count} submissions</span>
                  <span className="text-xs font-mono font-bold" style={{ color }}>
                    {(p.gap_score * 100).toFixed(0)}%
                  </span>
                </div>
                <GapBar score={p.gap_score} />
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}
