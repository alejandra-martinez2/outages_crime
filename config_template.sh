# SOURCED by gcloud_command.sh to set environment variables
# This is a TEMPLATE. Each user must fill blanks.
# And rename to config.sh
# ---------------------------------------------------------------------
# User-Specific Variables
# ---------------------------------------------------------------------
#1: GCP_PROJECT_ID.
PROJECT_ID= #Example: "outages-crime"

#2: the region to deploy into
REGION= #Example: "us-west1"

#3: absolute path to your .env file. 
ENV_FILE= #Example: "/Users/x/outages_crime/.env"

#4: absolute path to your service account JSON key on your laptop
LOCAL_KEY_FILE= #Example: "/Users/x/.ssh/outages-crime-key.json"

#5: the ports the two Dockerfiles EXPOSE. 
API_PORT= #Suggested: "8000"
WEBAPP_PORT= #Suggested: "8501"

# ---------------------------------------------------------------------
# Project Constants
# ---------------------------------------------------------------------
# Secret Manager holds the key, and we need to mount it.
GCP_KEY_SECRET=outages-crime-gcp-key
SECRET_MOUNT_PATH=/run/secrets/gcp_key

# Cloud Run service names.
API_SERVICE=outages-crime-api-server
WEBAPP_SERVICE=outages-crime-webapp

# 2 Cloud Scheduler jobs: name, schedule, and the request body.
SCHEDULER_JOB_CRIME=crime-refresh-trigger
SCHEDULE_CRIME="0 0 * * *"
#request body for crime endpoint
MESSAGE_BODY_CRIME= #Example: '{
#     "number_records": 100000
# }'

SCHEDULER_JOB_LIGHT=light-refresh-trigger
SCHEDULE_LIGHT="0 0 * * *"
#request body for light endpoint
MESSAGE_BODY_LIGHT= #Example: '{
#     "number_records": 100000
# }'

# The 2 API endpoint to refresh
SEARCH_PATH_CRIME=/call_and_save/crime
SEARCH_PATH_LIGHT=/call_and_save/light

# =====================================================================
# Validation 
# =====================================================================
for _outages_crime_var in PROJECT_ID REGION ENV_FILE LOCAL_KEY_FILE API_PORT \
                WEBAPP_PORT; do
  if [ -z "${!_outages_crime_var}" ]; then
    echo "ERROR: $_outages_crime_var is empty - fill in blanks in config.sh" \
         "before running this script." >&2
    exit 1
  fi
done
unset _outages_crime_var

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: ENV_FILE '$ENV_FILE' does not exist." >&2
  exit 1
fi
if [ ! -f "$LOCAL_KEY_FILE" ]; then
  echo "ERROR: LOCAL_KEY_FILE '$LOCAL_KEY_FILE' does not exist." >&2
  exit 1
fi
