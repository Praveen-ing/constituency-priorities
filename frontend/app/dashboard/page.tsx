"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { RefreshCw, Sliders, Map, List, Activity, LogOut } from "lucide-react";
import { auth, signOut } from "../../lib/firebase";
import { useRouter } from "next/navigation";
import PriorityList from "./components/PriorityList";
import GapScoreCard from "./components/GapScoreCard";
import WeightSliders from "./components/WeightSliders";
import ThemeDrilldown from "./components/ThemeDrilldown";
import HotspotMap from "./components/HotspotMap";
import LiveFeed from "./components/LiveFeed";
import DataChat from "./components/DataChat";
import ExportReport from "./components/ExportReport";
import AccelerationToggle from "./components/AccelerationToggle";

export interface Priority {
  priority_id: string;
  theme_id: string;
  theme_label: string;
  ward_id: string;
  ward_name: string;
  gap_score: number;
  breakdown: {
    citizen_volume_norm: number;
    urgency_norm: number;
    data_deficit_norm: number;
    population_norm: number;
    w1: number;
    w2: number;
    w3: number;
    w4: number;
  };
  justification: string;
  rank: number;
  submission_count: number;
}

export interface Weights {
  w1: number;
  w2: number;
  w3: number;
  w4: number;
}

const DEFAULT_WEIGHTS: Weights = { w1: 0.30, w2: 0.20, w3: 0.35, w4: 0.15 };

// Mock data for demo when API is unavailable
const MOCK_PRIORITIES: Priority[] = [
  {
    priority_id: "p1",
    theme_id: "education",
    theme_label: "Education",
    ward_id: "rajapuram",
    ward_name: "Rajapuram Ward",
    gap_score: 0.87,
    breakdown: { citizen_volume_norm: 0.92, urgency_norm: 0.78, data_deficit_norm: 0.95, population_norm: 0.72, w1: 0.30, w2: 0.20, w3: 0.35, w4: 0.15 },
    justification: "42 urgent submissions + school enrollment 142% of capacity + nearest alternate school 6.2km away supports HIGH priority for Rajapuram ward school expansion.",
    rank: 1,
    submission_count: 42,
  },
  {
    priority_id: "p2",
    theme_id: "water",
    theme_label: "Water Supply",
    ward_id: "old_city",
    ward_name: "Old City Ward",
    gap_score: 0.74,
    breakdown: { citizen_volume_norm: 0.65, urgency_norm: 0.85, data_deficit_norm: 0.82, population_norm: 0.58, w1: 0.30, w2: 0.20, w3: 0.35, w4: 0.15 },
    justification: "31 submissions with 85% urgency + 67% of households lack piped water access per Census data drives HIGH priority rating.",
    rank: 2,
    submission_count: 31,
  },
  {
    priority_id: "p3",
    theme_id: "roads",
    theme_label: "Roads",
    ward_id: "new_market",
    ward_name: "New Market Ward",
    gap_score: 0.61,
    breakdown: { citizen_volume_norm: 0.55, urgency_norm: 0.62, data_deficit_norm: 0.70, population_norm: 0.48, w1: 0.30, w2: 0.20, w3: 0.35, w4: 0.15 },
    justification: "26 road complaints at 6.2 per km above baseline + major connectivity gap in New Market ward.",
    rank: 3,
    submission_count: 26,
  },
  {
    priority_id: "p4",
    theme_id: "health",
    theme_label: "Health",
    ward_id: "green_valley",
    ward_name: "Green Valley Ward",
    gap_score: 0.48,
    breakdown: { citizen_volume_norm: 0.40, urgency_norm: 0.55, data_deficit_norm: 0.52, population_norm: 0.38, w1: 0.30, w2: 0.20, w3: 0.35, w4: 0.15 },
    justification: "18 submissions + PHC serving 3.2x its intended population capacity across Green Valley ward.",
    rank: 4,
    submission_count: 18,
  },
  {
    priority_id: "p5",
    theme_id: "sanitation",
    theme_label: "Sanitation",
    ward_id: "riverside",
    ward_name: "Riverside Ward",
    gap_score: 0.35,
    breakdown: { citizen_volume_norm: 0.30, urgency_norm: 0.42, data_deficit_norm: 0.38, population_norm: 0.25, w1: 0.30, w2: 0.20, w3: 0.35, w4: 0.15 },
    justification: "12 sanitation complaints + 38% of households lack toilets per Census data — moderate priority.",
    rank: 5,
    submission_count: 12,
  },
];

export default function DashboardPage() {
  const [priorities, setPriorities] = useState<Priority[]>(MOCK_PRIORITIES);
  const [selected, setSelected] = useState<Priority | null>(MOCK_PRIORITIES[0]);
  const [weights, setWeights] = useState<Weights>(DEFAULT_WEIGHTS);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"list" | "map">("list");
  const [showWeights, setShowWeights] = useState(false);
  const [useGpu, setUseGpu] = useState(false);
  const [lastElapsedMs, setLastElapsedMs] = useState<number | undefined>(undefined);
  const [lastAccelerated, setLastAccelerated] = useState<boolean | undefined>(undefined);
  const router = useRouter();
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const fetchPriorities = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/priorities?limit=20`);
      if (res.ok) {
        const data = await res.json();
        if (data.priorities?.length) {
          setPriorities(data.priorities);
          setSelected(data.priorities[0]);
        }
      }
    } catch {
      // Use mock data if API unavailable
    } finally {
      setLoading(false);
    }
  };

  const recompute = async () => {
    setLoading(true);
    const t0 = performance.now();
    try {
      const res = await fetch(`${apiBase}/priorities/recompute?use_gpu=${useGpu}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(weights),
      });
      const elapsed = Math.round(performance.now() - t0);
      setLastElapsedMs(elapsed);
      setLastAccelerated(useGpu);
      // Optimistic update — recompute weights locally on mock data
      const updated = applyWeightsLocally(priorities, weights);
      setPriorities(updated);
      setSelected(updated[0]);
    } catch {
      const elapsed = Math.round(performance.now() - t0);
      setLastElapsedMs(elapsed);
      setLastAccelerated(false);
      const updated = applyWeightsLocally(priorities, weights);
      setPriorities(updated);
      setSelected(updated[0]);
    } finally {
      setLoading(false);
    }
  };

  function applyWeightsLocally(ps: Priority[], w: Weights): Priority[] {
    const scored = ps.map((p) => ({
      ...p,
      gap_score:
        w.w1 * p.breakdown.citizen_volume_norm +
        w.w2 * p.breakdown.urgency_norm +
        w.w3 * p.breakdown.data_deficit_norm +
        w.w4 * p.breakdown.population_norm,
      breakdown: { ...p.breakdown, ...w },
    }));
    return scored
      .sort((a, b) => b.gap_score - a.gap_score)
      .map((p, i) => ({ ...p, rank: i + 1 }));
  }

  useEffect(() => { fetchPriorities(); }, []);

  const totalSubmissions = priorities.reduce((s, p) => s + p.submission_count, 0);

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      router.push("/login");
    } catch (err) {
      console.error("Sign out error", err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Top nav ── */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-surface-900/80 backdrop-blur-sm sticky top-0 z-10">
        <Link href="/" className="text-xl font-bold gradient-text">Jan Awaaz</Link>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500 hidden md:block">MP Dashboard · Hyderabad Constituency</span>
          <button
            onClick={handleSignOut}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
            title="Sign Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
          <div className="w-px h-5 bg-slate-800 mx-1" />
          <button
            id="toggle-weights-btn"
            onClick={() => setShowWeights((v) => !v)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${showWeights ? "bg-brand-700 text-white" : "text-slate-400 hover:text-white hover:bg-white/5"}`}
          >
            <Sliders className="w-4 h-4" />
            <span className="hidden sm:inline">Weights</span>
          </button>
          
          <ExportReport priorities={priorities} />

          <button
            id="recompute-btn"
            onClick={recompute}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            <span className="hidden sm:inline">{loading ? "Computing..." : "Recompute"}</span>
          </button>
        </div>
      </header>

      {/* ── Weight sliders + Acceleration Toggle ── */}
      {showWeights && (
        <div className="border-b border-slate-800 bg-surface-800 px-6 py-4 animate-slide-up">
          <div className="flex flex-col lg:flex-row gap-6 items-start">
            <div className="flex-1">
              <WeightSliders weights={weights} onChange={setWeights} />
            </div>
            <div className="shrink-0">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Compute Engine</div>
              <AccelerationToggle
                useGpu={useGpu}
                onChange={setUseGpu}
                lastElapsedMs={lastElapsedMs}
                lastAccelerated={lastAccelerated}
              />
            </div>
          </div>
        </div>
      )}


      {/* ── Stats bar ── */}
      <div className="grid grid-cols-3 divide-x divide-slate-800 border-b border-slate-800 bg-surface-800/50">
        {[
          { label: "Total Submissions", value: totalSubmissions, icon: Activity },
          { label: "Priority Areas", value: priorities.length, icon: List },
          { label: "Top Gap Score", value: `${(priorities[0]?.gap_score * 100 || 0).toFixed(0)}%`, icon: Map },
        ].map(({ label, value, icon: Icon }) => (
          <div key={label} className="flex items-center gap-3 px-6 py-3">
            <Icon className="w-4 h-4 text-brand-400 shrink-0" />
            <div>
              <div className="text-lg font-bold text-white">{value}</div>
              <div className="text-xs text-slate-500">{label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* ── Main content ── */}
      <div className="flex flex-1 overflow-hidden">
        {/* Priority list */}
        <aside className="w-full md:w-96 border-r border-slate-800 overflow-y-auto shrink-0">
          <div className="px-4 py-3 border-b border-slate-800 flex items-center gap-2">
            <List className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-semibold text-slate-300">Priority Rankings</span>
          </div>
          <PriorityList
            priorities={priorities}
            selected={selected}
            onSelect={setSelected}
          />
        </aside>

        {/* Detail panel */}
        <main className="flex-1 overflow-y-auto p-6">
          {selected ? (
            <div className="animate-fade-in max-w-2xl">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-brand-400">RANK #{selected.rank}</span>
                    <span className="text-xs text-slate-600">·</span>
                    <span className="text-xs text-slate-400">{selected.ward_name}</span>
                  </div>
                  <h2 className="text-2xl font-bold text-white">{selected.theme_label}</h2>
                </div>
                <div className="flex flex-col items-end">
                  <div
                    className="text-3xl font-black"
                    style={{ color: selected.gap_score > 0.7 ? "#f87171" : selected.gap_score > 0.5 ? "#fb923c" : "#34d399" }}
                  >
                    {(selected.gap_score * 100).toFixed(0)}
                  </div>
                  <div className="text-xs text-slate-500">Gap Score / 100</div>
                </div>
              </div>

              {/* Justification */}
              <div className="glass-card p-5 mb-6 border-l-4 border-brand-500">
                <div className="text-xs text-brand-400 font-semibold mb-2 uppercase tracking-wider">AI Justification</div>
                <p className="text-slate-200 leading-relaxed">{selected.justification}</p>
              </div>

              {/* Gap Score breakdown */}
              <GapScoreCard priority={selected} />

              {/* Hotspot Map */}
              <HotspotMap priority={selected} />

              {/* Submissions Drilldown */}
              <ThemeDrilldown priority={selected} />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-600">
              <p>Select a priority to view details</p>
            </div>
          )}
        </main>

        {/* Live Feed Sidebar (Right) */}
        <aside className="w-80 border-l border-slate-800 hidden xl:block bg-surface-900 overflow-hidden shrink-0">
          <LiveFeed />
        </aside>
      </div>

      {/* Ask the Data Chat Bot */}
      <DataChat priorities={priorities} />
    </div>
  );
}
