import json
import re

from google.oauth2 import service_account
from google.cloud import storage
import streamlit as st
import pandas as pd

from user_definition import (bucket_name, file_name_prefix, project_id,
                             service_account_file_path)


def retrieve_data_from_gcs(service_account_key: str,
                           project_id: str,
                           bucket_name: str,
                           file_name_prefix: str
                           ) -> pd.DataFrame:

    credentials = service_account.Credentials.from_service_account_file(
            service_account_key)
    client = storage.Client(project=project_id,
                                credentials=credentials)
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()

    frames = []
