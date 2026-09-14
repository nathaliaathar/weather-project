"""Home page — plan a photography session (`streamlit run app.py`)."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

import streamlit as st

from photo_planner.validation import ISRAEL_CITIES, SHOOT_TYPES

st.set_page_config(
    page_title="Shoot Window — photography planner",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _default_city() -> str:
    saved = st.session_state.get("city", ISRAEL_CITIES[0])
    return saved if saved in ISRAEL_CITIES else ISRAEL_CITIES[0]


def _default_date() -> date:
    today = date.today()
    saved = st.session_state.get("shoot_date")
    if isinstance(saved, str):
        try:
            parsed = datetime.strptime(saved, "%Y-%m-%d").date()
            if today <= parsed <= today + timedelta(days=4):
                return parsed
        except ValueError:
            pass
    return today + timedelta(days=1)


def _default_time() -> time:
    saved = st.session_state.get("preferred_time", "17:00")
    if isinstance(saved, time):
        return saved
    try:
        return datetime.strptime(str(saved), "%H:%M").time()
    except ValueError:
        return time(17, 0)


def _default_shoot_type() -> str:
    saved = str(st.session_state.get("shoot_type", SHOOT_TYPES[0])).lower()
    return saved if saved in SHOOT_TYPES else SHOOT_TYPES[0]


st.markdown(
    """
    <style>
      [data-testid="stSidebar"] { display: none; }
      [data-testid="stSidebarCollapsedControl"] { display: none; }
      .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

head_left, head_right = st.columns([3, 2], vertical_alignment="center")
with head_left:
    logo_col, title_col = st.columns([1, 10], vertical_alignment="center")
    with logo_col:
        st.image("assets/logo.png", width=90)
    with title_col:
        st.markdown("### Shoot Window")
with head_right:
    st.caption("Outdoor photography, planned.")
st.divider()

col_hero, col_form = st.columns([1.1, 1], gap="large")

with col_hero:
    st.caption("FOR OUTDOOR PHOTOGRAPHERS IN ISRAEL")

    st.markdown("## Know when it's worth the shoot.")

    st.write(
        "Turn the weather into a clear shooting decision. "
        "Get a 0–100 Photography Score tailored to your shoot type, "
        "plus the best shooting window for your chosen date and location."
    )

    st.image("assets/city.png", use_container_width=True)

    st.markdown(
        '<p style="text-align:center; font-size:14px; color:#8a7a70; margin-top:0.25rem;">'
        "Portrait · Event · Sunset · Landscape"
        "</p>",
        unsafe_allow_html=True,
    )


with col_form:
    st.subheader("Plan a session")
    st.caption("Choose where, when, and what you'll shoot.")

    row1_left, row1_right = st.columns(2)
    with row1_left:
        city = st.selectbox(
            "Location",
            ISRAEL_CITIES,
            index=ISRAEL_CITIES.index(_default_city()),
        )
    with row1_right:
        # Free forecast covers about 5 days from today.
        today = date.today()
        shoot_date = st.date_input(
            "Date",
            value=_default_date(),
            min_value=today,
            max_value=today + timedelta(days=4),
        )

    row2_left, row2_right = st.columns(2)
    with row2_left:
        preferred_time = st.time_input(
            "Preferred time",
            value=_default_time(),
        )
    with row2_right:
        shoot_type = st.selectbox(
            "Photography type",
            SHOOT_TYPES,
            index=SHOOT_TYPES.index(_default_shoot_type()),
        )

    plan = st.button("Plan shoot →", type="primary", use_container_width=True)
    st.caption("Find your score and best shooting window.")

    if plan:
        st.session_state["city"] = city
        st.session_state["shoot_date"] = shoot_date.isoformat()
        st.session_state["preferred_time"] = preferred_time.strftime("%H:%M")
        st.session_state["shoot_type"] = shoot_type
        st.session_state["plan_ready"] = True
        st.session_state["heatmap_page"] = 0
        st.session_state["heatmap_city_filter"] = "All cities"
        st.switch_page("pages/results.py")

st.divider()
st.caption("Better timing. More confident bookings.")
