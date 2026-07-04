"""
Seed the local SQLite development database with realistic demo data.

Run once before starting the backend for the first time:
    python -m app.db.seed_local_db

This populates:
- 50 citizen submissions across 5 themes and 5 wards
- 8 theme cluster entries
- 12 pre-computed priority entries with Gap Scores and justifications
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
import random
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "local_dev.sqlite3")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

THEMES = ["water", "education", "roads", "sanitation", "health", "electricity", "waste_management", "housing"]
WARDS = ["old_city", "gachibowli", "rajapuram", "riverside", "green_valley"]
SOURCES = ["whatsapp", "web", "sms", "voice_ivr"]

SAMPLE_SUBMISSIONS = [
    ("water", "old_city", "Our street has no water supply for 3 days. Children are suffering.", 0.92),
    ("water", "old_city", "Borewell at community center is broken since last month.", 0.78),
    ("water", "old_city", "Request for new water pipeline in our colony.", 0.65),
    ("water", "riverside", "Water comes only for 30 minutes per day. Not enough.", 0.85),
    ("education", "rajapuram", "School has 900 students but capacity for only 400. Classes held in corridors.", 0.95),
    ("education", "rajapuram", "We need more teachers. One teacher for 80 students.", 0.88),
    ("education", "rajapuram", "School toilets are broken. Girls are dropping out.", 0.90),
    ("education", "gachibowli", "No computer lab in our government school.", 0.60),
    ("roads", "new_market", "Large potholes on main road causing accidents.", 0.82),
    ("roads", "new_market", "Road near the market completely broken after monsoon.", 0.79),
    ("sanitation", "riverside", "Open drains near houses causing disease outbreak.", 0.88),
    ("sanitation", "riverside", "No public toilet for 500 households in our area.", 0.91),
    ("health", "green_valley", "Nearest PHC is 12km away. Pregnant women at risk.", 0.94),
    ("health", "green_valley", "PHC has no doctor assigned since 6 months.", 0.89),
    ("electricity", "old_city", "Load shedding 8 hours per day. Small businesses suffering.", 0.71),
]

PRE_COMPUTED_PRIORITIES = [
    {
        "theme_id": "education", "ward_id": "rajapuram",
        "gap_score": 0.87, "rank": 1, "submission_count": 42,
        "citizen_volume_norm": 0.92, "urgency_norm": 0.88, "data_deficit_norm": 0.95, "population_norm": 0.72,
        "justification": "42 urgent submissions + school enrollment 142% of capacity + nearest alternate school 6.2km away supports HIGH priority for Rajapuram ward school expansion.",
    },
    {
        "theme_id": "water", "ward_id": "old_city",
        "gap_score": 0.74, "rank": 2, "submission_count": 31,
        "citizen_volume_norm": 0.65, "urgency_norm": 0.85, "data_deficit_norm": 0.82, "population_norm": 0.58,
        "justification": "31 submissions with 85% urgency + 67% of Old City households lack piped water per Census data drives HIGH priority water infrastructure.",
    },
    {
        "theme_id": "health", "ward_id": "green_valley",
        "gap_score": 0.71, "rank": 3, "submission_count": 18,
        "citizen_volume_norm": 0.45, "urgency_norm": 0.94, "data_deficit_norm": 0.88, "population_norm": 0.62,
        "justification": "18 critical health submissions + nearest PHC 12km away serving 54,000 residents = urgent need for Green Valley primary health facility.",
    },
    {
        "theme_id": "sanitation", "ward_id": "riverside",
        "gap_score": 0.63, "rank": 4, "submission_count": 24,
        "citizen_volume_norm": 0.55, "urgency_norm": 0.89, "data_deficit_norm": 0.72, "population_norm": 0.48,
        "justification": "24 sanitation complaints + open drains and zero public toilets for 8,000+ residents in Riverside drives HIGH priority sanitation investment.",
    },
    {
        "theme_id": "roads", "ward_id": "new_market",
        "gap_score": 0.54, "rank": 5, "submission_count": 19,
        "citizen_volume_norm": 0.48, "urgency_norm": 0.80, "data_deficit_norm": 0.60, "population_norm": 0.45,
        "justification": "19 road damage reports post-monsoon + market road serving 300+ daily commercial vehicles warrants medium-high road repair priority.",
    },
    {
        "theme_id": "electricity", "ward_id": "old_city",
        "gap_score": 0.46, "rank": 6, "submission_count": 14,
        "citizen_volume_norm": 0.38, "urgency_norm": 0.71, "data_deficit_norm": 0.52, "population_norm": 0.55,
        "justification": "14 electricity outage complaints with 8hr daily load-shedding affecting small businesses in Old City warrants medium priority grid upgrade.",
    },
    {
        "theme_id": "water", "ward_id": "riverside",
        "gap_score": 0.41, "rank": 7, "submission_count": 11,
        "citizen_volume_norm": 0.30, "urgency_norm": 0.65, "data_deficit_norm": 0.48, "population_norm": 0.40,
        "justification": "11 water supply complaints in Riverside with 30-minute daily supply window indicates medium infrastructure gap needing attention.",
    },
    {
        "theme_id": "education", "ward_id": "gachibowli",
        "gap_score": 0.35, "rank": 8, "submission_count": 8,
        "citizen_volume_norm": 0.25, "urgency_norm": 0.60, "data_deficit_norm": 0.40, "population_norm": 0.35,
        "justification": "8 education submissions in Gachibowli focused on digital infrastructure gap — moderate priority for computer lab investment.",
    },
]

def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS submissions (
            id TEXT PRIMARY KEY, media_type TEXT, content TEXT,
            original_language TEXT DEFAULT 'en', source TEXT DEFAULT 'web',
            theme TEXT, ward_id TEXT, urgency_score REAL DEFAULT 0.5,
            sentiment_score REAL DEFAULT 0.0, is_anonymous INTEGER DEFAULT 0,
            created_at TEXT, processed INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS themes (
            theme_id TEXT PRIMARY KEY, label TEXT,
            submission_count INTEGER DEFAULT 0, mean_urgency REAL DEFAULT 0.5
        );
        CREATE TABLE IF NOT EXISTS priorities (
            priority_id TEXT PRIMARY KEY, theme_id TEXT, ward_id TEXT,
            gap_score REAL, citizen_volume_norm REAL, urgency_norm REAL,
            data_deficit_norm REAL, population_norm REAL, justification TEXT,
            rank INTEGER, submission_count INTEGER DEFAULT 0,
            elapsed_ms INTEGER DEFAULT 0, accelerated INTEGER DEFAULT 0,
            computed_at TEXT
        );
        DELETE FROM submissions;
        DELETE FROM themes;
        DELETE FROM priorities;
    """)

    # Insert submissions
    base_time = datetime.now(timezone.utc) - timedelta(days=30)
    rows = []
    for theme, ward, content, urgency in SAMPLE_SUBMISSIONS:
        ts = base_time + timedelta(hours=random.randint(0, 720))
        rows.append((str(uuid.uuid4()), "text", content, "en", random.choice(SOURCES),
                     theme, ward, urgency, random.uniform(-0.3, 0.3), 0, ts.isoformat()))
    
    # Add extra random ones to reach ~50
    for _ in range(35):
        theme = random.choice(THEMES)
        ward = random.choice(WARDS)
        ts = base_time + timedelta(hours=random.randint(0, 720))
        rows.append((str(uuid.uuid4()), "text", f"Issue with {theme} in our area needs urgent attention.", 
                     "en", random.choice(SOURCES), theme, ward, 
                     round(random.uniform(0.3, 0.9), 2), round(random.uniform(-0.5, 0.5), 2),
                     1 if random.random() > 0.6 else 0, ts.isoformat()))

    conn.executemany("""INSERT INTO submissions 
        (id, media_type, content, original_language, source, theme, ward_id,
         urgency_score, sentiment_score, is_anonymous, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", rows)

    # Insert themes
    theme_labels = {
        "water": "Water Supply", "education": "Education", "roads": "Roads & Infrastructure",
        "sanitation": "Sanitation", "health": "Healthcare Access", "electricity": "Electricity",
        "waste_management": "Waste Management", "housing": "Housing"
    }
    for theme_id, label in theme_labels.items():
        count = conn.execute("SELECT COUNT(*) FROM submissions WHERE theme=?", (theme_id,)).fetchone()[0]
        avg_urgency = conn.execute("SELECT AVG(urgency_score) FROM submissions WHERE theme=?", (theme_id,)).fetchone()[0] or 0.5
        conn.execute("INSERT INTO themes VALUES (?,?,?,?)", (theme_id, label, count, avg_urgency))

    # Insert priorities
    now = datetime.now(timezone.utc).isoformat()
    for p in PRE_COMPUTED_PRIORITIES:
        conn.execute("""INSERT INTO priorities 
            (priority_id, theme_id, ward_id, gap_score, citizen_volume_norm,
             urgency_norm, data_deficit_norm, population_norm, justification,
             rank, submission_count, elapsed_ms, accelerated, computed_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (str(uuid.uuid4()), p["theme_id"], p["ward_id"], p["gap_score"],
             p["citizen_volume_norm"], p["urgency_norm"], p["data_deficit_norm"],
             p["population_norm"], p["justification"], p["rank"],
             p["submission_count"], 0, 0, now))

    conn.commit()
    sub_count = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
    pri_count = conn.execute("SELECT COUNT(*) FROM priorities").fetchone()[0]
    conn.close()
    print(f"Seeded OK: {sub_count} submissions, {pri_count} priorities -> {DB_PATH}")

if __name__ == "__main__":
    seed()
