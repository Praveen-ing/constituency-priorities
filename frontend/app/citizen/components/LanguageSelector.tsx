"use client";

interface Props {
  lang: string;
  onLangChange: (lang: string) => void;
}

const LANGS = [
  { code: "en", label: "EN" },
  { code: "hi", label: "हि" },
  { code: "te", label: "తె" },
];

export default function LanguageSelector({ lang, onLangChange }: Props) {
  return (
    <div className="flex gap-1 p-1 rounded-lg bg-surface-700 border border-slate-700">
      {LANGS.map((l) => (
        <button
          key={l.code}
          id={`lang-${l.code}`}
          onClick={() => onLangChange(l.code)}
          className={`px-3 py-1.5 rounded-md text-sm font-semibold transition-all duration-200 ${
            lang === l.code
              ? "bg-brand-600 text-white shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          {l.label}
        </button>
      ))}
    </div>
  );
}
