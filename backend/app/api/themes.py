"""
GET /themes — clustered theme list with submission counts.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.db.bigquery_client import get_theme_stats

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("")
async def list_themes() -> list[dict]:
    """Return aggregated theme stats from BigQuery."""
    stats = get_theme_stats()
    return [
        {
            "theme_id": s["theme"],
            "label": s["theme"].replace("_", " ").title(),
            "submission_count": int(s.get("submission_count", 0)),
            "mean_urgency": float(s.get("mean_urgency", 0)),
            "ward_ids": s.get("ward_ids", []),
        }
        for s in stats
    ]
