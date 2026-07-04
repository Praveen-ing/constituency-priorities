"use client";

import { useEffect, useState } from "react";
import { Mic, FileText, Image as ImageIcon, Bell } from "lucide-react";

interface FeedItem {
  id: string;
  type: "text" | "audio" | "image";
  content: string;
  ward: string;
  time: string;
  isNew: boolean;
}

export default function LiveFeed() {
  const [items, setItems] = useState<FeedItem[]>([]);
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    let isMounted = true;
    let previousIds = new Set<string>();

    const fetchSubmissions = async () => {
      try {
        const res = await fetch(`${apiBase}/submissions?limit=10`);
        if (!res.ok) return;
        const data = await res.json();
        if (!isMounted) return;

        const newItems: FeedItem[] = data.map((sub: any) => ({
          id: sub.id,
          type: sub.media_type || "text",
          content: sub.content || "Submission received",
          ward: sub.ward_id ? sub.ward_id.replace("_", " ") : "Unknown Ward",
          time: new Date(sub.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isNew: !previousIds.has(sub.id) && previousIds.size > 0, // Flag as new if it wasn't in previous fetch
        }));

        setItems(newItems);
        previousIds = new Set(newItems.map(item => item.id));

        // Clear the 'isNew' flag after animation
        if (newItems.some(i => i.isNew)) {
          setTimeout(() => {
            if (isMounted) {
              setItems(current => current.map(item => ({ ...item, isNew: false })));
            }
          }, 3000);
        }
      } catch (err) {
        console.error("Failed to fetch live feed", err);
      }
    };

    fetchSubmissions();
    const interval = setInterval(fetchSubmissions, 10000);
    
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [apiBase]);

  return (
    <div className="glass-card flex flex-col h-[500px]">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between sticky top-0 bg-surface-900/90 backdrop-blur z-10 rounded-t-xl">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-brand-500"></span>
          </span>
          Live Feed
        </h3>
        <button className="text-slate-400 hover:text-white transition-colors">
          <Bell className="w-4 h-4" />
        </button>
      </div>

      <div className="p-4 flex-1 overflow-y-auto space-y-3 custom-scrollbar">
        {items.map((item) => (
          <div 
            key={item.id} 
            className={`p-3 rounded-lg border transition-all duration-500 ${
              item.isNew 
                ? "bg-brand-900/30 border-brand-500/50 transform translate-x-0 opacity-100" 
                : "bg-surface-800 border-slate-700/50"
            }`}
            style={item.isNew ? { animation: 'slideInRight 0.5s ease-out forwards' } : {}}
          >
            <div className="flex items-start gap-3">
              <div className={`mt-0.5 p-1.5 rounded-md ${
                item.type === 'audio' ? 'bg-blue-500/10 text-blue-400' :
                item.type === 'image' ? 'bg-purple-500/10 text-purple-400' :
                'bg-emerald-500/10 text-emerald-400'
              }`}>
                {item.type === "audio" && <Mic className="w-3.5 h-3.5" />}
                {item.type === "image" && <ImageIcon className="w-3.5 h-3.5" />}
                {item.type === "text" && <FileText className="w-3.5 h-3.5" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-slate-200 font-medium truncate">
                  {item.content}
                </p>
                <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                  <span className="truncate">{item.ward}</span>
                  <span>•</span>
                  <span>{item.time}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Global CSS for animation */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #334155;
          border-radius: 4px;
        }
      `}} />
    </div>
  );
}
