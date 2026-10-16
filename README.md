# Outages Crime
Are dark streets associated with increased crime in Chicago? We examine this question using crime and light-outage data from Chicago’s open data portal. Understanding whether crime is associated with street-light outages could help public officials allocate repair and public safety resources more effectively.

**Live web app:** [https://outages-crime-webapp-1051461652831.us-west1.run.app/#outages-crimes](https://outages-crime-webapp-1051461652831.us-west1.run.app/#outages-crimes)
**API (private):** [https://outages-crime-api-server-1051461652831.us-west1.run.app](https://outages-crime-api-server-1051461652831.us-west1.run.app)

---

## Team Members

| Name | GitHubID | Role / Focus |
| --- | --- | --- |
| Seth Prisament| seprisament | Data Acquisition / Fastapi |
| Anugrha Tamang| atamang3-star |  Data Visualization / Streamlit |
| Alejandra Martinez| alejandra-martinez2 | Data Acquisition / Fastapi|
| Simran Zaveri| simran587  | Data Visualization / Streamlit |
| Micayla Fong| mdfong35 | Data Processing and Integration |

---

## Problem Statement
We examine the relationship between crime and street-light outages in Chicago by combining reported crime incidents with street-light outage reports. Specifically, we compare street-light outage and crime rates across Chicago’s community areas (our geographic unit of analysis) to investigate whether areas with higher outage rates also experience higher crime rates. Understanding this relationship could help public officials better allocate street-light repair and public safety resources.

To make more meaningful comparisons between community areas, we account for two factors:

Population: Community areas vary in population size, making raw counts of crime or outages difficult to compare. To address this, we normalize crime and outage counts by population to calculate rates per capita.
Socioeconomic differences:  Lower-income areas may experience both higher crime rates and more street-light outages. To explore this potential relationship, we include per capita income for each community area.


### Visualizations

We present our findings through two types of visualizations:

1. Bubble Scatter Plot

This plot shows the relationship between street-light outage and crime rates directly, while containing income as a third variable.

2. Maps

We create three maps of Chicago, each shading community areas according to a different variable:
- Street-light outage rate per 1,000 residents 
- Crime rate per 1,000 residents
- Per capita income

We also allow the user to filter each visualization by income group to better compare the association between light-outages and crime rates. 


## Data Sources and Integration Goal

### Sources
| # | Source & Link | Method | What it contains | Update frequency | Env var for the key |
| --- | --- | --- | --- | --- | --- |
| 1 | [Crimes - 2001 to Present](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2) | API | One row per crime, filtered to user-specified number of records (defaults to 50,000), sorted by date of crime descending. Used fields: date, community area, latitude (used to filter out rows with missing location) | Daily | `SOCRATA_APP_TOKEN` |
| 2 | [311 Service Requests](https://data.cityofchicago.org/Service-Requests/311-Service-Requests/v6vf-nfxy) | API | One row per service request, filtered service request type (`sr_type`) to 'Street Light Out Complaint' and 'Alley Light Out Complaint', further filtered to user-specified number of records (defaults to 50,000), sorted created_date descending. Used fields: created_date, community area, duplicate (to filter out duplicate of the same request) | Multiple times per day | `SOCRATA_APP_TOKEN` |
| 3 | [Census Data - Selected socioeconomic indicators in Chicago, 2008–2012](https://data.cityofchicago.org/Health-Human-Services/Census-Data-Selected-socioeconomic-indicators-in-C/kn9c-c2s2) | File | One row per community area. Used fields: community area, per capita income | Static | none |
| 4 | [ACS 5-Year Data by Community Area](https://data.cityofchicago.org/Community-Economic-Development/ACS-5-Year-Data-by-Community-Area/t68z-cikk) | File | One row per community area. Used fields: total population per community area. Used as the denominator to convert crime and outage counts into per-capita rates. | Annual | none |
| 5 | [Boundaries - Community Areas](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas/igwz-8jzy) | API | One feature per community area. Fields are the community area's boundary and the join field is area_numbe. Provides the shapes for streamlit maps. | Static | none |

**Note on the SOCRATA_APP_TOKEN**
The crime and streetlight endpoints call the Chicago Data Portal's Socrata API,
which rate-limits anonymous requests. A free app token raises that limit.

1. Create an account at https://data.cityofchicago.org.
2. Go to your profile → Developer Settings.
3. Click Create New App Token.
4. Copy the generated **App Token** (not the Secret Token) into your `.env`


### Integration Goal
The Chicago crime dataset provides individual crime records, the 311 Service Requests dataset provides reported streetlight outage complaints, the socioeconomic dataset provides per capita income, and the population dataset provides population counts for each community area.
We first filter the crime and outage data to their overlapping date range to ensure we are comparing the same time period. We then aggregate both datasets by community area to calculate the total number of crimes and outage complaints in each area. These counts are merged with income and population data using community area codes. Population data is used to normalize crime and outage counts into rates per 1,000 residents, while per capita income is used to divide community areas into three income categories (Low, Medium, High).
Finally, we use Chicago community area boundary data to create geographic visualizations. Together, these datasets allow us to examine whether community areas with higher streetlight outage complaint rates also experience higher crime rates, and whether this relationship differs across income levels.


---

## Repository Structure

```

outages_crime/
├── fastapi/                    
│   ├── Dockerfile               # Builds the API container image
│   ├── data_processing.py       # Reads GCS files, aggregates to community area, computes rates
│   ├── extract_save_data.py     # FastAPI: endpoints that pull sources and save to GCS
│   ├── requirements.txt         
│   └── user_definition.py       # Loads env vars (project, bucket, token) and file prefixes
├── streamlit/                   
│   ├── Dockerfile               # Builds the web-app container image
│   ├── requirements.txt      
│   ├── user_definition.py       # Loads env vars needed by the web app
│   └── webapp.py                # Streamlit dashboard: maps + scatter plot
├── gcloud_command.sh            # Deploy script: build/push images, deploy to Cloud Run, scheduler
├── .env_template                # Template for .env 
├── config_template.sh           # Template for config.sh 
└── README.md                    # Project overview, setup, and usage



```

---

## API Endpoints

| Method | Path | Purpose | Example body |
| --- | --- | --- | --- |
| `POST` | `/call_and_save/crime` | Fetch most recent crime incidents from the Socrata API and write to GCS as a dated JSON file in **crime**/{YYYY-MM-DD}.json | `{"number_records": 50000}` |
| `POST` | `/call_and_save/light` | Fetch most recent street-light outage requests and write to GCS as a dated JSON file in **light**/{YYYY-MM-DD}.json | `{"number_records": 50000}` |
| `POST` | `/call_and_save/income` | Download the socioeconomic-indicators CSV and write to GCS as **income**/income.json | _(no body)_ |
| `POST` | `/call_and_save/population` | Download the ACS population CSV and write to GCS as **population**/population.json | _(no body)_ |
| `POST` | `/call_and_save/geographic` | Fetch Chicago community-area boundaries from the Socrata API and write to GCS as **geographic**/geographic.json | _(no body)_ |
| `GET` | `/data` | Process the newest crime, outage, income, population, and geographic data from GCS and return it for the web app | _(no body)_ |

Access the auto-doc here: https://outages-crime-api-server-1051461652831.us-west1.run.app/docs 


---

## Setup — Local

### Prerequisites

- Docker Desktop, `gcloud` CLI
- A GCP service account key with read/write on your bucket

### 1. Clone and configure

```bash
git clone https://github.com/alejandra-martinez2/outages_crime.git
cd outages_crime
cp .env_template .env

```
After copying .env_template to .env, fill in `.env` with your `GCP_PROJECT_ID`, `GCP_BUCKET_NAME`, and `SOCRATA_APP_TOKEN`. Leave `GCP_SERVICE_ACCOUNT_KEY=/tmp/gcp-key.json` as-is since that's the path your key is mounted to inside the container  See table below.

| Variable | Description | Example |
| --- | --- | --- |
| `GCP_PROJECT_ID` | GCP project | `outages-crime` |
| `GCP_BUCKET_NAME` | Bucket for raw data | `dsai692-group-project` |
| `GCP_SERVICE_ACCOUNT_KEY` | In-container key path | /tmp/gcp-key.json |
| `SOCRATA_APP_TOKEN` | Key for SOCRATA API. See note on app token creation instructions below  | `abc123...` |
| `API_SERVICE_URL` | Where the web app reaches the API | http://host.docker.internal:8000|

`.env` and your `*.json` key are in `.gitignore`. **Never commit them.**

### 2. Run both services

From the `outages_crime` folder:

**API**
```bash
cd fastapi
docker build -t api .
docker run -p 8000:8000 -v PATH_TO_GCP_KEY:/tmp/gcp-key.json --env-file ../.env api
```
Replace PATH_TO_GCP_KEY with the absolute path to your service-account key on your computer.

**Web app** (in a second terminal)
```bash
cd streamlit
docker build -t streamlit .
docker run --env-file ../.env -p 8501:8501 streamlit
```

- API docs: http://localhost:8000/docs
- Web app: http://localhost:8501


### 3. Trigger a collection run

With the API running, call each endpoint to populate the bucket:
```bash
curl -X POST http://localhost:8000/call_and_save/crime      -H "Content-Type: application/json" -d '{"number_records": 50000}'
curl -X POST http://localhost:8000/call_and_save/light      -H "Content-Type: application/json" -d '{"number_records": 50000}'
curl -X POST http://localhost:8000/call_and_save/income
curl -X POST http://localhost:8000/call_and_save/population
curl -X POST http://localhost:8000/call_and_save/geographic
```

Then confirm the object landed in your bucket.

---

## Setup — Deploy to GCP
Deployment uses Cloud Run and Cloud Scheduler; first configure, then run the deploy script.

####  config.sh

```bash
cp config_template.sh config.sh   
```
After copying `config_template.sh` to `config.sh`, fill in the values below. 

| Variable | Description | Example |
| --- | --- | --- |
| `PROJECT_ID` | GCP project ID | `outages-crime` |
| `REGION` | GCP region to deploy into | `us-west1` |
| `ENV_FILE` | Absolute path to your `.env` file | `/Users/x/outages_crime/.env` |
| `LOCAL_KEY_FILE` | Absolute path to your service account JSON key on your machine | `/Users/x/.ssh/outages-crime-key.json` |
| `API_PORT` | Port the API Dockerfile EXPOSEs | `8000` |
| `WEBAPP_PORT` | Port Streamlit Dockerfile EXPOSEs | `8501` |
| `MESSAGE_BODY_CRIME` | JSON request body for the scheduled crime job (sets the record limit) | `'{ "number_records": 100000 }'` |
| `MESSAGE_BODY_LIGHT` | JSON request body for the scheduled light job (sets the record limit) | `'{ "number_records": 100000 }'` |

From the `outages_crime` folder, sign in first:
```bash
gcloud auth login
```

On a new GCP project, required APIs may not be enabled. If this is the case, first run:
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com cloudscheduler.googleapis.com secretmanager.googleapis.com
```

To run the whole GCP deployment script:
```bash
bash gcloud_command.sh
```
This runs every step in order, each time:
1. Uploads the service account key to Secret Manager (as a new version) and grants the Cloud Run service account access to it
2. Builds and deploys the FastAPI service to Cloud Run
3. Builds and deploys the Streamlit web app, pointed at the API's URL
4. Creates or updates the two Cloud Scheduler jobs (crime and light)
5. Prints the API URL, dashboard URL, and scheduler job names

Re-run the same command to redeploy everything after code changes.
Or one piece at a time while iterating:
```bash
source config.sh
```

Redeploy only the API (keeps its existing env vars, secret, and resources):
```bash
gcloud run deploy "$API_SERVICE" --source ./fastapi --region "$REGION" --project "$PROJECT_ID"
```

Redeploy only the web app:
```bash
gcloud run deploy "$WEBAPP_SERVICE" --source ./streamlit --region "$REGION" --project "$PROJECT_ID"
```

Change a job's schedule or request body (after editing `config.sh`):
```bash
gcloud scheduler jobs update http "$SCHEDULER_JOB_LIGHT" --location "$REGION" --schedule "$SCHEDULE_LIGHT" --message-body "$MESSAGE_BODY_LIGHT"
```

Run a scheduler job now instead of waiting for its schedule:
```bash
gcloud scheduler jobs run "$SCHEDULER_JOB_CRIME" --location "$REGION"
gcloud scheduler jobs run "$SCHEDULER_JOB_LIGHT" --location "$REGION"
```
