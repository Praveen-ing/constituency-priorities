"""
Per-theme data_deficit calculators.
Each function returns a float [0, +inf] representing the objective supply gap.
0 = no gap; higher values = bigger gap.

All functions are deterministic — no LLM calls.
Data comes from BigQuery public dataset tables (Census, UDISE+, NFHS).
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def education_deficit(
    enrollment: int,
    school_capacity: int,
    nearest_school_km: float = 0.0,
) -> float:
    """
    Education supply gap.
    deficit = (enrollment / capacity) - 1  +  distance_penalty

    - enrollment > capacity → overcrowding → higher gap
    - large distance to nearest school → higher gap
    """
    if school_capacity <= 0:
        return 1.0  # no data = treat as moderate gap

    overcrowding = max(0.0, (enrollment / school_capacity) - 1.0)
    distance_penalty = min(1.0, nearest_school_km / 10.0)  # normalise over 10km
    return round(overcrowding + distance_penalty, 4)


def water_deficit(
    households_without_tap: int,
    total_households: int,
) -> float:
    """
    Water supply gap.
    deficit = fraction of households without piped water access
    """
    if total_households <= 0:
        return 0.5
    return round(households_without_tap / total_households, 4)


def road_deficit(
    complaints_in_ward: int,
    ward_road_length_km: float,
) -> float:
    """
    Road quality gap.
    deficit = complaints per km of road (normalized against a baseline of 5 complaints/km)
    """
    if ward_road_length_km <= 0:
        return 0.0
    complaints_per_km = complaints_in_ward / ward_road_length_km
    baseline = 5.0
    return round(complaints_per_km / baseline, 4)


def health_deficit(
    ward_population: int,
    nearest_phc_capacity: int,
    distance_to_phc_km: float = 0.0,
) -> float:
    """
    Health facility supply gap.
    deficit = (population / PHC_capacity) normalised  +  distance_penalty
    """
    if nearest_phc_capacity <= 0:
        return 1.0

    load_ratio = max(0.0, (ward_population / nearest_phc_capacity) - 1.0)
    distance_penalty = min(1.0, distance_to_phc_km / 15.0)  # normalise over 15km
    return round(load_ratio + distance_penalty, 4)


def sanitation_deficit(
    households_without_toilet: int,
    total_households: int,
) -> float:
    """
    Sanitation gap = fraction of HHs without toilet (similar to water).
    """
    if total_households <= 0:
        return 0.5
    return round(households_without_toilet / total_households, 4)


def electricity_deficit(
    households_without_electricity: int,
    total_households: int,
) -> float:
    """Electricity supply gap."""
    if total_households <= 0:
        return 0.5
    return round(households_without_electricity / total_households, 4)


# Fallback for themes without a specific calculator
def generic_deficit(urgency_signal: float) -> float:
    """
    For themes without a specific public dataset (housing, employment, other).
    Use urgency_signal as a proxy deficit measure.
    """
    return round(urgency_signal, 4)


DEFICIT_CALCULATOR_MAP = {
    "education": None,    # call education_deficit() with UDISE+ args
    "water": None,        # call water_deficit() with Census args
    "roads": None,        # call road_deficit()
    "health": None,       # call health_deficit() with NFHS args
    "sanitation": None,   # call sanitation_deficit()
    "electricity": None,  # call electricity_deficit()
    "housing": "generic",
    "employment": "generic",
    "other": "generic",
}
