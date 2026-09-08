# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# This is the entry point of the application — the file you
# start with `streamlit run app.py`.
#
# Think of it as the coordinator. It should:
#   1. Ask the photographer for location, date, time, shoot type
#   2. Call the weather client (written in another file)
#   3. Call scoring.py (the product)
#   4. Show the score, the best window, and charts
#
# WHY WE KEEP THIS SEPARATE:
# Parsing JSON belongs in photo_planner/models.py.
# Talking to the API belongs in photo_planner/client.py.
# Thinking like a photographer belongs in photo_planner/scoring.py.
# This file only handles the interface (what the user sees).
#
# Person B owns this file. See docs/PAIR.md.
# ============================================================

from __future__ import annotations

import os
from datetime import date, time, timedelta

# WHY THIS EXISTS:
# streamlit is the library that turns this Python file into a web page.
import streamlit as st  # KEEP

# WHY THIS EXISTS:
# load_dotenv reads the .env file so OPENWEATHER_API_KEY is available locally.
from dotenv import load_dotenv  # KEEP

# WHY THIS EXISTS:
# OpenWeatherClient is written in photo_planner/client.py.
# This import lets app.py call get_forecast() without talking to the API itself.
# Uncomment this line when you are ready to connect the UI to the client.
from photo_planner.client import OpenWeatherClient

# WHY THIS EXISTS:
# WeatherError is the parent of all weather errors (invalid city, 404, bad key).
# Catching WeatherError lets you show a friendly message with st.error(...).
from photo_planner.errors import WeatherError

# WHY THIS EXISTS:
# score_forecast and best_shooting_window are written in scoring.py.
# That file is the product — this page only displays what they return.
from photo_planner.scoring import score_forecast, best_shooting_window

# WHY THIS EXISTS:
# Chart functions are written in charts.py.
from photo_planner.charts import (
    photography_score_chart,
    temperature_chart,
    clouds_and_rain_chart,
)

# WHY THIS EXISTS:
# SHOOT_TYPES is written in photo_planner/validation.py.
# Using the same list here keeps the dropdown in sync with scoring.
# from photo_planner.validation import SHOOT_TYPES

load_dotenv()  # KEEP — loads .env on your computer (Streamlit Cloud uses secrets instead)

st.set_page_config(  # KEEP — browser tab title and layout
    page_title="Shoot Window — photography planner",
    layout="wide",
)

st.title("Shoot Window")  # KEEP
st.caption(  # KEEP
    "A decision tool for outdoor photographers in Israel. "
    "Weather is the input. The Photography Score is the product."
)

# KEEP — common outdoor-shoot locations. Person B may add more later.
ISRAEL_CITIES = [  # KEEP
    "Tel Aviv",
    "Jerusalem",
    "Haifa",
    "Herzliya",
    "Eilat",
    "Netanya",
    "Caesarea",
    "Akko",
]


def _api_key() -> str | None:
    """
    Return the OpenWeatherMap API key, or None if it is missing.

    WHY THIS EXISTS:
    Locally the key lives in a .env file.
    On Streamlit Cloud the key lives in App settings → Secrets.
    This helper checks Cloud first, then .env.

    An API key is a secret password the weather service gives you.
    Never print it on the page or commit it to GitHub.
    """
    # KEEP — this helper is project infrastructure, not the assignment logic
    try:
        return st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        return os.getenv("OPENWEATHER_API_KEY")


# ------------------------------------------------------------
# STUDENT TASK 1: Photographer input (layout already started)
# ------------------------------------------------------------
# KEEP: the widgets so you can focus on calling scoring and displaying results.

st.subheader("Plan a session")  # KEEP

col_city, col_date, col_time, col_type = st.columns(4)  # KEEP

with col_city:
    city = st.selectbox("Location", ISRAEL_CITIES, index=0)  # KEEP

with col_date:
    # KEEP — the free forecast covers about 5 days from today
    today = date.today()
    shoot_date = st.date_input(
        "Date",
        value=today + timedelta(days=1),
        min_value=today,
        max_value=today + timedelta(days=4),
    )

with col_time:
    preferred_time = st.time_input("Preferred time", value=time(17, 0))  # KEEP

with col_type:
    shoot_type = st.selectbox(  # KEEP
        "Photography type",
        ("portrait", "sunset", "landscape"),
        index=0,
    )

plan = st.button("Plan shoot", type="primary")  # KEEP


if plan:
    # ------------------------------------------------------------
    # STUDENT TASK 2: Fetch forecast + compute Photography Score
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
            shoot_date.isoformat(),
        )
        window = best_shooting_window(scored)
        # window is (start_time, end_time, best_score) or None

    except WeatherError as err:
        st.error(str(err))
        st.stop()

    # ------------------------------------------------------------
    # STUDENT TASK 3: Show the decision (not raw weather dumps)
    # ------------------------------------------------------------
    if window is None:
        st.warning("No forecast hours found for that date. Try another day.")
        st.stop()

    start, end, best_score = window

    st.caption(f"{city}  ·  {shoot_date}  ·  {shoot_type}")

    col_score, col_window, col_booked = st.columns(3)
    with col_score:
        st.metric("Photography Score", f"{best_score} / 100")
    with col_window:
        st.metric("Best shooting window", f"{start} – {end}")
    with col_booked:
        st.metric("Your booked time", preferred_time.strftime("%H:%M"))

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

else:
    st.write(  # KEEP
        "Choose a location in Israel, a date, a time, and a photography type, "
        "then press **Plan shoot**."
    )

    st.markdown(  # KEEP — product reminder, not assignment logic
        """
**What this app is**

Weather Data → Analysis → Photography Score → Recommendation → Decision.

The forecast is the input. The output is whether (and when) you should shoot.
"""
    )
