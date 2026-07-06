"""
Pydantic models for citizen submissions.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MediaType(str, Enum):
    text = "text"
    audio = "audio"
    image = "image"


class SubmissionCreate(BaseModel):
    """Payload accepted by POST /submissions."""
    media_type: MediaType
    content: str = Field(..., description="Raw text, GCS URI for audio, or GCS URI for image")
    original_language: str = Field("unknown", description="BCP-47 language code if known")
    ward_hint: Optional[str] = Field(None, description="Ward or locality name if user provided")
    lat: Optional[float] = None
    lng: Optional[float] = None
    source: str = Field("web", description="web | whatsapp | sms")
    quality_score: Optional[float] = Field(None, description="0.0 to 100.0 quality score")
    quality_suggestions: Optional[list[str]] = Field(None, description="List of improvement suggestions")
    user_id: Optional[str] = None

class QualityCheckRequest(BaseModel):
    media_type: MediaType
    content: str
    original_language: str = "en"

class QualityCheckResponse(BaseModel):
    score: float
    suggestions: list[str]


class Submission(BaseModel):
    """Full submission record as stored in BigQuery."""
    id: str
    created_at: datetime
    media_type: MediaType
    original_content: str
    original_language: str
    translated_text: str
    theme: Optional[str] = None
    urgency: float = 0.0
    facility_type: Optional[str] = None
    ward_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    cluster_id: Optional[int] = None
    source: str = "web"
    is_emergency: bool = False
    emergency_type: Optional[str] = None
    user_id: Optional[str] = None
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None

    class Config:
        from_attributes = True


class SubmissionResponse(BaseModel):
    """Response returned after creating a submission."""
    id: str
    message: str = "Submission received and queued for processing"
    theme: Optional[str] = None
    urgency: Optional[float] = None
    is_emergency: bool = False
    emergency_type: Optional[str] = None
    user_id: Optional[str] = None
