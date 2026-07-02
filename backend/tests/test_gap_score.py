"""
Unit tests for gap_score.py — CRITICAL: every function must have test coverage.
The Gap Score formula is our core technical IP — judges will probe it.
"""
import pytest

from app.scoring.gap_score import (
    GapScoreInput,
    GapScoreResult,
    _normalize_deficit,
    _normalize_population,
    _normalize_urgency,
    _normalize_volume,
    batch_compute_and_rank,
    compute_gap_score,
)


# ── Normalization function tests ──────────────────────────────────────────────

class TestNormalizeVolume:
    def test_zero_volume(self):
        assert _normalize_volume(0, 100) == 0.0

    def test_max_volume(self):
        assert _normalize_volume(100, 100) == 1.0

    def test_half_volume(self):
        assert _normalize_volume(50, 100) == 0.5

    def test_zero_max(self):
        assert _normalize_volume(50, 0) == 0.0

    def test_exceeds_max_capped(self):
        assert _normalize_volume(150, 100) == 1.0


class TestNormalizeUrgency:
    def test_zero(self):
        assert _normalize_urgency(0.0) == 0.0

    def test_one(self):
        assert _normalize_urgency(1.0) == 1.0

    def test_midpoint(self):
        assert _normalize_urgency(0.5) == 0.5

    def test_below_zero_clamped(self):
        assert _normalize_urgency(-0.5) == 0.0

    def test_above_one_clamped(self):
        assert _normalize_urgency(1.5) == 1.0


class TestNormalizeDeficit:
    def test_zero_deficit(self):
        assert _normalize_deficit(0.0) == 0.0

    def test_at_cap(self):
        assert _normalize_deficit(3.0) == 1.0

    def test_above_cap_capped(self):
        assert _normalize_deficit(5.0) == 1.0

    def test_half_cap(self):
        assert abs(_normalize_deficit(1.5) - 0.5) < 0.001

    def test_negative_is_zero(self):
        assert _normalize_deficit(-1.0) == 0.0


class TestNormalizePopulation:
    def test_zero(self):
        assert _normalize_population(0, 100000) == 0.0

    def test_max(self):
        assert _normalize_population(100000, 100000) == 1.0

    def test_zero_max(self):
        assert _normalize_population(50000, 0) == 0.0


# ── compute_gap_score tests ───────────────────────────────────────────────────

class TestComputeGapScore:
    def _make_input(self, **kwargs) -> GapScoreInput:
        defaults = dict(
            citizen_volume=50,
            urgency_signal=0.6,
            data_deficit=1.5,
            population_affected=40000,
            w1=0.30,
            w2=0.20,
            w3=0.35,
            w4=0.15,
        )
        defaults.update(kwargs)
        return GapScoreInput(**defaults)

    def test_result_is_in_range(self):
        inp = self._make_input()
        result = compute_gap_score(inp, max_volume=100, max_population=100000)
        assert 0.0 <= result.gap_score <= 1.0

    def test_zero_inputs_produce_zero_score(self):
        inp = self._make_input(citizen_volume=0, urgency_signal=0.0, data_deficit=0.0, population_affected=0)
        result = compute_gap_score(inp, max_volume=100, max_population=100000)
        assert result.gap_score == 0.0

    def test_max_inputs_produce_one_score(self):
        inp = self._make_input(
            citizen_volume=100, urgency_signal=1.0, data_deficit=3.0, population_affected=100000
        )
        result = compute_gap_score(inp, max_volume=100, max_population=100000)
        assert abs(result.gap_score - 1.0) < 0.001

    def test_weight_renormalization(self):
        # Weights don't sum to 1 — should be renormalized
        inp = self._make_input(w1=1.0, w2=1.0, w3=1.0, w4=1.0)
        result = compute_gap_score(inp, max_volume=100, max_population=100000)
        assert 0.0 <= result.gap_score <= 1.0

    def test_high_deficit_increases_score(self):
        inp_low = self._make_input(data_deficit=0.1)
        inp_high = self._make_input(data_deficit=2.9)
        r_low = compute_gap_score(inp_low, max_volume=100, max_population=100000)
        r_high = compute_gap_score(inp_high, max_volume=100, max_population=100000)
        assert r_high.gap_score > r_low.gap_score

    def test_high_volume_increases_score(self):
        inp_low = self._make_input(citizen_volume=5)
        inp_high = self._make_input(citizen_volume=95)
        r_low = compute_gap_score(inp_low, max_volume=100, max_population=100000)
        r_high = compute_gap_score(inp_high, max_volume=100, max_population=100000)
        assert r_high.gap_score > r_low.gap_score

    def test_breakdown_components_sum_to_score(self):
        inp = self._make_input()
        result = compute_gap_score(inp, max_volume=100, max_population=100000)
        expected = (
            result.w1 * result.citizen_volume_norm
            + result.w2 * result.urgency_norm
            + result.w3 * result.data_deficit_norm
            + result.w4 * result.population_norm
        )
        assert abs(result.gap_score - expected) < 1e-9


# ── batch_compute_and_rank tests ──────────────────────────────────────────────

class TestBatchComputeAndRank:
    def _make_inp(self, volume: int, deficit: float) -> GapScoreInput:
        return GapScoreInput(
            citizen_volume=volume,
            urgency_signal=0.5,
            data_deficit=deficit,
            population_affected=30000,
        )

    def test_empty_input_returns_empty(self):
        assert batch_compute_and_rank([]) == []

    def test_single_item_is_rank_1(self):
        inp = self._make_inp(50, 1.0)
        results = batch_compute_and_rank([("education", "ward_a", inp)])
        assert len(results) == 1
        assert results[0][3] == 1  # rank

    def test_higher_score_ranked_first(self):
        inp_low = self._make_inp(volume=5, deficit=0.1)
        inp_high = self._make_inp(volume=90, deficit=2.5)
        results = batch_compute_and_rank([
            ("water", "ward_x", inp_low),
            ("education", "ward_y", inp_high),
        ])
        # The high-score one should be rank 1
        assert results[0][0] == "education"
        assert results[0][3] == 1
        assert results[1][3] == 2

    def test_ranks_are_sequential(self):
        inputs = [
            ("theme_a", "ward_1", self._make_inp(10, 0.5)),
            ("theme_b", "ward_2", self._make_inp(30, 1.0)),
            ("theme_c", "ward_3", self._make_inp(60, 2.0)),
        ]
        results = batch_compute_and_rank(inputs)
        ranks = [r[3] for r in results]
        assert ranks == [1, 2, 3]
