# Build with AI: Code for Communities — Master Winning Plan
## Track 1: People's Priorities — AI for Constituency Development Planning

> **Status**: Active Development
> **Last Updated**: June 2026
> **Hackathon**: Google Cloud — Build with AI: Code for Communities

---

## 0. Why Track 1 Wins (and Why the Others Don't)

Scoring weights: Deployability & Scalability (**25%**) · AI/Technical Execution (**25%**) · Problem-Solution Fit (**20%**) · Inclusivity & Accessibility (**15%**) · Impact Potential (**10%**) · Presentation (**5%**)

**50% of your score is "does the AI do real, non-decorative work" + "could this run in a real constituency in weeks."**
Track 1 is the ONLY track where you satisfy both without faking your core data:

| Track | Fatal flaw |
|---|---|
| Track 2 (CleanAir) | Real sensor networks + satellite pipelines you can't access. 24h spike predictor on toy data = seen through by reviewers who know the AQI space. |
| Track 3 (Smart Health) | PHC inventory/footfall data doesn't exist digitally. Becomes data-entry software with a forecasting bolt-on = decorative AI. |
| Track 4 (Kisan Alert) | Three components (crop rec + advisory + diagnosis) — too much surface area for a month. Photo-crop-disease is the most commoditized ML problem in the list. |
| **Track 1 (This one)** | Text/voice/image inputs you fully control + real public datasets (Census, UDISE+, data.gov.in). NLP clustering + multi-criteria ranking = technically deep AND deployable. |

This is the pick. Here is how to win it.

---

## 1. The Winning Strategy

### 1.1 Your Differentiator: The Demand vs Supply Gap Score

Judges have seen 50 teams build "citizen complaint chatbot + dashboard." That scores ~60%.
**To win you need something structurally hard to copy in a weekend** — combining heterogeneous data with auditable reasoning.

**Your differentiator:** For every recurring theme (e.g., school overcrowding), compute:

1. **Citizen signal** — submission volume + sentiment + urgency (from NLP pipeline)
2. **Public data numbers** — UDISE+ enrollment, Census ward population, distance-to-facility
3. **Gap Score** — deterministic weighted formula, NOT a black-box LLM score
4. **Plain-English justification** — Gemini explains the score in one sentence the MP's PA reads in 5 seconds:
   *"42 citizen requests + enrollment 38% above capacity + nearest alternate school 6.2km away -> HIGH PRIORITY"*

This hits simultaneously:
- **Problem-Solution Fit** — directly answers the problem statement's "weigh competing proposals against real demand"
- **AI/Technical Execution** — multi-source reasoning, auditable formula, LLM bounded to explanation only
- **Presentation** — a non-technical reader gets it instantly

### 1.2 Core Demo Flow (What Judges Will Literally Watch)

1. Citizen submits via 3 channels on stage: WhatsApp-style text, voice note in Hindi/Telugu, photo with caption (e.g., broken handpump)
2. **Live processing visualization**: transcription -> translation -> classification -> entity extraction -> geotagging, shown as pipeline cards — not a black box
3. **Dashboard updates in real-time**: new pin on map, themes re-cluster, priority ranking shifts
4. **MP-facing view**: ranked list of top 5 priorities, each with Gap Score breakdown + Gemini justification
5. **Drill-down**: click a priority -> see citizen submissions + public data + recommended action
6. **Inclusivity moment**: switch to low-literacy icon-based voice-guided flow on screen

**Rule**: Never show a screen judges can't understand in 5 seconds. Design for the MP's PA, not a CS professor.

### 1.3 Inclusivity (15% — do not treat as afterthought)

Worth more than Impact + Presentation combined. Concrete requirements:

- Voice intake in **Hindi + Telugu** (or Hindi + Tamil — pick based on team; both well-supported by Cloud Speech-to-Text chirp_2)
- **Low-literacy mode**: icon-based / voice-guided submission flow — NOT a text form with a language dropdown
- **Low-connectivity design**: offline-tolerant submission (queue-and-sync PWA pattern), SMS fallback path
- Dedicated slide with a concrete "low-literacy citizen, no smartphone" user journey walkthrough

### 1.4 Deployability (25% — most underrated category)

Build a literal slide titled **"Why this runs in a real constituency in weeks, not months"**:

- Ingests existing channels (WhatsApp, SMS) — citizens don't need a new app
- Read-only/advisory to MP's office — zero government IT system integration required on day one
- Data sources are public/open (Census, data.gov.in) — no MoU or data-sharing agreement needed
- Show rough monthly GCP cost: ~$50-150/month at pilot scale (Cloud Run scale-to-zero + BigQuery on-demand)

---

## 2. Team Structure & Division of Labor

### 2.1 Roles (4-person team)

| Role | Owns | Primary Tools |
|---|---|---|
| **A — AI/NLP Lead** | Intake pipeline: STT, translation, classification, theme clustering, Gap Score reasoning prompts | Gemini 2.5 Pro/Flash, Cloud Speech-to-Text, Translation API, Vertex AI Embeddings |
| **B — Data/Backend Lead** | Data model, public dataset ingestion (Census/UDISE+/data.gov.in), BigQuery schema, ranking algorithm, FastAPI layer | BigQuery, Cloud Run, Python/FastAPI, Cloud Storage |
| **C — Frontend Lead** | Citizen-facing submission PWA + MP-facing dashboard + map view | Next.js 15, Google Maps Platform, Firebase Hosting, Framer Motion |
| **D — Infra/Integration + Deck Lead** | Auth, CI/CD pipeline, WhatsApp/SMS intake wiring, demo video, pitch deck | Cloud Run, Firebase Auth, Twilio, GitHub Actions, Figma/Canva |

> **3-person team?** Merge C + D — frontend lead also owns deployment + deck. Firebase Hosting deploys are trivial; Cloud Run is one command once set up.

### 2.2 Collaboration Stack

| Tool | Purpose |
|---|---|
| **GitHub** (this repo) | Single source of truth. Branch-per-feature, PRs to main. Judges check commit history — make it real incremental work. |
| **Antigravity IDE** | Primary agentic coding IDE. Each member runs it on their own branch/worktree. Use AGENTS.md to encode conventions so every agent session follows the same rules. |
| **Google AI Studio** | Rapid prompt iteration for classification/extraction prompts before porting to Cloud Run |
| **BigQuery Studio** | Ad-hoc SQL for validating data joins and Gap Score computations during development |
| **Figma / Excalidraw** | Architecture diagrams for deck and README |

---

## 3. Full Technical Architecture

### 3.1 System Architecture Diagram

```
+------------------------------------------------------------------+
|                         INTAKE LAYER                              |
|   WhatsApp (Twilio)  |  SMS  |  Web PWA  |  Voice IVR (future)  |
+------------------------------+-----------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|              INGESTION SERVICE  (Cloud Run / FastAPI)             |
|  +-- audio  --> Cloud Speech-to-Text v2 (chirp_2 model)          |
|  |            --> Cloud Translation API --> normalized text       |
|  +-- image  --> Gemini 2.5 Flash multimodal                       |
|  |            --> caption + issue classification                   |
|  +-- text   --> direct to NLP stage                               |
+------------------------------+-----------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|           NLP / REASONING LAYER  (Gemini 2.5 Pro + Flash)        |
|  +-- Theme classification  --> structured JSON (controlled output)|
|  +-- Entity extraction     --> location, facility type, urgency  |
|  +-- Embedding generation  --> Vertex AI text-embedding-005      |
|  +-- Theme clustering      --> HDBSCAN on embeddings             |
+------------------------------+-----------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|           DATA FUSION LAYER  (BigQuery)                           |
|  +-- submissions table                                            |
|  +-- themes table (clustered)                                     |
|  +-- public datasets: Census wards, UDISE+ schools,              |
|  |   local dev plan line items, NFHS health data                 |
|  +-- Gap Score computation: theme + geography --> score          |
+------------------------------+-----------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|            API LAYER  (Cloud Run / FastAPI)                       |
|  /submissions  /themes  /priorities  /gapscore  /webhooks        |
|  Firebase Auth JWT validation on MP-facing endpoints             |
+------------------------------+-----------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|            FRONTEND  (Next.js 15 --> Firebase Hosting)           |
|  +-- Citizen PWA: voice-first, icon-based, multilingual          |
|  +-- MP Dashboard: ranked priorities, hotspot map, drill-down    |
+------------------------------------------------------------------+
```

### 3.2 Tech Stack — Locked Decisions

| Layer | Choice | Rationale |
|---|---|---|
| **Primary AI reasoning** | **Gemini 2.5 Pro** | Deep multi-step reasoning for Gap Score justification. Use only where quality matters more than cost. |
| **High-volume classification** | **Gemini 2.5 Flash** | All per-submission classification calls. 10x cheaper than Pro, same quality for structured classification. |
| **Voice transcription** | **Cloud Speech-to-Text v2 (chirp_2)** | Best Indic language support. Handles code-switching (Hindi + English in same sentence), critical for real submissions. |
| **Translation** | **Cloud Translation API (Advanced)** | Normalize all submissions to English/Hindi for clustering. Store originals for display. |
| **Image understanding** | **Gemini 2.5 Flash multimodal** | Single model handles captioning + classification. No separate CV model needed. |
| **Embeddings** | **Vertex AI text-embedding-005** | Current best Vertex embedding model. Store in BigQuery for vector similarity search. |
| **Theme clustering** | **HDBSCAN** (hdbscan library) | Handles variable-density clusters, doesn't force all points into a cluster. Better than k-means for messy grievance data. |
| **Data warehouse** | **BigQuery** | Natural fit for joining submissions with Census/public datasets. On-demand pricing = near-zero cost at pilot scale. |
| **Backend API** | **Cloud Run (Python 3.12 / FastAPI)** | Serverless, scales to zero, trivial to deploy. Async support for streaming AI responses. |
| **Frontend** | **Next.js 15 (App Router) + Tailwind CSS** | Fast to build, SSR for SEO, judges get a real URL. Server components for initial data load. |
| **Maps** | **Google Maps Platform (Maps JS + Geocoding + Places)** | Hotspot heatmap visualization. Required-looking integration for this track. |
| **Auth** | **Firebase Auth** | Minimal setup for MP-dashboard login. Google Sign-In for demo. |
| **Real-time updates** | **Firebase Realtime Database** | Push new submission pins to dashboard map in real-time during the demo. |
| **Messaging intake** | **Twilio WhatsApp Sandbox** | Live within hours. Never gate timeline on full WhatsApp Business API approval (takes days). |
| **File storage** | **Google Cloud Storage** | Store uploaded audio/image files before processing. |
| **CI/CD** | **GitHub Actions** | Auto-deploy to Cloud Run + Firebase on merge to main. |

### 3.3 Gemini Model Usage Strategy (Cost Control)

```
Submission arrives
    |
    +-- Text classification (per submission)       --> Gemini 2.5 Flash (fast, cheap, structured JSON)
    +-- Image captioning + classification           --> Gemini 2.5 Flash multimodal
    +-- Entity extraction (per submission)          --> Gemini 2.5 Flash with structured output schema
    +-- Theme cluster justification (per cluster)   --> Gemini 2.5 Pro (richer reasoning, run infrequently)
    +-- Gap Score plain-English explanation          --> Gemini 2.5 Pro (most important output = best model)
```

**Cost control**: Flash for per-submission ops (volume = high), Pro for per-priority ops (volume = ~20 priorities/constituency).
At 1000 submissions/day, cost stays well under $10/day.

---

## 4. The Gap Score — Core Technical IP

Document this clearly. Judges WILL probe it. **The LLM never produces the ranking number — it only explains a deterministic calculation.** This is your strongest answer to "is this decorative AI?"

### 4.1 Formula

```
GapScore(theme T, location L) =
    w1 * normalize(citizen_volume(T, L))        [citizen demand signal]
  + w2 * normalize(urgency_signal(T, L))         [urgency weight]
  + w3 * normalize(data_deficit(T, L))           [objective supply gap]
  + w4 * normalize(population_affected(T, L))    [scale of impact]

where:
  citizen_volume(T, L)     = count of submissions tagged theme T in ward L
  urgency_signal(T, L)     = mean Gemini-extracted urgency score [0-1] for T in L
  data_deficit(T, L)       = theme-specific:
      education theme  --> (enrollment / school_capacity) - 1    [UDISE+]
      water theme      --> households_without_tap / total_hh     [Census]
      road theme       --> complaints_per_km / baseline_ratio    [local dev plan]
      health theme     --> population / nearest_PHC_capacity     [NFHS/state data]
  population_affected(T,L) = Census ward population in catchment area

  Default weights: w1=0.30, w2=0.20, w3=0.35, w4=0.15
  (w3 highest: objective data anchors the score, not just raw complaint volume)

  Weights are exposed as sliders on the MP dashboard.
  Live reweighting is a great demo moment: "watch the ranking change."
```

### 4.2 Justification String (Gemini 2.5 Pro)

A separate Gemini call — NEVER inside the scoring hot path — generates the explanation:

**Prompt template** (stored in `backend/app/nlp/prompts.py`, versioned):
```
You are an advisory assistant for an MP's constituency office.
Generate a single justification sentence (max 25 words) explaining why this theme
is ranked at the given priority level. Be specific with numbers. No caveats or hedges.

Theme: {theme_name}
Location: {ward_name}, {constituency_name}
Citizen submissions: {volume} in the last {days} days
Mean urgency: {urgency_pct}% flagged as urgent
Data deficit: {deficit_description}
Population affected: {population} residents
Gap Score: {gap_score:.2f} / 1.00 (ranked #{rank} of {total} priorities)

Output only the justification sentence, nothing else.
```

**Example output:**
*"38 urgent submissions + school enrollment 142% of capacity + nearest school 6.2km away supports HIGH priority for Rajapuram ward school expansion."*

### 4.3 Why This Architecture is Auditable (Key Deck Point)

- The ranking number comes from a **deterministic formula** (independently verifiable in BigQuery)
- The LLM's role is **bounded to natural language explanation** of that deterministic output
- Formula uses **real public datasets** — claims are independently verifiable
- An MP's office or journalist can audit any priority decision — this is a deployability superpower
- Explicitly state this in the deck: "The AI explains; the formula decides."

---

## 5. Repository Structure (Full File Tree)

```
constituency-priorities/
+-- AGENTS.md                           # Agent conventions: naming, testing rules, style
+-- README.md                           # Setup, architecture, deploy instructions
+-- .github/
|   +-- workflows/
|       +-- deploy-backend.yml          # Test + build + deploy Cloud Run on push to main
|       +-- deploy-frontend.yml         # Build + deploy Firebase Hosting on push to main
|       +-- lint.yml                    # Ruff (Python) + ESLint (TS) on every PR
|
+-- docs/
|   +-- architecture.md                 # Detailed architecture with diagrams
|   +-- gap-score-formula.md            # Formula, weights, per-theme data sources
|   +-- data-sources.md                 # Every public dataset used + URL + license
|   +-- prompt-catalog.md               # All Gemini prompts, versioned
|   +-- api-reference.md                # OpenAPI endpoint docs (auto-generated by FastAPI)
|
+-- infra/
|   +-- terraform/
|   |   +-- main.tf                     # GCP provider, project setup
|   |   +-- bigquery.tf                 # Dataset + table definitions
|   |   +-- cloudrun.tf                 # Cloud Run service + IAM
|   |   +-- storage.tf                  # GCS bucket for audio/image uploads
|   |   +-- variables.tf
|   +-- setup-gcp.sh                    # One-shot: enable APIs, create BQ datasets, set IAM
|
+-- backend/
|   +-- pyproject.toml                  # Project metadata + dev deps (ruff, pytest, mypy)
|   +-- requirements.txt                # Runtime deps
|   +-- Dockerfile                      # Multi-stage: builder + slim runtime image
|   +-- main.py                         # FastAPI app entrypoint + CORS + middleware
|   +-- app/
|   |   +-- config.py                   # Settings (pydantic-settings, reads from env)
|   |   |
|   |   +-- api/
|   |   |   +-- __init__.py
|   |   |   +-- submissions.py          # POST /submissions, GET /submissions
|   |   |   +-- themes.py               # GET /themes (clustered theme list)
|   |   |   +-- priorities.py           # GET /priorities (ranked + gap scores)
|   |   |   +-- gapscore.py             # GET /gapscore/{theme_id} (detailed breakdown)
|   |   |   +-- webhooks.py             # POST /webhook/twilio (WhatsApp/SMS inbound)
|   |   |
|   |   +-- ingestion/
|   |   |   +-- __init__.py
|   |   |   +-- router.py               # Route submission by media_type
|   |   |   +-- audio_pipeline.py       # Cloud STT --> Translation API --> text
|   |   |   +-- image_pipeline.py       # GCS upload --> Gemini Flash multimodal
|   |   |   +-- text_pipeline.py        # Minimal preprocessing for direct text input
|   |   |
|   |   +-- nlp/
|   |   |   +-- __init__.py
|   |   |   +-- classify.py             # Gemini Flash: structured theme classification
|   |   |   +-- extract_entities.py     # Gemini Flash: location, urgency, facility_type
|   |   |   +-- embeddings.py           # Vertex AI text-embedding-005 generation
|   |   |   +-- cluster.py              # HDBSCAN clustering on embeddings
|   |   |   +-- prompts.py              # All prompt templates (versioned strings)
|   |   |
|   |   +-- scoring/
|   |   |   +-- __init__.py
|   |   |   +-- gap_score.py            # Deterministic Gap Score formula -- NO LLM calls here
|   |   |   +-- normalizers.py          # Per-metric normalization functions
|   |   |   +-- deficit_calculators.py  # Per-theme data_deficit computation
|   |   |   +-- justification.py        # Gemini Pro: plain-English justification string
|   |   |
|   |   +-- data/
|   |   |   +-- __init__.py
|   |   |   +-- census_loader.py        # Load/clean Census ward data --> BigQuery
|   |   |   +-- udise_loader.py         # School enrollment data --> BigQuery
|   |   |   +-- devplan_loader.py       # Local dev plan line items --> BigQuery
|   |   |   +-- nfhs_loader.py          # NFHS health facility data --> BigQuery
|   |   |
|   |   +-- db/
|   |   |   +-- __init__.py
|   |   |   +-- bigquery_client.py      # Singleton BQ client + query helpers
|   |   |   +-- firebase_client.py      # Firebase Admin SDK (real-time push)
|   |   |   +-- schema.sql              # BQ table DDL (also used by Terraform)
|   |   |
|   |   +-- models/
|   |       +-- __init__.py
|   |       +-- submission.py           # Pydantic models for submissions
|   |       +-- theme.py                # Theme + cluster models
|   |       +-- priority.py             # Priority + GapScore response models
|   |
|   +-- tests/
|       +-- conftest.py
|       +-- test_gap_score.py           # CRITICAL: formula edge cases, weight normalization
|       +-- test_classify.py            # Classification accuracy on labeled test set
|       +-- test_ingestion.py           # Audio/image/text pipeline unit tests
|       +-- test_api.py                 # FastAPI endpoint integration tests
|
+-- frontend/
|   +-- package.json
|   +-- next.config.js
|   +-- tailwind.config.js
|   +-- tsconfig.json
|   +-- .env.local.example             # Template for environment variables
|   |
|   +-- public/
|   |   +-- icons/                     # Low-literacy iconography (SVG per issue type)
|   |   +-- locales/                   # i18n strings: en.json, hi.json, te.json
|   |   +-- manifest.json              # PWA manifest
|   |
|   +-- app/
|   |   +-- layout.tsx                 # Root layout, fonts, theme provider
|   |   +-- page.tsx                   # Landing/home page
|   |   |
|   |   +-- citizen/                   # Citizen-facing submission flow
|   |   |   +-- page.tsx               # Landing: choose input mode
|   |   |   +-- voice/page.tsx         # Voice recorder flow
|   |   |   +-- photo/page.tsx         # Photo upload + caption flow
|   |   |   +-- text/page.tsx          # Text/typed submission flow
|   |   |   +-- icon/page.tsx          # Low-literacy icon-selection flow
|   |   |   +-- components/
|   |   |       +-- LanguageSelector.tsx
|   |   |       +-- VoiceRecorder.tsx   # Web Audio API, uploads to GCS/backend
|   |   |       +-- LowLiteracyFlow.tsx # Icon grid, voice read-back of selection
|   |   |       +-- PhotoCapture.tsx
|   |   |       +-- SubmissionConfirm.tsx
|   |   |
|   |   +-- dashboard/                 # MP-facing dashboard (Firebase Auth protected)
|   |   |   +-- page.tsx               # Main dashboard: priority list + map
|   |   |   +-- priorities/[id]/page.tsx  # Drill-down: single priority detail
|   |   |   +-- components/
|   |   |       +-- PriorityList.tsx    # Ranked list with Gap Score badges
|   |   |       +-- HotspotMap.tsx      # Google Maps Platform + heatmap layer
|   |   |       +-- GapScoreCard.tsx    # Visual breakdown of score components
|   |   |       +-- WeightSliders.tsx   # Live weight adjustment (great demo moment)
|   |   |       +-- ThemeDrilldown.tsx  # Submissions behind a theme
|   |   |       +-- JustificationText.tsx  # Gemini-generated explanation display
|   |   |       +-- LiveFeed.tsx        # Real-time submission notification panel
|   |   |
|   |   +-- api/                       # Next.js API routes (thin proxies to backend)
|   |       +-- proxy/[...path]/route.ts
|   |
|   +-- lib/
|       +-- api.ts                     # Backend API client (typed, using fetch)
|       +-- firebase.ts                # Firebase client SDK init
|       +-- maps.ts                    # Google Maps loader utility
|       +-- i18n/
|           +-- provider.tsx
|           +-- useTranslation.ts
|
+-- data/
|   +-- seed-submissions/
|   |   +-- submissions_hi.json        # ~100 Hindi submissions (write manually)
|   |   +-- submissions_te.json        # ~100 Telugu submissions (write manually)
|   |   +-- submissions_en.json        # ~50 English submissions (write manually)
|   +-- public-datasets/
|       +-- census_ward_data.csv       # Census 2011 ward-level (pilot constituency)
|       +-- udise_school_data.csv      # UDISE+ school enrollment (pilot district)
|       +-- devplan_lineitems.csv      # Local dev plan projects (manually digitized)
|       +-- nfhs_health_data.csv       # NFHS-5 facility data
|
+-- scripts/
|   +-- seed_data.py                   # Loads seed-submissions + public datasets into BQ
|   +-- load_test.py                   # Generates 1000+ synthetic submissions for scale demo
|   +-- validate_gap_scores.py         # Sanity-check Gap Scores across all theme+location pairs
|   +-- export_demo_snapshot.py        # Exports a frozen BQ snapshot for offline demo backup
|
+-- pitch/
    +-- deck-outline.md                # 12-slide outline with speaker notes
    +-- demo-video-script.md           # Beat-by-beat demo script (timed)
```

---

## 6. Data Strategy — Real Public Datasets

| Dataset | Source | What it powers |
|---|---|---|
| **Census 2011 ward-level** | censusindia.gov.in (Tables B-2, B-28) | Population affected, household water/sanitation access |
| **UDISE+ 2022-23** | udiseplus.gov.in | School enrollment, capacity, teacher counts per school |
| **NFHS-5 district data** | rchiips.org/nfhs | Health facility access, PHC coverage ratios |
| **data.gov.in infrastructure** | data.gov.in | Road length, connectivity, infrastructure line items |
| **Local development plan PDF** | MP/constituency website or RTI | Proposed projects — manually digitize top 30 line items |

**Pilot constituency recommendation**: Pick a real Lok Sabha constituency with rich Census ward data — e.g., Hyderabad, Pune, or Jaipur. Use this single constituency throughout all demos. Makes the demo credible and avoids "this is made-up data" skepticism.

---

## 7. Detailed 4-Week Timeline

### Week 1 — Foundation (No UI yet)

**Goal: End-to-end pipeline on dummy data, deployed (even if broken)**

- [ ] Finalize pilot constituency (pick ONE — see section 6)
- [ ] GCP project setup: enable all APIs (Speech, Translation, Vertex AI, BigQuery, Cloud Run, Maps, Firebase)
- [ ] GitHub repo + branch conventions + AGENTS.md populated with conventions
- [ ] Acquire and clean 2-3 real public datasets (Census ward, UDISE+, one dev plan PDF)
- [ ] BigQuery schema defined and created (schema.sql + setup-gcp.sh)
- [ ] FastAPI skeleton: POST /submissions endpoint accepts JSON, stores to BQ (no NLP yet)
- [ ] Cloud Run deployment working (broken is fine, CI pipeline is wired)
- [ ] Firebase project created, Hosting configured

**Week 1 success check**: `curl -X POST [cloud-run-url]/submissions` -> row appears in BigQuery. Yes = Week 1 done.

### Week 2 — Core Intelligence

**Goal: The AI pipeline works end-to-end for all three input types**

- [ ] Audio pipeline: Cloud STT (chirp_2) -> Translation API -> text
- [ ] Image pipeline: GCS upload -> Gemini 2.5 Flash multimodal -> caption + classification JSON
- [ ] Text pipeline: Gemini 2.5 Flash -> structured theme classification (JSON: theme, urgency, facility_type, location_text)
- [ ] Entity extraction: Gemini 2.5 Flash -> extract lat/lon hint (geocoded via Maps API), ward name
- [ ] Vertex AI embeddings generated per submission, stored in BQ
- [ ] HDBSCAN clustering running on embeddings, theme labels computed
- [ ] Gap Score v1: implement formula for education + water themes with real UDISE+/Census data
- [ ] Seed dataset: write 300 realistic synthetic submissions in Hindi/Telugu/English (manually — critical for demo credibility)

**Week 2 success check**: Submit a Hindi voice note -> see it classified, embedded, Gap Scored in BQ. Yes = Week 2 done.

### Week 3 — Product Layer

**Goal: Judges can see and use the thing**

- [ ] Citizen PWA: language selector -> voice/photo/text/icon mode -> submit -> confirmation
- [ ] MP Dashboard: ranked priority list + hotspot map (Google Maps Platform heatmap layer)
- [ ] GapScoreCard: visual bar chart per component (citizen volume / urgency / data deficit / population)
- [ ] WeightSliders: MP drags to re-weight and sees ranking update live (great demo moment)
- [ ] ThemeDrilldown: click priority -> see raw submissions behind it
- [ ] JustificationText: Gemini 2.5 Pro explanation rendered per priority
- [ ] Twilio WhatsApp Sandbox: wire inbound webhook to /webhook/twilio -> same ingestion pipeline
- [ ] Firebase Realtime Database: push new submissions to dashboard LiveFeed in real-time
- [ ] Low-literacy icon flow: complete and styled (this is 15% of score)

**Week 3 success check**: Demo flow from section 1.2 works start-to-finish. Yes = Week 3 done.

### Week 4 — Polish, Scale, Submission

**Goal: Win-ready**

- [ ] Seed deployed instance with 300-submission dataset (dashboard must look real on demo day)
- [ ] Load test: load_test.py generates 1000+ submissions, run through pipeline, verify BQ handles it
- [ ] Inclusivity audit: test entire citizen flow on mobile device with no keyboard (voice-only path)
- [ ] Record demo video (script from pitch/demo-video-script.md, target 4:30)
- [ ] Build 12-slide pitch deck (structure from section 9 below)
- [ ] Ensure deployed prototype URL is stable and populated
- [ ] Commit history review: squash nothing, let real incremental commits show
- [ ] Rehearse live demo walkthrough 3x timed (2 min hard cap on any one screen)
- [ ] Cost model slide: run BigQuery + Cloud Run cost estimator for 500 submissions/day/constituency

---

## 8. Deployment & Infrastructure

### 8.1 GCP Services to Enable (setup-gcp.sh)

```bash
gcloud services enable \
  speech.googleapis.com \
  translate.googleapis.com \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  run.googleapis.com \
  storage.googleapis.com \
  maps-backend.googleapis.com \
  geocoding-backend.googleapis.com \
  firebase.googleapis.com
```

### 8.2 Cloud Run Deployment

```bash
cd backend
gcloud run deploy constituency-priorities-api \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT=YOUR_PROJECT,BQ_DATASET=constituency_data" \
  --memory 1Gi \
  --min-instances 0 \
  --max-instances 10
```

**Region: asia-south1 (Mumbai)** — lowest latency for Indian users, required for Vertex AI Indic language models.

### 8.3 Firebase Hosting Deploy

```bash
cd frontend && npm run build && firebase deploy --only hosting
```

### 8.4 BigQuery Schema (Key Tables)

```sql
-- One row per citizen submission
CREATE TABLE constituency_data.submissions (
  id STRING NOT NULL,
  created_at TIMESTAMP,
  media_type STRING,           -- 'text' | 'audio' | 'image'
  original_content STRING,     -- raw text or GCS URI
  original_language STRING,    -- BCP-47 code
  translated_text STRING,      -- normalized English
  theme STRING,                -- classified theme label
  urgency FLOAT64,             -- 0.0 - 1.0
  facility_type STRING,
  ward_id STRING,
  lat FLOAT64,
  lng FLOAT64,
  embedding ARRAY<FLOAT64>,    -- 768-dim text-embedding-005
  cluster_id INT64
);

-- One row per discovered cluster
CREATE TABLE constituency_data.themes (
  theme_id STRING NOT NULL,
  label STRING,
  description STRING,
  submission_count INT64,
  mean_urgency FLOAT64,
  ward_ids ARRAY<STRING>,
  last_updated TIMESTAMP
);

-- Computed gap scores per theme+ward
CREATE TABLE constituency_data.priorities (
  priority_id STRING NOT NULL,
  theme_id STRING,
  ward_id STRING,
  gap_score FLOAT64,
  citizen_volume_norm FLOAT64,
  urgency_norm FLOAT64,
  data_deficit_norm FLOAT64,
  population_norm FLOAT64,
  justification STRING,        -- Gemini Pro plain-English explanation
  rank INT64,
  computed_at TIMESTAMP
);
```

---

## 9. Pitch Deck Structure (12 Slides)

| Slide | Title | Key Content |
|---|---|---|
| 1 | **Title + Team** | Product name, hackathon, team names + roles |
| 2 | **The Problem** | Specific: MP's office in [pilot constituency] receiving 200+ monthly grievances with no way to compare proposals against real data |
| 3 | **Who It Serves** | Two personas: (a) MP's PA needs ranked actionable list Monday morning; (b) Low-literacy rural citizen can speak but cannot type |
| 4 | **The Solution** | One clean architecture diagram. "Citizens submit by voice/photo/text. AI clusters and scores. MP gets a ranked, auditable priority list." |
| 5 | **AI/Technical Approach** | Gap Score formula, Gemini roles (Flash for volume, Pro for reasoning), auditable vs decorative AI distinction |
| 6 | **Citizen Flow Screenshots** | Voice submission in Hindi, low-literacy icon mode, confirmation screen |
| 7 | **MP Dashboard Screenshots** | Priority list with Gap Score badges, hotspot map, drill-down, weight sliders |
| 8 | **Inclusivity & Accessibility** | Voice-first, multilingual (Hindi + Telugu + English), low-literacy icon flow, SMS fallback, offline-tolerant PWA |
| 9 | **Deployability in Weeks** | 4 bullets: existing channels, read-only advisory, public data (no MoU needed), cost model ($X/month) |
| 10 | **Scaling Beyond Pilot** | Multi-constituency BQ architecture, shared API, centralized analytics for parliamentary/state oversight |
| 11 | **Roadmap if Piloted** | Month 1: one constituency. Month 3: SMS IVR. Month 6: WhatsApp Business API. Year 1: state-level rollout with NIC partnership |
| 12 | **Thank You + Links** | GitHub repo URL, deployed prototype URL, demo video URL + QR codes |

---

## 10. Demo Video Script (4:30 Target)

| Time | Beat | What to Show |
|---|---|---|
| 0:00-0:30 | **The Problem** | Voiceover: "In [Constituency], the MP's office receives 200+ development requests monthly with no way to compare a school upgrade against real enrollment data." Show: a WhatsApp inbox with unread messages. |
| 0:30-1:00 | **Voice submission in Hindi** | Citizen PWA. Record Hindi voice note. Show: live transcription, translation, classification appearing. |
| 1:00-1:20 | **Photo submission** | Upload photo of broken handpump. Show: Gemini multimodal classification appearing. |
| 1:20-1:40 | **WhatsApp intake** | Send WhatsApp message via Twilio sandbox. Show: new pin appearing on dashboard map in real-time. |
| 1:40-2:30 | **Dashboard: Gap Score reveal** | Zoom into Priority 1 (school overcrowding). GapScoreCard bar chart: "42 submissions + 38% over capacity (UDISE+) + 6.2km to nearest school (Census) = Gap Score 0.87 — HIGH PRIORITY." Show Gemini justification string. |
| 2:30-3:00 | **Live reweighting** | Drag urgency weight slider up. Watch ranking reshuffle. "The MP's office can tune the algorithm — it's not a black box." |
| 3:00-3:30 | **Drill-down** | Click Priority 1. Show 42 actual citizen submissions behind it + public data table + recommended action card. |
| 3:30-4:00 | **Inclusivity** | Switch to low-literacy icon mode. Tap icons for "road broken" -> voice read-back in Telugu. "This works for a farmer who has never typed on a phone." |
| 4:00-4:30 | **Deployability close** | Cost model slide. "Runs on WhatsApp citizens already have. Reads public data. Advises, doesn't replace government systems." Repo + URL + QR code. |

---

## 11. Risk Register — Check Weekly

| Risk | Mitigation |
|---|---|
| WhatsApp Business API approval delays | Use Twilio sandbox. Build web form that visually mimics a chat interface for demo. Label real integration as "designed, partially wired." |
| Clustering becomes a research project | Use embeddings + HDBSCAN. Do NOT train a custom model. If HDBSCAN is flaky on small data, fall back to k-means. |
| Gap Score becomes unauditable | Keep deterministic formula strictly in gap_score.py. LLM strictly in justification.py. No exceptions. |
| Census/UDISE+ data join fails for pilot | Pre-validate data join in BigQuery Studio in Week 1. Fallback: use state-level ratios if ward-level join fails. |
| Gemini costs spike | Flash for all per-submission calls. Pro only for per-priority justification. Set a daily budget alert in GCP billing. |
| Dashboard looks empty on demo day | Seed 300+ realistic submissions in Week 2. Never wipe the deployed BQ dataset. |
| Deploy fails night before | CI/CD auto-deploys on every merge to main from Week 1. Never deploy for the first time the night before. |
| Inclusivity slide is generic | Demo the icon flow ON SCREEN in the video. "Multilingual support" in text alone scores zero — judges need to see it working. |

---

## 12. AGENTS.md — Repo Conventions (Copy Into AGENTS.md)

```markdown
# Repo Agent Conventions — constituency-priorities

## Language and Formatting
- Python: use ruff for formatting and linting. Line length 100. Type annotations on all public functions.
- TypeScript: ESLint + Prettier. All components typed. No `any`.
- All UI strings must go through the i18n system. Never hardcode English strings in JSX.

## Testing
- Every function in scoring/ MUST have unit tests. The Gap Score formula is our core IP.
- Classification tests must include at least 3 non-English test cases.
- Run `pytest backend/tests/` before every PR merge.

## Gemini Prompt Management
- All prompt templates live in backend/app/nlp/prompts.py. No inline prompt strings elsewhere.
- Every prompt must have a version comment: # v1.2 — added urgency extraction 2026-06-XX
- When changing a prompt, bump the version and add a comment explaining why.

## Architecture Rules
- gap_score.py is deterministic. No LLM calls inside it. Ever.
- justification.py calls Gemini Pro. It receives computed numbers, not raw submissions.
- Never call Gemini Pro in a per-submission hot path. Pro is only for per-priority operations.

## Git Conventions
- Branch naming: feature/description, fix/description, data/description
- Commit messages: type(scope): description
  Examples: feat(nlp): add urgency extraction to Flash classifier
            fix(scoring): handle zero-division in normalization
- No squash merges. Judges check commit history. Real incremental commits matter.
- Tag release candidates: v0.x-rc1

## Environment Variables
- Never commit secrets. Use .env.local (gitignored) for local dev.
- All secrets managed via Cloud Run --set-secrets.
- Required vars documented in .env.local.example.
```

---

## 13. Final Pre-Submission Checklist

- [ ] All 4 submission items submitted: code, video, deck, deployed URL
- [ ] Deployed instance is populated with seed data (not empty)
- [ ] Demo video is exactly 3:00-5:00 (penalize for going over)
- [ ] GitHub repo is public (or access granted to judging org account)
- [ ] README has one-command local setup that actually works
- [ ] Every screen in the demo video is understandable in under 5 seconds to a non-technical viewer
- [ ] Inclusivity flow is shown ON SCREEN in the video (not just mentioned in the deck)
- [ ] Gap Score formula is documented in docs/gap-score-formula.md
- [ ] Cost model is in the deck
- [ ] Cloud Run URL and Firebase Hosting URL are stable and accessible
- [ ] Commit history shows real incremental work across the month, not one squashed commit
