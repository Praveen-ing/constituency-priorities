#!/bin/bash
set -e

# setup-gcp.sh
# Initializes GCP project for Constituency Priorities Project

PROJECT_ID="constituency-priorities"
REGION="asia-south1"
BQ_DATASET="constituency_data"
GCS_BUCKET="${PROJECT_ID}-uploads"

echo "Setting active project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

echo "Enabling necessary GCP APIs..."
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

echo "Creating BigQuery dataset..."
bq mk --location=${REGION} -d \
  --description "Constituency Priorities Dataset" \
  ${PROJECT_ID}:${BQ_DATASET} || echo "Dataset already exists"

echo "Creating GCS upload bucket..."
gcloud storage buckets create gs://${GCS_BUCKET} --location=${REGION} || echo "Bucket already exists"

echo "Applying BigQuery schema..."
# Replace placeholders with actual project/dataset and apply DDL
sed "s/\${GCP_PROJECT}/${PROJECT_ID}/g" ../backend/app/db/schema.sql | \
sed "s/\${BQ_DATASET}/${BQ_DATASET}/g" > temp_schema.sql

bq query --use_legacy_sql=false < temp_schema.sql
rm temp_schema.sql

echo "✅ GCP Setup Complete!"
echo "Next steps:"
echo "1. Get your API keys for Gemini and Maps"
echo "2. Add them to your .env.local files"
