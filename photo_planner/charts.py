# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# This file builds interactive charts from scored forecast hours.
#
# WHY WE KEEP THIS SEPARATE:
# Drawing charts is a different job from talking to the API
# and from computing the Photography Score.
# app.py will call these functions and pass the result to
# st.plotly_chart(...). This file never calls the API.
#
# Person B owns this file.
# ============================================================

from __future__ import annotations

from photo_planner.models import HourlyConditions  # KEEP

# WHY THIS EXISTS:
# Plotly is the chart library. Import plotly.express or plotly.graph_objects
# when you implement the functions below.
# import plotly.express as px
# import plotly.graph_objects as go

# OPTIONAL: pandas is handy for turning scored_hours into a small table
# before you plot. Import it when you need it.
# import pandas as pd


def photography_score_chart(scored_hours: list[tuple[HourlyConditions, float]]):
    """
    YOUR TASK:

    Line (or bar) chart of Photography Score across the day.
    This is the main product chart — it answers "when should I shoot?"

    Called by:
        app.py, after score_forecast(...)

    HINT:
    X = clock time, Y = score (0–100).
    Mark the highest point if you can (a different colour is enough).
    One interactive Plotly figure is enough. Do not call Streamlit here.
    """

    # YOUR CODE GOES HERE 👇
    # TODO (STUDENT): Build and return a Plotly figure of score vs time.

    raise NotImplementedError("Person B: Photography Score chart")  # DELETE LATER


def temperature_chart(scored_hours: list[tuple[HourlyConditions, float]]):
    """
    YOUR TASK:

    Chart temperature_c across the same hours.

    HINT:
    You already have the HourlyConditions objects — use hour.temperature_c.
    The score is in the tuple but you do not have to plot it here.
    """

    # YOUR CODE GOES HERE 👇
    # TODO (STUDENT): Build and return a Plotly figure of temperature vs time.

    raise NotImplementedError("Person B: temperature chart")  # DELETE LATER


def clouds_and_rain_chart(scored_hours: list[tuple[HourlyConditions, float]]):
    """
    YOUR TASK:

    Chart cloud cover and/or rain probability across the day.

    HINT:
    cloud_cover is 0–100.
    rain_probability is 0–1 — multiply by 100 if you want percent on the axis.
    Two lines on one figure, or two bars, both work.

    Called by:
        app.py (this is the third chart; do it after the score chart works)
    """

    # YOUR CODE GOES HERE 👇
    # TODO (STUDENT): Build and return a Plotly figure for clouds and/or rain.

    raise NotImplementedError("Person B: clouds / rain chart")  # DELETE LATER
