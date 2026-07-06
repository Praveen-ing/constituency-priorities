"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, MessageSquare, AlertCircle, RefreshCw } from "lucide-react";
import { auth, signInWithPopup, googleProvider } from "../../../lib/firebase";
import LanguageSelector from "../components/LanguageSelector";
import { t } from "../../../lib/i18n/strings";

// Note: since firebase takes time to init, we listen for state changes.
export default function MySubmissionsPage() {
  const [lang, setLang] = useState("en");
  const [user, setUser] = useState<any>(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [loadingData, setLoadingData] = useState(false);

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((u: any) => {
      setUser(u);
      setLoadingUser(false);
    });
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (user) {
      fetchSubmissions(user.uid);
    }
  }, [user]);

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const fetchSubmissions = async (uid: string) => {
    setLoadingData(true);
    try {
      const res = await fetch(`${apiBase}/submissions?user_id=${uid}`);
      const data = await res.json();
      setSubmissions(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingData(false);
    }
  };

  const handleLogin = async () => {
    try {
      await signInWithPopup(auth, googleProvider);
    } catch (error) {
      console.error("Login failed", error);
    }
  };

  const getUrgency = (u: number | undefined) => {
    if (u === undefined || u === null) return null;
    if (u < 0.3) return t("urgency_low", lang);
    if (u > 0.7) return t("urgency_high", lang);
    return t("urgency_medium", lang);
  };

  const getStatus = (sub: any) => {
    if (!sub.theme || sub.theme === "other") return { label: t("status_received", lang), color: "text-slate-400" };
    return { label: t("status_classified", lang), color: "text-brand-400" };
  };

  if (loadingUser) {
    return <div className="min-h-screen flex items-center justify-center text-white"><RefreshCw className="w-6 h-6 animate-spin" /></div>;
  }

  return (
    <div className="min-h-screen flex flex-col bg-surface-900 text-white">
      <header className="flex items-center justify-between px-6 py-5 border-b border-slate-800">
        <Link href="/citizen" className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">Back</span>
        </Link>
        <h1 className="text-lg font-semibold">{t("my_submissions_title", lang)}</h1>
        <LanguageSelector lang={lang} onLangChange={setLang} />
      </header>

      <div className="flex-1 max-w-3xl mx-auto w-full px-6 py-8">
        {!user ? (
          <div className="flex flex-col items-center justify-center mt-20 text-center">
            <AlertCircle className="w-12 h-12 text-slate-500 mb-4" />
            <p className="text-slate-400 mb-6">{t("sign_in_to_view", lang)}</p>
            <button
              onClick={handleLogin}
              className="bg-white text-slate-900 px-6 py-3 rounded-full font-bold shadow-lg hover:bg-slate-100 transition-colors"
            >
              {t("sign_in_btn", lang)}
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-slate-400 text-sm">Signed in as {user.email || user.displayName}</span>
            </div>
            {loadingData ? (
              <div className="flex justify-center py-10"><RefreshCw className="w-6 h-6 animate-spin text-slate-500" /></div>
            ) : submissions.length === 0 ? (
              <div className="text-center py-10 text-slate-500">No submissions found.</div>
            ) : (
              submissions.map((sub) => (
                <SubmissionCard key={sub.id} sub={sub} lang={lang} apiBase={apiBase} getUrgency={getUrgency} getStatus={getStatus} />
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function SubmissionCard({ sub, lang, apiBase, getUrgency, getStatus }: any) {
  const status = getStatus(sub);
  const urgencyLabel = getUrgency(sub.urgency);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [loadingExp, setLoadingExp] = useState(false);

  useEffect(() => {
    if (sub.theme && sub.ward_id) {
      setLoadingExp(true);
      fetch(`${apiBase}/submissions/${sub.id}/explanation?lang=${lang}`)
        .then(res => res.json())
        .then(data => {
          if (data.explanation) {
            setExplanation(data.explanation);
          }
        })
        .catch(console.error)
        .finally(() => setLoadingExp(false));
    }
  }, [sub.id, sub.theme, sub.ward_id, lang, apiBase]);

  return (
    <div className="bg-surface-800 rounded-xl p-5 border border-slate-700">
      <div className="flex justify-between items-start mb-3">
        <span className="text-xs text-slate-400">{new Date(sub.created_at).toLocaleString()}</span>
        <span className={`text-xs font-semibold px-2 py-1 rounded-full bg-surface-700 ${explanation && explanation.includes("contributing") ? "text-emerald-400" : status.color}`}>
          {explanation && explanation.includes("contributing") ? t("status_contributing", lang) : status.label}
        </span>
      </div>
      
      <p className="text-sm mb-4 line-clamp-3">"{sub.original_content || sub.translated_text}"</p>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-slate-500">{t("theme", lang)}</p>
          <p className="text-sm capitalize">{sub.theme ? sub.theme.replace("_", " ") : "-"}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">{t("ward", lang)}</p>
          <p className="text-sm capitalize">{sub.ward_id ? sub.ward_id.replace("_", " ") : "-"}</p>
        </div>
        <div>
           <p className="text-xs text-slate-500">Urgency</p>
           <p className="text-sm">{urgencyLabel || "-"}</p>
        </div>
      </div>

      <div className="bg-surface-700 rounded-lg p-4 mt-2 border border-slate-600">
        <p className="text-xs font-semibold text-brand-300 mb-1">AI Impact Analysis</p>
        {loadingExp ? (
          <p className="text-xs text-slate-400 flex items-center gap-2"><RefreshCw className="w-3 h-3 animate-spin" /> {t("generating_explanation", lang)}</p>
        ) : explanation ? (
          <p className="text-sm text-slate-300 leading-relaxed">{explanation}</p>
        ) : (
          <p className="text-xs text-slate-500">Not enough data to analyze impact yet.</p>
        )}
      </div>
    </div>
  );
}
