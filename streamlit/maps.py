import copy
import os
import sys
import pandas as pd
import pydeck as pdk
import streamlit as st
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", ".env"))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "fastapi")))
for mod in ("user_definition", "data_processing"):
   sys.modules.pop(mod, None)
from data_processing import get_data # type: ignore

income_cal_col = "income_category"

MAPS = [
   ("Income", "per_capita_income", "Per capita income ($)",
    (229, 245, 224), (0,109, 44), False),
    ("Light outages", "outage_rate", "Light outages per 1000 residents ({period})",
     (255, 247, 188), (217,95,14), True),
     ("Crime", "crime_rate", "Crimes per 1000 residents ({period})",
      (254, 229, 217), (165, 15, 21), True),
]

@st.cache_data(ttl=3600, show_spinner="Loading csv data")
def load_data():
   df, geo, start_date, end_date = get_data()
   return df, geo, str(start_date), str(end_date)

def summarize (df):
   return (df.groupby(["community_area", "community_name"], as_index=False)).agg(crime_rate=("crime_rate", "mean"),
             outage_rate=("outage_rate", "mean"),
             per_capita_income=("per_capita_income", "first"),
             income_category=("income_category", "first"))

def blend(low,high,t):
    return [int(low[i]+t*(high[i]-low[i])) for i in range (3)] +[200]


def build_map(data,geo, col, label, low, high, title):
   geo = copy.deepcopy(geo)
   by_area = data.set_index("community_area")
   name_to_area = {n.upper(). strip(): a
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
        unmatched +=1
        continue

       v = float(by_area.at[key, col])
       t = (v - lo) / ((hi - lo) or 1)
       p["value"] = f"{v:,.2f}"
       p["fill"] = blend(low, high, t)

   layer = pdk.Layer (
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
                    "color" : "white",
                    "fontSize": "11px",
                    "padding": "4px 8px",
                    "maxWidth": "150px",
                    "borderRadius": "4px",
            },
      },
   )

   return deck, lo, hi , unmatched

# Used AI model Sonnet 5.5 for function legend to get the HTML and CSS properties
#prompt: give me html and css for reamlit function named legend to show a thin gradiend descent bar from low to high rgb color and low and high values at 2 decimal points. use st.markdown with css html
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

@st.cache_data(ttl=3600, show_spinner="Loading csv data")
def load():
    df, start_date, end_date = get_data()
    return df, start_date, end_date

# App

st.set_page_config(page_title="Outages and Crime Maps", layout = "wide")
st.title("Chicago Outages Crime")

try:
    df, geo, start_date, end_date = load_data()
except Exception as e:
   st.error("Failed to load data: {e}")
   st.stop()

if df.empty:
   st.error("get_data() returned no rows")
   st.stop()

if not geo.get("features"):
    st.error("geographic.json has no 'features'." )
    st.stop()

nums_cols = df.select_dtypes("number").columns.tolist()

summary = summarize(df)
order = (summary.groupby("income_category")["per_capita_income"]
                 .mean().sort_values().index.tolist())
selected = st.sidebar.multiselect("Income category (crime and light maps)", order, default=order)

cols = st.columns(3)
for c, (title, col, label, low, high, use_filter) in zip (cols, MAPS):
   with c:
      st.subheader(title)
      label = label.format(period = f"{start_date} to {end_date}")
      filtered = use_filter
      map_data= (summary[summary["income_category"].isin(selected)] if filtered else summary)
      if map_data.empty:
         st.info("No areas match the selected income categories.")

      deck, lo, hi, unmatched = build_map(map_data, geo, col, label, low, high, title)
      legend(label, low, high, lo, hi)
      st.pydeck_chart(deck, height = 500)

      if use_filter:
         st.caption(f"Showing {len(map_data)} of {len(summary)} areas (others in gray)")
      if unmatched:
         st.caption (f"{unmatched} areas had no matching data")
