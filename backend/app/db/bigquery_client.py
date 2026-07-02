"""
BigQuery client — singleton + typed query helpers.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from google.cloud import bigquery

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_bq_client() -> bigquery.Client:
    settings = get_settings()
    return bigquery.Client(project=settings.gcp_project)


def _table(name: str) -> str:
    settings = get_settings()
    return f"{settings.gcp_project}.{settings.bq_dataset}.{name}"


def insert_submission(row: dict[str, Any]) -> str:
    """Insert a submission row and return its ID."""
    client = get_bq_client()
    row.setdefault("id", str(uuid.uuid4()))
    row.setdefault("created_at", datetime.now(timezone.utc).isoformat())

    errors = client.insert_rows_json(_table("submissions"), [row])
    if errors:
        logger.error("BQ insert errors: %s", errors)
    return row["id"]


def get_submissions(
    theme: str | None = None,
    ward_id: str | None = None,
    limit: int = 100,
) -> list[dict]:
    client = get_bq_client()
    where_clauses = []
    params = []

    if theme:
        where_clauses.append("theme = @theme")
        params.append(bigquery.ScalarQueryParameter("theme", "STRING", theme))
    if ward_id:
        where_clauses.append("ward_id = @ward_id")
        params.append(bigquery.ScalarQueryParameter("ward_id", "STRING", ward_id))

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"""
        SELECT * FROM `{_table("submissions")}`
        {where_sql}
        ORDER BY created_at DESC
        LIMIT @limit
    """
    params.append(bigquery.ScalarQueryParameter("limit", "INT64", limit))

    job = client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
    return [dict(row) for row in job.result()]


def get_priorities(
    constituency: str | None = None,
    limit: int = 20,
) -> list[dict]:
    client = get_bq_client()
    query = f"""
        SELECT p.*, t.label as theme_label
        FROM `{_table("priorities")}` p
        LEFT JOIN `{_table("themes")}` t ON p.theme_id = t.theme_id
        ORDER BY p.gap_score DESC
        LIMIT @limit
    """
    params = [bigquery.ScalarQueryParameter("limit", "INT64", limit)]
    job = client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
    return [dict(row) for row in job.result()]


def upsert_priority(row: dict[str, Any]) -> None:
    """Insert or update a priority row."""
    client = get_bq_client()
    row.setdefault("priority_id", str(uuid.uuid4()))
    row.setdefault("computed_at", datetime.now(timezone.utc).isoformat())
    errors = client.insert_rows_json(_table("priorities"), [row])
    if errors:
        logger.error("BQ priority insert errors: %s", errors)


def get_theme_stats() -> list[dict]:
    """Aggregate submission counts + mean urgency per theme."""
    client = get_bq_client()
    query = f"""
        SELECT
            theme,
            COUNT(*) as submission_count,
            AVG(urgency) as mean_urgency,
            ARRAY_AGG(DISTINCT ward_id IGNORE NULLS) as ward_ids
        FROM `{_table("submissions")}`
        WHERE theme IS NOT NULL
        GROUP BY theme
        ORDER BY submission_count DESC
    """
    job = client.query(query)
    return [dict(row) for row in job.result()]
