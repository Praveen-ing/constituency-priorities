# Constituency Priorities — AI for Constituency Development Planning

> **Hackathon**: Google Cloud — Build with AI: Code for Communities  
> **Track**: Track 1 — People's Priorities

A multilingual AI platform where citizens submit development suggestions via voice, text, or photos. The system clusters submissions, cross-references real public datasets (Census, UDISE+), and surfaces a ranked priority list with an auditable **Demand vs Supply Gap Score** for the MP's office.

---

## Architecture

```
Citizens (WhatsApp / SMS / Web PWA)
        ↓
Ingestion Service (Cloud Run / FastAPI)
  · audio → Cloud Speech-to-Text v2 (chirp_2) → Translation API
  · image → Gemini 2.5 Flash multimodal
  · text  → direct NLP path
        ↓
NLP / Reasoning (Gemini 2.5 Flash + Pro)
  · Theme classification (Flash, structured JSON)
  · Entity extraction: location, urgency, facility type (Flash)
  · Embeddings → HDBSCAN clustering (Vertex AI text-embedding-005)
  · Gap Score justification string (Pro)
        ↓
Data Fusion (BigQuery)
  · Joins citizen submissions with Census, UDISE+, NFHS, dev plan data
  · Computes deterministic Gap Score per theme × ward
        ↓
Frontend (Next.js 15 → Firebase Hosting)
  · Citizen PWA: voice-first, icon-based, multilingual
  · MP Dashboard: ranked priorities, hotspot map, drill-down, weight sliders
```

See [`docs/architecture.md`](docs/architecture.md) for the full diagram.

---

## Quick Start (Local Dev)

### Prerequisites
- Python 3.12+
- Node.js 20+
- Google Cloud SDK authenticated (`gcloud auth application-default login`)
- Firebase CLI (`npm install -g firebase-tools`)

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env.local
# Fill in GCP_PROJECT, BQ_DATASET, GEMINI_API_KEY in .env.local
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Fill in NEXT_PUBLIC_API_URL, NEXT_PUBLIC_MAPS_KEY, NEXT_PUBLIC_FIREBASE_* in .env.local
npm run dev
```

Visit `http://localhost:3000`

---

## Deployment

### Backend (Cloud Run)

```bash
cd backend
gcloud run deploy constituency-priorities-api \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 1Gi
```

### Frontend (Firebase Hosting)

```bash
cd frontend
npm run build
firebase deploy --only hosting
```

---

## Seed Data

To populate the dashboard with realistic demo data:

```bash
cd scripts
python seed_data.py           # Loads 300 synthetic submissions + public datasets into BQ
python validate_gap_scores.py # Sanity-check Gap Scores
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI (reasoning) | Gemini 2.5 Pro |
| AI (classification) | Gemini 2.5 Flash |
| Voice | Cloud Speech-to-Text v2 (chirp_2) |
| Translation | Cloud Translation API |
| Embeddings | Vertex AI text-embedding-005 |
| Clustering | HDBSCAN |
| Data warehouse | BigQuery |
| Backend | Python 3.12 / FastAPI / Cloud Run |
| Frontend | Next.js 15 / Tailwind CSS / Firebase Hosting |
| Maps | Google Maps Platform |
| Auth | Firebase Auth |
| Real-time | Firebase Realtime Database |
| Messaging | Twilio WhatsApp Sandbox |

---

## Key Links

- **Deployed prototype**: [Firebase Hosting URL]
- **Backend API**: [Cloud Run URL]
- **Demo video**: [YouTube/Drive link]
- **Pitch deck**: [Slides link]
