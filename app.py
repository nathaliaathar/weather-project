# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# This is the HOME page — the entry point you start with
# `streamlit run app.py`.
#
# Think of it as the landing screen from the mockup:
#   LEFT  → why the product exists (headline + short copy)
#   RIGHT → "Plan a session" form
#
# When the photographer clicks "Plan shoot", we SAVE their
# choices in st.session_state and JUMP to pages/results.py.
#
# WHY WE KEEP THIS SEPARATE FROM results.py:
# The home page is about choosing inputs.
# The results page is about showing the decision (score + charts).
# Two jobs → two pages → less scrolling on each screen.
#
# Person B owns the UI. See docs/PAIR.md.
# ============================================================

from __future__ import annotations

from datetime import date, time, timedelta

# WHY THIS EXISTS:
# streamlit turns this Python file into a web page.
import streamlit as st  # KEEP

st.set_page_config(  # KEEP — browser tab title and wide layout
    page_title="Shoot Window — photography planner",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# KEEP — common outdoor-shoot locations. You may add more later.
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

# ------------------------------------------------------------
# OPTIONAL polish: hide the multipage sidebar for a cleaner look
# DELETE LATER if you prefer the default Streamlit sidebar.
# ------------------------------------------------------------
st.markdown(  # KEEP — small UX helper, not assignment logic
    """
    <style>
      [data-testid="stSidebar"] { display: none; }
      [data-testid="stSidebarCollapsedControl"] { display: none; }
      .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header: logo + product name (left), tagline (right)
# vertical_alignment keeps the logo and title on the same midline
head_left, head_right = st.columns([3, 2], vertical_alignment="center")
with head_left:
    logo_col, title_col = st.columns([1, 10], vertical_alignment="center")
    with logo_col:
        # KEEP — logo is square with cream padding; ~56px reads clearly next to the title
        st.image("assets/logo.png", width=90)
    with title_col:
        st.markdown("### Shoot Window")
with head_right:
    st.caption("Outdoor photography, planned.")
st.divider()


# Two columns like the mockup (hero | form card)

col_hero, col_form = st.columns([1.1, 1], gap="large")

with col_hero:
    st.caption("FOR OUTDOOR PHOTOGRAPHERS IN ISRAEL")

    st.markdown("## Know when it's worth the shoot.")

    st.write(
        "Turn the weather into a clear shooting decision. "
        "Get a 0–100 Photography Score tailored to your shoot type, "
        "plus the best shooting window for your chosen date and location."
    )

    # This part is the illustration city + the photogragy type options
    st.image("assets/city.png", use_container_width=True)

    st.markdown(
        '<p style="text-align:center; font-size:14px; color:#8a7a70; margin-top:0.25rem;">'
        "Portrait · Sunset · Landscape"
        "</p>",
        unsafe_allow_html=True,
    )


with col_form:
    # KEEP — the form widgets. Layout can change; the inputs matter.
    st.subheader("Plan a session")
    st.caption("Choose where, when, and what you'll shoot.")

    # WHY 2x2: mockup uses a grid, not one long row of 4 fields.
    row1_left, row1_right = st.columns(2)
    with row1_left:
        city = st.selectbox("Location", ISRAEL_CITIES, index=0)  # KEEP
    with row1_right:
        # KEEP — free forecast covers about 5 days from today
        today = date.today()
        shoot_date = st.date_input(
            "Date",
            value=today + timedelta(days=1),
            min_value=today,
            max_value=today + timedelta(days=4),
        )

    row2_left, row2_right = st.columns(2)
    with row2_left:
        preferred_time = st.time_input("Preferred time", value=time(17, 0))  # KEEP
    with row2_right:
        shoot_type = st.selectbox(  # KEEP
            "Photography type",
            ("portrait", "sunset", "landscape"),
            index=0,
        )

    plan = st.button("Plan shoot →", type="primary", use_container_width=True)  # KEEP
    st.caption("Find your score and best shooting window.")

    # ------------------------------------------------------------
    # NAVIGATION: save inputs, then open the results page
    # WHY session_state:
    # pages cannot see local variables from app.py.
    # session_state is a shared notebook the app remembers
    # while the browser tab stays open.
    # ------------------------------------------------------------
    if plan:
        st.session_state["city"] = city
        st.session_state["shoot_date"] = shoot_date.isoformat()
        st.session_state["preferred_time"] = preferred_time.strftime("%H:%M")
        st.session_state["shoot_type"] = shoot_type
        st.session_state["plan_ready"] = True
        # KEEP — Streamlit opens pages/results.py as a second page
        st.switch_page("pages/results.py")

st.divider()
st.caption("Better timing. More confident bookings.")  # KEEP — footer line
