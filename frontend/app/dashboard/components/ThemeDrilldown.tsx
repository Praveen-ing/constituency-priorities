"use client";

import { useEffect, useState } from "react";
import { Mic, Image as ImageIcon, FileText } from "lucide-react";
import type { Priority } from "../page";

interface Submission {
  id: string;
  created_at: string;
  media_type: "text" | "audio" | "image";
  original_content: string;
  original_language: string;
  translated_text: string;
  theme: string;
  urgency: number;
  ward_id: string;
}

interface Props {
  priority: Priority;
}

export default function ThemeDrilldown({ priority }: Props) {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, we'd fetch from `/api/submissions?theme=${priority.theme_id}&ward=${priority.ward_id}`
    // For the demo, we fetch the generated mock JSON and filter it
    const fetchMocks = async () => {
      setLoading(true);
      try {
        const res = await fetch("/mock_submissions.json");
        if (res.ok) {
          const all: Submission[] = await res.json();
          const filtered = all.filter(
            (s) => s.theme === priority.theme_id && s.ward_id === priority.ward_id
          );
          // Just taking top 10 for display performance
          setSubmissions(filtered.slice(0, 10));
        }
      } catch (err) {
        console.error("Failed to load mock submissions", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMocks();
  }, [priority]);

  if (loading) {
    return (
      <div className="glass-card p-5 mt-6 animate-pulse">
        <div className="h-6 w-1/3 bg-slate-800 rounded mb-4" />
        <div className="space-y-3">
          <div className="h-20 w-full bg-slate-800 rounded" />
          <div className="h-20 w-full bg-slate-800 rounded" />
        </div>
      </div>
    );
  }

  if (submissions.length === 0) {
    return (
      <div className="glass-card p-5 mt-6 text-center text-slate-500 text-sm">
        No raw submissions found for this specific area in the mock dataset.
      </div>
    );
  }

  return (
    <div className="glass-card p-5 mt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white flex items-center gap-2">
          Raw Citizen Submissions
        </h3>
        <span className="text-xs text-brand-400 bg-brand-900/30 px-2 py-1 rounded-full border border-brand-500/20">
          Showing recent
        </span>
      </div>

      <div className="space-y-3">
        {submissions.map((sub) => (
          <div key={sub.id} className="bg-surface-800 border border-slate-700 p-4 rounded-xl relative overflow-hidden group">
            {/* Urgency indicator line */}
            <div 
              className="absolute left-0 top-0 bottom-0 w-1"
              style={{ backgroundColor: sub.urgency > 0.7 ? '#f87171' : sub.urgency > 0.4 ? '#fb923c' : '#34d399' }}
            />

            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2 text-xs text-slate-400">
                {sub.media_type === "audio" && <Mic className="w-3.5 h-3.5 text-blue-400" />}
                {sub.media_type === "image" && <ImageIcon className="w-3.5 h-3.5 text-purple-400" />}
                {sub.media_type === "text" && <FileText className="w-3.5 h-3.5 text-emerald-400" />}
                <span>{new Date(sub.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</span>
                <span>•</span>
                <span className="uppercase text-[10px] tracking-wider">{sub.original_language.split('-')[0]}</span>
              </div>
              <div className="text-xs font-mono" style={{ color: sub.urgency > 0.7 ? '#f87171' : sub.urgency > 0.4 ? '#fb923c' : '#34d399' }}>
                Urgency: {(sub.urgency * 100).toFixed(0)}%
              </div>
            </div>

            <p className="text-sm font-medium text-slate-200 mb-1 leading-relaxed">
              "{sub.translated_text}"
            </p>
            
            {sub.original_language !== "en-IN" && (
              <p className="text-xs text-slate-500 italic">
                Original: {sub.original_content}
              </p>
            )}
          </div>
        ))}
      </div>
      
      <button className="w-full mt-4 py-2 text-sm text-brand-400 hover:text-brand-300 transition-colors font-medium">
        View all {priority.submission_count} submissions →
      </button>
    </div>
  );
}
