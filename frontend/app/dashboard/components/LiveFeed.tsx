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

  // Simulate real-time incoming submissions
  useEffect(() => {
    // Initial load
    setItems([
      { id: "1", type: "audio", content: "Voice note received (0:14s)", ward: "Old City", time: "2 min ago", isNew: false },
      { id: "2", type: "text", content: "\"Drainage pipe is broken near...\"", ward: "Gachibowli", time: "15 min ago", isNew: false },
      { id: "3", type: "image", content: "Photo of pothole uploaded", ward: "Rajapuram", time: "1 hr ago", isNew: false },
    ]);

    // Simulate new submission coming in after 10 seconds to show judges the "live" aspect
    const timer1 = setTimeout(() => {
      setItems(prev => [
        { id: "4", type: "text", content: "\"No drinking water supply since...\"", ward: "Banjara Hills", time: "Just now", isNew: true },
        ...prev
      ]);
      
      // Remove the "isNew" flag after animation completes
      setTimeout(() => {
        setItems(current => current.map(item => item.id === "4" ? { ...item, isNew: false } : item));
      }, 3000);
      
    }, 10000);

    return () => clearTimeout(timer1);
  }, []);

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
