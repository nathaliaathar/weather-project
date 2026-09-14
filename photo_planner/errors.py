"""Named errors the UI can catch and show as clear messages."""


class WeatherError(Exception):
    """Base error for anything the app wants to show the photographer."""


class InvalidCityError(WeatherError):
    """The user submitted an empty or invalid city name."""


class InvalidShootTypeError(WeatherError):
    """The user picked a photography type the app does not support."""


class CityNotFoundError(WeatherError):
    """OpenWeatherMap returned 404 — city not found."""


class InvalidApiKeyError(WeatherError):
    """OpenWeatherMap returned 401 — missing or wrong API key."""


class WeatherRequestError(WeatherError):
    """Network, timeout, or unexpected HTTP status."""
