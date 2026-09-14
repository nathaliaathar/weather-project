"""Tests for Photography Score: weights, bounds, labels, and session selection."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from photo_planner.models import ForecastReport, HourlyConditions
from photo_planner.scoring import (
    RAIN_CAP_BASE,
    RAIN_CAP_SPAN,
    SHOOT_WEIGHTS,
    STATUS_NOT_RECOMMENDED,
    STATUS_UNAVAILABLE,
    HourScore,
    best_shooting_window,
    condition_label,
    display_score,
    hours_on_date,
    photography_score,
    photography_score_breakdown,
    score_forecast,
    score_session,
    weights_sum_to_one,
)
from photo_planner.validation import normalize_shoot_type

SAMPLE_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_forecast.json"

TEL_AVIV_LAT = 32.0853
TEL_AVIV_LON = 34.7806


def _forecast() -> ForecastReport:
    payload = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    return ForecastReport.from_api_json(payload)


def _hour(**overrides) -> HourlyConditions:
    values: dict = {
        "time_text": "2026-09-04 18:00:00",
        "timestamp_unix": 1788540000,
        "temperature_c": 22.0,
        "feels_like_c": 22.0,
        "humidity": 50,
        "wind_speed": 2.0,
        "cloud_cover": 25,
        "rain_probability": 0.0,
        "rain_mm": 0.0,
        "description": "clear sky",
        "icon": "01d",
        "wind_gust_ms": None,
        "visibility_m": 10000.0,
        "weather_id": 800,
    }
    values.update(overrides)
    return HourlyConditions(**values)


def _score_kw() -> dict:
    forecast = _forecast()
    return {
        "sunset_unix": forecast.sunset_unix,
        "latitude": forecast.latitude,
        "longitude": forecast.longitude,
        "timezone_offset_seconds": forecast.timezone_offset_seconds,
    }


def _hour_score(
    time_text: str,
    score: float,
    *,
    rain_suit: float = 1.0,
    wind_suit: float = 1.0,
    comfort_suit: float = 1.0,
    status: str = "ok",
    sun_height: float | None = None,
    is_afternoon: bool | None = None,
) -> HourScore:
    caps = {
        "light": 100.0,
        "rain": 35.0 + 65.0 * rain_suit,
        "wind": 35.0 + 65.0 * wind_suit,
        "comfort": 40.0 + 60.0 * comfort_suit,
    }
    hour = _hour(time_text=time_text, timestamp_unix=0)
    return HourScore(
        hour=hour,
        score=score,
        shoot_type="portrait",
        status=status,
        light=1.0,
        rain=rain_suit,
        wind=wind_suit,
        comfort=comfort_suit,
        visibility=1.0,
        weights=dict(SHOOT_WEIGHTS["portrait"]),
        caps=caps,
        sun_height=sun_height,
        is_afternoon=is_afternoon,
    )


def test_hours_on_date_drops_other_days() -> None:
    day = hours_on_date(_forecast(), "2026-09-04")
    assert len(day) == 4
    assert all(hour.time_text.startswith("2026-09-04") for hour in day)


def test_score_is_between_0_and_100() -> None:
    hour = _forecast().hours[0]
    score = photography_score(hour, "portrait", **_score_kw())
    assert score is not None
    assert 0 <= score <= 100


def test_score_forecast_returns_pairs_for_that_day() -> None:
    scored = score_forecast(_forecast(), "portrait", "2026-09-04")
    assert len(scored) == 4
    hour, score = scored[0]
    assert hour.time_text.startswith("2026-09-04")
    assert score is not None
    assert 0 <= score <= 100


def test_best_window_has_start_end_and_score() -> None:
    scored = score_forecast(_forecast(), "portrait", "2026-09-04")
    window = best_shooting_window(scored)
    assert window is not None
    assert isinstance(window.start, str) and isinstance(window.end, str)
    assert 0 <= window.score <= 100
    assert window.score == display_score(window.raw_score)


def test_score_breakdown_matches_photography_score() -> None:
    hour = _forecast().hours[0]
    kwargs = _score_kw()
    score = photography_score(hour, "portrait", **kwargs)
    breakdown = photography_score_breakdown(hour, "portrait", **kwargs)
    assert breakdown.score == score
    assert score is not None
    for value in (
        breakdown.light,
        breakdown.rain,
        breakdown.wind,
        breakdown.comfort,
        breakdown.visibility,
    ):
        assert value is not None
        assert 0 <= value <= 1
    assert abs(sum(breakdown.weights.values()) - 1.0) < 1e-9
    assert "portrait" in breakdown.top_factors_sentence().lower()
    assert breakdown.main_drag_sentence()


def test_weight_totals_are_100_percent() -> None:
    assert weights_sum_to_one()
    for name, weights in SHOOT_WEIGHTS.items():
        assert abs(sum(weights.values()) - 1.0) < 1e-9, name


def test_event_is_a_supported_shoot_type() -> None:
    assert normalize_shoot_type("Event") == "event"
    hour = _hour()
    score = photography_score(hour, "event", **_score_kw())
    assert score is not None
    assert 0 <= score <= 100


def test_display_score_rounds_half_upward() -> None:
    assert display_score(86.5) == 87
    assert display_score(86.4) == 86
    assert display_score(0.5) == 1
    assert display_score(99.5) == 100
    assert display_score(100.0) == 100


def test_label_boundaries_use_displayed_score() -> None:
    assert condition_label(80) == "Good conditions"
    assert condition_label(79) == "Fair conditions"
    assert condition_label(60) == "Fair conditions"
    assert condition_label(59) == "Challenging conditions"
    assert condition_label(0) == "Challenging conditions"
    assert condition_label(100) == "Good conditions"
    # 79.5 displays as 80, so the label follows the integer.
    assert display_score(79.5) == 80
    assert condition_label(79.5) == "Good conditions"
    assert condition_label(None, STATUS_UNAVAILABLE) == "Unavailable"
    assert condition_label(40, STATUS_NOT_RECOMMENDED) == "Not recommended"


def test_sunset_scores_evening_not_dry_midday() -> None:
    kwargs = _score_kw()
    midday = _hour(
        time_text="2026-09-04 12:00:00",
        timestamp_unix=1788518400,
        rain_probability=0.0,
        rain_mm=0.0,
        cloud_cover=10,
    )
    evening = _hour(
        time_text="2026-09-04 18:00:00",
        timestamp_unix=1788540000,
        rain_probability=0.0,
        rain_mm=0.0,
        cloud_cover=25,
    )
    morning = _hour(
        time_text="2026-09-04 09:00:00",
        timestamp_unix=1788507600,
        rain_probability=0.0,
        rain_mm=0.0,
        cloud_cover=25,
    )
    midday_b = photography_score_breakdown(midday, "sunset", **kwargs)
    evening_b = photography_score_breakdown(evening, "sunset", **kwargs)
    morning_b = photography_score_breakdown(morning, "sunset", **kwargs)
    assert evening_b.light is not None and midday_b.light is not None
    assert evening_b.light > midday_b.light
    assert evening_b.score is not None and midday_b.score is not None
    assert evening_b.score > midday_b.score
    assert morning_b.light is not None
    assert evening_b.light > morning_b.light


def test_rain_and_wind_penalties_reduce_score() -> None:
    kwargs = _score_kw()
    dry_calm = _hour(
        time_text="2026-09-04 12:00:00",
        timestamp_unix=1788518400,
        rain_probability=0.05,
        rain_mm=0.0,
        wind_speed=2.0,
    )
    wet = _hour(
        time_text="2026-09-04 12:00:00",
        timestamp_unix=1788518400,
        rain_probability=0.80,
        rain_mm=3.5,
        wind_speed=2.0,
    )
    windy = _hour(
        time_text="2026-09-04 12:00:00",
        timestamp_unix=1788518400,
        rain_probability=0.05,
        rain_mm=0.0,
        wind_speed=10.0,
        wind_gust_ms=14.0,
    )
    dry_score = photography_score(dry_calm, "portrait", **kwargs)
    wet_score = photography_score(wet, "portrait", **kwargs)
    wind_score = photography_score(windy, "portrait", **kwargs)
    assert dry_score is not None and wet_score is not None and wind_score is not None
    assert wet_score < dry_score
    assert wind_score < dry_score
    wet_b = photography_score_breakdown(wet, "portrait", **kwargs)
    wind_b = photography_score_breakdown(windy, "portrait", **kwargs)
    dry_b = photography_score_breakdown(dry_calm, "portrait", **kwargs)
    assert wet_b.rain < dry_b.rain
    assert wind_b.wind < dry_b.wind


def test_hourly_caps_block_compensation() -> None:
    kwargs = _score_kw()
    # Excellent light/comfort cannot hide a washout.
    washout = _hour(rain_probability=1.0, rain_mm=8.0, wind_speed=1.5, cloud_cover=20)
    breakdown = photography_score_breakdown(washout, "landscape", **kwargs)
    assert breakdown.score is not None
    assert breakdown.rain is not None
    rain_cap = RAIN_CAP_BASE + RAIN_CAP_SPAN * breakdown.rain
    assert breakdown.score <= rain_cap + 1e-9
    assert breakdown.score < 50


def test_missing_visibility_is_unavailable_not_zero() -> None:
    hour = _hour(visibility_m=None)
    breakdown = photography_score_breakdown(hour, "portrait", **_score_kw())
    assert breakdown.status == STATUS_UNAVAILABLE
    assert breakdown.score is None
    assert photography_score(hour, "portrait", **_score_kw()) is None


def test_missing_location_is_unavailable() -> None:
    hour = _hour()
    breakdown = photography_score_breakdown(hour, "portrait", sunset_unix=1)
    assert breakdown.status == STATUS_UNAVAILABLE
    assert breakdown.score is None


def test_hazard_is_not_recommended_not_a_zero_score() -> None:
    hour = _hour(weather_id=201, description="thunderstorm")
    breakdown = photography_score_breakdown(hour, "event", **_score_kw())
    assert breakdown.status == STATUS_NOT_RECOMMENDED
    assert breakdown.score is not None
    assert breakdown.score > 0
    assert condition_label(breakdown.score, breakdown.status) == "Not recommended"


def test_complete_session_beats_a_single_peak_hour() -> None:
    """A 95 next to a 40 should lose to a steady 78–80 window."""
    hours = [
        _hour_score("2026-09-04 12:00:00", 95.0, rain_suit=1.0),
        _hour_score("2026-09-04 15:00:00", 40.0, rain_suit=0.10),
        _hour_score("2026-09-04 18:00:00", 78.0, rain_suit=1.0),
        _hour_score("2026-09-04 21:00:00", 80.0, rain_suit=1.0),
    ]
    window = best_shooting_window(hours, duration_hours=6.0)
    assert window is not None
    assert window.start == "18:00"
    assert window.end == "00:00"
    peak = score_session(
        hours,
        datetime.strptime("2026-09-04 12:00", "%Y-%m-%d %H:%M"),
        duration_hours=6.0,
    )
    assert peak is not None
    assert window.raw_score > peak.raw_score


def test_best_window_skips_pre_sunrise_even_if_score_is_higher() -> None:
    """A strong pre-dawn slot must not beat a weaker post-sunrise window."""
    hours = [
        _hour_score(
            "2026-09-04 03:00:00",
            99.0,
            sun_height=-25.0,
            is_afternoon=False,
        ),
        _hour_score(
            "2026-09-04 06:00:00",
            97.0,
            sun_height=-4.0,
            is_afternoon=False,
        ),
        _hour_score(
            "2026-09-04 09:00:00",
            70.0,
            sun_height=35.0,
            is_afternoon=False,
        ),
        _hour_score(
            "2026-09-04 12:00:00",
            68.0,
            sun_height=55.0,
            is_afternoon=False,
        ),
    ]
    window = best_shooting_window(hours, duration_hours=3.0)
    assert window is not None
    assert window.start == "09:00"
    assert window.end == "12:00"


def test_best_window_allows_evening_after_sunset() -> None:
    """Dusk (sun below horizon in the afternoon) remains eligible."""
    hours = [
        _hour_score(
            "2026-09-04 12:00:00",
            50.0,
            sun_height=55.0,
            is_afternoon=False,
        ),
        _hour_score(
            "2026-09-04 18:00:00",
            88.0,
            sun_height=-2.0,
            is_afternoon=True,
        ),
    ]
    window = best_shooting_window(hours, duration_hours=3.0)
    assert window is not None
    assert window.start == "18:00"
