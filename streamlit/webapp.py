import pandas as pd
import requests
import streamlit as st

from user_definition import api_server_url

@st.cache_data(ttl=3600)
def load_data():
    response = requests.get(f"{api_server_url}/data", timeout=300)
    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    st.title("Outages Crimes")
    payload = load_data()
    df = pd.DataFrame(payload["data"])
    geo = payload["geographic"]
    st.caption(f"Data from {payload['start_date']} to {payload['end_date']}")
    st.dataframe(df)