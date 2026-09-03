# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# This file defines the "boxes" that hold weather fields the
# rest of the app needs.
#
# WHY WE KEEP THIS SEPARATE:
# The forecast API returns a large JSON object with many keys
# you do not need. This file extracts only the useful fields,
# once, for every 3-hour slot.
# scoring.py, charts.py, and app.py then read HourlyConditions
# — they never parse JSON.
#
# Person A owns this file. Freeze field names before Person B
# builds the UI. See docs/PAIR.md.
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HourlyConditions:
    """
    Weather for ONE forecast slot (the free API sends a slot every 3 hours).

    WHY THIS EXISTS:
    A dataclass is a simple class that mainly stores data.
    frozen=True means the values cannot be changed after creation —
    that keeps scoring and charts looking at the same numbers.

    Practice this mapping with data/sample_forecast.json
    before you call the live API.
    """

    # KEEP — these field names are the contract with scoring.py and charts.py.
    # If the score needs a new field, add it here first, then tell Person B.
    time_text: str          # slot["dt_txt"], example: "2026-09-04 15:00:00"
    timestamp_unix: int     # slot["dt"]
    temperature_c: float
    feels_like_c: float
    humidity: int
    wind_speed: float
    cloud_cover: int        # 0–100, from slot["clouds"]["all"]
    rain_probability: float # 0.0–1.0, from slot["pop"]  (0.4 means 40%)
    rain_mm: float          # mm in that 3-hour window; 0.0 if "rain" is missing
    description: str
    icon: str

    @classmethod
    def from_slot_json(cls, slot: dict[str, Any]) -> HourlyConditions:
        """
        YOUR TASK:

        `slot` is ONE item from payload["list"] (one 3-hour forecast).

        Map official API paths to the fields above:

            time_text        ← slot["dt_txt"]
            timestamp_unix   ← slot["dt"]
            temperature_c, feels_like_c, humidity ← slot["main"]
            wind_speed       ← slot["wind"]["speed"]
            cloud_cover      ← slot["clouds"]["all"]
            rain_probability ← slot["pop"]
            rain_mm          ← slot["rain"]["3h"] if rain exists, else 0.0
            description      ← slot["weather"][0]["description"]
            icon             ← slot["weather"][0]["icon"]

        Called by:
            ForecastReport.from_api_json (this same file)
            tests/test_models.py (uses the sample JSON, no internet)

        HINT:
        Open data/sample_forecast.json and look at the first object in "list".
        The key "3h" is a string, not a Python name. rain may be absent
        when there is no rain — .get(...) is safer than ["rain"]["3h"].
        pop is a fraction: 0.25 means 25% chance of rain, not 25.
        """

        # YOUR CODE GOES HERE 👇
        # TODO (STUDENT): Read the keys listed above from `slot`.
        # TODO (STUDENT): Return cls(...) with every field filled.

        raise NotImplementedError("Person A: parse one forecast slot")  # DELETE LATER


@dataclass(frozen=True)
class ForecastReport:
    """
    A full forecast for one city: location info + a list of hourly slots.

    WHY THIS EXISTS:
    scoring.py needs many hours, not only "now".
    Sunset time lives on the city object, not on each slot — that matters
    for sunset photography.
    """

    city: str
    country: str
    latitude: float
    longitude: float
    timezone_offset_seconds: int
    sunrise_unix: int
    sunset_unix: int
    hours: list[HourlyConditions]

    @classmethod
    def from_api_json(cls, payload: dict[str, Any]) -> ForecastReport:
        """
        YOUR TASK:

        `payload` is the JSON dict from the 5-day / 3-hour forecast API
        (or from data/sample_forecast.json).

        Map:

            city, country, coord, timezone, sunrise, sunset
                ← payload["city"]
            hours
                ← a HourlyConditions for every item in payload["list"]

        Called by:
            OpenWeatherClient.get_forecast in client.py
            tests/test_models.py

        HINT:
        You can build the list with a for-loop:
            hours = []
            for slot in payload["list"]:
                hours.append(HourlyConditions.from_slot_json(slot))
        A list comprehension does the same job in one line if you prefer.
        """

        # YOUR CODE GOES HERE 👇
        # TODO (STUDENT): Read city-level fields from payload["city"].
        # TODO (STUDENT): Turn payload["list"] into a list of HourlyConditions.
        # TODO (STUDENT): Return cls(city=..., hours=..., ...).

        raise NotImplementedError("Person A: parse the forecast JSON")  # DELETE LATER
