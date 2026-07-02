"""
GET /priorities — ranked priority list with Gap Scores.
POST /priorities/recompute — trigger a fresh Gap Score computation.
GET /priorities/{priority_id} — single priority with drill-down data.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.config import get_settings
from app.db.bigquery_client import (
    get_priorities,
    get_submissions,
    get_theme_stats,
    upsert_priority,
)
from app.models.priority import GapScoreBreakdown, Priority, PriorityListResponse, WeightOverride
from app.scoring.deficit_calculators import generic_deficit
from app.scoring.gap_score import GapScoreInput, batch_compute_and_rank
from app.scoring.justification import generate_justification

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/priorities", tags=["priorities"])


def _build_priorities_from_bq(rows: list[dict]) -> list[Priority]:
    """Convert raw BQ rows into Priority Pydantic models."""
    priorities = []
    for rank, row in enumerate(rows, start=1):
        breakdown = GapScoreBreakdown(
            citizen_volume_norm=float(row.get("citizen_volume_norm", 0)),
            urgency_norm=float(row.get("urgency_norm", 0)),
            data_deficit_norm=float(row.get("data_deficit_norm", 0)),
            population_norm=float(row.get("population_norm", 0)),
        )
        priorities.append(
            Priority(
                priority_id=row["priority_id"],
                theme_id=row["theme_id"],
                theme_label=row.get("theme_label", row.get("theme_id", "Unknown")),
                ward_id=row.get("ward_id", "unknown"),
                ward_name=row.get("ward_id", "").replace("_", " ").title(),
                gap_score=float(row.get("gap_score", 0)),
                breakdown=breakdown,
                justification=row.get("justification", ""),
                rank=row.get("rank", rank),
                computed_at=row.get("computed_at", datetime.now(timezone.utc)),
                submission_count=int(row.get("submission_count", 0)),
            )
        )
    return priorities


@router.get("", response_model=PriorityListResponse)
async def list_priorities(limit: int = 20) -> PriorityListResponse:
    """Return the ranked priority list from BigQuery."""
    settings = get_settings()
    rows = get_priorities(limit=min(limit, 50))
    priorities = _build_priorities_from_bq(rows)

    return PriorityListResponse(
        priorities=priorities,
        constituency=settings.pilot_constituency,
        total=len(priorities),
        computed_at=datetime.now(timezone.utc),
    )


@router.post("/recompute", status_code=202)
async def recompute_priorities(
    weights: WeightOverride = WeightOverride(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> dict:
    """
    Trigger a fresh Gap Score computation with the given weight overrides.
    Runs asynchronously — dashboard should poll /priorities after a few seconds.
    """
    background_tasks.add_task(_recompute_task, weights)
    return {"message": "Recomputation triggered", "weights": weights.model_dump()}


def _recompute_task(weights: WeightOverride) -> None:
    """
    Background: aggregate submissions → compute Gap Scores → upsert priorities.
    Called with ~20 theme×ward combinations — Pro justification is generated here.
    """
    settings = get_settings()
    try:
        theme_stats = get_theme_stats()
        if not theme_stats:
            logger.warning("No theme stats found — skipping recompute")
            return

        inputs = []
        for stat in theme_stats:
            theme = stat["theme"]
            # Use urgency as proxy deficit for non-specific themes
            deficit = generic_deficit(float(stat.get("mean_urgency", 0.3)))
            ward_ids = stat.get("ward_ids") or ["unknown"]

            for ward_id in ward_ids[:3]:  # top 3 wards per theme
                inp = GapScoreInput(
                    citizen_volume=int(stat.get("submission_count", 0)),
                    urgency_signal=float(stat.get("mean_urgency", 0.3)),
                    data_deficit=deficit,
                    population_affected=50000,  # placeholder — replace with Census join
                    w1=weights.w1,
                    w2=weights.w2,
                    w3=weights.w3,
                    w4=weights.w4,
                )
                inputs.append((theme, ward_id, inp))

        ranked = batch_compute_and_rank(inputs)
        total = len(ranked)

        for theme_id, ward_id, result, rank in ranked:
            justification = generate_justification(
                theme_name=theme_id.replace("_", " ").title(),
                ward_name=ward_id.replace("_", " ").title(),
                constituency_name=settings.pilot_constituency,
                volume=int(result.citizen_volume_norm * 100),  # approx
                days=30,
                urgency_pct=result.urgency_norm * 100,
                deficit_description=f"supply gap score {result.data_deficit_norm:.2f}",
                population=50000,
                gap_score=result.gap_score,
                rank=rank,
                total=total,
            )

            upsert_priority({
                "theme_id": theme_id,
                "ward_id": ward_id,
                "gap_score": result.gap_score,
                "citizen_volume_norm": result.citizen_volume_norm,
                "urgency_norm": result.urgency_norm,
                "data_deficit_norm": result.data_deficit_norm,
                "population_norm": result.population_norm,
                "justification": justification,
                "rank": rank,
            })

        logger.info("Recomputed %d priorities", total)
    except Exception as exc:
        logger.error("Recompute task failed: %s", exc)
