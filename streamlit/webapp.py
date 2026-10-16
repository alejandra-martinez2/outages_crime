import copy

import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests
import streamlit as st

from user_definition import api_server_url

order_of_income = ["Low", "Medium", "High"]
colors_of_income = {"Low": "#93c5fd", "Medium": "#3b82f6", "High": "#1d4ed8"}

# (title, column, legend label, low rgb, high rgb, use income filter)
MAPS = [
    ("Income", "per_capita_income", "Per capita income ($)",
     (229, 245, 224), (0, 109, 44), False),
    ("Light outages", "outage_rate", "Light outages per 1000 residents ({period})",
     (255, 247, 188), (217, 95, 14), True),
    ("Crime", "crime_rate", "Crimes per 1000 residents ({period})",
     (254, 229, 217), (165, 15, 21), True),
]


@st.cache_data(ttl=3600, show_spinner="Loading data")
def load_data():
    response = requests.get(f"{api_server_url}/data", timeout=300)
    response.raise_for_status()
    return response.json()


# ---------- Maps ----------

def summarize(df):
    return (df.groupby(["community_area", "community_name"], as_index=False)
              .agg(crime_rate=("crime_rate", "mean"),
                   outage_rate=("outage_rate", "mean"),
                   per_capita_income=("per_capita_income", "first"),
                   income_category=("income_category", "first")))


def blend(low, high, t):
    return [int(low[i] + t * (high[i] - low[i])) for i in range(3)] + [200]


def build_map(data, geo, col, low, high, title):
    geo = copy.deepcopy(geo)
    by_area = data.set_index("community_area")
    name_to_area = {n.upper().strip(): a
                    for a, n in zip(data["community_area"], data["community_name"])}
    lo, hi = float(by_area[col].min()), float(by_area[col].max())

    unmatched = 0
    for f in geo["features"]:
        p = f["properties"]
        p["name"] = p["community"].title()

        key = int(p["area_numbe"])
        if key not in by_area.index:
            key = name_to_area.get(p["community"].upper().strip())

        if key is None or pd.isna(by_area.at[key, col]):
            p["value"] = "N/A"
            p["fill"] = [200, 200, 200, 120]
            unmatched += 1
            continue

        v = float(by_area.at[key, col])
        t = (v - lo) / ((hi - lo) or 1)
        p["value"] = f"{v:,.2f}"
        p["fill"] = blend(low, high, t)

    layer = pdk.Layer(
        "GeoJsonLayer", data=geo,
        get_fill_color="properties.fill",
        get_line_color=[255, 255, 255],
        line_width_min_pixels=1,
        stroked=True, filled=True, pickable=True,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(latitude=41.84, longitude=-87.68, zoom=8.8),
        map_style="light",
        tooltip={
            "html": "<b>{name}</b><br/>" + title + ": {value}",
            "style": {
                "backgroundColor": "rgb(30,30,30,0.9)",
                "color": "white",
                "fontSize": "11px",
                "padding": "4px 8px",
                "maxWidth": "150px",
                "borderRadius": "4px",
            },
        },
    )

    return deck, lo, hi, unmatched


# Used AI model Sonnet 5.5 for function legend to get the HTML and CSS properties
#prompt: give me html and css for reamlit function named legend to show a thin 
# gradiend descent bar from low to high rgb color and low and high values at 2 decimal points. 
# use st.markdown with css html
def legend(label, low, high, lo, hi):
    grad = f"linear-gradient(to right, rgb{tuple(low)}, rgb{tuple(high)})"
    st.markdown(
        f"<div style='max-width:420px'>"
        f"<div style='font-size:0.85rem;margin-bottom:4px'>{label}</div>"
        f"<div style='height:14px;border-radius:4px;background:{grad}'></div>"
        f"<div style='display:flex;justify-content:space-between;font-size:0.8rem'>"
        f"<span>{lo:,.2f}</span><span>{hi:,.2f}</span></div></div>",
        unsafe_allow_html=True,
    )


def maps_tab(df, geo, start_date, end_date):
    if not geo.get("features"):
        st.error("geographic data has no 'features'.")
        return

    summary = summarize(df)
    selected = st.multiselect("Income category (crime and light maps)",
                              order_of_income, default=order_of_income)

    cols = st.columns(3)
    for c, (title, col, label, low, high, use_filter) in zip(cols, MAPS):
        with c:
            st.subheader(title)
            label = label.format(period=f"{start_date} to {end_date}")
            map_data = (summary[summary["income_category"].isin(selected)]
                        if use_filter else summary)
            if map_data.empty:
                st.info("No areas match the selected income categories.")
                continue

            deck, lo, hi, unmatched = build_map(map_data, geo, col, low, high, title)
            legend(label, low, high, lo, hi)
            st.pydeck_chart(deck, height=500)

            if use_filter:
                st.caption(f"Showing {len(map_data)} of {len(summary)} areas (others in gray)")
            if unmatched:
                st.caption(f"{unmatched} areas had no matching data")


# ---------- Bubble chart ----------

def bubble_chart(df, x_col, y_col, x_label, y_label, show_trend):
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
        trendline="ols" if show_trend else None,  # AI Prompt: for a bubble plot, give me the right code structure to  add a trendline. The package I am using is plotly.express
        trendline_scope="overall",                # Model used: Claude Sonnet 5.5
        trendline_color_override="red",
        opacity=0.6,
        size_max=28,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Bigger bubble size = Higher community area income")


def bubble_tab(df):
    st.subheader("Streetlight Outages vs. Crime Rates by Community Area")

    # AI Prompt:  I want a checkbox on the sidebar that says show trendline in the Streamlit app
    show_trend = st.checkbox("Show trendline", value=False)

    users_choice = st.radio("Income group", ["All"] + order_of_income, horizontal=True)   # AI Prompt: Help me create a radio button that allows  the users to select from one button
    if users_choice == "All": # Filtering the data by what rhe user selects               # Model used: Claude Sonnet 5.5
        filtered = df
    else:
        filtered = df[df["income_category"] == users_choice]

    st.write(f"Showing {len(filtered)} of {len(df)} community areas") # Shows the number of community areas listed depending on what the user selects
    if filtered.empty:
        st.write("No community areas in this income group.")
    else:
        bubble_chart(
            filtered,
            "outage_rate",
            "crime_rate",
            "Streetlight outages per 1,000 residents",
            "Crime incidents per 1,000 residents",
            show_trend,
        )


if __name__ == '__main__':
    st.set_page_config(page_title="Outages and Crime", layout="wide")
    st.title("Chicago Streetlight Outages and Crime")

    try:
        payload = load_data()
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

    df = pd.DataFrame(payload["data"])
    geo = payload["geographic"]
    start_date, end_date = payload["start_date"], payload["end_date"]

    if df.empty:
        st.error("API returned no rows")
        st.stop()

    st.caption(f"Data from {start_date} to {end_date}")

    maps, bubble, table = st.tabs(["Maps", "Outages vs. Crime", "Data"])
    with maps:
        maps_tab(df, geo, start_date, end_date)
    with bubble:
        bubble_tab(df)
    with table:
        st.dataframe(df)
