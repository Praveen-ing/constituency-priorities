"""
Gemini Flash: structured theme classification and entity extraction.
Uses ONLY prompts from prompts.py — no inline prompt strings.
"""
from __future__ import annotations

import json
import logging

import google.generativeai as genai

from app.config import get_settings
from app.nlp.prompts import CLASSIFY_THEME_PROMPT

logger = logging.getLogger(__name__)

VALID_THEMES = {
    "education", "water", "roads", "health",
    "sanitation", "electricity", "housing", "employment", "other",
}


class ClassificationResult:
    __slots__ = ("theme", "urgency", "facility_type", "location_text")

    def __init__(
        self,
        theme: str,
        urgency: float,
        facility_type: str | None,
        location_text: str | None,
    ) -> None:
        self.theme = theme
        self.urgency = urgency
        self.facility_type = facility_type
        self.location_text = location_text


def _get_model() -> genai.GenerativeModel:
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel(
        model_name=settings.gemini_flash_model,
        generation_config=genai.types.GenerationConfig(
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )


def classify_submission(text: str) -> ClassificationResult:
    """
    Classify a (translated) citizen submission using Gemini 2.5 Flash.
    Returns theme, urgency score, facility_type, location_text.
    """
    model = _get_model()
    prompt = CLASSIFY_THEME_PROMPT.format(submission_text=text)

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception) as exc:
        logger.warning("Classification failed, defaulting to 'other': %s", exc)
        return ClassificationResult("other", 0.3, None, None)

    theme = data.get("theme", "other")
    if theme not in VALID_THEMES:
        theme = "other"

    urgency = float(data.get("urgency", 0.3))
    urgency = max(0.0, min(1.0, urgency))

    return ClassificationResult(
        theme=theme,
        urgency=urgency,
        facility_type=data.get("facility_type"),
        location_text=data.get("location_text"),
    )
