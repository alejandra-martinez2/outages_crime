import os

from dotenv import load_dotenv

load_dotenv()
project_id = os.getenv('GCP_PROJECT_ID')
bucket_name = os.getenv('GCP_BUCKET_NAME')
service_account_file_path = os.getenv('GCP_SERVICE_ACCOUNT_KEY')
socrata_app_token = os.getenv("SOCRATA_APP_TOKEN", "")
file_name_prefix_crime = "crime"
file_name_prefix_light = "light"