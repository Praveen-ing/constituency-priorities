"""
Generate 5,000,000 mock citizen submissions spanning 5 years.
Saves to data/submissions_5m.parquet for use by the Gap Score computation pipeline.

Usage:
    python -m app.data.generate_massive_dataset

Output:
    backend/data/submissions_5m.parquet (~120MB compressed)
"""
import os
import time
import numpy as np
import pandas as pd

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "submissions_5m.parquet")
N_ROWS = 5_000_000

THEMES = ["water", "sanitation", "education", "road", "health", "electricity", "waste_management", "housing"]
WARDS = ["old_city", "gachibowli", "rajapuram", "riverside", "green_valley", "banjara_hills", "new_market", "madhapur"]
SOURCES = ["whatsapp", "web", "sms", "voice_ivr"]
LANGUAGES = ["hi", "te", "en", "en", "en"]  # en weighted higher

def generate() -> None:
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    print(f"Generating {N_ROWS:,} rows of mock submission data...")
    t0 = time.time()

    rng = np.random.default_rng(seed=42)

    # Simulate non-uniform distributions — some themes/wards are much busier
    theme_weights = np.array([0.22, 0.18, 0.15, 0.14, 0.10, 0.09, 0.07, 0.05])
    ward_weights = np.array([0.20, 0.18, 0.15, 0.12, 0.12, 0.10, 0.08, 0.05])

    theme_indices = rng.choice(len(THEMES), size=N_ROWS, p=theme_weights / theme_weights.sum())
    ward_indices = rng.choice(len(WARDS), size=N_ROWS, p=ward_weights / ward_weights.sum())

    df = pd.DataFrame({
        "submission_id": [f"sub_{i:08d}" for i in range(N_ROWS)],
        "theme": pd.Categorical([THEMES[i] for i in theme_indices]),
        "ward_id": pd.Categorical([WARDS[i] for i in ward_indices]),
        "source": pd.Categorical(rng.choice(SOURCES, size=N_ROWS)),
        "language": pd.Categorical(rng.choice(LANGUAGES, size=N_ROWS)),
        "urgency_score": rng.beta(2, 5, size=N_ROWS).astype("float32"),     # skewed low (most are medium urgency)
        "sentiment_score": rng.uniform(-1.0, 1.0, size=N_ROWS).astype("float32"),
        "created_at": pd.to_datetime(
            rng.integers(
                pd.Timestamp("2020-01-01").value,
                pd.Timestamp("2025-07-01").value,
                size=N_ROWS,
            )
        ),
        "is_anonymous": rng.choice([True, False], size=N_ROWS, p=[0.4, 0.6]),
        "vote_count": rng.negative_binomial(2, 0.5, size=N_ROWS).astype("int32"),
    })

    # Add computed columns that the Gap Score will aggregate over
    df["urgency_flag"] = (df["urgency_score"] > 0.65).astype("int8")
    df["year"] = df["created_at"].dt.year.astype("int16")
    df["month"] = df["created_at"].dt.month.astype("int8")

    t1 = time.time()
    print(f"Generated DataFrame in {t1 - t0:.2f}s. Saving to Parquet...")

    df.to_parquet(OUTPUT_PATH, engine="pyarrow", compression="snappy", index=False)

    t2 = time.time()
    size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    print(f"Saved {N_ROWS:,} rows ({size_mb:.1f} MB) to {OUTPUT_PATH} in {t2 - t1:.2f}s")
    print(f"Total time: {t2 - t0:.2f}s")

if __name__ == "__main__":
    generate()
