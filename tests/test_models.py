# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# These tests check that ForecastReport / HourlyConditions read
# the sample JSON correctly. They do NOT call the live API.
#
# WHY TESTS EXIST:
# You can run `pytest` after changing models.py and know if the
# mapping still matches data/sample_forecast.json.
#
# Person A: implement from_slot_json and from_api_json, then
# remove the @pytest.mark.skip line above each test you are ready for.
# ============================================================

from __future__ import annotations

import json
from pathlib import Path

import pytest

# WHY THIS EXISTS:
# HourlyConditions and ForecastReport are written in photo_planner/models.py.
from photo_planner.models import ForecastReport, HourlyConditions  # KEEP

SAMPLE_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_forecast.json"  # KEEP


def _sample() -> dict:
    """Load the practice JSON file as a Python dict."""
    # KEEP — tests should use the sample file, not the internet.
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


# TODO (STUDENT): After from_slot_json works, delete the skip marker on this test.
#@pytest.mark.skip(reason="Remove this skip after implementing from_slot_json")
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


# TODO (STUDENT): After from_slot_json handles missing/present rain, delete this skip.
#@pytest.mark.skip(reason="Remove this skip after implementing from_slot_json")
def test_rain_slot_reads_3h_mm() -> None:
    slot = _sample()["list"][3]
    hour = HourlyConditions.from_slot_json(slot)
    assert hour.time_text == "2026-09-04 21:00:00"
    assert hour.rain_probability == 0.61
    assert hour.rain_mm == 1.4
    assert hour.cloud_cover == 78


# TODO (STUDENT): After from_api_json works, delete the skip marker on this test.
#@pytest.mark.skip(reason="Remove this skip after implementing from_api_json")
def test_forecast_city_and_sunset() -> None:
    report = ForecastReport.from_api_json(_sample())
    assert report.city == "Tel Aviv"
    assert report.country == "IL"
    assert report.latitude == 32.0853
    assert report.longitude == 34.7806
    assert report.sunset_unix == 1788534300
    assert len(report.hours) == 5
