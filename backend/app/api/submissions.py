"""
POST /submissions — accept citizen submissions (text, audio, image).
GET  /submissions — list submissions with optional filtering.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db.bigquery_client import get_bq_client, insert_submission, get_submissions
from app.ingestion.audio_pipeline import process_audio
from app.ingestion.image_pipeline import process_image
from app.ingestion.text_pipeline import process_text
from app.models.submission import SubmissionCreate, SubmissionResponse, MediaType
from app.nlp.classify import classify_submission
from app.nlp.extract_entities import extract_entities

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/submissions", tags=["submissions"])


def _run_nlp_pipeline(submission_id: str, translated_text: str, ward_hint: str | None) -> dict:
    """Run classification + entity extraction on the translated text."""
    classification = classify_submission(translated_text)
    entities = extract_entities(translated_text, ward_hint)

    updates = {
        "theme": classification.theme,
        "urgency": classification.urgency,
        "facility_type": classification.facility_type,
        "ward_id": entities.ward_id or (
            classification.location_text.lower().replace(" ", "_")
            if classification.location_text else None
        ),
        "lat": entities.lat,
        "lng": entities.lng,
    }
    return updates


def _process_submission_background(submission_id: str, row: dict, ward_hint: str | None) -> None:
    """Background task: run NLP pipeline and update BigQuery row."""
    try:
        text = row.get("translated_text", "")
        if not text:
            return
        updates = _run_nlp_pipeline(submission_id, text, ward_hint)
        # BigQuery streaming inserts are append-only; for simplicity we
        # re-insert an updated row. In production use BQ UPDATE via DML.
        updated_row = {**row, **updates}
        insert_submission(updated_row)
    except Exception as exc:
        logger.error("Background NLP failed for %s: %s", submission_id, exc)


@router.post("", response_model=SubmissionResponse, status_code=202)
async def create_submission(
    payload: SubmissionCreate,
    background_tasks: BackgroundTasks,
) -> SubmissionResponse:
    """
    Accept a citizen submission. Supported media types:
    - text: direct text string
    - audio: GCS URI to uploaded audio file
    - image: GCS URI to uploaded image file

    NLP classification runs asynchronously in the background.
    """
    submission_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Build base row
    row: dict = {
        "id": submission_id,
        "created_at": now,
        "media_type": payload.media_type.value,
        "original_content": payload.content,
        "original_language": payload.original_language,
        "translated_text": "",
        "source": payload.source,
        "ward_id": payload.ward_hint,
        "lat": payload.lat,
        "lng": payload.lng,
    }

    # Synchronous pre-processing to get translated text
    if payload.media_type == MediaType.audio:
        result = process_audio(payload.content, payload.original_language or "hi-IN")
        row["translated_text"] = result["translated_text"]
        row["original_language"] = result["detected_language"]

    elif payload.media_type == MediaType.image:
        result = process_image(payload.content)
        row["translated_text"] = result["translated_text"]
        row["theme"] = result["theme"]
        row["urgency"] = result["urgency"]
        row["facility_type"] = result["facility_type"]

    elif payload.media_type == MediaType.text:
        row["translated_text"] = process_text(payload.content)

    # Insert raw row immediately so it's in BQ
    insert_submission(row)

    # Run NLP classification asynchronously
    background_tasks.add_task(
        _process_submission_background, submission_id, row, payload.ward_hint
    )

    return SubmissionResponse(
        id=submission_id,
        theme=row.get("theme"),
        urgency=row.get("urgency"),
    )


@router.get("", response_model=list[dict])
async def list_submissions(
    theme: str | None = None,
    ward_id: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List submissions with optional filtering."""
    return get_submissions(theme=theme, ward_id=ward_id, limit=min(limit, 200))
