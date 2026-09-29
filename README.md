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
 We combine 311 streetlight outage reports with police incident reports for Chicago city, and Census block group data for demographic controls. We test whether street segments with open/unresolved outages see elevated nighttime crime incidents during the outage window compared to the same segments before the outage or after repair, and whether this effect concentrates in specific crime types versus daytime-driven crimes. A dashboard maps outage locations, repair duration, and nearby crime density, filterable by crime type and time of day. This would be useful to a city public works department prioritizing repair queues, or a police department making the case for infrastructure investment in high-crime areas.


---

## Data Sources and Integration Goal
- Follow the direction given in the 1st assignment

### Sources
| # | Source & Link | Method | What it contains | Update frequency | Access requirements |
| --- | --- | --- | --- | --- | --- |
| 1 | [311 street light outages](https://data.cityofchicago.org/resource/v6vf-nfxy.json) | API | creation_date, completion_date, status, lat/long | daily / monthly / static | free key, 100 req/day | 
| 2 | [Crime Incidents](https://www.kaggle.com/datasets/chicago/chicago-crime) | File | ... | ... | none |

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
