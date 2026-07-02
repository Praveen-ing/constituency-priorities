import Link from "next/link";
import { ArrowRight, Mic, Camera, MessageSquare, BarChart3, Map, Zap } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-hidden">
      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <section className="relative flex flex-col items-center justify-center min-h-screen px-6 text-center">
        {/* Ambient glow backgrounds */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-brand-600/10 blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-saffron-500/10 blur-3xl" />
        </div>

        {/* Tricolor accent bar */}
        <div className="flex gap-1 mb-8 opacity-80">
          <span className="h-1.5 w-10 rounded-full bg-saffron-500" />
          <span className="h-1.5 w-10 rounded-full bg-white" />
          <span className="h-1.5 w-10 rounded-full bg-emerald-500" />
        </div>

        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight">
          <span className="gradient-text">जन आवाज़</span>
          <br />
          <span className="text-slate-200 text-4xl md:text-5xl font-semibold mt-2 block">
            Jan Awaaz
          </span>
        </h1>

        <p className="text-xl md:text-2xl text-slate-400 max-w-2xl mb-4 leading-relaxed">
          Citizens speak. AI listens. MPs act.
        </p>
        <p className="text-base text-slate-500 max-w-xl mb-12">
          Submit your development priorities by voice, photo, or text — in any language.
          Our AI surfaces the most urgent needs for your constituency.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mb-20">
          <Link
            id="submit-btn"
            href="/citizen"
            className="flex items-center gap-2 px-8 py-4 rounded-full font-semibold text-white text-lg transition-all duration-300 hover:scale-105 hover:shadow-lg"
            style={{ background: "linear-gradient(135deg, #1e88ed, #1671da)" }}
          >
            Submit a Priority
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            id="dashboard-btn"
            href="/dashboard"
            className="flex items-center gap-2 px-8 py-4 rounded-full font-semibold text-slate-200 text-lg border border-slate-600 hover:border-slate-400 hover:bg-white/5 transition-all duration-300"
          >
            MP Dashboard
            <BarChart3 className="w-5 h-5" />
          </Link>
        </div>

        {/* Input mode cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl w-full">
          {[
            { icon: Mic, label: "Voice", desc: "Speak in Hindi, Telugu, or English", color: "text-brand-400" },
            { icon: Camera, label: "Photo", desc: "Photograph a local issue", color: "text-saffron-400" },
            { icon: MessageSquare, label: "Text", desc: "Type your concern", color: "text-emerald-400" },
          ].map(({ icon: Icon, label, desc, color }) => (
            <div key={label} className="glass-card p-5 text-left hover:border-slate-500 transition-colors cursor-pointer">
              <Icon className={`w-7 h-7 mb-3 ${color}`} />
              <div className="font-semibold text-white mb-1">{label}</div>
              <div className="text-sm text-slate-400">{desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────────────────── */}
      <section className="py-24 px-6 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-4 text-white">How It Works</h2>
        <p className="text-center text-slate-400 mb-14 max-w-xl mx-auto">
          A transparent, auditable process from citizen voice to MP action
        </p>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              step: "01",
              icon: Mic,
              title: "Citizens Submit",
              desc: "Voice, photo, or text in any language — even without internet via SMS.",
              color: "from-brand-600/20 to-brand-800/10",
            },
            {
              step: "02",
              icon: Zap,
              title: "AI Analyses",
              desc: "Gemini Flash classifies, clusters, and cross-references public data (Census, UDISE+).",
              color: "from-saffron-500/20 to-saffron-700/10",
            },
            {
              step: "03",
              icon: Map,
              title: "Priorities Surface",
              desc: "MP sees a ranked, auditable list with a Gap Score breakdown they can trust.",
              color: "from-emerald-500/20 to-emerald-700/10",
            },
          ].map(({ step, icon: Icon, title, desc, color }) => (
            <div key={step} className={`glass-card p-6 bg-gradient-to-br ${color}`}>
              <div className="text-5xl font-black text-slate-700 mb-4">{step}</div>
              <Icon className="w-6 h-6 text-slate-300 mb-3" />
              <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────────────── */}
      <footer className="border-t border-slate-800 py-8 px-6 text-center text-slate-500 text-sm">
        <p>
          Built for{" "}
          <a href="https://cloud.google.com" className="text-brand-400 hover:underline" target="_blank" rel="noopener noreferrer">
            Google Cloud
          </a>{" "}
          · Code for Communities Hackathon · Track 1: People's Priorities
        </p>
      </footer>
    </main>
  );
}
