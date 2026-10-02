# Outages Crime
For our project we will be working with the police incident reports in the city of Chicago where we will showcase a map to outage the locations, crime type and day. 


## Team Members

| Name | GitHubID | Role / Focus |
| --- | --- | --- |
| Seth Prisament| seprisament | e.g. Streamlit app - map |
| Anugrha Tamang | atamang3-star | e.g. scraping for SF news data  + scheduled collection |
| Alejandra | alejandra-martinez2 | e.g. API call for SF crimedata + data cleaning |
| Simran Zaveri | simran587  | e.g. Streamlit app - interactive bargraph|
| Micalaya Fong| mdfong35 | e.g. API call weather data +  scheduled collection|
---

## Problem Statement
For our project, we will be combining the 311 streetlight outage reports that are related to the police reports happening in the city of Chicago. We will test whether areas with open, unresolved outages have a higher number of nighttime crime incidents during the outage window than in the periods before the outage or after the repair. Therefore, we will build a dashboard that maps outage locations, repair times, and crime frequency, and filters by crime type and time of day. This project would be helpful to the city public works department who are in need of prioritizing the repair requests and helping to create decisions to create more infrastructure where high-crimes rely.


---

## Data Sources and Integration Goal

### Sources
| # | Source & Link | Method | What it contains | Update frequency | Access requirements |
| --- | --- | --- | --- | --- | --- |
| 1 | [311 Street Light Outages]( "https://data.cityofchicago.org/api/v3/views/zuxi-7xem/export.csv")| API | One row per street light outage reports: creation_date, completion_date, status, lat/long. January 1, 2011 to present. | [daily] | [none / free key in ``CHICAGO_APP_TOKEN`] |
| 2 | [Crime Incidents]("https://data.cityofchicago.org/resource/ijzp-q8t2.json") | [File/API] | Police incident reports: [date, category, lat/long, neighborhood]. [Time range, SF] | [daily] | [none] |


Note: If we need a key, say which environment variable holds it and make sure that variable also appears in the .env_template

### Integration Goal
- Follow the direction given in the 1st assignment

---

## Setup Instructions (Locally)

### Prerequisites
- Python 3.11+
- A GCP service account key with access to PROJECT/BUCKET/DATASET
- Any source API keys listed in the table below

### 1. Clone the repository
```bash
git clone https://github.com/ORG/REPO.git
cd REPO
```

### 2. Configure environment variables
Copy the example file and fill in your own values:

```bash
cp .env_template .env
```

| Variable | Description | Example |
| --- | --- | --- |
| `GCP_SERVICE_ACCOUNT_KEY` | Absolute path to your service account JSON | `/Users/you/.ssh/key.json` |
| `SOURCE_API_KEY` | Key for SOURCE NAME (free tier) | `abc123...` |
| `API_SERVICE_URL` | Where the web app reaches the API | `http://api-server:8000` |

### 4. How to call your endpoint
To start the API server,
```python
fastapi run mycode.py
```

```python
requests.post("http://localhost:8000/something", json=something)
```
Make sure it writes the data in the bucket.

---
## Repository Structure
```
.
├── your_code.py
├── .env_template
└── README.md
```
