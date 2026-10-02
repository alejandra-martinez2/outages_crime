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
For our project we will assess crime frequency by relating police reports with the 311 streetlight outage reports happening in Chicago. We aim to test if areas with currently unresolved power outages have a positive relationship with crime incidents, particularly in the nighttime. We will compare the frequency of crime during current outages to times of repair, or periods following when the outage is resolved. We then plan to build a dashboard to map outage locations, repair times, and crime frequency with filters to sort by crime type and time of day. This project could prove beneficial to the city works department who can use this information to prioritize certain repair requests and allocate resources in order to reduce crime based on historical patterns.


---

## Data Sources and Integration Goal

### Sources
| # | Source & Link | Method | What it contains | Update frequency | Access requirements |
| --- | --- | --- | --- | --- | --- |
| 1 | [311 Street Light Outages](https://data.cityofchicago.org/api/v3/views/zuxi-7xem/export.csv)| API | One row per street light outage reports: Creation Date, status lat/long,location. [January 1, 2011 to present] | daily | [none / free key in ‘CHICAGO_APP_TOKEN`] |
| 2 | [Crime Incidents](https://data.cityofchicago.org/resource/ijzp-q8t2.json) | File | Police incident reports: creation_date,last_modified_date, status,sr_type. [2001 to present] | daily | none |


Note: If we need a key, say which environment variable holds it and make sure that variable also appears in the .env_template

### Integration Goal
What does each source contribute?
311 Street Lights Outages contribute to when and where the streetlight outage was reported such as the Creation date, and the latitude and longitude. In addition, it also has the status of when it was repaired such that this will show each event when the outage happened.
Chicago Crimes Incidents contributed to when and where each one of the crimes happened such as the street_name. Also what type of crime it was given by sr_type. Such is the output of the street light outages.
 What can the combination reveal?
When answering these questions that we have set for our project, not only one of the two sources can answer the question alone. Therefore we would need to combine both of the sources to truly answer the question such as if there is a high crime rate due to the outage happening in nighttime rather than daytime or even understanding the rate of crimes happening before the outage and after the repair.
How can we combine them?
We can combine them by understanding how to use both sources to match the different crimes happening to the outage. By doing this each of the crimes are clearly in an assigned position if it ranges to be in a certain distance within the latitude and longitude.
Also we would need to define the different outage windows happening and occurring between the creation_date to the completion_date. In order to do this we take the calculation of finding the timestamp of the time spent repairing. This would be helpful in order to evaluate each of window timestamps to what was pulled to the data

---

## Setup Instructions (Locally)

### Prerequisites
- Python 3.11+
- A GCP service account key with access to outages-crime/BUCKET/DATASET
- Any source API keys listed in the table below

### 1. Clone the repository
```bash
git clone https://github.com/alejandra-martinez2/outages_crime.git
cd outages_crime.git
```

### 2. Configure environment variables
Copy the example file and fill in your own values:

```bash
cp .env_template .env
```

| Variable | Description | Example |
| --- | --- | --- |
| `GCP_SERVICE_ACCOUNT_KEY` | Absolute path to your service account JSON | `/Users/you/.ssh/key.json` |
| ``CHICAGO_APP_TOKEN`` | Optional app token for the Chicago data portal (higher rate limits) | `abc123...` |
| `API_SERVICE_URL` | Where the web app reaches the API | `http://api-server:8000` |

### 4. How to call your endpoint
To start the API server,
```python
fastapi run extract_save_data.py
```
Collect and save the crime data:
```python
requests.post("http://localhost:8000/call_and_save/crime", json=crime)
```

Collect and save the street light data:
```python
requests.post("http://localhost:8000/call_and_save/light", json=light)
```

Make sure it writes the data in the bucket.
---
## Repository Structure
```

├── fastapi
├── .env_template
└── .gitignore
└── README.md
└── requirements.txt
```


