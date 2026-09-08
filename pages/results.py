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
from datetime import datetime, time
from pathlib import Path

import streamlit as st  # KEEP
from dotenv import load_dotenv  # KEEP

from photo_planner.charts import (
    CHART_HEIGHT,
    city_scores_heatmap,
    photography_score_chart,
    rain_probability_chart,
    temperature_chart,
)
from photo_planner.client import OpenWeatherClient
from photo_planner.errors import WeatherError
from photo_planner.scoring import (
    best_shooting_window,
    score_forecast,
)
from photo_planner.validation import ISRAEL_CITIES

load_dotenv()  # KEEP

BURGUNDY = "#7B3C3C"
IVORY = "#F0F0E4"

LOGO_PATH = Path(__file__).resolve().parents[1] / "assets" / "logo.png"

st.set_page_config(  # KEEP
    page_title="Results — Shoot Window",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    f"""
    <style>
      [data-testid="stSidebar"] {{ display: none; }}
      [data-testid="stSidebarCollapsedControl"] {{ display: none; }}
      header[data-testid="stHeader"] {{ display: none; }}
      #MainMenu {{ visibility: hidden; }}
      footer {{ visibility: hidden; }}
      html, body, [data-testid="stAppViewContainer"] {{
        background-color: {IVORY} !important;
      }}
      .block-container {{
        padding-top: 0.7rem !important;
        padding-bottom: 0.8rem !important;
        padding-left: 1.4rem !important;
        padding-right: 1.4rem !important;
        max-width: 1320px;
      }}
      h1 {{
        color: {BURGUNDY} !important;
        font-size: 1.55rem !important;
        margin: 0.1rem 0 0.15rem 0 !important;
        line-height: 1.15 !important;
      }}
      h3 {{
        color: {BURGUNDY} !important;
        font-size: 0.95rem !important;
        margin: 0.15rem 0 !important;
      }}
      .sw-brand {{
        display: flex; align-items: center; gap: 0.45rem;
        color: {BURGUNDY}; font-weight: 700; font-size: 1.05rem;
      }}
      .sw-tagline {{
        color: {BURGUNDY}; opacity: 0.75; font-size: 0.85rem;
        text-align: right; padding-top: 0.2rem;
      }}
      .sw-caption {{
        color: {BURGUNDY}; opacity: 0.8; font-size: 0.85rem;
        margin: 0 0 0.4rem 0;
      }}
      .sw-card {{
        background: #fff;
        border: 1.5px solid {BURGUNDY};
        border-radius: 12px;
        padding: 0.55rem 0.8rem 0.5rem 0.8rem;
        min-height: 78px;
      }}
      .sw-card-label {{
        color: {BURGUNDY}; font-size: 0.78rem; font-weight: 600;
        margin-bottom: 0.12rem;
      }}
      .sw-card-value {{
        color: {BURGUNDY}; font-size: 1.35rem; font-weight: 700;
        line-height: 1.15;
      }}
      .sw-card-sub {{
        color: {BURGUNDY}; opacity: 0.75; font-size: 0.72rem;
        margin-top: 0.12rem;
      }}
      [data-testid="stHorizontalBlock"] {{
        align-items: stretch !important;
      }}
      div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #ffffff !important;
        border: 1.5px solid {BURGUNDY} !important;
        border-radius: 12px !important;
        padding: 0.55rem 0.7rem 0.4rem 0.7rem !important;
        margin-bottom: 0.55rem;
        height: 100% !important;
        box-sizing: border-box;
      }}
      .sw-chart-title {{
        color: {BURGUNDY};
        font-size: 0.92rem;
        font-weight: 700;
        margin: 0;
        height: 2.4rem;
        line-height: 2.4rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }}
      div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSelectbox"] {{
        margin-bottom: 0 !important;
      }}
      div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSelectbox"] > div {{
        min-height: 2.4rem;
      }}
      [data-testid="stPlotlyChart"] {{
        margin-bottom: 0 !important;
        background: #ffffff !important;
      }}
      [data-testid="stPlotlyChart"] > div {{
        height: {CHART_HEIGHT}px !important;
      }}
      .stButton > button {{
        border: 1.5px solid {BURGUNDY};
        color: {BURGUNDY};
        background: #ffffff;
        border-radius: 8px;
        font-weight: 600;
      }}
      @media (max-width: 900px) {{
        .block-container {{ padding-top: 0.8rem !important; }}
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


def _api_key() -> str | None:
    """Return the OpenWeatherMap API key, or None if missing."""
    try:
        return st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        return os.getenv("OPENWEATHER_API_KEY")


def _format_date_label(iso_date: str) -> str:
    try:
        parsed = datetime.strptime(iso_date, "%Y-%m-%d")
        return f"{parsed.strftime('%b')} {parsed.day}, {parsed.year}"
    except ValueError:
        return iso_date


def _condition_label(score: float) -> str:
    if score >= 80:
        return "Good conditions"
    if score >= 60:
        return "Fair conditions"
    return "Challenging conditions"


def _parse_hhmm(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def _booked_within_window(booked: str, start: str, end: str) -> bool:
    """True if booked time falls in [start, end), handling midnight wrap."""
    b = _parse_hhmm(booked)
    s = _parse_hhmm(start)
    e = _parse_hhmm(end)
    if s <= e:
        return s <= b < e
    return b >= s or b < e


def _chart_header(title: str) -> None:
    """Fixed-height title so cards in a row stay aligned."""
    st.markdown(f'<p class="sw-chart-title">{title}</p>', unsafe_allow_html=True)


def _show_chart(fig) -> None:
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )


@st.cache_data(ttl=600, show_spinner=False)
def _score_city(
    city: str,
    shoot_type: str,
    shoot_date: str,
    api_key: str,
) -> dict[str, float] | None:
    """Return {HH:MM: score} for one city, or None if the forecast failed."""
    try:
        client = OpenWeatherClient(api_key=api_key)
        forecast = client.get_forecast(city)
        scored = score_forecast(forecast, shoot_type, shoot_date)
        return {
            hour.time_text.split(" ")[1][:5]: round(score, 1)
            for hour, score in scored
        }
    except WeatherError:
        return None


def _build_city_matrix(
    cities: list[str],
    shoot_type: str,
    shoot_date: str,
    api_key: str,
    hour_columns: list[str],
) -> dict[str, dict[str, float | None]]:
    matrix: dict[str, dict[str, float | None]] = {}
    for city in cities:
        scored = _score_city(city, shoot_type, shoot_date, api_key)
        if scored is None:
            matrix[city] = {h: None for h in hour_columns}
        else:
            matrix[city] = {h: scored.get(h) for h in hour_columns}
    return matrix


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

# ------------------------------------------------------------
# Brand header
# ------------------------------------------------------------
brand_left, brand_right = st.columns([2.2, 1.2])
with brand_left:
    if LOGO_PATH.exists():
        c_logo, c_name = st.columns([0.18, 1.2])
        with c_logo:
            st.image(str(LOGO_PATH), width=42)
        with c_name:
            st.markdown(
                '<div class="sw-brand">Shoot Window</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="sw-brand">Shoot Window</div>',
            unsafe_allow_html=True,
        )
with brand_right:
    st.markdown(
        '<div class="sw-tagline">Outdoor photography, planned.</div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------
# Title + edit
# ------------------------------------------------------------
title_left, title_right = st.columns([3.4, 1])
with title_left:
    st.title("Your shoot plan")
    date_label = _format_date_label(shoot_date)
    st.markdown(
        f'<p class="sw-caption">{city}  ·  {date_label}  ·  '
        f'{shoot_type.capitalize()}</p>',
        unsafe_allow_html=True,
    )
with title_right:
    if st.button("✎ Edit session", use_container_width=True):
        st.session_state["plan_ready"] = False
        # Keep city / date / time / type so the form can restore them.
        st.switch_page("app.py")

# ------------------------------------------------------------
# Fetch selected-city forecast + score
# ------------------------------------------------------------
api_key = _api_key()
if not api_key:
    st.error("Missing API key. Copy .env.example to .env.")
    st.stop()

try:
    with st.spinner("Loading forecast…"):
        client = OpenWeatherClient(api_key=api_key)
        forecast = client.get_forecast(city)
        scored = score_forecast(forecast, shoot_type, shoot_date)
        window = best_shooting_window(scored)
except WeatherError as err:
    st.error(str(err))
    if st.button("← Edit session"):
        st.session_state["plan_ready"] = False
        st.switch_page("app.py")
    st.stop()

if not scored or window is None:
    st.warning("No forecast hours found for that date. Try another day.")
    if st.button("← Edit session"):
        st.session_state["plan_ready"] = False
        st.switch_page("app.py")
    st.stop()

start, end, best_score = window
within_window = _booked_within_window(preferred_time, start, end)
booked_sub = (
    "Within the recommended window."
    if within_window
    else "Outside the recommended window."
)

# ------------------------------------------------------------
# Summary cards
# ------------------------------------------------------------
col_score, col_window, col_booked = st.columns(3)
with col_score:
    st.markdown(
        f"""
        <div class="sw-card">
          <div class="sw-card-label">Photography Score</div>
          <div class="sw-card-value">{best_score} / 100</div>
          <div class="sw-card-sub">{_condition_label(best_score)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_window:
    st.markdown(
        f"""
        <div class="sw-card">
          <div class="sw-card-label">Best shooting window</div>
          <div class="sw-card-value">{start} – {end}</div>
          <div class="sw-card-sub">Highest-rated window for your shoot.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_booked:
    st.markdown(
        f"""
        <div class="sw-card">
          <div class="sw-card-label">Your booked time</div>
          <div class="sw-card-value">{preferred_time}</div>
          <div class="sw-card-sub">{booked_sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------
# Charts 2×2 — same card size, same header row, same plot height
# ------------------------------------------------------------
hour_columns = [hour.time_text.split(" ")[1][:5] for hour, _ in scored]

filter_options = ["All cities", *ISRAEL_CITIES]
city_filter = st.session_state.get("heatmap_city_filter", "All cities")

top_left, top_right = st.columns(2, gap="medium", vertical_alignment="top")
with top_left:
    with st.container(border=True):
        head_l, head_r = st.columns([1.7, 1.1], vertical_alignment="center")
        with head_l:
            _chart_header("Photography Score throughout the day")
        with head_r:
            st.markdown('<p class="sw-chart-title">&nbsp;</p>', unsafe_allow_html=True)
        _show_chart(
            photography_score_chart(
                scored,
                window_start=start,
                window_end=end,
                booked_time=preferred_time,
            )
        )

with top_right:
    with st.container(border=True):
        head_l, head_r = st.columns([1.7, 1.1], vertical_alignment="center")
        with head_l:
            _chart_header("City scores by hour")
        with head_r:
            city_filter = st.selectbox(
                "Cities",
                filter_options,
                index=filter_options.index(city_filter)
                if city_filter in filter_options
                else 0,
                label_visibility="collapsed",
                key="heatmap_city_filter",
            )
        if city_filter == "All cities":
            visible = [city] + [c for c in ISRAEL_CITIES if c != city]
        else:
            visible = [city_filter]

        with st.spinner("Comparing cities…"):
            matrix = _build_city_matrix(
                visible,
                shoot_type,
                shoot_date,
                api_key,
                hour_columns,
            )
        _show_chart(
            city_scores_heatmap(
                matrix,
                selected_city=city,
                hour_columns=hour_columns,
            )
        )

bot_left, bot_right = st.columns(2, gap="medium", vertical_alignment="top")
with bot_left:
    with st.container(border=True):
        head_l, head_r = st.columns([1.7, 1.1], vertical_alignment="center")
        with head_l:
            _chart_header("Temperature")
        with head_r:
            st.markdown('<p class="sw-chart-title">&nbsp;</p>', unsafe_allow_html=True)
        _show_chart(temperature_chart(scored))
with bot_right:
    with st.container(border=True):
        head_l, head_r = st.columns([1.7, 1.1], vertical_alignment="center")
        with head_l:
            _chart_header("Rain probability")
        with head_r:
            st.markdown('<p class="sw-chart-title">&nbsp;</p>', unsafe_allow_html=True)
        _show_chart(rain_probability_chart(scored))
