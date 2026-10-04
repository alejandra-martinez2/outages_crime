# Outages Crime

Are Dark Streets Associated with Increased Crime in Chicago?

For our project, we will be analyzing police incident reports and 311 streetlight outage data from the City of Chicago to explore the relationship between streetlight outages and crime rates. Therefore, we will be developing an interactive dashboard with visualizations that highlight the outage locations, crime patterns, and the different income levels, and how the streetlight outages may be associated with crime



## Team Members

| Name | GitHubID | Role / Focus |
| --- | --- | --- |
| Seth Prisament| seprisament | API structure + Creating crime endpoint |
| Anugrha Tamang| atamang3-star |  Data Visualization + Analysis |
| Alejandra Martinez| alejandra-martinez2 | Creating light + Income endpoint|
| Simran Zaveri| simran587  | Data Visualization + Analysis |
| Micayla Fong| mdfong35 | Data-Processing and Integration |


## Problem Statement
This project examines the relationship between crime and street-light outages in Chicago by combining reported crime incidents with 311 street-light outage reports. We hypothesize that areas with more street-light outages have higher subsequent crime rates. To account for differences in underlying economic conditions, we include per capita income when comparing areas, allowing us to assess the association between street-light outages and crime. We will develop a dashboard that maps street-light outages and crime rates by community area and month. Understanding how crime relates to street-light outages could help public officials identify areas and periods when additional public-safety resources may be needed.


---

## Data Sources and Integration Goal

### Sources

| # | Source & Link | Method | What it contains | Update frequency | Access requirements |
|---|---|---|---|---|---|
| 1 | [311 Street Light Outages](https://data.cityofchicago.org/resource/v6vf-nfxy.json) | API | One row per street light outage report: created_date, status, latitude, longitude, and location. (Jan 1, 2011 – present) | Daily | SOCRATA_APP_TOKEN |
| 2 | [Crime Incidents](https://data.cityofchicago.org/resource/ijzp-q8t2.json) | API | Police incident reports: id, date, primary_type, description, community area, latitude, longitude, location (2001 – present) | Daily | Socrata SODA App Token |
| 3 | [Income Levels](https://data.cityofchicago.org/api/views/kn9c-c2s2/rows.csv?accessType=DOWNLOAD) | File | Census Socioeconomic factors: Community Area Number, Community Area Name, Per Capita Income. | Updated as new data becomes available | None |


### Integration Goal

The Chicago crime dataset provides individual crime records, the 311 Street Light Outages dataset provides reported light outages, and the socioeconomic dataset provides per capita income. All three sources have a community area code, which identifies a geographic area in Chicago. We will aggregate the crime and outage data by community area and month, then merge them with the income data by community area. Taken together, these sources let us calculate crime and light-outage rates for each community area and month, and the area's income level. This will let us visualize whether neighborhoods with more outages tend to see more crime, and whether that relationship holds after accounting for income levels.

---

## Setup Instructions (Locally)

### Prerequisites
- Python 3.11+
- A GCP service account key with access to outages-crime/BUCKET/DATASET
- Any source API keys listed in the table below
- Socrata app token to get a higher rate limit
### 1. Clone the repository
```bash
git clone https://github.com/alejandra-martinez2/outages_crime.git
cd outages_crime.git
```

### 2. Configure environment variables
Copy the template file and fill in your own values:

```bash
cp .env_template.env
```


| Variable | Description | Example |
| --- | --- | --- |
| `GCP_PROJECT_ID` | Google Cloud Platform project ID | `outages-crime` |
| `GCP_SERVICE_ACCOUNT_KEY` | Absolute path to your service account JSON key | `/path/to/your/service-account-key.json` |
| `GCP_BUCKET_NAME` | Google Cloud Storage bucket name | `dsai692-group-project` |
| `SOCRATA_APP_TOKEN` | Optional app token for the Chicago data portal, used for higher rate limits (e.g., like the Crime Incidents endpoint) | `your-socrata-app-token-here` |



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

---
## Repository Structure
```
├── fastapi
    └── extract_save_data.py
    └── user_definition.py
├── .env_template
├── .gitignore
├──  README.md
├── requirements.txt
```














