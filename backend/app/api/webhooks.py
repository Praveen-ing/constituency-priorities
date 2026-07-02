"""
POST /webhook/twilio — inbound WhatsApp/SMS from Twilio.
Parses the Twilio webhook payload and routes to the submission pipeline.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Form, Request, Response
from fastapi.responses import PlainTextResponse

from app.api.submissions import _process_submission_background
from app.db.bigquery_client import insert_submission
from app.ingestion.text_pipeline import process_text
from app.nlp.classify import classify_submission
from app.nlp.extract_entities import extract_entities

import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhooks"])


@router.post("/twilio", response_class=PlainTextResponse)
async def twilio_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    Body: str = Form(default=""),
    From: str = Form(default=""),
    MediaUrl0: str = Form(default=""),
    MediaContentType0: str = Form(default=""),
) -> str:
    """
    Handle inbound WhatsApp/SMS from Twilio.
    Twilio sends form-encoded POST with Body, From, and optional MediaUrl fields.
    """
    submission_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    source = "whatsapp" if From.startswith("whatsapp:") else "sms"
    media_type = "text"
    content = Body
    translated_text = process_text(Body) if Body else ""

    # Handle media (image) if present
    if MediaUrl0 and "image" in MediaContentType0:
        media_type = "image"
        content = MediaUrl0
        translated_text = f"[Image submitted via {source}]"

    row = {
        "id": submission_id,
        "created_at": now,
        "media_type": media_type,
        "original_content": content,
        "original_language": "unknown",
        "translated_text": translated_text,
        "source": source,
    }

    insert_submission(row)
    background_tasks.add_task(_process_submission_background, submission_id, row, None)

    # Return a localized TwiML response to close the loop with the citizen
    twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>
        Thank you for contacting Jan Awaaz. Your issue has been logged and is being reviewed by the MP's office.
        
        जन आवाज़ से संपर्क करने के लिए धन्यवाद। आपकी समस्या दर्ज कर ली गई है और सांसद कार्यालय द्वारा इसकी समीक्षा की जा रही है।
        
        జన్ ఆవాజ్‌ని సంప్రదించినందుకు ధన్యవాదాలు. మీ సమస్య నమోదు చేయబడింది మరియు MP కార్యాలయం ద్వారా సమీక్షించబడుతోంది.
    </Message>
</Response>"""

    return Response(content=twiml_response, media_type="application/xml")
