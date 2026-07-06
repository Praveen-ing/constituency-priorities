"""
Pydantic models for themes (clustered submission groups) and priorities (Gap Score results).
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Theme(BaseModel):
    theme_id: str
    label: str
    description: str
    submission_count: int
    mean_urgency: float
    ward_ids: list[str]
    last_updated: datetime


class HealthScoreComponent(BaseModel):
    name: str
    score: float
    weight: float

class ConstituencyHealthScore(BaseModel):
    score: int
    trend: str
    explanation: str
    components: list[HealthScoreComponent]

class GapScoreBreakdown(BaseModel):
    """The four components of the Gap Score, each normalized 0-1."""
    citizen_volume_norm: float = Field(..., ge=0, le=1)
    urgency_norm: float = Field(..., ge=0, le=1)
    data_deficit_norm: float = Field(..., ge=0, le=1)
    population_norm: float = Field(..., ge=0, le=1)
    # Weights used (can be tuned by MP dashboard sliders)
    w1: float = 0.30
    w2: float = 0.20
    w3: float = 0.35
    w4: float = 0.15


class Priority(BaseModel):
    priority_id: str
    theme_id: str
    theme_label: str
    ward_id: str
    ward_name: Optional[str] = None
    gap_score: float = Field(..., ge=0, le=1)
    breakdown: GapScoreBreakdown
    justification: str = ""    # Gemini 2.5 Pro plain-English explanation
    rank: int
    computed_at: datetime
    submission_count: int = 0
    # Transparency additions
    confidence: str = "High"
    urgency_histogram: dict[str, int] = {}
    data_deficit_figure: str = ""
    weights_used: dict[str, float] = {}


class PriorityListResponse(BaseModel):
    priorities: list[Priority]
    constituency: str
    total: int
    computed_at: datetime
    health_score: Optional[ConstituencyHealthScore] = None
    duplicate_count: int = 0


class WeightOverride(BaseModel):
    """Sent from the MP dashboard weight sliders."""
    w1: float = Field(0.30, ge=0, le=1, description="citizen_volume weight")
    w2: float = Field(0.20, ge=0, le=1, description="urgency weight")
    w3: float = Field(0.35, ge=0, le=1, description="data_deficit weight")
    w4: float = Field(0.15, ge=0, le=1, description="population weight")
