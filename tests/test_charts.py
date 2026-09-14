"""Checks that results-page charts stay readable (height, margins, labels)."""

from photo_planner.charts import (
    CHART_HEIGHT,
    city_scores_heatmap,
    photography_score_chart,
    rain_probability_chart,
    temperature_chart,
)
from photo_planner.models import HourlyConditions

TIMES = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
TEMPS = [26.0, 24.3, 26.7, 29.7, 32.2, 30.3, 28.7, 27.2]
SCORES = [29.0, 81.0, 81.0, 59.0, 60.0, 70.0, 29.0, 29.0]


def make_hour(clock: str, temperature: float) -> HourlyConditions:
    return HourlyConditions(
        time_text=f"2026-09-11 {clock}:00",
        timestamp_unix=0,
        temperature_c=temperature,
        feels_like_c=temperature,
        humidity=55,
        wind_speed=3.0,
        cloud_cover=20,
        rain_probability=0.2,
        rain_mm=0.0,
        description="clear sky",
        icon="01d",
        visibility_m=10000.0,
        weather_id=800,
    )


def make_scored() -> list[tuple[HourlyConditions, float]]:
    return [
        (make_hour(clock, TEMPS[i]), SCORES[i]) for i, clock in enumerate(TIMES)
    ]


def all_charts():
    scored = make_scored()
    matrix = {
        "Tel Aviv": dict(zip(TIMES, SCORES)),
        "Haifa": dict(zip(TIMES, SCORES)),
    }
    return [
        photography_score_chart(
            scored, window_start="03:00", window_end="06:00", booked_time="17:00"
        ),
        city_scores_heatmap(matrix, selected_city="Tel Aviv", hour_columns=TIMES),
        temperature_chart(scored),
        rain_probability_chart(scored),
    ]


def test_every_chart_has_the_same_height():
    for fig in all_charts():
        assert fig.layout.height == CHART_HEIGHT


def test_every_chart_is_white_and_has_no_title():
    # The card already shows the title, so the figure must not repeat it.
    for fig in all_charts():
        assert fig.layout.paper_bgcolor == "white"
        assert fig.layout.plot_bgcolor == "white"
        assert fig.layout.title.text == ""


def test_line_and_bar_charts_have_room_for_labels():
    # These charts print the value above each point or bar.
    scored = make_scored()
    for fig in (
        photography_score_chart(scored),
        temperature_chart(scored),
        rain_probability_chart(scored),
    ):
        margin = fig.layout.margin
        assert margin.t >= 24  # space for labels on top
        assert margin.b >= 32  # space for the hour ticks
        assert margin.l >= 36  # space for the axis numbers


def test_heatmap_has_room_for_the_city_names():
    matrix = {"Jerusalem": dict(zip(TIMES, SCORES))}
    fig = city_scores_heatmap(matrix, selected_city="Jerusalem", hour_columns=TIMES)
    margin = fig.layout.margin
    # "● Jerusalem" is about 70px wide at 12px font, so we need more than that.
    assert margin.l >= 85
    assert margin.r >= 50  # space for the colour legend
    # Labels live inside the squares, so tall rows matter more than top space.
    plot_height = fig.layout.height - margin.t - margin.b
    assert plot_height >= 190


def test_zoom_is_disabled_but_tooltip_stays():
    for fig in all_charts():
        assert fig.layout.dragmode is False
        assert fig.layout.xaxis.fixedrange is True
        assert fig.layout.yaxis.fixedrange is True


def test_score_chart_labels_fit_inside_the_plot():
    fig = photography_score_chart(make_scored())
    # Labels sit above the points, so the top of the axis must clear 100.
    assert fig.layout.yaxis.range[1] > max(SCORES) + 10
    # First and last labels need side padding, otherwise they get cut.
    assert fig.layout.xaxis.range[0] < 0
    assert fig.layout.xaxis.range[1] > len(TIMES) - 1


def test_temperature_chart_leaves_space_above_the_warmest_hour():
    fig = temperature_chart(make_scored())
    low, high = fig.layout.yaxis.range
    assert high > max(TEMPS)
    assert low < min(TEMPS)


def test_rain_chart_labels_fit():
    fig = rain_probability_chart(make_scored())
    assert fig.layout.yaxis.range[1] > 100
