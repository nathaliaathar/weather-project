# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# This is the RESULTS page — the second screen of the app.
#
# It reads the photographer's choices from st.session_state
# (saved on the home page), then:
#   1. Calls the weather client
#   2. Calls scoring.py (Photography Score + best window)
#   3. Shows metrics, recommendation, and charts
#
# WHY THIS FILE LIVES IN pages/:
# Streamlit turns every .py file inside pages/ into another
# page of the app. Home = app.py. Results = this file.
#
# Person B owns the UI. Scoring/API stay in photo_planner/.
# ============================================================

from __future__ import annotations

import os

import streamlit as st  # KEEP
from dotenv import load_dotenv  # KEEP

# WHY THESE IMPORTS:
# Same building blocks as before — only the *page* changed.
from photo_planner.client import OpenWeatherClient
from photo_planner.errors import WeatherError
from photo_planner.scoring import score_forecast, best_shooting_window
from photo_planner.charts import (
    photography_score_chart,
    temperature_chart,
    clouds_and_rain_chart,
)

load_dotenv()  # KEEP

st.set_page_config(  # KEEP
    page_title="Results — Shoot Window",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(  # KEEP — match home: hide sidebar chrome
    """
    <style>
      [data-testid="stSidebar"] { display: none; }
      [data-testid="stSidebarCollapsedControl"] { display: none; }
      .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _api_key() -> str | None:
    """Return the OpenWeatherMap API key, or None if missing."""
    # KEEP — Cloud secrets first, then local .env
    try:
        return st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        return os.getenv("OPENWEATHER_API_KEY")


# ------------------------------------------------------------
# Guard: user must come from the home form first
# ------------------------------------------------------------
if not st.session_state.get("plan_ready"):
    st.warning("Start on the home page — choose a session, then press Plan shoot.")
    if st.button("← Back to plan"):
        st.switch_page("app.py")
    st.stop()

city = st.session_state["city"]
shoot_date = st.session_state["shoot_date"]  # ISO string YYYY-MM-DD
preferred_time = st.session_state["preferred_time"]  # "HH:MM"
shoot_type = st.session_state["shoot_type"]

# Header + back navigation
top_left, top_right = st.columns([3, 1])
with top_left:
    st.title("Your shoot plan")
    st.caption(f"{city}  ·  {shoot_date}  ·  {shoot_type}")
with top_right:
    if st.button("← Plan another session"):
        st.session_state["plan_ready"] = False
        st.switch_page("app.py")

# ------------------------------------------------------------
# Fetch forecast + compute Photography Score
# ------------------------------------------------------------
api_key = _api_key()
if not api_key:
    st.error("Missing API key. Copy .env.example to .env.")
    st.stop()

try:
    client = OpenWeatherClient(api_key=api_key)
    forecast = client.get_forecast(city)

    scored = score_forecast(
        forecast,
        shoot_type,
        shoot_date,  # already ISO from session_state
    )
    window = best_shooting_window(scored)

except WeatherError as err:
    st.error(str(err))
    st.stop()

if window is None:
    st.warning("No forecast hours found for that date. Try another day.")
    st.stop()

start, end, best_score = window

# ------------------------------------------------------------
# Decision UI (metrics + recommendation + charts)
# TODO (STUDENT): OPTIONAL polish — shorter charts, tabs, expanders
#   so this page also needs less scrolling.
# ------------------------------------------------------------
col_score, col_window, col_booked = st.columns(3)
with col_score:
    st.metric("Photography Score", f"{best_score} / 100")
with col_window:
    st.metric("Best shooting window", f"{start} – {end}")
with col_booked:
    st.metric("Your booked time", preferred_time)

st.success(
    f"Conditions look good for a {shoot_type} session in {city}. "
    f"Best shooting window: {start}–{end} (score {best_score})."
)

st.subheader("Photography Score during the day")
st.plotly_chart(photography_score_chart(scored), use_container_width=True)

col_temp, col_sky = st.columns(2)
with col_temp:
    st.plotly_chart(temperature_chart(scored), use_container_width=True)
with col_sky:
    st.plotly_chart(clouds_and_rain_chart(scored), use_container_width=True)
