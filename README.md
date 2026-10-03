# Outages Crime
For our project we will be working with the police incident reports in the streetlight 311 data in the city of Chicago. Where we will be building an interactive dashboard and visualization of the outage, the locations, outages, and the different income levels.


## Team Members

| Name | GitHubID | Role / Focus |
| --- | --- | --- |
| Seth Prisament| seprisament | API structure + Creating time endpoint |
| Anugrha Tamang | atamang3-star |  Data Visualization + Analysis |
| Alejandra | alejandra-martinez2 | Creating light + Income endpoint|
| Simran Zaveri | simran587  | Data Visualization + Analysis |
| Micalaya Fong| mdfong35 | Feature engineering |


## Problem Statement
For our project we will assess crime frequency by relating police reports with the 311 streetlight outage reports happening in Chicago. We aim to test if areas with currently unresolved power outages have a positive relationship with crime incidents and income, particularly in the nighttime. We will compare the frequency of crime during current outages to times of repair, or periods following when the outage is resolved and also evaluate how socioeconomic factors interact with both infrastructure neglect and public safety. We then plan to build a dashboard to map outage locations, repair times, and crime frequency with filters to sort by crime type and time of day, and socioeconomic indicators.This project could prove beneficial to the city works department who can use this information to prioritize certain repair requests and allocate resources in order to reduce crime based on historical patterns.

---

## Data Sources and Integration Goal

### Sources
| # | Source & Link | Method | What it contains | Update frequency | Access requirements |
| --- | --- | --- | --- | --- | --- |
| 1 | [311 Street Light Outages](https://data.cityofchicago.org/api/v3/views/zuxi-7xem/export.csv)| File |One row per street light outage report: creation date, status, lat/long, location. [January 1, 2011 to present] | Daily | [none / free key in ‘CHICAGO_APP_TOKEN`] |
| 2 | [Crime Incidents](https://data.cityofchicago.org/resource/ijzp-q8t2.json) | File | Police incident reports: creation_date,last_modified_date, status,sr_type. [2001 to present] | Daily| none |




| 3 | [Income Levels](https://data.cityofchicago.org/api/views/kn9c-c2s2/rows.csv?accessType=DOWNLOAD) | API | Socioeconomic factors: Community Area Number, Community Area Name, Per Capita Income| Static | none |

Note: If we need a key, say which environment variable holds it and make sure that variable also appears in the .env_template

### Integration Goal
What does each source contribute?
311 Street Lights Outages contribute to when and where the streetlight outage was reported, such as the creation date and the latitude and longitude. In addition, it also has the status of when it was repaired, such that this will show each event when the outage happened.
Chicago Crimes Incidents contributed to when and where each one of the crimes happened, such as the street_name. Also, the type of crime is given by sr_type. This is the output of the street light outages. In addition, the income source is vital to understanding the socioeconomic status and factors. It contributes to the community area name and community area number. 

 What can the combination reveal?
When answering these questions that we have set for our project, neither of the two sources can answer the question alone. Therefore, we would need to combine all three sources to truly answer the question, such as whether there is a high crime rate due to the outage happening at night rather than during the day, or to understand the rate of crimes happening before the outage and after the repair. Also, combining income helps to determine the factors to understand how socioeconomic factors affect the public safety measure. Therefore, combining all three helps to reveal how the light outages in Chicago are impacting the community, which will help to resolve the problem. 


How can we combine them?
We can combine them by understanding how to use all three sources to match the different crimes to the outages. Therefore, we will be building a unified dataset that includes all three sources- the light outages, crimes, and income datasets to create a dataset that includes the columns of year, month, community_code,  income, total_outages, and total_crimes to determine the main effect on the outages and resolve these issues by creating visualizations that would be helpful to analyze certain patterns and find outputs that will help to reduce crime rates when outages do occur.

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


Collect and save the income data:
```python
requests.post("http://localhost:8000/call_and_save/income", json=income)
```

Make sure it writes the data in the bucket.
---
## Repository Structure
```

├── fastapi
    └── extract_save_data.py
    └──  user_definition.py
├── .env_template
├── .gitignore
├──  README.md
├── requirements.txt
```






