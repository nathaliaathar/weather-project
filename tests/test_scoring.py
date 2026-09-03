# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# These tests check the Photography Score helpers.
# They use data/sample_forecast.json — no live API.
#
# There is no single "correct" score. These tests only check
# the SHAPE of your functions (date filter, 0–100 range,
# window format). Your weights can still be your own.
#
# Person A: implement scoring.py, then remove each skip.
# ============================================================

from __future__ import annotations

import json
from pathlib import Path

import pytest

from photo_planner.models import ForecastReport  # KEEP
from photo_planner.scoring import (  # KEEP
    best_shooting_window,
    hours_on_date,
    photography_score,
    score_forecast,
)

SAMPLE_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_forecast.json"  # KEEP


def _forecast() -> ForecastReport:
    payload = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    return ForecastReport.from_api_json(payload)


# TODO (STUDENT): After hours_on_date works, delete this skip.
@pytest.mark.skip(reason="Remove this skip after implementing hours_on_date")
def test_hours_on_date_drops_other_days() -> None:
    day = hours_on_date(_forecast(), "2026-09-04")
    assert len(day) == 4
    assert all(hour.time_text.startswith("2026-09-04") for hour in day)


# TODO (STUDENT): After photography_score works, delete this skip.
@pytest.mark.skip(reason="Remove this skip after implementing photography_score")
def test_score_is_between_0_and_100() -> None:
    hour = _forecast().hours[0]
    score = photography_score(hour, "portrait", sunset_unix=_forecast().sunset_unix)
    assert 0 <= score <= 100


# TODO (STUDENT): After score_forecast works, delete this skip.
@pytest.mark.skip(reason="Remove this skip after implementing score_forecast")
def test_score_forecast_returns_pairs_for_that_day() -> None:
    scored = score_forecast(_forecast(), "portrait", "2026-09-04")
    assert len(scored) == 4
    hour, score = scored[0]
    assert hour.time_text.startswith("2026-09-04")
    assert 0 <= score <= 100


# TODO (STUDENT): After best_shooting_window works, delete this skip.
@pytest.mark.skip(reason="Remove this skip after implementing best_shooting_window")
def test_best_window_has_start_end_and_score() -> None:
    scored = score_forecast(_forecast(), "portrait", "2026-09-04")
    window = best_shooting_window(scored)
    assert window is not None
    start, end, score = window
    assert isinstance(start, str) and isinstance(end, str)
    assert 0 <= score <= 100
