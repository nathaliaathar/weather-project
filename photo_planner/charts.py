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
from photo_planner.scoring import display_score

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

BURGUNDY = "#7B3C3C"
ORANGE = "#DB5F29"
IVORY = "#F0F0E4"
SKY = "#68BDE1"


def _clock_label(time_text: str) -> str:
    """'2026-09-04 15:00:00' → '15:00'."""
    return time_text.split(" ")[1][:5]


def _minutes(label: str) -> int:
    hours, mins = label.split(":")
    return int(hours) * 60 + int(mins)


CHART_HEIGHT = 240

# Room on the left of the heatmap for the longest city name
# ("● Tel Aviv", "Jerusalem") so it is never cut off.
HEATMAP_LEFT_MARGIN = 92


def _compact_layout(
    fig: go.Figure,
    *,
    height: int = CHART_HEIGHT,
    left: int = 40,
    right: int = 32,
    top: int = 28,
    bottom: int = 36,
) -> go.Figure:
    """Shared look for every chart. The margins can grow when a chart
    needs more room, e.g. the heatmap needs space for the city names."""
    fig.update_layout(
        height=height,
        margin=dict(l=left, r=right, t=top, b=bottom),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color=BURGUNDY, size=12),
        title=dict(text=""),
        showlegend=False,
        dragmode=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=11)),
    )
    fig.update_xaxes(
        showgrid=False,
        tickfont=dict(size=12),
        title_font=dict(size=12),
        fixedrange=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(123,60,60,0.14)",
        tickfont=dict(size=12),
        title_font=dict(size=12),
        fixedrange=True,
    )
    return fig


def photography_score_chart(
    scored_hours: list[tuple[HourlyConditions, float | None]],
    *,
    window_start: str | None = None,
    window_end: str | None = None,
    booked_time: str | None = None,
):
    """
    Burgundy line of Photography Score across the day (0–100).
    Optionally shades the best window and marks the booked time.

    Uses numeric x positions so Plotly vrect/vline work reliably;
    tick labels still show clock times. Displayed values are integers.
    Missing scores stay gaps, never coerced to 0.
    """
    _ = window_end  # window length is derived from consecutive slots
    times = [_clock_label(hour.time_text) for hour, _ in scored_hours]
    scores = [
        None if score is None else float(display_score(score))
        for _, score in scored_hours
    ]
    x_idx = list(range(len(times)))
    labels = ["" if s is None else str(int(s)) for s in scores]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_idx,
            y=scores,
            mode="lines+markers+text",
            name="Score",
            line=dict(color=BURGUNDY, width=3),
            marker=dict(size=9, color=BURGUNDY),
            text=labels,
            textposition="top center",
            textfont=dict(size=12, color=BURGUNDY),
            cliponaxis=False,
            customdata=times,
            hovertemplate="Time %{customdata}<br>Score %{y:.0f}<extra></extra>",
            connectgaps=False,
        )
    )

    if window_start and times:
        if window_start in times:
            i0 = times.index(window_start)
        else:
            target = _minutes(window_start)
            i0 = min(range(len(times)), key=lambda i: abs(_minutes(times[i]) - target))
        x1 = (i0 + 1) - 0.35 if i0 + 1 < len(times) else i0 + 0.65
        fig.add_vrect(
            x0=i0 - 0.35,
            x1=x1,
            fillcolor=SKY,
            opacity=0.22,
            layer="below",
            line_width=0,
            annotation_text="Best window",
            annotation_position="top left",
            annotation_font_size=12,
            annotation_font_color=BURGUNDY,
        )

    if booked_time and times:
        booked_m = _minutes(booked_time)
        minutes = [_minutes(t) for t in times]
        if booked_time in times:
            x_booked = float(times.index(booked_time))
        elif booked_m <= minutes[0]:
            x_booked = 0.0
        elif booked_m >= minutes[-1]:
            x_booked = float(len(times) - 1)
        else:
            x_booked = float(len(times) - 1)
            for i in range(len(minutes) - 1):
                if minutes[i] <= booked_m <= minutes[i + 1]:
                    span = minutes[i + 1] - minutes[i] or 1
                    x_booked = i + (booked_m - minutes[i]) / span
                    break
        fig.add_vline(
            x=x_booked,
            line_dash="dash",
            line_color=ORANGE,
            line_width=2,
            annotation_text=f"Booked {booked_time}",
            annotation_position="top right",
            annotation_font_size=12,
            annotation_font_color=ORANGE,
        )

    fig.update_yaxes(range=[0, 118], title_text="Score")
    fig.update_xaxes(
        title_text="",
        tickmode="array",
        tickvals=x_idx,
        ticktext=times,
        # Extra room so the first/last value labels are not cut off
        range=[-0.6, len(times) - 0.4] if times else None,
    )
    fig.update_layout(showlegend=False)
    return _compact_layout(fig)


def temperature_chart(scored_hours: list[tuple[HourlyConditions, float]]):
    """Orange line chart of temperature_c across the same hours."""
    times = [_clock_label(hour.time_text) for hour, _ in scored_hours]
    temperatures = [hour.temperature_c for hour, _ in scored_hours]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=temperatures,
            mode="lines+markers+text",
            name="°C",
            line=dict(color=ORANGE, width=3),
            marker=dict(size=9, color=ORANGE),
            text=[f"{t:.1f}" for t in temperatures],
            textposition="top center",
            textfont=dict(size=12, color=ORANGE),
            cliponaxis=False,
            hovertemplate="Time %{x}<br>%{y:.1f} °C<extra></extra>",
        )
    )
    fig.update_yaxes(title_text="°C")
    if temperatures:
        low = min(temperatures)
        high = max(temperatures)
        extra = max(2.0, (high - low) * 0.2)
        fig.update_yaxes(range=[low - extra * 0.25, high + extra])
    fig.update_xaxes(title_text="")
    fig.update_layout(showlegend=False)
    return _compact_layout(fig)


def rain_probability_chart(scored_hours: list[tuple[HourlyConditions, float]]):
    """
    Vertical bars of rain probability (0–100%).
    Source pop is 0–1; labels sit above each bar, including 0%.
    """
    times = [_clock_label(hour.time_text) for hour, _ in scored_hours]
    rain_pct = [hour.rain_probability * 100 for hour, _ in scored_hours]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=times,
            y=rain_pct,
            name="Rain",
            marker_color=SKY,
            text=[f"{p:.0f}%" for p in rain_pct],
            textposition="outside",
            textfont=dict(size=12, color=BURGUNDY),
            cliponaxis=False,
            hovertemplate="Time %{x}<br>Rain %{y:.0f}%<extra></extra>",
        )
    )
    fig.update_yaxes(range=[0, 118], title_text="Rain %", ticksuffix="")
    fig.update_xaxes(title_text="")
    fig.update_layout(showlegend=False, bargap=0.35)
    return _compact_layout(fig)


def clouds_and_rain_chart(scored_hours: list[tuple[HourlyConditions, float]]):
    """Legacy dual-line chart kept for callers that still expect it."""
    times = [_clock_label(hour.time_text) for hour, _ in scored_hours]
    clouds = [hour.cloud_cover for hour, _ in scored_hours]
    rain = [hour.rain_probability * 100 for hour, _ in scored_hours]

    df = pd.DataFrame({"Time": times, "Clouds": clouds, "Rain": rain})
    fig = px.line(
        df,
        x="Time",
        y=["Clouds", "Rain"],
        title="Clouds and Rain Probability",
        labels={"value": "Percentage", "variable": "Series"},
        color_discrete_map={"Clouds": BURGUNDY, "Rain": SKY},
    )
    return _compact_layout(fig, height=200)


def city_scores_heatmap(
    city_hour_scores: dict[str, dict[str, float | None]],
    *,
    selected_city: str,
    hour_columns: list[str] | None = None,
):
    """
    Heatmap: cities as rows, hours as columns, scores 0–100.
    Missing values stay unavailable (None → blank), never coerced to 0.
    """
    if not city_hour_scores:
        fig = go.Figure()
        return _compact_layout(fig)

    if hour_columns is None:
        hour_set: list[str] = []
        for hours in city_hour_scores.values():
            for h in hours:
                if h not in hour_set:
                    hour_set.append(h)
        hour_columns = sorted(hour_set)

    cities = list(city_hour_scores.keys())
    z: list[list[float | None]] = []
    text: list[list[str]] = []
    for city in cities:
        row_scores = city_hour_scores[city]
        row_z: list[float | None] = []
        row_text: list[str] = []
        for hour in hour_columns:
            value = row_scores.get(hour)
            if value is None:
                row_z.append(None)
                row_text.append("—")
            else:
                shown = display_score(value)
                row_z.append(shown)
                row_text.append(str(shown))
        z.append(row_z)
        text.append(row_text)

    y_labels = [f"● {city}" if city == selected_city else city for city in cities]

    # Absolute 0–100 legend: coral at 0, blue at 100.
    # Extra stops in the mid/high band so nearby scores (e.g. 70 vs 80) read clearly.
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=hour_columns,
            y=y_labels,
            text=text,
            texttemplate="%{text}",
            textfont=dict(size=13),
            colorscale=[
                [0.00, ORANGE],
                [0.35, "#E8926A"],
                [0.50, "#D4A090"],
                [0.62, "#B9B3B0"],
                [0.74, "#8BBFD9"],
                [0.88, "#74B8DE"],
                [1.00, SKY],
            ],
            reversescale=False,
            zmin=0,
            zmax=100,
            colorbar=dict(
                title=dict(text="Score", font=dict(size=10)),
                thickness=10,
                len=0.85,
                tickfont=dict(size=9),
                tickvals=[0, 25, 50, 75, 100],
            ),
            hovertemplate="%{y}<br>%{x}<br>Score %{z}<extra></extra>",
            xgap=2,
            ygap=2,
        )
    )
    fig.update_layout(
        xaxis=dict(side="bottom", title="", fixedrange=True),
        yaxis=dict(title="", autorange="reversed", fixedrange=True),
    )
    # Wide left margin so the full city name is visible, and small
    # top/bottom margins so the rows stay tall enough to read.
    return _compact_layout(fig, left=HEATMAP_LEFT_MARGIN, right=58, top=10, bottom=30)
