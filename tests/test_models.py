"""Tests that ForecastReport / HourlyConditions read sample JSON correctly."""

from __future__ import annotations

import json
from pathlib import Path

from photo_planner.models import ForecastReport, HourlyConditions

SAMPLE_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_forecast.json"


def _sample() -> dict:
    """Load the sample forecast JSON as a Python dict."""
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


def test_first_slot_metrics() -> None:
    slot = _sample()["list"][0]
    hour = HourlyConditions.from_slot_json(slot)
    assert hour.time_text == "2026-09-04 12:00:00"
    assert hour.temperature_c == 31.2
    assert hour.wind_speed == 5.8
    assert hour.cloud_cover == 18
    assert hour.rain_probability == 0.05
    assert hour.rain_mm == 0.0
    assert hour.icon == "02d"
    assert hour.visibility_m == 10000
    assert hour.weather_id == 801
    assert hour.wind_gust_ms is None


def test_rain_slot_reads_3h_mm() -> None:
    slot = _sample()["list"][3]
    hour = HourlyConditions.from_slot_json(slot)
    assert hour.time_text == "2026-09-04 21:00:00"
    assert hour.rain_probability == 0.61
    assert hour.rain_mm == 1.4
    assert hour.cloud_cover == 78


def test_forecast_city_and_sunset() -> None:
    report = ForecastReport.from_api_json(_sample())
    assert report.city == "Tel Aviv"
    assert report.country == "IL"
    assert report.latitude == 32.0853
    assert report.longitude == 34.7806
    assert report.sunset_unix == 1788534300
    assert len(report.hours) == 5
