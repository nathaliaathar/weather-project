"""Render the four result charts to PNG so we can check nothing is cut off."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from photo_planner.charts import (  # noqa: E402
    CHART_HEIGHT,
    city_scores_heatmap,
    photography_score_chart,
    rain_probability_chart,
    temperature_chart,
)
from photo_planner.models import HourlyConditions  # noqa: E402

OUT = Path(__file__).resolve().parent / "preview"
OUT.mkdir(exist_ok=True)

# Card width on a 1680px page: left column + gaps ≈ 560px per chart card.
CARD_WIDTH = 560

TIMES = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
TEMPS = [26.0, 24.3, 26.7, 29.7, 32.2, 30.3, 28.7, 27.2]
SCORES = [29.0, 81.0, 81.0, 59.0, 60.0, 70.0, 29.0, 29.0]
RAIN = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

BASE_UNIX = 1788486000


def make_hours() -> list[tuple[HourlyConditions, float]]:
    pairs = []
    for i, clock in enumerate(TIMES):
        hour = HourlyConditions(
            time_text=f"2026-09-11 {clock}:00",
            timestamp_unix=BASE_UNIX + i * 10800,
            temperature_c=TEMPS[i],
            feels_like_c=TEMPS[i],
            humidity=55,
            wind_speed=3.0,
            cloud_cover=20,
            rain_probability=RAIN[i],
            rain_mm=0.0,
            description="clear sky",
            icon="01d",
            visibility_m=10000.0,
            weather_id=800,
        )
        pairs.append((hour, SCORES[i]))
    return pairs


def city_matrix() -> dict[str, dict[str, float]]:
    cities = [
        "Tel Aviv",
        "Jerusalem",
        "Haifa",
        "Herzliya",
        "Eilat",
        "Netanya",
        "Caesarea",
        "Akko",
    ]
    matrix = {}
    for row, name in enumerate(cities):
        matrix[name] = {
            clock: (SCORES[col] + row) % 100 for col, clock in enumerate(TIMES)
        }
    return matrix


def save(fig, name: str) -> None:
    path = OUT / f"{name}.png"
    fig.write_image(str(path), width=CARD_WIDTH, height=CHART_HEIGHT, scale=2)
    print("wrote", path)


def main() -> None:
    hours = make_hours()
    save(
        photography_score_chart(
            hours, window_start="03:00", window_end="06:00", booked_time="17:00"
        ),
        "score",
    )
    save(
        city_scores_heatmap(
            city_matrix(), selected_city="Tel Aviv", hour_columns=TIMES
        ),
        "heatmap",
    )
    save(temperature_chart(hours), "temperature")
    save(rain_probability_chart(hours), "rain")


if __name__ == "__main__":
    main()
