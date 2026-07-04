"""
BigQuery client — singleton + typed query helpers.

In LOCAL / DEV mode (when GCP credentials or project ID are not configured),
this module automatically falls back to an in-memory SQLite database so the
entire backend API works perfectly without any cloud setup.

The fallback is activated when:
  - `gcp_project` is the default placeholder ("constituency-priorities") AND
    no valid GOOGLE_APPLICATION_CREDENTIALS env var is set, OR
  - any BigQuery operation raises an exception.

Run `python -m app.db.seed_local_db` once to populate the SQLite DB with
realistic demo data.
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SQLite fallback — used when BigQuery is not configured
# ---------------------------------------------------------------------------
_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "local_dev.sqlite3")

def _get_sqlite_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _ensure_sqlite_schema() -> None:
    conn = _get_sqlite_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS submissions (
            id TEXT PRIMARY KEY,
            media_type TEXT,
            content TEXT,
            original_language TEXT DEFAULT 'en',
            source TEXT DEFAULT 'web',
            theme TEXT,
            ward_id TEXT,
            urgency_score REAL DEFAULT 0.5,
            sentiment_score REAL DEFAULT 0.0,
            is_anonymous INTEGER DEFAULT 0,
            created_at TEXT,
            processed INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS themes (
            theme_id TEXT PRIMARY KEY,
            label TEXT,
            submission_count INTEGER DEFAULT 0,
            mean_urgency REAL DEFAULT 0.5
        );
        CREATE TABLE IF NOT EXISTS priorities (
            priority_id TEXT PRIMARY KEY,
            theme_id TEXT,
            ward_id TEXT,
            gap_score REAL,
            citizen_volume_norm REAL,
            urgency_norm REAL,
            data_deficit_norm REAL,
            population_norm REAL,
            justification TEXT,
            rank INTEGER,
            submission_count INTEGER DEFAULT 0,
            elapsed_ms INTEGER DEFAULT 0,
            accelerated INTEGER DEFAULT 0,
            computed_at TEXT
        );
    """)
    conn.commit()
    conn.close()

_ensure_sqlite_schema()

# ---------------------------------------------------------------------------
# Detect whether we should use BigQuery or SQLite
# ---------------------------------------------------------------------------
def _use_bigquery() -> bool:
    """Return True only if real GCP credentials appear to be available."""
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    gcp_project = os.environ.get("GCP_PROJECT", "")
    # Use BigQuery only if both credentials file and project are explicitly set
    if creds and os.path.exists(creds) and gcp_project:
        return True
    return False


@lru_cache(maxsize=1)
def get_bq_client():
    if not _use_bigquery():
        return None
    from google.cloud import bigquery
    from app.config import get_settings
    settings = get_settings()
    return bigquery.Client(project=settings.gcp_project)


def _table(name: str) -> str:
    from app.config import get_settings
    settings = get_settings()
    return f"{settings.gcp_project}.{settings.bq_dataset}.{name}"


# ---------------------------------------------------------------------------
# Public API — delegates to BigQuery or SQLite transparently
# ---------------------------------------------------------------------------

def insert_submission(row: dict[str, Any]) -> str:
    """Insert a submission row and return its ID."""
    row.setdefault("id", str(uuid.uuid4()))
    row.setdefault("created_at", datetime.now(timezone.utc).isoformat())

    if _use_bigquery():
        try:
            client = get_bq_client()
            from google.cloud import bigquery
            errors = client.insert_rows_json(_table("submissions"), [row])
            if errors:
                logger.error("BQ insert errors: %s", errors)
            return row["id"]
        except Exception as e:
            logger.warning("BigQuery insert failed, using SQLite: %s", e)

    # SQLite fallback
    conn = _get_sqlite_conn()
    conn.execute(
        """INSERT OR REPLACE INTO submissions
           (id, media_type, content, original_language, source, theme, ward_id,
            urgency_score, sentiment_score, is_anonymous, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            row.get("id"), row.get("media_type", "text"), row.get("content", ""),
            row.get("original_language", "en"), row.get("source", "web"),
            row.get("theme"), row.get("ward_id"),
            row.get("urgency_score", 0.5), row.get("sentiment_score", 0.0),
            1 if row.get("is_anonymous") else 0, row.get("created_at"),
        )
    )
    conn.commit()
    conn.close()
    logger.info("Submission %s saved to SQLite", row["id"])
    return row["id"]


def get_submissions(
    theme: str | None = None,
    ward_id: str | None = None,
    limit: int = 100,
) -> list[dict]:
    if _use_bigquery():
        try:
            client = get_bq_client()
            from google.cloud import bigquery
            where_clauses, params = [], []
            if theme:
                where_clauses.append("theme = @theme")
                params.append(bigquery.ScalarQueryParameter("theme", "STRING", theme))
            if ward_id:
                where_clauses.append("ward_id = @ward_id")
                params.append(bigquery.ScalarQueryParameter("ward_id", "STRING", ward_id))
            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
            query = f"SELECT * FROM `{_table('submissions')}` {where_sql} ORDER BY created_at DESC LIMIT @limit"
            params.append(bigquery.ScalarQueryParameter("limit", "INT64", limit))
            job = client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
            return [dict(row) for row in job.result()]
        except Exception as e:
            logger.warning("BigQuery get_submissions failed, using SQLite: %s", e)

    # SQLite fallback
    conn = _get_sqlite_conn()
    wheres, vals = [], []
    if theme:
        wheres.append("theme = ?")
        vals.append(theme)
    if ward_id:
        wheres.append("ward_id = ?")
        vals.append(ward_id)
    where_sql = f"WHERE {' AND '.join(wheres)}" if wheres else ""
    vals.append(limit)
    rows = conn.execute(f"SELECT * FROM submissions {where_sql} ORDER BY created_at DESC LIMIT ?", vals).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_priorities(constituency: str | None = None, limit: int = 20) -> list[dict]:
    if _use_bigquery():
        try:
            client = get_bq_client()
            from google.cloud import bigquery
            query = f"""
                SELECT p.*, t.label as theme_label
                FROM `{_table("priorities")}` p
                LEFT JOIN `{_table("themes")}` t ON p.theme_id = t.theme_id
                ORDER BY p.gap_score DESC LIMIT @limit
            """
            params = [bigquery.ScalarQueryParameter("limit", "INT64", limit)]
            job = client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
            return [dict(row) for row in job.result()]
        except Exception as e:
            logger.warning("BigQuery get_priorities failed, using SQLite: %s", e)

    # SQLite fallback
    conn = _get_sqlite_conn()
    rows = conn.execute("""
        SELECT p.*, p.theme_id as theme_label
        FROM priorities p
        ORDER BY p.gap_score DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_priority(row: dict[str, Any]) -> None:
    row.setdefault("priority_id", str(uuid.uuid4()))
    row.setdefault("computed_at", datetime.now(timezone.utc).isoformat())

    if _use_bigquery():
        try:
            client = get_bq_client()
            from google.cloud import bigquery
            errors = client.insert_rows_json(_table("priorities"), [row])
            if errors:
                logger.error("BQ priority insert errors: %s", errors)
            return
        except Exception as e:
            logger.warning("BigQuery upsert_priority failed, using SQLite: %s", e)

    # SQLite fallback
    conn = _get_sqlite_conn()
    conn.execute(
        """INSERT OR REPLACE INTO priorities
           (priority_id, theme_id, ward_id, gap_score, citizen_volume_norm,
            urgency_norm, data_deficit_norm, population_norm, justification,
            rank, submission_count, elapsed_ms, accelerated, computed_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            row.get("priority_id"), row.get("theme_id"), row.get("ward_id"),
            row.get("gap_score", 0.0), row.get("citizen_volume_norm", 0.0),
            row.get("urgency_norm", 0.0), row.get("data_deficit_norm", 0.0),
            row.get("population_norm", 0.0), row.get("justification", ""),
            row.get("rank", 99), row.get("submission_count", 0),
            row.get("elapsed_ms", 0), 1 if row.get("accelerated") else 0,
            row.get("computed_at"),
        )
    )
    conn.commit()
    conn.close()


def get_theme_stats() -> list[dict]:
    if _use_bigquery():
        try:
            client = get_bq_client()
            query = f"""
                SELECT theme, COUNT(*) as submission_count,
                       AVG(urgency_score) as mean_urgency,
                       ARRAY_AGG(DISTINCT ward_id IGNORE NULLS LIMIT 5) as ward_ids
                FROM `{_table("submissions")}`
                WHERE theme IS NOT NULL
                GROUP BY theme ORDER BY submission_count DESC
            """
            job = client.query(query)
            return [dict(row) for row in job.result()]
        except Exception as e:
            logger.warning("BigQuery get_theme_stats failed, using SQLite: %s", e)

    # SQLite fallback
    conn = _get_sqlite_conn()
    rows = conn.execute("""
        SELECT theme, COUNT(*) as submission_count,
               AVG(urgency_score) as mean_urgency
        FROM submissions WHERE theme IS NOT NULL
        GROUP BY theme ORDER BY submission_count DESC
    """).fetchall()
    # Fetch wards per theme
    result = []
    for r in rows:
        d = dict(r)
        ward_rows = conn.execute(
            "SELECT DISTINCT ward_id FROM submissions WHERE theme=? AND ward_id IS NOT NULL LIMIT 5",
            (d["theme"],)
        ).fetchall()
        d["ward_ids"] = [w["ward_id"] for w in ward_rows]
        result.append(d)
    conn.close()
    return result
