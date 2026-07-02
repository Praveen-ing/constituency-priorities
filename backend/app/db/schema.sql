-- BigQuery DDL for Constituency Priorities Project

-- 1. Submissions Table
-- Stores raw and processed citizen submissions from all channels
CREATE TABLE IF NOT EXISTS `${GCP_PROJECT}.${BQ_DATASET}.submissions` (
  id STRING NOT NULL,
  created_at TIMESTAMP,
  media_type STRING,           -- 'text' | 'audio' | 'image'
  original_content STRING,     -- raw text or GCS URI for media
  original_language STRING,    -- BCP-47 code (e.g., 'hi-IN', 'te-IN')
  translated_text STRING,      -- normalized English text
  theme STRING,                -- classified theme label (e.g., 'education', 'water')
  urgency FLOAT64,             -- 0.0 - 1.0 AI-determined urgency score
  facility_type STRING,        -- extracted entity (e.g., 'primary school', 'borewell')
  ward_id STRING,              -- extracted location ID mapped to Ward
  lat FLOAT64,                 -- geocoded latitude
  lng FLOAT64,                 -- geocoded longitude
  embedding ARRAY<FLOAT64>,    -- 768-dim vertex AI embedding
  cluster_id INT64             -- computed by HDBSCAN clustering job
);

-- 2. Themes Table
-- Stores clustered recurring themes/issues across the constituency
CREATE TABLE IF NOT EXISTS `${GCP_PROJECT}.${BQ_DATASET}.themes` (
  theme_id STRING NOT NULL,
  label STRING,                -- Human readable theme label
  description STRING,          -- AI generated summary of the cluster
  submission_count INT64,      -- total submissions mapped to this theme
  mean_urgency FLOAT64,        -- average urgency score across submissions
  ward_ids ARRAY<STRING>,      -- list of affected wards
  last_updated TIMESTAMP
);

-- 3. Priorities Table
-- The output of the Gap Score computation. 
-- This is what drives the MP Dashboard UI.
CREATE TABLE IF NOT EXISTS `${GCP_PROJECT}.${BQ_DATASET}.priorities` (
  priority_id STRING NOT NULL,
  theme_id STRING,
  theme_label STRING,
  ward_id STRING,
  ward_name STRING,
  gap_score FLOAT64,           -- 0.0 - 1.0 computed final score
  citizen_volume_norm FLOAT64, -- normalized component
  urgency_norm FLOAT64,        -- normalized component
  data_deficit_norm FLOAT64,   -- normalized component (from public datasets)
  population_norm FLOAT64,     -- normalized component (from Census)
  w1 FLOAT64,                  -- applied weight for volume
  w2 FLOAT64,                  -- applied weight for urgency
  w3 FLOAT64,                  -- applied weight for deficit
  w4 FLOAT64,                  -- applied weight for population
  justification STRING,        -- Gemini Pro plain-English explanation
  rank INT64,                  -- computed rank (1 is highest)
  computed_at TIMESTAMP
);

-- 4. Public Dataset: Census Wards (Pilot Data)
-- Used for population normalization and baseline water/sanitation access
CREATE TABLE IF NOT EXISTS `${GCP_PROJECT}.${BQ_DATASET}.census_wards` (
  ward_id STRING NOT NULL,
  ward_name STRING,
  total_population INT64,
  households INT64,
  households_with_water INT64,
  households_with_toilet INT64,
  area_sqkm FLOAT64
);

-- 5. Public Dataset: UDISE+ Schools (Pilot Data)
-- Used for education data deficit normalization
CREATE TABLE IF NOT EXISTS `${GCP_PROJECT}.${BQ_DATASET}.udise_schools` (
  school_id STRING NOT NULL,
  ward_id STRING,
  school_name STRING,
  total_enrollment INT64,
  student_capacity INT64,
  teacher_count INT64
);
