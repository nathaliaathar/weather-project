"""Tests for city-name and shoot-type validation (no live API calls)."""

import pytest

from photo_planner.errors import InvalidCityError, InvalidShootTypeError
from photo_planner.validation import normalize_city_name, normalize_shoot_type


def test_strips_whitespace() -> None:
    assert normalize_city_name("  Tel Aviv  ") == "Tel Aviv"


def test_rejects_empty() -> None:
    with pytest.raises(InvalidCityError):
        normalize_city_name("   ")


def test_shoot_type_lowercase() -> None:
    assert normalize_shoot_type("Portrait") == "portrait"
    assert normalize_shoot_type("Event") == "event"


def test_rejects_unknown_shoot_type() -> None:
    with pytest.raises(InvalidShootTypeError):
        normalize_shoot_type("wedding-drone")
