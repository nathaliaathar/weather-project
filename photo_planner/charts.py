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
# Plotly Express (px) is enough for the MVP charts. Use graph_objects only
# later if you need something px cannot do.
import plotly.express as px
# pandas: build a small table when a chart needs more than one Y series
import pandas as pd


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
    # empty lists that will hold the X and Y values for the chart
    times = []
    scores = []

    # scored_hours is a list of (hour, score) pairs from scoring.py
    for hour, score in scored_hours:
        # get the time from the time_text ("2026-09-04 15:00:00" → "15:00:00")
        clock = hour.time_text.split(" ")[1]
        times.append(clock)   # X axis: clock time
        scores.append(score)  # Y axis: photography score 0–100

    # build a line chart with Plotly Express (no Streamlit here)
    fig = px.line(
        x=times,
        y=scores,
        title="Photography Score",
        labels={"x": "Time", "y": "Score"},
    )
    # name the axes so the photographer can read the chart easily
    fig.update_layout(xaxis_title="Time", yaxis_title="Score")
    return fig  # app.py will show this with st.plotly_chart(...)


def temperature_chart(scored_hours: list[tuple[HourlyConditions, float]]):
    """
    YOUR TASK:

    Chart temperature_c across the same hours.

    HINT:
    You already have the HourlyConditions objects — use hour.temperature_c.
    The score is in the tuple but you do not have to plot it here.
    """

    # YOUR CODE GOES HERE 👇
    # TODO (STUDENT): same idea as photography_score_chart, but Y = hour.temperature_c
    # HINT: loop scored_hours, collect times + temperatures, then px.line(...)

    times = []
    temperatures = []

    for hour,score in scored_hours:
        clock = hour.time_text.split(" ")[1]
        times.append(clock)
        temperatures.append(hour.temperature_c)

    fig = px.line(
        x=times,
        y=temperatures,
        title = "Temperature Over Time",
        labels={"x": "Time", "y": "Temperature"},
    )
    fig.update_layout(xaxis_title="Time", yaxis_title="Temperature")
    return fig  # app.py will show this with st.plotly_chart(...)


    


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
    # TODO (STUDENT): collect times, cloud_cover, and rain_probability (* 100 for %)
    # HINT: you can put both series on one figure (two lines) with pandas + px.line


    # 2 lines in same chart. clouds & rain probability

    times = []
    clouds = []
    rain = []

    for hour,score in scored_hours:
        clock = hour.time_text.split(" ")[1]
        times.append(clock)
        clouds.append(hour.cloud_cover)
        rain.append(hour.rain_probability * 100)

    df = pd.DataFrame({
        "Time": times,
        "Clouds": clouds,
        "Rain": rain,
    })

    fig = px.line(
        df,
        x="Time",
        y=["Clouds", "Rain"],
        title="Clouds and Rain Probability",
        labels={"x": "Time", "y": "Percentage"},
    )
    fig.update_layout(xaxis_title="Time", yaxis_title="Percentage")
    return fig  # app.py will show this with st.plotly_chart(...)   
    