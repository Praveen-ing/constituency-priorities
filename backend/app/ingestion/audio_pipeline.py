"""
Audio ingestion pipeline: Cloud Speech-to-Text v2 (chirp_2) → Translation API → normalized text.
"""
from __future__ import annotations

import logging

from google.cloud import speech_v2 as speech
from google.cloud import translate_v2 as translate

from app.config import get_settings

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "hi-IN": "Hindi",
    "te-IN": "Telugu",
    "ta-IN": "Tamil",
    "kn-IN": "Kannada",
    "mr-IN": "Marathi",
    "en-IN": "English (India)",
}
TARGET_LANGUAGE = "en"


def transcribe_audio(gcs_uri: str, language_code: str = "hi-IN") -> tuple[str, str]:
    """
    Transcribe audio from a GCS URI using Cloud Speech-to-Text v2 (chirp_2).

    Args:
        gcs_uri: GCS URI of the audio file (e.g. gs://bucket/file.ogg)
        language_code: BCP-47 code of the spoken language

    Returns:
        (transcript, detected_language_code) tuple
    """
    settings = get_settings()
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        auto_decoding_config=speech.AutoDetectDecodingConfig(),
        language_codes=[language_code, "hi-IN", "en-IN"],  # fallback order
        model="chirp_2",
    )

    audio = speech.BatchRecognizeFileMetadata(uri=gcs_uri)
    request = speech.RecognizeRequest(
        recognizer=f"projects/{settings.gcp_project}/locations/global/recognizers/_",
        config=config,
        uri=gcs_uri,
    )

    try:
        response = client.recognize(request=request)
        transcript = " ".join(
            result.alternatives[0].transcript
            for result in response.results
            if result.alternatives
        )
        detected = language_code
        return transcript.strip(), detected
    except Exception as exc:
        logger.error("STT failed for %s: %s", gcs_uri, exc)
        return "", language_code


def translate_to_english(text: str, source_language: str = "hi") -> str:
    """
    Translate text to English using Cloud Translation API.
    Returns original text if already English or translation fails.
    """
    if not text or source_language.startswith("en"):
        return text

    try:
        client = translate.Client()
        result = client.translate(text, source_language=source_language, target_language="en")
        return result["translatedText"]
    except Exception as exc:
        logger.warning("Translation failed: %s", exc)
        return text


def process_audio(gcs_uri: str, language_hint: str = "hi-IN") -> dict[str, str]:
    """
    Full audio pipeline: GCS URI → transcript → English translation.

    Returns dict with keys: transcript, translated_text, detected_language
    """
    transcript, detected_lang = transcribe_audio(gcs_uri, language_hint)
    lang_short = detected_lang.split("-")[0]  # "hi-IN" → "hi"
    translated = translate_to_english(transcript, lang_short)

    return {
        "transcript": transcript,
        "translated_text": translated,
        "detected_language": detected_lang,
    }
