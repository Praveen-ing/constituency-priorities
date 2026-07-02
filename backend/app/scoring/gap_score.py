"""
Gap Score computation — DETERMINISTIC. No LLM calls here. Ever.

Formula:
    GapScore(theme T, location L) =
        w1 * normalize(citizen_volume)   [citizen demand signal]
      + w2 * normalize(urgency_signal)   [urgency weight]
      + w3 * normalize(data_deficit)     [objective supply gap]
      + w4 * normalize(population)       [scale of impact]

All inputs are floats. The LLM's job is ONLY to explain this score (in justification.py).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GapScoreInput:
    """All inputs required to compute a Gap Score for one (theme, ward) pair."""
    # Raw (un-normalized) values
    citizen_volume: int        # count of submissions for this theme in this ward
    urgency_signal: float      # mean urgency score [0, 1] across submissions
    data_deficit: float        # theme-specific supply gap metric [0, +inf]; see deficit_calculators.py
    population_affected: int   # Census ward population
    # Weights (can be overridden by MP dashboard sliders)
    w1: float = 0.30
    w2: float = 0.20
    w3: float = 0.35
    w4: float = 0.15


@dataclass
class GapScoreResult:
    gap_score: float           # final score [0, 1]
    citizen_volume_norm: float
    urgency_norm: float
    data_deficit_norm: float
    population_norm: float
    w1: float
    w2: float
    w3: float
    w4: float


def _normalize_volume(volume: int, max_volume: int) -> float:
    """Normalize submission count relative to the constituency max."""
    if max_volume <= 0:
        return 0.0
    return min(1.0, volume / max_volume)


def _normalize_urgency(urgency: float) -> float:
    """Urgency is already [0, 1] from Gemini Flash classification."""
    return max(0.0, min(1.0, urgency))


def _normalize_deficit(deficit: float, cap: float = 3.0) -> float:
    """
    Normalize data_deficit to [0, 1].
    Cap at `cap` to prevent one extreme outlier dominating the score.
    deficit = 0 means no gap; deficit = cap means maximum possible gap.
    """
    if deficit <= 0:
        return 0.0
    return min(1.0, deficit / cap)


def _normalize_population(population: int, max_population: int) -> float:
    """Normalize ward population relative to constituency's most populous ward."""
    if max_population <= 0:
        return 0.0
    return min(1.0, population / max_population)


def compute_gap_score(
    inp: GapScoreInput,
    max_volume: int,
    max_population: int,
) -> GapScoreResult:
    """
    Compute the Gap Score for a single (theme, ward) pair.

    Args:
        inp: GapScoreInput with raw values and weights.
        max_volume: Maximum citizen_volume across ALL (theme, ward) pairs in this run
                    (used for normalization).
        max_population: Maximum ward population across all wards (for normalization).

    Returns:
        GapScoreResult with the final gap_score and all normalized components.
    """
    # Validate weights sum approximately to 1
    weight_sum = inp.w1 + inp.w2 + inp.w3 + inp.w4
    if abs(weight_sum - 1.0) > 0.01:
        # Renormalize weights
        inp.w1 /= weight_sum
        inp.w2 /= weight_sum
        inp.w3 /= weight_sum
        inp.w4 /= weight_sum

    cv_norm = _normalize_volume(inp.citizen_volume, max_volume)
    urg_norm = _normalize_urgency(inp.urgency_signal)
    def_norm = _normalize_deficit(inp.data_deficit)
    pop_norm = _normalize_population(inp.population_affected, max_population)

    gap_score = (
        inp.w1 * cv_norm
        + inp.w2 * urg_norm
        + inp.w3 * def_norm
        + inp.w4 * pop_norm
    )
    gap_score = max(0.0, min(1.0, gap_score))

    return GapScoreResult(
        gap_score=gap_score,
        citizen_volume_norm=cv_norm,
        urgency_norm=urg_norm,
        data_deficit_norm=def_norm,
        population_norm=pop_norm,
        w1=inp.w1,
        w2=inp.w2,
        w3=inp.w3,
        w4=inp.w4,
    )


def batch_compute_and_rank(
    inputs: list[tuple[str, str, GapScoreInput]],  # (theme_id, ward_id, input)
    max_volume: int | None = None,
    max_population: int | None = None,
) -> list[tuple[str, str, GapScoreResult, int]]:
    """
    Compute Gap Scores for a batch of (theme, ward) pairs and rank them.

    Returns list of (theme_id, ward_id, result, rank) sorted by gap_score descending.
    """
    if not inputs:
        return []

    # Determine normalization bounds from the batch itself if not provided
    if max_volume is None:
        max_volume = max(i.citizen_volume for _, _, i in inputs) or 1
    if max_population is None:
        max_population = max(i.population_affected for _, _, i in inputs) or 1

    results = []
    for theme_id, ward_id, inp in inputs:
        result = compute_gap_score(inp, max_volume, max_population)
        results.append((theme_id, ward_id, result))

    # Sort descending by gap_score and assign ranks
    results.sort(key=lambda x: x[2].gap_score, reverse=True)
    return [(tid, wid, res, rank + 1) for rank, (tid, wid, res) in enumerate(results)]
