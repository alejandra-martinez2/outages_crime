import json
import datetime
import pandas as pd
import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from google.cloud import storage
from google.oauth2 import service_account
from pydantic import BaseModel

from user_definition import (
    socrata_app_token,
    service_account_file_path,
    project_id,
    bucket_name,
    file_name_prefix_crime,
    file_name_prefix_light
)

app = FastAPI()

CRIME_URL = "https://data.cityofchicago.org/resource/ijzp-q8t2.json"
LIGHT_URL = "https://data.cityofchicago.org/api/v3/views/zuxi-7xem/export.csv"

# user parameter for '/call_and_save/crime' endpoint
class CrimeSearchModel(BaseModel):
    number_records: int

# parameters for calling the Chicago crime API
class CrimeQuery(BaseModel):
    socrata_app_token: str
    number_records: int
    crime_url: str = CRIME_URL
    # fields requested
    select: str = (
        "date, primary_type, description, location_description, "
        "latitude, longitude, block, community_area, ward, beat, arrest"
    )
    where: str = "latitude IS NOT NULL"

# parameters for saving the Chicago crime data to GCS
class GcsStringUpload(BaseModel):
    service_account_key: str
    gcp_project_id: str
    bucket_name: str
    file_name: str
    data: str

def call_light_webfile_download():
    try:
        df = pd.read_csv(LIGHT_URL)
        return df.to_json(orient="records")
    except Exception as e:
        print(f"Error making download request: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": f"Error making download request: {e}"},
        )    


def call_chicago_crime_api(query_params: CrimeQuery):
    """
    Call Chicago crime incidents from the API and return as a list or the API's JSON response.
    On failure, returns a JSONResponse with status_code=500
    """
    headers = {"X-App-Token": query_params.socrata_app_token}
    params = {"$select": query_params.select,
              "$where": query_params.where,
              "$limit": query_params.number_records}
    try:
        return requests.get(query_params.crime_url, headers=headers,
                        params=params, timeout=60).json()
    except Exception as e:
        print(f"Error making API request: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": f"Error making API request: {e}"},
        )


def save_to_gcs(gcs_upload_param: GcsStringUpload):
    """
    Access the bucket with service_account_key, and upload the object
    to the storage. Returns a dict with a status message.
    """
    credentials = service_account.Credentials.\
        from_service_account_file(gcs_upload_param.service_account_key)
    client = storage.Client(project=gcs_upload_param.gcp_project_id,
                            credentials=credentials)
    bucket = client.bucket(gcs_upload_param.bucket_name)
    file = bucket.blob(gcs_upload_param.file_name)
    file.upload_from_string(gcs_upload_param.data)
    return {"message": f"file {gcs_upload_param.file_name} has been uploaded "
            f"to {gcs_upload_param.bucket_name} successfully."}


@app.post("/call_and_save/crime")
def call_crime(crime_input: CrimeSearchModel):
    """
    Combine call_chicago_crime_api() and save_to_gcs() to call crime
    incidents and save the results as a JSON blob in GCS.
    """
    crime_query_param = CrimeQuery(
        socrata_app_token=socrata_app_token,
        number_records=crime_input.number_records,
    )
    crime_response = call_chicago_crime_api(crime_query_param)
    if isinstance(crime_response, JSONResponse):
        return crime_response
    gcs_data = GcsStringUpload(
        service_account_key=service_account_file_path,
        gcp_project_id=project_id,
        bucket_name=bucket_name,
        file_name=f"{file_name_prefix_crime}/{datetime.date.today()}.json",
        data=json.dumps(crime_response),
    )
    return save_to_gcs(gcs_data)

@app.post("/call_and_save/light")
def call_light():
    light_response = call_light_webfile_download()
    if isinstance(light_response, JSONResponse):
        return light_response
    gcs_data = GcsStringUpload(
        service_account_key=service_account_file_path,
        gcp_project_id=project_id,
        bucket_name=bucket_name,
        file_name=f"{file_name_prefix_light}/{datetime.date.today()}.json",
        data=json.dumps(light_response),
    )    
    return save_to_gcs(gcs_data)
