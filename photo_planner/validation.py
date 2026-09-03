# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# This file checks user input before we spend an API call.
#
# WHY WE KEEP THIS SEPARATE:
# Validation (is this input usable?) is a different job from
# "talk to the internet" and from "score the weather".
# You can test these rules without a network.
#
# Person A owns this file.
# Call this from the client OR from app.py — not both with
# different rules.
# ============================================================

# WHY THIS EXISTS:
# InvalidCityError and InvalidShootTypeError are written in errors.py.
# Raising them lets app.py show a clear message instead of crashing.
from photo_planner.errors import InvalidCityError, InvalidShootTypeError  # KEEP

# WHY THIS EXISTS:
# These are the photography types the product supports in the MVP.
# Person B should use the same list in the Streamlit dropdown.
# KEEP this tuple. Add a type only if you and Dafna agree to score it.
SHOOT_TYPES = ("portrait", "sunset", "landscape")  # KEEP


def normalize_city_name(city: str) -> str:
    """
    YOUR TASK:

    `city` is whatever the user typed or selected (maybe with extra spaces).

    Return a cleaned city name, or raise InvalidCityError if it is not usable.

    Suggested checks (implement these, then add more if you want):
      - reject None / non-strings
      - strip whitespace
      - reject empty string
      - reject names that are only digits or punctuation

    Called by:
        OpenWeatherClient.get_forecast in client.py
        tests/test_validation.py

    HINT:
    "  Tel Aviv  ".strip() becomes "Tel Aviv".
    After strip, an empty string should raise InvalidCityError.
    """

    # YOUR CODE GOES HERE 👇
    # TODO (STUDENT): Clean `city` and return it, or raise InvalidCityError.

    raise NotImplementedError("Person A: implement city validation")  # DELETE LATER


def normalize_shoot_type(shoot_type: str) -> str:
    """
    YOUR TASK:

    `shoot_type` is the kind of outdoor session, for example "portrait".

    Return a cleaned value that exists in SHOOT_TYPES, or raise
    InvalidShootTypeError.

    Suggested checks:
      - strip whitespace
      - compare in lowercase so "Portrait" still works
      - reject anything not in SHOOT_TYPES

    Called by:
        scoring.py (before weights are applied)
        tests/test_validation.py
        optionally app.py

    HINT:
    shoot_type.strip().lower() is a good first line.
    Then check: if cleaned not in SHOOT_TYPES: raise InvalidShootTypeError.
    """

    # YOUR CODE GOES HERE 👇
    # TODO (STUDENT): Clean `shoot_type` and return it, or raise InvalidShootTypeError.

    raise NotImplementedError("Person A: implement shoot type validation")  # DELETE LATER
