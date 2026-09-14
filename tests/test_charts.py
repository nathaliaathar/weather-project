"""Basic checks that the results-page charts build without errors."""

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


def test_charts_build_and_share_height():
    scored = make_scored()
    matrix = {
        "Tel Aviv": dict(zip(TIMES, SCORES)),
        "Haifa": dict(zip(TIMES, SCORES)),
    }
    figs = [
        photography_score_chart(
            scored, window_start="03:00", window_end="06:00", booked_time="17:00"
        ),
        city_scores_heatmap(matrix, selected_city="Tel Aviv", hour_columns=TIMES),
        temperature_chart(scored),
        rain_probability_chart(scored),
    ]
    for fig in figs:
        assert fig.layout.height == CHART_HEIGHT
        assert fig.layout.title.text == ""
        assert fig.layout.dragmode is False


def test_score_and_temperature_use_the_hour_labels():
    scored = make_scored()
    score_fig = photography_score_chart(scored)
    temp_fig = temperature_chart(scored)
    assert score_fig.layout.yaxis.range[1] > max(SCORES)
    assert temp_fig.layout.yaxis.range[1] > max(TEMPS)
