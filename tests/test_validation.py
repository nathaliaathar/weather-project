# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# These tests check city-name and shoot-type cleaning.
# They do NOT call the live API.
#
# Person A: implement the functions in validation.py, then
# remove each @pytest.mark.skip when that test should run.
# ============================================================

import pytest

# WHY THIS EXISTS:
# These errors are written in errors.py.
from photo_planner.errors import InvalidCityError, InvalidShootTypeError  # KEEP

# WHY THIS EXISTS:
# normalize_city_name and normalize_shoot_type are written in validation.py.
from photo_planner.validation import normalize_city_name, normalize_shoot_type  # KEEP


# TODO (STUDENT): After normalize_city_name strips spaces, delete this skip.
#@pytest.mark.skip(reason="Remove this skip after implementing normalize_city_name")
def test_strips_whitespace() -> None:
    assert normalize_city_name("  Tel Aviv  ") == "Tel Aviv"


# TODO (STUDENT): After empty names raise InvalidCityError, delete this skip.
#@pytest.mark.skip(reason="Remove this skip after implementing normalize_city_name")
def test_rejects_empty() -> None:
    with pytest.raises(InvalidCityError):
        normalize_city_name("   ")


# TODO (STUDENT): After normalize_shoot_type works, delete this skip.
#@pytest.mark.skip(reason="Remove this skip after implementing normalize_shoot_type")
def test_shoot_type_lowercase() -> None:
    assert normalize_shoot_type("Portrait") == "portrait"
    assert normalize_shoot_type("Event") == "event"


# TODO (STUDENT): After unknown types raise InvalidShootTypeError, delete this skip.
#@pytest.mark.skip(reason="Remove this skip after implementing normalize_shoot_type")
def test_rejects_unknown_shoot_type() -> None:
    with pytest.raises(InvalidShootTypeError):
        normalize_shoot_type("wedding-drone")
