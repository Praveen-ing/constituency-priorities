"use client";

import { useState } from "react";
import { Zap, Cpu } from "lucide-react";

interface Props {
  useGpu: boolean;
  onChange: (useGpu: boolean) => void;
  lastElapsedMs?: number;
  lastAccelerated?: boolean;
}

export default function AccelerationToggle({ useGpu, onChange, lastElapsedMs, lastAccelerated }: Props) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-3 bg-surface-800 border border-slate-700 rounded-xl px-4 py-2.5">
        {/* CPU side */}
        <div className={`flex items-center gap-1.5 text-sm font-medium transition-colors ${!useGpu ? "text-white" : "text-slate-500"}`}>
          <Cpu className="w-4 h-4" />
          <span className="hidden sm:inline">CPU</span>
        </div>

        {/* Toggle */}
        <button
          id="acceleration-toggle"
          onClick={() => onChange(!useGpu)}
          className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
            useGpu ? "bg-green-500" : "bg-slate-600"
          }`}
          aria-label="Toggle GPU Acceleration"
        >
          <span
            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out ${
              useGpu ? "translate-x-5" : "translate-x-0"
            }`}
          />
        </button>

        {/* GPU side */}
        <div className={`flex items-center gap-1.5 text-sm font-semibold transition-colors ${useGpu ? "text-green-400" : "text-slate-500"}`}>
          <Zap className={`w-4 h-4 ${useGpu ? "animate-pulse" : ""}`} />
          <span className="hidden sm:inline">NVIDIA GPU</span>
        </div>
      </div>

      {/* Timing badge — shown after a recompute */}
      {lastElapsedMs !== undefined && (
        <div className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg border ${
          lastAccelerated
            ? "bg-green-900/20 border-green-500/30 text-green-400"
            : "bg-slate-800 border-slate-700 text-slate-400"
        }`}>
          {lastAccelerated ? (
            <>
              <Zap className="w-3 h-3 shrink-0" />
              <span>NVIDIA cuDF: <strong>{lastElapsedMs}ms</strong> — 5M rows</span>
            </>
          ) : (
            <>
              <Cpu className="w-3 h-3 shrink-0" />
              <span>Standard pandas: <strong>{lastElapsedMs}ms</strong> — 5M rows</span>
            </>
          )}
        </div>
      )}

      {/* Label */}
      <p className="text-xs text-slate-500 text-center">
        {useGpu ? "Accelerated via NVIDIA RAPIDS cuDF" : "Standard pandas (benchmark mode)"}
      </p>
    </div>
  );
}
