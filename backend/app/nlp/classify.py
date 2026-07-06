"""
Gemini Flash: structured theme classification and entity extraction.
Uses ONLY prompts from prompts.py — no inline prompt strings.
"""
from __future__ import annotations

import json
import logging

import google.generativeai as genai

from app.config import get_settings
from app.nlp.prompts import CLASSIFY_THEME_PROMPT, QUALITY_CHECK_PROMPT, SUBMISSION_EXPLANATION_PROMPT, DEDUPLICATION_PROMPT, HEALTH_SCORE_PROMPT

logger = logging.getLogger(__name__)

VALID_THEMES = {
    "education", "water", "roads", "health",
    "sanitation", "electricity", "housing", "employment", "other",
}


class ClassificationResult:
    __slots__ = ("theme", "urgency", "facility_type", "location_text", "is_emergency", "emergency_type")

    def __init__(
        self,
        theme: str,
        urgency: float,
        facility_type: str | None,
        location_text: str | None,
        is_emergency: bool = False,
        emergency_type: str | None = None,
    ) -> None:
        self.theme = theme
        self.urgency = urgency
        self.facility_type = facility_type
        self.location_text = location_text
        self.is_emergency = is_emergency
        self.emergency_type = emergency_type


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
        is_emergency=bool(data.get("is_emergency", False)),
        emergency_type=data.get("emergency_type")
    )

def check_submission_quality(text: str, target_language: str = "en") -> dict:
    """
    Check the quality of a submission before it is fully submitted.
    Returns a dict with 'score' (0-100) and 'suggestions' (list of strings).
    """
    model = _get_model()
    prompt = QUALITY_CHECK_PROMPT.format(
        submission_text=text,
        target_language=target_language
    )

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        data = json.loads(raw)
        
        score = float(data.get("score", 100.0))
        suggestions = data.get("suggestions", [])
        if not isinstance(suggestions, list):
            suggestions = []
            
        return {"score": score, "suggestions": suggestions}
    except Exception as exc:
        logger.warning("Quality check failed, defaulting to 100: %s", exc)
        return {"score": 100.0, "suggestions": []}

def generate_submission_explanation(
    theme: str,
    ward_id: str,
    rank: int,
    submission_count: int,
    target_language: str
) -> str:
    """
    Generate an AI explanation of how a submission contributed to its ward's priority.
    """
    model = _get_model()
    # Use text model without json enforcement
    genai.configure(api_key=get_settings().gemini_api_key)
    text_model = genai.GenerativeModel(model_name=get_settings().gemini_flash_model)
    
    prompt = SUBMISSION_EXPLANATION_PROMPT.format(
        theme=theme,
        ward_id=ward_id,
        rank=rank,
        submission_count=submission_count,
        target_language=target_language
    )

    try:
        response = text_model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.warning("Explanation generation failed: %s", exc)
        return "Your submission has been received and is contributing to your ward's priorities."

def check_for_duplicates(new_content: str, recent_submissions: list[dict]) -> dict:
    """
    Check if a new submission is a semantic duplicate of recent ones.
    Returns: {"is_near_duplicate": bool, "similarity_score": float, "reasoning": str, "duplicate_of": str|None}
    """
    if not recent_submissions:
        return {"is_near_duplicate": False, "similarity_score": 0.0, "reasoning": "No recent submissions to compare", "duplicate_of": None}
        
    model = _get_model()
    
    # Format recent submissions for prompt
    formatted_recent = "\n".join([
        f"- ID: {sub.get('id', 'unknown')}, Content: {sub.get('content', sub.get('original_content', ''))}"
        for sub in recent_submissions
    ])
    
    prompt = DEDUPLICATION_PROMPT.format(
        new_content=new_content,
        recent_submissions=formatted_recent
    )

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        data = json.loads(raw)
        return {
            "is_near_duplicate": bool(data.get("is_near_duplicate", False)),
            "similarity_score": float(data.get("similarity_score", 0.0)),
            "reasoning": data.get("reasoning", ""),
            "duplicate_of": data.get("duplicate_of")
        }
    except Exception as exc:
        logger.warning("Deduplication check failed, defaulting to False: %s", exc)
        return {"is_near_duplicate": False, "similarity_score": 0.0, "reasoning": "Failed to check", "duplicate_of": None}

def generate_health_score_explanation(health_score: int, components: list[dict]) -> str:
    """
    Generate a 2-3 sentence AI explanation for the Constituency Health Score.
    """
    model = _get_model()
    # Use text model without json enforcement
    genai.configure(api_key=get_settings().gemini_api_key)
    text_model = genai.GenerativeModel(model_name=get_settings().gemini_pro_model)
    
    components_text = "\n".join([f"- {c['name']}: {c['score']:.1f} (Weight: {c['weight']:.2f})" for c in components])
    
    prompt = HEALTH_SCORE_PROMPT.format(
        health_score=health_score,
        components_text=components_text
    )

    try:
        response = text_model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.warning("Health score explanation generation failed: %s", exc)
        return "The overall health score reflects recent citizen engagement and priority resolution trends."
