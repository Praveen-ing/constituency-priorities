"use client";

import { useState } from "react";
import { MessageSquare, Send, Loader2, Bot } from "lucide-react";
import { Priority } from "../page";

interface Props {
  priorities: Priority[];
}

export default function DataChat({ priorities }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: "user" | "bot"; content: string }[]>([
    { role: "bot", content: "Hi! Ask me any question about the current constituency priorities. For example: 'Which ward has the most urgent water issues?'" }
  ]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    
    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMsg,
          context_data: priorities.map(p => ({
            theme: p.theme_label,
            ward: p.ward_name,
            gap_score: p.gap_score,
            submissions: p.submission_count
          }))
        })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "bot", content: data.reply }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: "bot", content: "Sorry, I couldn't reach the backend." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 p-4 bg-brand-600 hover:bg-brand-500 rounded-full shadow-2xl shadow-brand-500/20 transition-all hover:scale-105 z-50 flex items-center justify-center text-white"
      >
        <MessageSquare className="w-6 h-6" />
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 max-h-[600px] h-[70vh] bg-surface-900 border border-slate-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden z-50 animate-slide-up">
          <div className="p-4 bg-surface-800 border-b border-slate-700 flex items-center gap-3">
            <div className="p-2 bg-brand-500/20 text-brand-400 rounded-lg">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Ask the Data</h3>
              <p className="text-xs text-slate-400">Gemini 1.5 Pro</p>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[85%] p-3 rounded-xl text-sm ${
                  m.role === "user" 
                    ? "bg-brand-600 text-white rounded-tr-sm" 
                    : "bg-surface-800 text-slate-200 border border-slate-700 rounded-tl-sm"
                }`}>
                  {m.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-surface-800 text-slate-400 p-3 rounded-xl border border-slate-700 flex items-center gap-2 rounded-tl-sm">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-xs">Analyzing data...</span>
                </div>
              </div>
            )}
          </div>

          <div className="p-3 border-t border-slate-800 bg-surface-800/50">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && sendMessage()}
                placeholder="Ask about priorities..."
                className="flex-1 bg-surface-900 border border-slate-700 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-brand-500"
              />
              <button 
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className="p-2.5 bg-brand-600 hover:bg-brand-500 rounded-xl text-white disabled:opacity-50 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
