import { AlertTriangle, CheckCircle, RefreshCcw } from "lucide-react";
import { t } from "../../../lib/i18n/strings";

interface QualityWarningProps {
  score: number;
  suggestions: string[];
  lang: string;
  onProceed: () => void;
  onImprove: () => void;
}

export default function QualityWarning({
  score,
  suggestions,
  lang,
  onProceed,
  onImprove,
}: QualityWarningProps) {
  if (score >= 65) return null;

  return (
    <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-5 mb-6 animate-fade-in">
      <div className="flex items-start gap-3 mb-4">
        <AlertTriangle className="w-6 h-6 text-orange-400 shrink-0 mt-1" />
        <div>
          <h3 className="font-bold text-orange-400">{t("quality_review_title", lang)}</h3>
          <p className="text-orange-200/80 text-sm mt-1 leading-relaxed">
            {t("quality_review_warning", lang)}
          </p>
        </div>
      </div>
      
      {suggestions.length > 0 && (
        <div className="mb-5 ml-9">
          <p className="text-orange-300 text-sm font-semibold mb-2">
            {t("quality_review_suggestions_title", lang)}
          </p>
          <ul className="list-disc list-outside text-orange-200 text-sm space-y-1 ml-4 marker:text-orange-500/60">
            {suggestions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3 ml-9">
        <button
          onClick={onImprove}
          className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-orange-500/20 hover:bg-orange-500/30 text-orange-300 font-semibold transition-colors"
        >
          <RefreshCcw className="w-4 h-4" />
          {t("quality_review_improve", lang)}
        </button>
        <button
          onClick={onProceed}
          className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg border border-orange-500/30 hover:bg-orange-500/10 text-orange-400/80 transition-colors text-sm font-medium"
        >
          <CheckCircle className="w-4 h-4" />
          {t("quality_review_proceed", lang)}
        </button>
      </div>
    </div>
  );
}
