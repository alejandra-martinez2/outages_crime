import statsmodels
import pandas as pd
import streamlit as st
import plotly.express as px

from dotenv import load_dotenv
import os


load_dotenv()
api_server_url = os.getenv("API_SERVICE_URL")

@st.cache_data(ttl=3600)
def load_data():
    response = requests.get(f"{api_server_url}/data", timeout=300)
    if not responseok:
        st.error(f"API returned {response.status_code}")
        st.code(response.text[:1000])
        st.stop()
    return response.json()

order_of_income = ["Low", "Medium", "High"]
colors_of_income = {"Low": "#93c5fd", "Medium": "#3b82f6", "High": "#1d4ed8"}


def bubble_chart(df, x_col, y_col, x_label, y_label):
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size="per_capita_income",
        color="income_category",
        category_orders={"income_category": order_of_income},
        color_discrete_map=colors_of_income,
        hover_name="community_name",
        hover_data={"per_capita_income": ":$,.0f", x_col: ":,.1f", y_col: ":,.1f"},
        labels={
            x_col: x_label,
            y_col: y_label,
            "per_capita_income": "Per capita income",
            "income_category": "Income group",
        },
        trendline="ols" if show_trend else None,  # AI Prompt: for a bubble plot, give me the right code structure to  add a trendline, the package I am using is plotly.express
        trendline_scope="overall",                # Model used: Claude Sonnet 5.5 
        trendline_color_override="red",
        opacity=0.6,
        size_max=28,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Bigger bubble size = Higher community area income")



if __name__ == "__main__":
    st.title("Streetlight Outages vs. Crime Rates by Community Area")
    payload = load_data()
   
    df = pd.DataFrame(payload["data"])
    st.caption(f"Data from {payload['start_date']} to {payload['end_date']}")


    # AI Prompt:  I want a checkbox on the sidebar that says show trendline in the Streamlit app
    with st.sidebar:
        st.header("Options")
        show_trend = st.checkbox("Show trendline", value=False)


    users_choice = st.radio("Income group", ["All"] + order_of_income, horizontal=True)   # AI Prompt: Help me create a radio button that allows  allows the users to select from one button
    if users_choice == "All": # Filtering the data by what rhe user selects               # Model used: Claude Sonnet 5.5 
        filtered = df
    else:
        filtered = df[df["income_category"] == users_choice]                                   


    st.write(f"Showing {len(filtered)} of {len(df)} community areas") # Shows the number of community areas listed depending on what the user selects
    if filtered is None:
        st.write("No community areas in this income group.") 
    else:
        bubble_chart(
            filtered,
            "outage_rate",
            "crime_rate",
            "Streetlight outages per 1,000 residents", 
            "Crime incidents per 1,000 residents",
        )
