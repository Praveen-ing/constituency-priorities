"""
Image ingestion pipeline: Gemini 2.5 Flash multimodal → caption + classification.
"""
from __future__ import annotations

import json
import logging

import google.generativeai as genai
from google.cloud import storage

from app.config import get_settings
from app.nlp.prompts import IMAGE_CLASSIFY_PROMPT

logger = logging.getLogger(__name__)


def download_from_gcs(gcs_uri: str) -> bytes:
    """Download file bytes from GCS URI."""
    # Parse gs://bucket/object
    path = gcs_uri.replace("gs://", "")
    bucket_name, *parts = path.split("/")
    blob_name = "/".join(parts)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()


def process_image(gcs_uri: str) -> dict:
    """
    Full image pipeline: GCS URI → Gemini 2.5 Flash multimodal analysis.

    Returns dict with keys:
        description, theme, urgency, facility_type, issue_summary
    """
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        model_name=settings.gemini_flash_model,
        generation_config=genai.types.GenerationConfig(
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )

    try:
        image_bytes = download_from_gcs(gcs_uri)
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}

        response = model.generate_content([IMAGE_CLASSIFY_PROMPT, image_part])
        data = json.loads(response.text.strip())

        return {
            "description": data.get("description", ""),
            "theme": data.get("theme", "other"),
            "urgency": float(data.get("urgency", 0.3)),
            "facility_type": data.get("facility_type"),
            "issue_summary": data.get("issue_summary", ""),
            "translated_text": data.get("issue_summary", data.get("description", "")),
        }
    except Exception as exc:
        logger.error("Image pipeline failed for %s: %s", gcs_uri, exc)
        return {
            "description": "Unable to analyze image.",
            "theme": "other",
            "urgency": 0.3,
            "facility_type": None,
            "issue_summary": "Citizen submitted a photo — manual review needed.",
            "translated_text": "Citizen submitted a photo.",
        }
