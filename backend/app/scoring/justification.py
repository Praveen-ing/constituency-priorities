"""
Justification string generation using Gemini 2.5 Pro.

This module receives COMPUTED NUMBERS from gap_score.py — it never
receives raw citizen submissions or raw data. It only explains the score.

Rule from AGENTS.md: Never call Gemini Pro in a per-submission hot path.
This is called ONCE per priority item (~20 calls per constituency).
"""
from __future__ import annotations

import logging

import google.generativeai as genai

from app.config import get_settings
from app.nlp.prompts import JUSTIFICATION_PROMPT

logger = logging.getLogger(__name__)


def generate_justification(
    theme_name: str,
    ward_name: str,
    constituency_name: str,
    volume: int,
    days: int,
    urgency_pct: float,
    deficit_description: str,
    population: int,
    gap_score: float,
    rank: int,
    total: int,
) -> str:
    """
    Generate a plain-English justification sentence for a Gap Score result.

    Args:
        theme_name: Human-readable theme label (e.g. "School Overcrowding")
        ward_name: Ward or area name
        constituency_name: Constituency name
        volume: Number of citizen submissions for this theme+ward
        days: Time window in days
        urgency_pct: Percentage of submissions flagged urgent (0-100)
        deficit_description: Human-readable description of the data deficit
                             (e.g. "enrollment 142% of capacity")
        population: Ward population affected
        gap_score: The computed Gap Score float [0, 1]
        rank: Rank of this priority
        total: Total number of priorities in this constituency
    Returns:
        A single justification sentence (≤30 words).
    """
    settings = get_settings()

    # --- Early exit if Gemini API key is not configured ---
    if not settings.gemini_api_key:
        logger.debug("GEMINI_API_KEY not set — using template justification")
        level = "HIGH" if gap_score >= 0.65 else "MEDIUM" if gap_score >= 0.40 else "LOW"
        return (
            f"{volume} citizen submissions ({urgency_pct:.0f}% urgent) + {deficit_description} "
            f"in {ward_name} drives {level} priority rating for {theme_name}."
        )

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        model_name=settings.gemini_pro_model,
        generation_config=genai.types.GenerationConfig(
            temperature=0.2,
            max_output_tokens=80,
        ),
    )

    prompt = JUSTIFICATION_PROMPT.format(
        theme_name=theme_name,
        ward_name=ward_name,
        constituency_name=constituency_name,
        volume=volume,
        days=days,
        urgency_pct=f"{urgency_pct:.0f}",
        deficit_description=deficit_description,
        population=f"{population:,}",
        gap_score=gap_score,
        rank=rank,
        total=total,
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.warning("Justification generation failed: %s", exc)
        return (
            f"{volume} citizen submissions and significant supply gap "
            f"in {ward_name} drive this HIGH priority rating."
        )
