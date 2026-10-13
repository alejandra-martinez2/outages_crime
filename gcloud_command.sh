#!/usr/bin/env bash
# =====================================================================
# Run it from this directory:
#   bash gcloud_command.sh
# =====================================================================
set -euo pipefail
# =====================================================================
# CONFIGURATION
# =====================================================================
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/config.sh"

gcloud config set project "$PROJECT_ID"
gcloud config set run/region "$REGION"

# =====================================================================
#1- put the service account key in Secret Manager.
# =====================================================================
gcloud services enable secretmanager.googleapis.com

# create secrets if it does not exist.
if ! gcloud secrets describe "$GCP_KEY_SECRET" >/dev/null 2>&1; then
  gcloud secrets create "$GCP_KEY_SECRET" --replication-policy=automatic
fi

# Add a new version of secret.
gcloud secrets versions add "$GCP_KEY_SECRET" --data-file="$LOCAL_KEY_FILE"

# Cloud Run source deploys run as the service account.
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" \
  --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding "$GCP_KEY_SECRET" \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role=roles/secretmanager.secretAccessor

# =====================================================================
#2- deploy the FastAPI service.
#=====================================================================
gcloud run deploy "$API_SERVICE" \
  --source ./fastapi \
  --region "$REGION" \
  --port="$API_PORT" \
  --allow-unauthenticated \
  --env-vars-file="$ENV_FILE" \
  --set-secrets="$SECRET_MOUNT_PATH=$GCP_KEY_SECRET:latest"\
  --memory 2Gi\
  --cpu 2\
  --timeout 3600

gcloud run services update "$API_SERVICE" \
  --region "$REGION" \
  --update-env-vars=GCP_SERVICE_ACCOUNT_KEY="$SECRET_MOUNT_PATH"

# =====================================================================
#3- read back the API server's public URL.
#=====================================================================
API_SERVER_URL=$(gcloud run services describe "$API_SERVICE" \
  --region "$REGION" --format="value(urls[0])")
# Older gcloud releases don't expose 'urls'; fall back to the alias.
if [ -z "$API_SERVER_URL" ]; then
  API_SERVER_URL=$(gcloud run services describe "$API_SERVICE" \
    --region "$REGION" --format="value(status.url)")
fi
# Without this check an empty URL silently propagates into the webapp's
# API_SERVICE_URL and the scheduler's --uri, which would cause errors.
if [ -z "$API_SERVER_URL" ]; then
  echo "ERROR: could not resolve the URL for Cloud Run service" \
       "'$API_SERVICE' in $REGION." >&2
  exit 1
fi
echo "$API_SERVICE deployed at $API_SERVER_URL"

# =====================================================================
#4- deploy the Streamlit service, pointed at the API server.
# =====================================================================
gcloud run deploy "$WEBAPP_SERVICE" \
  --source ./streamlit \
  --region "$REGION" \
  --port="$WEBAPP_PORT" \
  --allow-unauthenticated \
  --env-vars-file="$ENV_FILE" \
  --set-secrets="$SECRET_MOUNT_PATH=$GCP_KEY_SECRET:latest" \
  --timeout 3600

gcloud run services update "$WEBAPP_SERVICE" \
  --region "$REGION" \
  --update-env-vars=GCP_SERVICE_ACCOUNT_KEY="$SECRET_MOUNT_PATH",API_SERVICE_URL="$API_SERVER_URL"

WEBAPP_URL=$(gcloud run services describe "$WEBAPP_SERVICE" \
  --region "$REGION" --format="value(urls[0])")
echo "$WEBAPP_SERVICE deployed at $WEBAPP_URL"

# =====================================================================
#5- schedule the daily search.
#=====================================================================
# create or update based on whether the job already exists.
if gcloud scheduler jobs describe "$SCHEDULER_JOB_CRIME" \
     --location="$REGION" >/dev/null 2>&1; then
  SCHEDULER_ACTION=update
  HEADER_FLAG="--update-headers=Content-Type=application/json"
else
  SCHEDULER_ACTION=create
  HEADER_FLAG="--headers=Content-Type=application/json"
fi

gcloud scheduler jobs "$SCHEDULER_ACTION" http "$SCHEDULER_JOB_CRIME" \
  --location="$REGION" \
  --schedule="$SCHEDULE_CRIME" \
  --uri="$API_SERVER_URL$SEARCH_PATH_CRIME" \
  --http-method=POST \
  "$HEADER_FLAG" \
  --message-body="$MESSAGE_BODY_CRIME"\
  --attempt-deadline=1800s

if gcloud scheduler jobs describe "$SCHEDULER_JOB_LIGHT" \
     --location="$REGION" >/dev/null 2>&1; then
  SCHEDULER_ACTION=update
  HEADER_FLAG="--update-headers=Content-Type=application/json"
else
  SCHEDULER_ACTION=create
  HEADER_FLAG="--headers=Content-Type=application/json"
fi

gcloud scheduler jobs "$SCHEDULER_ACTION" http "$SCHEDULER_JOB_LIGHT" \
  --location="$REGION" \
  --schedule="$SCHEDULE_LIGHT" \
  --uri="$API_SERVER_URL$SEARCH_PATH_LIGHT" \
  --http-method=POST \
  "$HEADER_FLAG" \
  --message-body="$MESSAGE_BODY_LIGHT"\
  --attempt-deadline=1800s

echo
echo "Done."
echo "  API:       $API_SERVER_URL"
echo "  Dashboard: $WEBAPP_URL"
echo "  Scheduler: $SCHEDULER_JOB_CRIME ($SCHEDULE_CRIME)"
echo "  Scheduler: $SCHEDULER_JOB_LIGHT ($SCHEDULE_LIGHT)"