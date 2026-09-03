# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# This file names the errors the rest of the app can catch.
#
# WHY WE KEEP THIS SEPARATE:
# If client.py raises CityNotFoundError, app.py can show
# "City not found" with st.error(...) instead of a traceback.
#
# These classes are infrastructure (KEEP). You do not need to
# add new classes unless you need another case.
#
# Person A uses these in client.py and validation.py.
# Person B catches WeatherError (the parent) in app.py.
# ============================================================


class WeatherError(Exception):
    """Base error for anything the app wants to show the photographer."""

    # KEEP — catch this one type in app.py to cover all weather problems.


class InvalidCityError(WeatherError):
    """The user submitted an empty or invalid city name."""

    # KEEP — raised by validation.py


class InvalidShootTypeError(WeatherError):
    """The user picked a photography type the app does not support."""

    # KEEP — raised by validation.py when shoot_type is not in SHOOT_TYPES


class CityNotFoundError(WeatherError):
    """OpenWeatherMap returned 404 — city not found."""

    # KEEP — raise this in client.py when status_code is 404


class InvalidApiKeyError(WeatherError):
    """OpenWeatherMap returned 401 — missing or wrong API key."""

    # KEEP — raise this in client.py when status_code is 401


class WeatherRequestError(WeatherError):
    """Network, timeout, or unexpected HTTP status."""

    # KEEP — raise this for other failed requests
