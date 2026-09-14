"""Input checks for city name and shoot type before API or scoring calls."""

from photo_planner.errors import InvalidCityError, InvalidShootTypeError

SHOOT_TYPES = ("portrait", "event", "sunset", "landscape")

ISRAEL_CITIES = (
    "Tel Aviv",
    "Jerusalem",
    "Haifa",
    "Herzliya",
    "Eilat",
    "Netanya",
    "Caesarea",
    "Akko",
)


def normalize_city_name(city: str) -> str:
    """Return a cleaned city name, or raise InvalidCityError if it is not usable."""
    if not isinstance(city, str):
        raise InvalidCityError("City must be a string.")

    cleaned_city = city.strip()

    if not cleaned_city:
        raise InvalidCityError("City cannot be empty.")

    if not any(char.isalpha() for char in cleaned_city):
        raise InvalidCityError("City must contain letters.")

    return cleaned_city


def normalize_shoot_type(shoot_type: str) -> str:
    """Return a cleaned shoot type in SHOOT_TYPES, or raise InvalidShootTypeError."""
    if not isinstance(shoot_type, str):
        raise InvalidShootTypeError("Shoot type must be a string.")

    cleaned_type = shoot_type.strip().lower()

    if cleaned_type not in SHOOT_TYPES:
        raise InvalidShootTypeError(
            f"Shoot type must be one of: {', '.join(SHOOT_TYPES)}"
        )

    return cleaned_type
