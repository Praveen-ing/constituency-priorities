"use client";

import { useState } from "react";
import { TrendingUp, TrendingDown, Minus, Activity, ChevronDown, ChevronUp } from "lucide-react";

interface HealthScoreComponent {
  name: string;
  score: number;
  weight: number;
}

export interface HealthScoreData {
  score: number;
  trend: "up" | "down" | "flat";
  explanation: string;
  components: HealthScoreComponent[];
}

interface Props {
  data: HealthScoreData | null;
}

export default function HealthScore({ data }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (!data) return null;

  return (
    <div className="bg-surface-800/80 border border-slate-700/50 rounded-xl p-6 shadow-lg relative overflow-hidden mb-6">
      {/* Background glow based on score */}
      <div 
        className="absolute top-0 right-0 w-64 h-64 blur-3xl opacity-10 pointer-events-none transform translate-x-1/2 -translate-y-1/2 rounded-full"
        style={{ backgroundColor: data.score > 70 ? '#34d399' : data.score > 40 ? '#fb923c' : '#f87171' }}
      />

      <div className="flex flex-col md:flex-row gap-6 items-start md:items-center relative z-10">
        
        {/* Score Display */}
        <div className="flex flex-col items-center justify-center shrink-0">
          <div className="text-sm font-semibold text-slate-400 uppercase tracking-widest mb-1 flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Health Score
          </div>
          <div className="flex items-end gap-2">
            <span 
              className="text-6xl font-black tracking-tighter"
              style={{ color: data.score > 70 ? '#34d399' : data.score > 40 ? '#fb923c' : '#f87171' }}
            >
              {data.score}
            </span>
            <span className="text-xl text-slate-500 mb-2">/100</span>
          </div>
          <div className="flex items-center gap-1 mt-1">
            {data.trend === "up" && <TrendingUp className="w-4 h-4 text-emerald-400" />}
            {data.trend === "down" && <TrendingDown className="w-4 h-4 text-red-400" />}
            {data.trend === "flat" && <Minus className="w-4 h-4 text-slate-400" />}
            <span className="text-xs font-medium text-slate-400">
              {data.trend === "up" ? "Improving" : data.trend === "down" ? "Declining" : "Stable"}
            </span>
          </div>
        </div>

        {/* Separator */}
        <div className="hidden md:block w-px h-24 bg-slate-700/50" />

        {/* Explanation */}
        <div className="flex-1">
          <p className="text-slate-200 leading-relaxed text-sm">
            {data.explanation}
          </p>
          
          <button 
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs font-semibold text-brand-400 hover:text-brand-300 mt-4 transition-colors"
          >
            {expanded ? "Hide Score Breakdown" : "View Score Breakdown"}
            {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {/* Expanded Components Breakdown */}
      {expanded && (
        <div className="mt-6 pt-5 border-t border-slate-700/50 animate-in fade-in slide-in-from-top-2">
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {data.components.map((comp) => (
              <div key={comp.name} className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/30">
                <div className="text-xs text-slate-500 mb-1">{comp.name}</div>
                <div className="flex items-baseline justify-between">
                  <div className="text-lg font-bold text-slate-200">{comp.score.toFixed(0)}</div>
                  <div className="text-[10px] text-brand-500/70 font-mono bg-brand-900/20 px-1.5 py-0.5 rounded">
                    w: {(comp.weight * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
