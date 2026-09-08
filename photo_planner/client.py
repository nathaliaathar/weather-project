# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# This file talks to the OpenWeatherMap forecast API (an
# external weather service) and brings the answer back as a
# ForecastReport.
#
# An API is a way for your program to ask another program for data.
# An endpoint is the specific URL you send that request to.
#
# WHY WE KEEP THIS SEPARATE:
# app.py should not know how HTTP requests work.
# This file focuses only on: build request → send it → handle
# errors → return data.
#
# Person A owns this file. See docs/PAIR.md.
#
# IMPORTANT: we use the 5-day / 3-hour FORECAST, not "current weather".
# Photographers need several hours so we can recommend a window.
#
# Docs: https://openweathermap.org/forecast5
# GET https://api.openweathermap.org/data/2.5/forecast
#     q=<city>           city name (optional country: Tel Aviv,IL)
#     appid=<api_key>
#     units=metric       temperatures in Celsius
# ============================================================

from __future__ import annotations

import os
from typing import Any
import requests

from photo_planner.errors import InvalidApiKeyError, WeatherRequestError  # KEEP
from photo_planner.errors import CityNotFoundError
from photo_planner.validation import normalize_city_name
from photo_planner.models import ForecastReport  # KEEP

# KEEP — this is the official 5-day / 3-hour forecast endpoint (the URL you call).
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


class OpenWeatherClient:
    """
    A small helper that stores the API key and fetches a forecast.

    WHY THIS EXISTS:
    app.py creates one client, then calls get_forecast(city).
    Keeping the key and timeout here means the Streamlit page stays simple.
    """

    def __init__(self, api_key: str | None = None, timeout_seconds: float = 10.0) -> None:
        # KEEP — reading the key is infrastructure; fetching weather is your task.
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.timeout_seconds = timeout_seconds
        if not self.api_key:
            raise InvalidApiKeyError(
                "Missing OPENWEATHER_API_KEY. Copy .env.example to .env "
                "or set Streamlit secrets."
            )

    def get_forecast(self, city: str, units: str = "metric") -> ForecastReport:
        """
        YOUR TASK:

        `city` is the name the photographer chose, for example "Tel Aviv".
        `units` should stay "metric" so temperatures arrive in Celsius.

        This function should:
          1. Clean the city name (validation.py)
          2. Send a GET request to FORECAST_URL
          3. Turn HTTP failures into errors from errors.py
          4. Parse JSON into a ForecastReport
          5. Return that ForecastReport to app.py

        Called by:
            app.py (Person B), after the photographer clicks "Plan shoot"

        Do not score the weather here. Only return data or raise an error.
        Scoring belongs in scoring.py — that is the product.
        """

        # TODO (STUDENT): Normalize `city` with normalize_city_name(...).

        # TODO (STUDENT): Build the query params (or call self._params).

        # TODO (STUDENT): Send requests.get(...) with timeout=self.timeout_seconds.

        # TODO (STUDENT): If status is 401 → raise InvalidApiKeyError.
        # TODO (STUDENT): If status is 404 → raise CityNotFoundError.
        # TODO (STUDENT): If status is not 200 → raise WeatherRequestError.

        # TODO (STUDENT): Convert the response to JSON and return
        #                 ForecastReport.from_api_json(...).

        # HINT:
        # JSON is the nested dictionary the API sends back.
        # response.json() turns that text into a Python dict.
        # The forecast payload has payload["list"] (many hours)
        # and payload["city"] (name, sunrise, sunset).

        clean_city = normalize_city_name(city)

        params = self._params(clean_city, units)

        try:
            response = requests.get(
                FORECAST_URL,
                params=params,
                timeout=self.timeout_seconds,
            )
        except requests.exceptions.SSLError as err:
            raise WeatherRequestError(
                "Could not verify the weather site's security certificate (SSL). "
                "On Windows, install project deps with: pip install -r requirements.txt"
            ) from err
        except requests.exceptions.RequestException as err:
            raise WeatherRequestError(
                f"Could not reach the weather service: {err}"
            ) from err

        if response.status_code == 401:
            raise InvalidApiKeyError(
                "Invalid OpenWeather API key. "
                "Check .env (OPENWEATHER_API_KEY) or wait if the key is brand new."
            )

        if response.status_code == 404:
            raise CityNotFoundError(f"City not found: {clean_city}")

        if response.status_code != 200:
            raise WeatherRequestError(
                f"Weather request failed with status code {response.status_code}"
            )

        payload = response.json()

        return ForecastReport.from_api_json(payload)

    def _params(self, city: str, units: str) -> dict[str, Any]:
        """
        YOUR TASK:

        Return the query string as a dictionary:
            {"q": city, "appid": self.api_key, "units": units}

        WHY THIS EXISTS:
        Keeping params in a tiny function makes them easier to test
        without calling the live API.

        Called by:
            get_forecast (in this same file)
        """

        # TODO (STUDENT): Return a dict with keys q, appid, and units.

        return {
            "q": city,
            "appid": self.api_key,
            "units": units
        }
