/**
 * i18n strings for the Citizen PWA
 */

export const STRINGS = {
  quality_review_title: {
    en: "Quality Review",
    hi: "गुणवत्ता जांच",
    te: "నాణ్యత సమీక్ష",
  },
  quality_review_warning: {
    en: "Your submission might be too vague or generic to be processed effectively.",
    hi: "आपकी शिकायत बहुत सामान्य है। कृपया अधिक जानकारी दें।",
    te: "మీ ఫిర్యాదు చాలా సాధారణంగా ఉంది. దయచేసి మరిన్ని వివరాలు ఇవ్వండి.",
  },
  quality_review_suggestions_title: {
    en: "Suggestions to improve:",
    hi: "सुधार के लिए सुझाव:",
    te: "మెరుగుపరచడానికి సూచనలు:",
  },
  quality_review_proceed: {
    en: "Proceed Anyway",
    hi: "फिर भी आगे बढ़ें",
    te: "అయినప్పటికీ కొనసాగించండి",
  },
  quality_review_improve: {
    en: "Improve Submission",
    hi: "शिकायत सुधारें",
    te: "సమర్పణను మెరుగుపరచండి",
  },
  quality_review_checking: {
    en: "Checking quality...",
    hi: "गुणवत्ता की जाँच हो रही है...",
    te: "నాణ్యతను తనిఖీ చేస్తోంది...",
  },
  my_submissions_title: {
    en: "My Submissions",
    hi: "मेरी शिकायतें",
    te: "నా సమర్పణలు",
  },
  sign_in_to_view: {
    en: "Sign in with Google to view your submissions",
    hi: "अपनी शिकायतें देखने के लिए Google से साइन इन करें",
    te: "మీ సమర్పణలను వీక్షించడానికి Googleతో సైన్ ఇన్ చేయండి",
  },
  sign_in_btn: {
    en: "Sign in with Google",
    hi: "Google से साइन इन करें",
    te: "Googleతో సైన్ ఇన్ చేయండి",
  },
  urgency_low: {
    en: "Low",
    hi: "कम",
    te: "తక్కువ",
  },
  urgency_medium: {
    en: "Medium",
    hi: "मध्यम",
    te: "మధ్యస్థం",
  },
  urgency_high: {
    en: "High",
    hi: "उच्च",
    te: "ఎక్కువ",
  },
  status_received: {
    en: "Received",
    hi: "प्राप्त हुआ",
    te: "స్వీకరించబడింది",
  },
  status_classified: {
    en: "Classified",
    hi: "वर्गीकृत",
    te: "వర్గీకరించబడింది",
  },
  status_contributing: {
    en: "Contributing to Priority",
    hi: "प्राथमिकता में योगदान",
    te: "ప్రాధాన్యతకు దోహదపడుతోంది",
  },
  theme: {
    en: "Theme",
    hi: "विषय",
    te: "అంశం",
  },
  ward: {
    en: "Ward",
    hi: "वार्ड",
    te: "వార్డు",
  },
  generating_explanation: {
    en: "Generating explanation...",
    hi: "विवरण तैयार हो रहा है...",
    te: "వివరణ సృష్టిస్తోంది...",
  }
} as const;

export type Language = "en" | "hi" | "te";
export type StringKey = keyof typeof STRINGS;

export function t(key: StringKey, lang: string): string {
  const safeLang = (lang === "hi" || lang === "te") ? lang : "en";
  return STRINGS[key][safeLang];
}
