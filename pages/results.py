# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# RESULTS page: score, best window, booked time, and charts.
# Left column explains HOW the score was built for the type
# the photographer chose. Right column is the plan + charts.
# ============================================================

from __future__ import annotations

import os
from datetime import datetime, time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

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
    FACTOR_LABELS,
    FACTOR_NAMES,
    SHOOT_WEIGHTS,
    STATUS_NOT_RECOMMENDED,
    STATUS_UNAVAILABLE,
    best_shooting_window,
    condition_label,
    score_booked_interval,
    score_forecast,
)
from photo_planner.validation import ISRAEL_CITIES, SHOOT_TYPES

load_dotenv()

BURGUNDY = "#7B3C3C"
IVORY = "#F3EFE6"
LOGO_PATH = Path(__file__).resolve().parents[1] / "assets" / "logo.png"

# Why this type uses these weights — only the chosen type is shown.
TYPE_WHY = {
    "portrait": (
        "Light is the priority (40%), then rain and wind to keep your "
        "subject comfortable and the session manageable."
    ),
    "event": (
        "Rain matters most (35%) because it can disrupt a schedule "
        "that may be difficult to change."
    ),
    "sunset": (
        "The sun’s position and sky conditions have the greatest "
        "influence (light 55%)."
    ),
    "landscape": (
        "Lighting and visibility help bring out the scene, while rain "
        "and wind affect shooting conditions."
    ),
}

TYPE_WEIGHT_TEXT = {
    "portrait": "Light 40%, rain 25%, wind 20%, comfort 10%, visibility 5%.",
    "event": "Light 30%, rain 35%, wind 20%, comfort 10%, visibility 5%.",
    "sunset": "Light 55%, rain 20%, wind 10%, comfort 5%, visibility 10%.",
    "landscape": "Light 45%, rain 20%, wind 15%, comfort 5%, visibility 15%.",
}

st.set_page_config(
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
        padding-top: 0.35rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1.1rem !important;
        padding-right: 1.1rem !important;
        max-width: 1680px;
      }}
      [data-testid="stMainBlockContainer"] {{
        max-width: 1680px;
      }}
      [data-testid="stVerticalBlock"] {{
        gap: 0.32rem !important;
      }}
      [data-testid="stHorizontalBlock"] {{
        gap: 0.7rem !important;
      }}
      h1 {{
        color: {BURGUNDY} !important;
        font-size: 1.4rem !important;
        margin: 0 !important;
      }}
      h3 {{
        color: {BURGUNDY} !important;
        font-size: 1.35rem !important;
        margin: 0.1rem 0 !important;
      }}
      .sw-brand {{
        color: {BURGUNDY}; font-weight: 700; font-size: 1.05rem;
      }}
      .sw-tagline {{
        color: {BURGUNDY}; opacity: 0.75; font-size: 0.85rem;
        text-align: right;
      }}
      .sw-caption {{
        color: {BURGUNDY}; opacity: 0.8; font-size: 0.8rem;
        margin: 0.08rem 0 0 0;
      }}
      .sw-ready {{
        display: inline-block;
        background: #E5F3EA;
        color: #2F6B45;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.12rem 0.45rem;
        border-radius: 999px;
        margin-left: 0.4rem;
        vertical-align: middle;
      }}
      .sw-card {{
        background: #fff;
        border: 1px solid #E4DDD3;
        border-radius: 12px;
        padding: 0.45rem 0.75rem;
        min-height: 72px;
      }}
      .sw-card-teal {{ background: #D8EEF4; border-color: #C5E4ED; }}
      .sw-card-peach {{ background: #F8E6D8; border-color: #F0D7C4; }}
      .sw-card-label {{
        color: {BURGUNDY}; font-size: 0.74rem; font-weight: 600;
      }}
      .sw-card-value {{
        color: {BURGUNDY}; font-size: 1.25rem; font-weight: 700;
        line-height: 1.15; margin: 0.05rem 0;
      }}
      .sw-card-sub {{
        color: {BURGUNDY}; opacity: 0.75; font-size: 0.7rem;
      }}
      .sw-mean {{
        background: #D8EEF4;
        border-radius: 10px;
        padding: 0.5rem 0.65rem;
        color: {BURGUNDY};
        font-size: 0.74rem;
        line-height: 1.35;
        margin-top: 0.2rem;
        margin-bottom: 0.5cm;
      }}
      /* 0.5 cm between rows of cards.
         "A ~ B" means: a row that comes after another row.
         The very first row (the page title) keeps no extra space. */
      [data-testid="stHorizontalBlock"] ~ [data-testid="stHorizontalBlock"] {{
        margin-top: 0.5cm !important;
      }}
      /* The small title row inside a chart card is not a page row. */
      div[data-testid="stVerticalBlockBorderWrapper"]
        [data-testid="stHorizontalBlock"] {{
        margin-top: 0 !important;
      }}
      /* Fixed header height so both cards in a row line up */
      .sw-chart-head {{
        background: #ffffff;
        background-color: #ffffff;
        height: 3rem;
        padding: 0.15rem 0 0.2rem 0;
        overflow: visible;
      }}
      .sw-chart-name {{
        color: {BURGUNDY};
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.25;
        background: #ffffff;
      }}
      .sw-chart-sub {{
        color: {BURGUNDY};
        opacity: 0.8;
        font-size: 0.82rem;
        margin: 0.08rem 0 0 0;
        line-height: 1.3;
        background: #ffffff;
      }}
      div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #ffffff !important;
        background-color: #ffffff !important;
        opacity: 1 !important;
        border: 1px solid #E4DDD3 !important;
        border-radius: 14px !important;
        padding: 0.5rem 0.7rem 0.5rem 0.7rem !important;
        overflow: visible !important;
      }}
      div[data-testid="stVerticalBlockBorderWrapper"] > div,
      div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"],
      div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"],
      div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stElementContainer"],
      div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"],
      div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"],
      div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stScrollToBottomContainer"],
      div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPlotlyChart"],
      div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPlotlyChart"] > div,
      div[data-testid="stVerticalBlockBorderWrapper"] .stPlotlyChart,
      div[data-testid="stVerticalBlockBorderWrapper"] .js-plotly-plot,
      div[data-testid="stVerticalBlockBorderWrapper"] .plot-container,
      div[data-testid="stVerticalBlockBorderWrapper"] .svg-container,
      div[data-testid="stVerticalBlockBorderWrapper"] .main-svg {{
        background: #ffffff !important;
        background-color: #ffffff !important;
        opacity: 1 !important;
      }}
      div[data-testid="stVerticalBlockBorderWrapper"] .js-plotly-plot .bg {{
        fill: #ffffff !important;
      }}
      div[data-testid="stVerticalBlockBorderWrapper"] p,
      div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdown"] {{
        background: #ffffff !important;
        background-color: #ffffff !important;
      }}
      [data-testid="stPlotlyChart"] {{
        margin: 0 !important;
        background: #ffffff !important;
        background-color: #ffffff !important;
      }}
      [data-testid="stPlotlyChart"] > div {{
        height: {CHART_HEIGHT}px !important;
        background: #ffffff !important;
        background-color: #ffffff !important;
      }}
      [data-testid="stCaption"] {{
        margin-top: 0 !important;
        font-size: 0.72rem !important;
      }}
      .stProgress {{
        margin-top: 0.1rem !important;
        margin-bottom: 0.15rem !important;
      }}
      .stButton > button {{
        border: 1.5px solid {BURGUNDY};
        color: {BURGUNDY};
        background: #ffffff;
        border-radius: 8px;
        font-weight: 600;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


def _api_key() -> str | None:
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


def _parse_hhmm(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def _booked_within_window(booked: str, start: str, end: str) -> bool:
    b = _parse_hhmm(booked)
    s = _parse_hhmm(start)
    e = _parse_hhmm(end)
    if s <= e:
        return s <= b < e
    return b >= s or b < e


def _clock(hour) -> str:
    return hour.time_text.split(" ")[1][:5]


def _hour_at(scored, start_clock: str):
    """Return the scored hour that starts the best window."""
    for item in scored:
        if _clock(item.hour) == start_clock:
            return item
    return scored[0]


def _chart_head(title: str, subtitle: str = "") -> None:
    """Chart title + subtitle on a white background."""
    extra = f'<p class="sw-chart-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div class="sw-chart-head">'
        f'<p class="sw-chart-name">{title}</p>'
        f"{extra}</div>",
        unsafe_allow_html=True,
    )


def _show_chart(fig) -> None:
    st.plotly_chart(
        fig,
        use_container_width=True,
        theme=None,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
            "showTips": False,
        },
    )


@st.cache_data(ttl=600, show_spinner=False)
def _score_city(city: str, shoot_type: str, shoot_date: str, api_key: str):
    try:
        client = OpenWeatherClient(api_key=api_key)
        forecast = client.get_forecast(city)
        scored = score_forecast(forecast, shoot_type, shoot_date)
        return {
            _clock(item.hour): item.display_score
            for item in scored
        }
    except WeatherError:
        return None


def _build_city_matrix(cities, shoot_type, shoot_date, api_key, hour_columns):
    matrix = {}
    for city_name in cities:
        scored = _score_city(city_name, shoot_type, shoot_date, api_key)
        if scored is None:
            matrix[city_name] = {h: None for h in hour_columns}
        else:
            matrix[city_name] = {h: scored.get(h) for h in hour_columns}
    return matrix


# ------------------------------------------------------------
# Guard
# ------------------------------------------------------------
if not st.session_state.get("plan_ready"):
    st.warning("Start on the home page — choose a session, then press Plan shoot.")
    if st.button("← Back to plan"):
        st.switch_page("app.py")
    st.stop()

city = st.session_state["city"]
shoot_date = st.session_state["shoot_date"]
preferred_time = st.session_state["preferred_time"]
shoot_type = str(st.session_state["shoot_type"]).lower()
if shoot_type not in SHOOT_TYPES:
    shoot_type = SHOOT_TYPES[0]

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
brand_left, brand_right = st.columns([2.2, 1.2])
with brand_left:
    if LOGO_PATH.exists():
        c_logo, c_name = st.columns([0.18, 1.2])
        with c_logo:
            st.image(str(LOGO_PATH), width=36)
        with c_name:
            st.markdown('<div class="sw-brand">Shoot Window</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sw-brand">Shoot Window</div>', unsafe_allow_html=True)
with brand_right:
    st.markdown(
        '<div class="sw-tagline">Outdoor photography, planned.</div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------
# Load forecast
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
booked = score_booked_interval(scored, shoot_date, preferred_time)
within_window = _booked_within_window(preferred_time, start, end)
window_hour = _hour_at(scored, start)
date_label = _format_date_label(shoot_date)
weights = SHOOT_WEIGHTS[shoot_type]

if window.status == STATUS_UNAVAILABLE:
    score_value = "—"
    score_sub = "Unavailable — missing forecast inputs."
elif window.status == STATUS_NOT_RECOMMENDED:
    score_value = f"{window.score} / 100"
    score_sub = "Not recommended"
else:
    score_value = f"{window.score} / 100"
    score_sub = condition_label(window.score, window.status)

if booked is None:
    booked_sub = "No overlapping forecast for that booking."
elif booked.status == STATUS_NOT_RECOMMENDED:
    booked_sub = "Not recommended"
elif within_window:
    booked_sub = "Within the recommended window"
else:
    booked_sub = "Outside the recommended window"

# ------------------------------------------------------------
# Layout: explain (left) | plan + charts (right)
# ------------------------------------------------------------
left, right = st.columns([0.78, 2.45], gap="medium")

with left:
    st.caption("PHOTOGRAPHY TYPE")
    chosen = st.selectbox(
        "Photography type",
        list(SHOOT_TYPES),
        index=list(SHOOT_TYPES).index(shoot_type),
        format_func=str.capitalize,
        label_visibility="collapsed",
    )
    if chosen != shoot_type:
        st.session_state["shoot_type"] = chosen
        st.rerun()

    if window.status == STATUS_UNAVAILABLE:
        st.markdown(f"### {score_value}")
    else:
        st.markdown(f"### {window.score} / 100")
    st.caption(score_sub)
    if window.status != STATUS_UNAVAILABLE:
        st.progress(window.score / 100)
        st.caption(f"Score vs perfect 100 · {window.score}%")

    st.markdown("**WHAT SHAPED IT**")
    for name in FACTOR_NAMES:
        suit = getattr(window_hour, name)
        weight_pct = int(round(weights[name] * 100))
        label = FACTOR_LABELS[name]
        if suit is None:
            st.caption(f"{label}  ·  —  ·  +{weight_pct}%")
            st.progress(0)
        else:
            shown = int(round(suit * 100))
            st.caption(f"{label}  ·  {shown}  ·  +{weight_pct}%")
            st.progress(min(1.0, max(0.0, suit)))

    st.caption(TYPE_WHY[shoot_type])

    st.markdown(
        f"""
        <div class="sw-mean">
          <strong>WHAT YOUR SCORE MEANS</strong><br>
          80–100 · Good — well suited to {shoot_type}.<br>
          60–79 · Fair — workable, you may need tweaks.<br>
          0–59 · Challenging — consider another time.<br>
          <em>A planning guide based on the forecast — not a guarantee of the final photos.</em>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("How your Photography Score works"):
        st.markdown(
            f"""
**{shoot_type.capitalize()}** (the type you chose)

Your score combines five factors: light, rain, wind, comfort, and visibility.
For this session they are weighted:

**{TYPE_WEIGHT_TEXT[shoot_type]}**

{TYPE_WHY[shoot_type]}

Each profile’s weights total **100%**. Cloud cover is included in the
**light** factor, together with the sun’s position — there is no extra
cloud weight.

The recommended window looks at the **full 3-hour session**, with extra
attention to weaker periods. Time itself does not get its own weight.
Heavy rain, strong wind, or very uncomfortable temperature can **cap**
the score even if other factors look good.
            """
        )

with right:
    title_left, title_right = st.columns([3.4, 1.1])
    with title_left:
        st.markdown(
            '<h1>Your shoot plan '
            '<span class="sw-ready">READY</span></h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="sw-caption">{city}  ·  {date_label}  ·  '
            f"{shoot_type.capitalize()}</p>",
            unsafe_allow_html=True,
        )
    with title_right:
        if st.button("✎ Edit session", use_container_width=True):
            st.session_state["plan_ready"] = False
            st.switch_page("app.py")

    col_score, col_window, col_booked = st.columns(3)
    with col_score:
        st.markdown(
            f"""
            <div class="sw-card">
              <div class="sw-card-label">Photography score</div>
              <div class="sw-card-value">{score_value}</div>
              <div class="sw-card-sub">{score_sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_window:
        st.markdown(
            f"""
            <div class="sw-card sw-card-teal">
              <div class="sw-card-label">Best shooting window</div>
              <div class="sw-card-value">{start} – {end}</div>
              <div class="sw-card-sub">Highest-rated light and weather</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_booked:
        st.markdown(
            f"""
            <div class="sw-card sw-card-peach">
              <div class="sw-card-label">Your booked time</div>
              <div class="sw-card-value">{preferred_time}</div>
              <div class="sw-card-sub">{booked_sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    hour_columns = [_clock(hour) for hour, _ in scored]
    filter_options = ["All cities", *ISRAEL_CITIES]
    city_filter = st.session_state.get("heatmap_city_filter", "All cities")
    if city_filter not in filter_options:
        city_filter = "All cities"
    if city_filter == "All cities":
        visible_cities = [city] + [c for c in ISRAEL_CITIES if c != city]
    else:
        visible_cities = [city_filter]

    city_matrix = _build_city_matrix(
        visible_cities,
        shoot_type,
        shoot_date,
        api_key,
        hour_columns,
    )

    top_left, top_right = st.columns(2, gap="small")
    with top_left:
        with st.container(border=True):
            _chart_head(
                "Photography score throughout the day",
                "Light, weather, and timing combined",
            )
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
            head_l, head_r = st.columns([1.6, 1], vertical_alignment="center")
            with head_l:
                _chart_head("City scores by hour", "Compare nearby locations")
            with head_r:
                st.selectbox(
                    "Cities",
                    filter_options,
                    index=filter_options.index(city_filter),
                    label_visibility="collapsed",
                    key="heatmap_city_filter",
                )
            _show_chart(
                city_scores_heatmap(
                    city_matrix,
                    selected_city=city,
                    hour_columns=hour_columns,
                )
            )

    bot_left, bot_right = st.columns(2, gap="small")
    with bot_left:
        with st.container(border=True):
            _chart_head("Temperature", "Comfort range across the session day")
            _show_chart(temperature_chart(scored))
    with bot_right:
        with st.container(border=True):
            _chart_head("Rain probability", "Rain chance across the session day")
            _show_chart(rain_probability_chart(scored))
