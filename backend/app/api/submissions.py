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
from app.models.submission import SubmissionCreate, SubmissionResponse, MediaType, QualityCheckRequest, QualityCheckResponse
from app.nlp.classify import classify_submission, check_submission_quality, generate_submission_explanation
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
        "is_emergency": classification.is_emergency,
        "emergency_type": classification.emergency_type,
    }
    return updates


def _process_submission_background(submission_id: str, row: dict, ward_hint: str | None) -> None:
    """Background task: run NLP pipeline and update BigQuery row."""
    try:
        text = row.get("translated_text", "")
        if not text:
            return
        updates = _run_nlp_pipeline(submission_id, text, ward_hint)
        updated_row = {**row, **updates}

        # Deduplication check
        theme = updated_row.get("theme")
        ward_id = updated_row.get("ward_id")
        if theme and ward_id and theme != "other":
            recent_subs = get_submissions(theme=theme, ward_id=ward_id, limit=6)
            recent_subs = [s for s in recent_subs if s["id"] != submission_id][:5]
            if recent_subs:
                from app.nlp.classify import check_for_duplicates
                dup_result = check_for_duplicates(text, recent_subs)
                if dup_result.get("is_near_duplicate") and dup_result.get("similarity_score", 0.0) > 0.88:
                    updated_row["is_duplicate"] = True
                    updated_row["duplicate_of"] = dup_result.get("duplicate_of")

        # BigQuery streaming inserts are append-only; for simplicity we
        # re-insert an updated row. In production use BQ UPDATE via DML.
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
        "quality_score": payload.quality_score,
        "quality_suggestions": payload.quality_suggestions,
        "user_id": payload.user_id,
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
    is_emergency: bool | None = None,
    user_id: str | None = None,
) -> list[dict]:
    """List submissions with optional filtering."""
    return get_submissions(theme=theme, ward_id=ward_id, limit=min(limit, 200), is_emergency=is_emergency, user_id=user_id)


@router.post("/quality-check", response_model=QualityCheckResponse)
async def check_quality(payload: QualityCheckRequest) -> QualityCheckResponse:
    """Evaluate submission quality before it is stored."""
    text = ""
    if payload.media_type == MediaType.audio:
        result = process_audio(payload.content, payload.original_language or "hi-IN")
        text = result["translated_text"]
    elif payload.media_type == MediaType.image:
        result = process_image(payload.content)
        text = result["translated_text"]
    else:
        text = process_text(payload.content)
        
    if not text:
        return QualityCheckResponse(score=0.0, suggestions=["Please provide a valid submission."])
        
    quality = check_submission_quality(text, payload.original_language)
    return QualityCheckResponse(score=quality["score"], suggestions=quality["suggestions"])

from app.db.bigquery_client import get_submission, get_priorities

@router.get("/{submission_id}/explanation")
async def get_explanation(submission_id: str, lang: str = "en") -> dict:
    """Generate an AI explanation of how a submission contributed to its ward's priority."""
    sub = get_submission(submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    theme = sub.get("theme")
    ward_id = sub.get("ward_id")
    
    if not theme or not ward_id:
        return {"explanation": "Your submission has been received and is being processed."}
        
    priorities = get_priorities()
    matching_priority = next((p for p in priorities if p.get("theme_id") == theme and p.get("ward_id") == ward_id), None)
    
    if not matching_priority:
        return {"explanation": "Your submission has been classified and is contributing to your ward's data."}
        
    rank = matching_priority.get("rank", 0)
    count = matching_priority.get("submission_count", 1)
    
    explanation = generate_submission_explanation(
        theme=theme,
        ward_id=ward_id,
        rank=rank,
        submission_count=count,
        target_language=lang
    )
    
    return {"explanation": explanation}
