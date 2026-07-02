from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # GCP
    gcp_project: str = "constituency-priorities"
    bq_dataset: str = "constituency_data"
    gcs_bucket: str = "constituency-uploads"
    gcp_region: str = "asia-south1"

    # Gemini / Vertex AI
    gemini_api_key: str = ""
    gemini_pro_model: str = "gemini-2.5-pro"
    gemini_flash_model: str = "gemini-2.5-flash"
    vertex_embedding_model: str = "text-embedding-005"

    # Firebase
    firebase_credentials_path: str = ""  # path to service account JSON
    firebase_db_url: str = ""            # https://<project>.firebaseio.com

    # Twilio (WhatsApp sandbox)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"  # Twilio sandbox default

    # Google Maps
    maps_api_key: str = ""

    # App
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000", "https://constituency-priorities.web.app"]

    # Pilot constituency (used for all data joins)
    pilot_constituency: str = "Hyderabad"
    pilot_state: str = "Telangana"


@lru_cache
def get_settings() -> Settings:
    return Settings()
