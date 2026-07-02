"""
Entity extraction: location geocoding via Gemini Flash + Google Maps.
"""
from __future__ import annotations

import json
import logging

import google.generativeai as genai
import httpx

from app.config import get_settings
from app.nlp.prompts import EXTRACT_LOCATION_PROMPT

logger = logging.getLogger(__name__)


class EntityResult:
    __slots__ = ("primary_location", "locations", "lat", "lng", "ward_id")

    def __init__(
        self,
        primary_location: str | None,
        locations: list[str],
        lat: float | None,
        lng: float | None,
        ward_id: str | None,
    ) -> None:
        self.primary_location = primary_location
        self.locations = locations
        self.lat = lat
        self.lng = lng
        self.ward_id = ward_id


def _geocode(location: str, constituency: str, state: str) -> tuple[float | None, float | None]:
    """Geocode a location string using the Google Maps Geocoding API."""
    settings = get_settings()
    if not settings.maps_api_key:
        return None, None

    query = f"{location}, {constituency}, {state}, India"
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    try:
        resp = httpx.get(url, params={"address": query, "key": settings.maps_api_key}, timeout=5.0)
        data = resp.json()
        if data.get("status") == "OK":
            loc = data["results"][0]["geometry"]["location"]
            return float(loc["lat"]), float(loc["lng"])
    except Exception as exc:
        logger.warning("Geocoding failed for %r: %s", query, exc)
    return None, None


def extract_entities(text: str, location_hint: str | None = None) -> EntityResult:
    """
    Extract location entities from submission text using Gemini Flash,
    then geocode the primary location.
    """
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        model_name=settings.gemini_flash_model,
        generation_config=genai.types.GenerationConfig(
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )

    prompt = EXTRACT_LOCATION_PROMPT.format(
        submission_text=text,
        constituency=settings.pilot_constituency,
        state=settings.pilot_state,
    )

    locations: list[str] = []
    primary_location: str | None = location_hint

    try:
        response = model.generate_content(prompt)
        data = json.loads(response.text.strip())
        locations = data.get("locations", [])
        primary_location = data.get("primary_location") or location_hint
    except Exception as exc:
        logger.warning("Entity extraction failed: %s", exc)

    lat, lng = None, None
    if primary_location:
        lat, lng = _geocode(primary_location, settings.pilot_constituency, settings.pilot_state)

    # ward_id: simplified — use location name as ward slug for now
    ward_id = primary_location.lower().replace(" ", "_") if primary_location else None

    return EntityResult(
        primary_location=primary_location,
        locations=locations,
        lat=lat,
        lng=lng,
        ward_id=ward_id,
    )
