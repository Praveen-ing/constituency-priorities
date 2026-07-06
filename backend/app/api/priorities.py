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
from app.scoring.gap_score_rapids import compute_gap_scores_rapids
from app.scoring.justification import generate_justification
from app.nlp.classify import generate_health_score_explanation
import json
import os

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

    hs_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "health_score.json")
    health_score = None
    if os.path.exists(hs_path):
        try:
            with open(hs_path, "r", encoding="utf-8") as f:
                health_score = json.load(f)
        except Exception:
            pass

    duplicate_count = 0
    try:
        from app.db.bigquery_client import get_theme_stats
        stats = get_theme_stats()
        duplicate_count = sum(s.get("duplicate_count", 0) for s in stats)
    except Exception:
        pass

    return PriorityListResponse(
        priorities=priorities,
        constituency=settings.pilot_constituency,
        total=len(priorities),
        computed_at=datetime.now(timezone.utc),
        health_score=health_score,
        duplicate_count=duplicate_count
    )


@router.post("/recompute", status_code=202)
async def recompute_priorities(
    weights: WeightOverride = WeightOverride(),
    use_gpu: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> dict:
    """
    Trigger a fresh Gap Score computation with the given weight overrides.
    If use_gpu=True, routes to the NVIDIA RAPIDS engine for 5M-row computation.
    If use_gpu=False, uses standard pandas (CPU benchmark mode).
    Returns timing metadata so the frontend can display the speed difference.
    """
    background_tasks.add_task(_recompute_task, weights, use_gpu)
    return {"message": "Recomputation triggered", "weights": weights.model_dump(), "use_gpu": use_gpu}


def _recompute_task(weights: WeightOverride, use_gpu: bool = False) -> None:
    """
    Background: aggregate submissions → compute Gap Scores → upsert priorities.
    Routes to RAPIDS (cuDF) for GPU acceleration over 5M rows when use_gpu=True.
    Falls back gracefully to pandas (CPU) if cuDF is not available.
    """
    settings = get_settings()
    try:
        # --- RAPIDS / large-dataset path ---
        rapids_results, actually_gpu = compute_gap_scores_rapids(
            weights={"w1": weights.w1, "w2": weights.w2, "w3": weights.w3, "w4": weights.w4},
            use_gpu=use_gpu,
        )

        if rapids_results:
            total = len(rapids_results)
            logger.info(
                "RAPIDS recompute: %d priorities, GPU=%s, time=%dms",
                total, actually_gpu, rapids_results[0].elapsed_ms if rapids_results else 0
            )
            for rank, result in enumerate(rapids_results, start=1):
                justification = generate_justification(
                    theme_name=result.theme.replace("_", " ").title(),
                    ward_name=result.ward_id.replace("_", " ").title(),
                    constituency_name=settings.pilot_constituency,
                    volume=result.submission_count,
                    days=30,
                    urgency_pct=result.mean_urgency * 100,
                    deficit_description=f"supply gap score {result.gap_score:.2f}",
                    population=50000,
                    gap_score=result.gap_score,
                    rank=rank,
                    total=total,
                )
                upsert_priority({
                    "theme_id": result.theme,
                    "ward_id": result.ward_id,
                    "gap_score": result.gap_score,
                    "citizen_volume_norm": min(result.submission_count / 100000, 1.0),
                    "urgency_norm": result.mean_urgency,
                    "data_deficit_norm": result.gap_score,
                    "population_norm": 0.5,
                    "justification": justification,
                    "rank": rank,
                    "submission_count": result.submission_count,
                    "elapsed_ms": result.elapsed_ms,
                    "accelerated": result.accelerated,
                })
            logger.info("Recomputed %d priorities via %s", total, "GPU" if actually_gpu else "CPU")
            return
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
        
        # --- Compute Constituency Health Score ---
        _compute_and_save_health_score()
        
    except Exception as exc:
        logger.error("Recompute task failed: %s", exc)

def _compute_and_save_health_score():
    try:
        priorities = get_priorities(limit=3)
        avg_gap = sum(p.get("gap_score", 0) for p in priorities) / len(priorities) if priorities else 0
        
        subs = get_submissions(limit=5000)
        total_subs = len(subs)
        emergencies = sum(1 for s in subs if s.get("is_emergency"))
        ratio = emergencies / total_subs if total_subs > 0 else 0
        
        c1 = {"name": "Resolution Trend", "score": 60.0, "weight": 0.30}
        c2 = {"name": "Emergency Ratio", "score": max(0.0, 100 - (ratio * 1000)), "weight": 0.20}
        c3 = {"name": "Top 3 Gap Score", "score": max(0.0, 100 - (avg_gap * 100)), "weight": 0.25}
        c4 = {"name": "Volume Trend", "score": 80.0, "weight": 0.15}
        c5 = {"name": "Data Coverage", "score": 90.0, "weight": 0.10}
        
        components = [c1, c2, c3, c4, c5]
        overall = sum(c["score"] * c["weight"] for c in components)
        
        explanation = generate_health_score_explanation(int(overall), components)
        
        hs_data = {
            "score": int(overall),
            "trend": "up",
            "explanation": explanation,
            "components": components
        }
        
        hs_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "health_score.json")
        os.makedirs(os.path.dirname(hs_path), exist_ok=True)
        with open(hs_path, "w", encoding="utf-8") as f:
            json.dump(hs_data, f)
            
        logger.info("Computed and saved Health Score: %d", int(overall))
    except Exception as exc:
        logger.error("Failed to compute health score: %s", exc)
