# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# This file is the PRODUCT.
#
# Weather data is only the input. Here you analyse conditions
# the way a photographer would, then return:
#   - a Photography Score (0–100) for each hour
#   - the best shooting window
#
# WHY WE KEEP THIS SEPARATE:
# client.py talks to the internet.
# models.py unpacks JSON.
# This file thinks. app.py only displays the numbers you return.
#
# Person A implements the functions.
# You and Dafna should DECIDE the weights together first —
# there is no single "correct" formula. Write down why rain
# matters more for portrait than for landscape, then code it.
#
# Do not start this file on day 1. First parse the forecast.
# ============================================================

from __future__ import annotations

# WHY THIS EXISTS:
# HourlyConditions and ForecastReport are written in models.py.
# You read fields like hour.wind_speed — you do not parse JSON here.
from photo_planner.models import ForecastReport, HourlyConditions  # KEEP

# WHY THIS EXISTS:
# SHOOT_TYPES and normalize_shoot_type live in validation.py
# so "Portrait" and "portrait" use the same list of types.
# Uncomment when you call normalize_shoot_type inside photography_score.
# from photo_planner.validation import SHOOT_TYPES, normalize_shoot_type


# ------------------------------------------------------------
# STUDENT TASK 1: Decide weights with Dafna (on paper first)
# ------------------------------------------------------------
# YOUR CODE GOES HERE 👇
#
# Each shoot type cares about weather differently:
#   portrait  → rain and wind often ruin hair, clothes, and comfort
#   sunset    → cloud cover and closeness to sunset often matter more
#   landscape → you may tolerate wind, but rain / visibility still matter
#
# HINT:
# One simple design is four numbers per type that add up to 1.0:
#   rain, wind, temperature, clouds
# You may add a fifth factor (for example "hours from sunset") later.
#
# TODO (STUDENT): Replace None with weights you both agree on.
# DELETE LATER: the None placeholders, once real numbers are in.

SHOOT_WEIGHTS = {
    "portrait": {
        "rain": None,
        "wind": None,
        "temperature": None,
        "clouds": None,
    },
    "sunset": {
        "rain": None,
        "wind": None,
        "temperature": None,
        "clouds": None,
    },
    "landscape": {
        "rain": None,
        "wind": None,
        "temperature": None,
        "clouds": None,
    },
}


def photography_score(
    hour: HourlyConditions,
    shoot_type: str,
    sunset_unix: int | None = None,
) -> float:
    """
    YOUR TASK:

    `hour` is one 3-hour slot (temperature, wind, clouds, rain chance, ...).
    `shoot_type` is "portrait", "sunset", or "landscape".
    `sunset_unix` is the city's sunset time (useful for sunset shoots).

    Return a Photography Score from 0 to 100 (higher = better to shoot).

    Think like a photographer, not like a weather app:
      - very low rain chance → usually good
      - strong wind → often bad for portrait
      - comfortable temperature → usually good
      - cloud cover: "good" depends on the shoot type
      - for sunset: a slot close to sunset may deserve extra points

    Called by:
        score_forecast (this same file)
        tests/test_scoring.py

    HINT:
    1. Turn EACH weather field into a 0–100 "goodness" number.
       Example question: if rain_probability is 0.9, should rain_goodness
       be high or low?
    2. Combine those numbers using SHOOT_WEIGHTS[shoot_type].
    3. Clip the final result so it stays between 0 and 100.

    Do not copy a formula from the internet. The interesting part of this
    project is YOUR rule set. Write a short comment above each factor
    explaining the rule in one sentence.
    """

    # YOUR CODE GOES HERE 👇
    # TODO (STUDENT): Convert rain, wind, temperature, clouds into goodness scores.
    # TODO (STUDENT): Combine them with SHOOT_WEIGHTS for this shoot_type.
    # TODO (STUDENT): Return a float between 0 and 100.
    #
    # OPTIONAL: use sunset_unix for sunset shoots (hours away from sunset).

    raise NotImplementedError("Person A: implement photography_score")  # DELETE LATER


def hours_on_date(forecast: ForecastReport, shoot_date: str) -> list[HourlyConditions]:
    """
    YOUR TASK:

    `forecast` has ~40 slots across 5 days.
    `shoot_date` is the day the photographer booked, as "YYYY-MM-DD"
    (example: "2026-09-04").

    Return only the HourlyConditions whose time_text starts with that date.

    Called by:
        score_forecast, and/or app.py

    HINT:
    hour.time_text looks like "2026-09-04 15:00:00".
    The date is the part before the space. A string startswith(...) check
    is enough for the MVP.
    """

    # YOUR CODE GOES HERE 👇
    # TODO (STUDENT): Filter forecast.hours to the chosen date and return the list.

    raise NotImplementedError("Person A: keep only hours on shoot_date")  # DELETE LATER


def score_forecast(
    forecast: ForecastReport,
    shoot_type: str,
    shoot_date: str,
) -> list[tuple[HourlyConditions, float]]:
    """
    YOUR TASK:

    Score every remaining hour on `shoot_date` for this `shoot_type`.

    Return a list of (hour, score) pairs, in time order.

    Called by:
        app.py (Person B), after get_forecast succeeds
        tests/test_scoring.py

    HINT:
    1. day_hours = hours_on_date(forecast, shoot_date)
    2. For each hour, call photography_score(hour, shoot_type, forecast.sunset_unix)
    3. Append (hour, score) to a list and return it
    """

    # YOUR CODE GOES HERE 👇
    # TODO (STUDENT): Filter by date, score each hour, return (hour, score) pairs.

    raise NotImplementedError("Person A: score every hour on the shoot date")  # DELETE LATER


def best_shooting_window(
    scored_hours: list[tuple[HourlyConditions, float]],
) -> tuple[str, str, float] | None:
    """
    YOUR TASK:

    `scored_hours` is the list from score_forecast.

    Return (start_time, end_time, best_score) for the best period, or None
    if the list is empty.

    MVP (good enough):
      Pick the single 3-hour slot with the highest score.
      Use that slot's clock time as the start, and three hours later as the end.
      Example: best slot "18:00:00" → ("18:00", "21:00", 94.0)

    OPTIONAL later:
      If two neighbouring slots are both high, merge them into a longer window
      (closer to "Best Shooting Window: 17:50–19:05").
      The free API only gives 3-hour steps, so exact minutes are an estimate.

    Called by:
        app.py, to print the recommendation

    HINT:
    max(scored_hours, key=...) can find the pair with the highest score.
    hour.time_text[-8:-3] is one way to get "18:00" from
    "2026-09-04 18:00:00" — or split on space and take [1][:5].
    """

    # YOUR CODE GOES HERE 👇
    # TODO (STUDENT): Find the highest score and return a start/end window.

    raise NotImplementedError("Person A: recommend the best shooting window")  # DELETE LATER


# ------------------------------------------------------------
# OPTIONAL — Phase 2 (do this AFTER the single-city app works)
# ------------------------------------------------------------
# The photographer asks: "I want to shoot sunset tomorrow. Where should I go?"
# You would call get_forecast for Tel Aviv, Haifa, Herzliya, score each city,
# and return the winner.
#
# def compare_locations(
#     forecasts: list[ForecastReport],
#     shoot_type: str,
#     shoot_date: str,
# ) -> tuple[str, float]:
#     ...
#
# Do not implement this until the one-city flow (score + charts) works.
