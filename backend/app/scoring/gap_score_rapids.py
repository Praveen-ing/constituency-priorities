"""
NVIDIA RAPIDS-accelerated Gap Score computation.

This module is the GPU-powered twin of gap_score.py. It uses cudf.pandas
(NVIDIA RAPIDS) to compute the same deterministic Gap Score formula over
the full 5M-row dataset in < 1 second on a GPU, vs 15-30s on a CPU.

Architecture rule (AGENTS.md): gap_score_rapids.py is DETERMINISTIC.
No LLM calls inside it. It receives the Parquet path and weights, returns ranked results.

Requires:
    - NVIDIA GPU with CUDA 12+
    - cudf installed: pip install cudf-cu12 --extra-index-url=https://pypi.nvidia.com
    - Falls back to standard pandas automatically if cudf is not available (CPU mode).
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "submissions_5m.parquet")

@dataclass
class AcceleratedResult:
    theme: str
    ward_id: str
    gap_score: float
    submission_count: int
    mean_urgency: float
    elapsed_ms: int
    accelerated: bool  # True = cuDF GPU, False = pandas CPU


def _compute_with_engine(df_lib, weights: dict) -> list[dict]:
    """
    The deterministic Gap Score aggregation logic.
    df_lib can be either cudf.pandas (GPU) or pandas (CPU).
    Same logic, different hardware.
    """
    df = df_lib.read_parquet(DATA_PATH)

    # --- Aggregate per (theme, ward_id) ---
    agg = df.groupby(["theme", "ward_id"]).agg(
        submission_count=("submission_id", "count"),
        mean_urgency=("urgency_score", "mean"),
        urgency_flag_sum=("urgency_flag", "sum"),
        mean_vote_count=("vote_count", "mean"),
        mean_sentiment=("sentiment_score", "mean"),
    ).reset_index()

    # --- Normalize 0-1 per column ---
    def normalize(col):
        min_v = col.min()
        max_v = col.max()
        rng = max_v - min_v
        if rng == 0:
            return col * 0.0
        return (col - min_v) / rng

    agg["vol_norm"] = normalize(agg["submission_count"])
    agg["urgency_norm"] = normalize(agg["mean_urgency"])
    agg["deficit_norm"] = normalize(agg["urgency_flag_sum"] / (agg["submission_count"] + 1))
    agg["pop_norm"] = normalize(agg["mean_vote_count"])

    # --- Weighted Gap Score (deterministic formula) ---
    w1 = weights.get("w1", 0.30)
    w2 = weights.get("w2", 0.20)
    w3 = weights.get("w3", 0.35)
    w4 = weights.get("w4", 0.15)

    agg["gap_score"] = (
        w1 * agg["vol_norm"] +
        w2 * agg["urgency_norm"] +
        w3 * agg["deficit_norm"] +
        w4 * agg["pop_norm"]
    )

    agg = agg.sort_values("gap_score", ascending=False)

    # Convert back to Python list (works for both cudf and pandas)
    return agg.head(20).to_pandas().to_dict(orient="records") if hasattr(agg, 'to_pandas') else agg.head(20).to_dict(orient="records")


def compute_gap_scores_rapids(weights: dict, use_gpu: bool = True) -> tuple[list[AcceleratedResult], bool]:
    """
    Main entry point. Routes to GPU (cuDF) or CPU (pandas) based on use_gpu flag and hardware availability.

    Returns:
        (results, actually_used_gpu)
    """
    if not os.path.exists(DATA_PATH):
        logger.warning("5M dataset not found at %s. Run generate_massive_dataset.py first.", DATA_PATH)
        # Return empty — caller should handle gracefully
        return [], False

    actually_gpu = False
    t0 = time.perf_counter()

    if use_gpu:
        try:
            import cudf.pandas as df_lib
            logger.info("Using NVIDIA cuDF (GPU) for Gap Score computation")
            records = _compute_with_engine(df_lib, weights)
            actually_gpu = True
        except ImportError:
            logger.warning("cudf not available — falling back to pandas (CPU mode)")
            import pandas as df_lib
            records = _compute_with_engine(df_lib, weights)
    else:
        logger.info("Using pandas (CPU) for Gap Score computation [benchmark mode]")
        import pandas as df_lib
        records = _compute_with_engine(df_lib, weights)

    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    logger.info("Gap Score computed in %dms (GPU=%s)", elapsed_ms, actually_gpu)

    results = [
        AcceleratedResult(
            theme=r["theme"],
            ward_id=r["ward_id"],
            gap_score=float(r["gap_score"]),
            submission_count=int(r["submission_count"]),
            mean_urgency=float(r["mean_urgency"]),
            elapsed_ms=elapsed_ms,
            accelerated=actually_gpu,
        )
        for r in records
    ]
    return results, actually_gpu
