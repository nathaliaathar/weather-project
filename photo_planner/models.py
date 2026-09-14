"""Data models that turn forecast JSON into typed objects used by the rest of the app."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HourlyConditions:
    """Weather for one forecast slot (OpenWeather free API: every 3 hours)."""

    time_text: str          # slot["dt_txt"], example: "2026-09-04 15:00:00"
    timestamp_unix: int     # slot["dt"] (UTC)
    temperature_c: float
    feels_like_c: float
    humidity: int
    wind_speed: float       # m/s, from slot["wind"]["speed"]
    cloud_cover: int        # 0–100, from slot["clouds"]["all"]
    rain_probability: float # 0.0–1.0, from slot["pop"]  (0.4 means 40%)
    rain_mm: float          # mm in that 3-hour window; 0.0 if "rain" is missing
    description: str
    icon: str
    # Optional provider fields. None means missing — never treat as 0.
    wind_gust_ms: float | None = None       # m/s, slot["wind"]["gust"]
    visibility_m: float | None = None       # metres, slot["visibility"]
    weather_id: int | None = None           # slot["weather"][0]["id"]

    @classmethod
    def from_slot_json(cls, slot: dict[str, Any]) -> HourlyConditions:
        """Build one HourlyConditions from a single item in payload["list"]."""
        wind = slot.get("wind") or {}
        weather0 = (slot.get("weather") or [{}])[0]
        gust = wind.get("gust")
        visibility = slot.get("visibility")

        return cls(
            time_text=slot["dt_txt"],
            timestamp_unix=slot["dt"],
            temperature_c=slot["main"]["temp"],
            feels_like_c=slot["main"]["feels_like"],
            humidity=slot["main"]["humidity"],
            wind_speed=wind["speed"],
            cloud_cover=slot["clouds"]["all"],
            rain_probability=slot["pop"],
            rain_mm=slot.get("rain", {}).get("3h", 0.0),
            description=weather0.get("description", ""),
            icon=weather0.get("icon", ""),
            wind_gust_ms=float(gust) if gust is not None else None,
            visibility_m=float(visibility) if visibility is not None else None,
            weather_id=weather0.get("id"),
        )


@dataclass(frozen=True)
class ForecastReport:
    """Full forecast for one city: location info plus a list of hourly slots."""

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
        """Build a ForecastReport from the 5-day / 3-hour forecast JSON payload."""
        city_data = payload["city"]

        hours = []
        for slot in payload["list"]:
            hours.append(HourlyConditions.from_slot_json(slot))

        return cls(
            city=city_data["name"],
            country=city_data["country"],
            latitude=city_data["coord"]["lat"],
            longitude=city_data["coord"]["lon"],
            timezone_offset_seconds=city_data["timezone"],
            sunrise_unix=city_data["sunrise"],
            sunset_unix=city_data["sunset"],
            hours=hours,
        )
