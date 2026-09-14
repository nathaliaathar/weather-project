"""OpenWeatherMap 5-day / 3-hour forecast client.

Docs: https://openweathermap.org/forecast5
GET https://api.openweathermap.org/data/2.5/forecast
"""

from __future__ import annotations

import os
from typing import Any

import requests

from photo_planner.errors import CityNotFoundError, InvalidApiKeyError, WeatherRequestError
from photo_planner.models import ForecastReport
from photo_planner.validation import normalize_city_name

FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


class OpenWeatherClient:
    """Fetches a ForecastReport for a city using an OpenWeatherMap API key."""

    def __init__(self, api_key: str | None = None, timeout_seconds: float = 10.0) -> None:
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.timeout_seconds = timeout_seconds
        if not self.api_key:
            raise InvalidApiKeyError(
                "Missing OPENWEATHER_API_KEY. Copy .env.example to .env "
                "or set Streamlit secrets."
            )

    def get_forecast(self, city: str, units: str = "metric") -> ForecastReport:
        """Fetch and parse the forecast for `city` (temperatures in Celsius by default)."""
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
        """Query parameters for the forecast endpoint."""
        return {
            "q": city,
            "appid": self.api_key,
            "units": units,
        }
