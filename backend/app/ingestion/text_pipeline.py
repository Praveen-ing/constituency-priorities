"""
Text pipeline — minimal preprocessing for direct text input.
"""
from __future__ import annotations

import re


def process_text(text: str) -> str:
    """
    Clean and normalize raw text submissions.
    Returns the cleaned text ready for NLP classification.
    """
    if not text:
        return ""

    # Remove URLs (not useful for classification)
    text = re.sub(r"https?://\S+", "", text)

    # Strip excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text
