"""Photography Score (0–100) and best shooting window from forecast hours.

87 means suitability 87 / 100, not "87% chance of a good shoot".
Missing data → status "unavailable". Dangerous weather → "not_recommended".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import math

from photo_planner.models import ForecastReport, HourlyConditions
from photo_planner.validation import normalize_shoot_type

# The free API sends one slot every 3 hours. Rain mm is for that 3h window.
SLOT_HOURS = 3
SESSION_HOURS = 3

STATUS_OK = "ok"
STATUS_UNAVAILABLE = "unavailable"
STATUS_NOT_RECOMMENDED = "not_recommended"

FACTOR_NAMES = ("light", "rain", "wind", "comfort", "visibility")
FACTOR_LABELS = {
    "light": "Light",
    "rain": "Rain",
    "wind": "Wind",
    "comfort": "Comfort",
    "visibility": "Visibility",
}

# Decimal weights. Each type must add up to 1.0 (100%).
SHOOT_WEIGHTS = {
    "portrait":  {"light": 0.40, "rain": 0.25, "wind": 0.20, "comfort": 0.10, "visibility": 0.05},
    "event":     {"light": 0.30, "rain": 0.35, "wind": 0.20, "comfort": 0.10, "visibility": 0.05},
    "sunset":    {"light": 0.55, "rain": 0.20, "wind": 0.10, "comfort": 0.05, "visibility": 0.10},
    "landscape": {"light": 0.45, "rain": 0.20, "wind": 0.15, "comfort": 0.05, "visibility": 0.15},
}

# Caps: a great factor cannot hide a serious problem.
# final = min(base, 25 + 75*light, 35 + 65*rain, 35 + 65*wind, 40 + 60*comfort)
LIGHT_CAP_BASE, LIGHT_CAP_SPAN = 25.0, 75.0
RAIN_CAP_BASE, RAIN_CAP_SPAN = 35.0, 65.0
WIND_CAP_BASE, WIND_CAP_SPAN = 35.0, 65.0
COMFORT_CAP_BASE, COMFORT_CAP_SPAN = 40.0, 60.0

# Full-session mix. The 20th percentile is the weaker part of the booking,
# not a "how sure is the forecast" number.
SESSION_MEAN_WEIGHT = 0.60
SESSION_WEAK_WEIGHT = 0.40
SESSION_WEAK_PERCENTILE = 0.20

# Rain: chance (0–1) + mm in the 3-hour slot.
RAIN_CHANCE_WEIGHT = 0.65
RAIN_MM_WEIGHT = 0.35
RAIN_MM_FOR_ZERO = 4.0

# Wind: metres per second (OpenWeather metric units).
WIND_CALM_MS = 2.5
WIND_BAD_MS = 12.0

# Comfort: feels-like °C.
COMFORT_LOW_C = 18.0
COMFORT_HIGH_C = 26.0
COMFORT_ZERO_LOW_C = 0.0
COMFORT_ZERO_HIGH_C = 40.0

# Visibility: OpenWeather metres (10000 is the usual maximum).
VISIBILITY_FULL_M = 10000.0


# ------------------------------------------------------------
# Tiny helpers
# ------------------------------------------------------------
def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Keep a number inside [low, high]."""
    return max(low, min(high, value))


def display_score(score: float) -> int:
    """Show the score as an integer. 86.5 becomes 87 (half rounds up)."""
    value = clamp(score, 0.0, 100.0)
    return min(100, int(value + 0.5))


def condition_label(score: float | int | None, status: str = STATUS_OK) -> str:
    """Labels use the integer the user sees."""
    if status == STATUS_UNAVAILABLE or score is None:
        return "Unavailable"
    if status == STATUS_NOT_RECOMMENDED:
        return "Not recommended"
    shown = display_score(float(score))
    if shown >= 80:
        return "Good conditions"
    if shown >= 60:
        return "Fair conditions"
    return "Challenging conditions"


def is_hazard(weather_id: int | None) -> bool:
    """OpenWeather condition ids that are not a safe outdoor shoot."""
    if weather_id is None:
        return False
    if 200 <= weather_id <= 232:  # thunderstorm
        return True
    if weather_id in (502, 503, 504, 511, 602, 622):  # heavy rain/snow
        return True
    if 731 <= weather_id <= 781:  # sand, ash, squall, tornado
        return True
    return False


def weights_sum_to_one(tolerance: float = 1e-9) -> bool:
    for weights in SHOOT_WEIGHTS.values():
        if abs(sum(weights.values()) - 1.0) > tolerance:
            return False
    return True


# ------------------------------------------------------------
# Sun height (astronomy from lat/lon + UTC time — not extra weather)
# ------------------------------------------------------------
def sun_height_degrees(latitude: float, longitude: float, timestamp_unix: int) -> tuple[float, bool]:
    """
    Return (height_degrees, is_afternoon).

    height_degrees: 90 = overhead, 0 = on the horizon, negative = below.
    is_afternoon: True after the sun's highest point (needed for sunset).
    """
    # Days since 1 Jan 2000, 12:00 UTC (a standard astronomy epoch).
    days = timestamp_unix / 86400.0 + 2440587.5 - 2451545.0
    mean_long = (280.460 + 0.9856474 * days) % 360.0
    mean_anom = math.radians((357.528 + 0.9856003 * days) % 360.0)
    ecliptic = math.radians(mean_long + 1.915 * math.sin(mean_anom))
    tilt = math.radians(23.439)
    declination = math.asin(math.sin(tilt) * math.sin(ecliptic))
    right_asc = math.atan2(math.cos(tilt) * math.sin(ecliptic), math.cos(ecliptic))
    gst = (280.46061837 + 360.98564736629 * days) % 360.0
    hour_angle = math.radians((gst + longitude) % 360.0) - right_asc
    lat = math.radians(latitude)
    height = math.asin(
        math.sin(lat) * math.sin(declination)
        + math.cos(lat) * math.cos(declination) * math.cos(hour_angle)
    )
    wrapped = ((math.degrees(hour_angle) + 180.0) % 360.0) - 180.0
    return math.degrees(height), wrapped >= 0.0


# ------------------------------------------------------------
# Suitability of each factor (always a number from 0 to 1)
# ------------------------------------------------------------
def light_suitability(
    shoot_type: str,
    cloud_cover: float,
    sun_height: float,
    is_afternoon: bool,
) -> float:
    """
    Light + clouds together.

    Portrait: likes low sun, but overcast daylight is still soft and usable.
    Sunset: only the real evening sunset, not "any dry hour".
    Event: most daylight is fine.
    Landscape: likes directional light; some clouds can help.
    """
    clouds = clamp(cloud_cover, 0.0, 100.0)

    if shoot_type == "sunset":
        if not is_afternoon:
            return 0.15
        # Best when the sun is near the horizon.
        if -6 <= sun_height <= 12:
            sun_part = 1.0
        elif sun_height < -12 or sun_height > 45:
            sun_part = 0.08
        elif sun_height < -6:
            sun_part = 0.45
        else:
            sun_part = 0.25
        # A little cloud can colour the sky; a full cover hides the sun.
        cloud_part = 1.0 - abs(clouds - 30.0) / 100.0
        return clamp(0.75 * sun_part + 0.25 * max(0.0, cloud_part))

    if sun_height < -6:
        return 0.05  # night

    # Soft overcast daylight.
    overcast = 0.90 if (clouds >= 60 and sun_height > 5) else None

    if shoot_type == "portrait":
        if 8 <= sun_height <= 25:
            sun_part = 1.00  # low-angle / golden hour
        elif sun_height > 50:
            sun_part = 0.45  # harsh midday
        else:
            sun_part = 0.75
        if overcast is not None:
            return clamp(0.45 * sun_part + 0.55 * overcast)
        return sun_part

    if shoot_type == "event":
        if sun_height > 5:
            sun_part = 0.95
        else:
            sun_part = 0.55
        if overcast is not None:
            return clamp(max(sun_part, overcast))
        return sun_part

    # landscape
    if 4 <= sun_height <= 25:
        sun_part = 1.00
    elif sun_height > 50:
        sun_part = 0.55
    else:
        sun_part = 0.70
    cloud_part = 1.0 - abs(clouds - 35.0) / 120.0
    mixed = 0.70 * sun_part + 0.30 * max(0.3, cloud_part)
    if overcast is not None:
        mixed = 0.60 * mixed + 0.40 * 0.70
    return clamp(mixed)

# this function calculates the suitability of the rain factor: it returns a value between 0 and 1
def rain_suitability(rain_probability: float, rain_mm: float) -> float:
    """Higher chance or more mm → lower suitability."""
    chance_ok = 1.0 - clamp(rain_probability, 0.0, 1.0)
    amount_ok = clamp(1.0 - max(0.0, rain_mm) / RAIN_MM_FOR_ZERO)
    return clamp(RAIN_CHANCE_WEIGHT * chance_ok + RAIN_MM_WEIGHT * amount_ok)

# this function calculates the suitability of the wind factor: it returns a value between 0 and 1
def wind_suitability(wind_speed: float, wind_gust: float | None) -> float:
    """Stronger wind (and gusts) → lower suitability. Units: m/s."""
    speed = max(0.0, wind_speed)
    if wind_gust is not None:
        speed = max(speed, wind_gust)
    if speed <= WIND_CALM_MS:
        return 1.0
    if speed >= WIND_BAD_MS:
        return 0.0
    return 1.0 - (speed - WIND_CALM_MS) / (WIND_BAD_MS - WIND_CALM_MS)

# this function calculates the suitability of the comfort factor: it returns a value between 0 and 1
def comfort_suitability(feels_like_c: float) -> float:
    """1.0 inside 18–26°C, then a straight fade toward 0°C or 40°C."""
    temp = feels_like_c
    if COMFORT_LOW_C <= temp <= COMFORT_HIGH_C:
        return 1.0
    if temp < COMFORT_LOW_C:
        return clamp((temp - COMFORT_ZERO_LOW_C) / (COMFORT_LOW_C - COMFORT_ZERO_LOW_C))
    return clamp((COMFORT_ZERO_HIGH_C - temp) / (COMFORT_ZERO_HIGH_C - COMFORT_HIGH_C))

# this function calculates the suitability of the visibility factor: it returns a value between 0 and 1
def visibility_suitability(visibility_m: float) -> float:
    """Clearer air scores higher. 10000 m is treated as fully clear."""
    return clamp(visibility_m / VISIBILITY_FULL_M)

# this function calculates the caps for the factors: it returns a dictionary with the caps for the factors
def factor_caps(light: float, rain: float, wind: float, comfort: float) -> dict[str, float]:
    return {
        "light": LIGHT_CAP_BASE + LIGHT_CAP_SPAN * light,
        "rain": RAIN_CAP_BASE + RAIN_CAP_SPAN * rain,
        "wind": WIND_CAP_BASE + WIND_CAP_SPAN * wind,
        "comfort": COMFORT_CAP_BASE + COMFORT_CAP_SPAN * comfort,
    }


# ------------------------------------------------------------
# One hour result
# ------------------------------------------------------------
@dataclass
class HourScore:
    """Score and factor values for one 3-hour forecast slot."""

    hour: HourlyConditions
    score: float | None
    shoot_type: str
    status: str
    light: float | None
    rain: float | None
    wind: float | None
    comfort: float | None
    visibility: float | None
    weights: dict[str, float]
    caps: dict[str, float] = field(default_factory=dict)
    # Sun position at this slot (for best-window daylight filter).
    sun_height: float | None = None
    is_afternoon: bool | None = None

    @property
    def display_score(self) -> int | None:
        if self.score is None or self.status == STATUS_UNAVAILABLE:
            return None
        return display_score(self.score)

    def factors(self) -> dict[str, float]:
        values = {
            "light": self.light,
            "rain": self.rain,
            "wind": self.wind,
            "comfort": self.comfort,
            "visibility": self.visibility,
        }
        return {name: value for name, value in values.items() if value is not None}

    def top_factors_sentence(self) -> str:
        ranked = sorted(self.weights.items(), key=lambda item: item[1], reverse=True)
        first = FACTOR_LABELS[ranked[0][0]].lower()
        second = FACTOR_LABELS[ranked[1][0]].lower()
        return f"For {self.shoot_type}, {first} and {second} matter most."

    def main_drag_sentence(self) -> str:
        return limiting_sentence(self)

    def __iter__(self):
        yield self.hour
        yield self.score


@dataclass
class SessionScore:
    """A full booking window (one or more 3-hour slots)."""

    start: str
    end: str
    score: int
    raw_score: float
    status: str
    explanation: str

    def __iter__(self):
        yield self.start
        yield self.end
        yield float(self.score)


def helping_sentence(item: HourScore) -> str:
    factors = item.factors()
    if not factors:
        return "Not enough forecast data to explain this hour."
    ranked = sorted(factors.items(), key=lambda pair: pair[1], reverse=True)
    names = [FACTOR_LABELS[name].lower() for name, value in ranked[:2] if value >= 0.7]
    if not names:
        return "No factor is strongly helping this hour."
    if len(names) == 1:
        return f"{names[0].capitalize()} is helping the score."
    return f"{names[0].capitalize()} and {names[1]} are helping the score."


def limiting_sentence(item: HourScore) -> str:
    factors = item.factors()
    if not factors:
        return "Not enough forecast data to explain this hour."
    worst_name = min(factors, key=factors.get)
    if factors[worst_name] >= 0.85:
        return "No single factor is reducing the score much."
    return f"{FACTOR_LABELS[worst_name]} is limiting the recommendation."


def explain_hour(item: HourScore) -> str:
    if item.status == STATUS_UNAVAILABLE:
        return "Score unavailable — essential forecast fields are missing."
    if item.status == STATUS_NOT_RECOMMENDED:
        return "Not recommended — hazardous conditions are in the forecast."
    return f"{helping_sentence(item)} {limiting_sentence(item)}"


def explain_session(group: list[HourScore]) -> str:
    if any(item.status == STATUS_NOT_RECOMMENDED for item in group):
        return "Not recommended — hazardous conditions occur during this session."
    if any(item.status == STATUS_UNAVAILABLE for item in group):
        return "Score unavailable — essential forecast fields are missing."
    totals = {name: 0.0 for name in FACTOR_NAMES}
    for item in group:
        for name, value in item.factors().items():
            totals[name] += value
    n = max(1, len(group))
    means = {name: totals[name] / n for name in FACTOR_NAMES}
    helping = [FACTOR_LABELS[k].lower() for k, v in sorted(means.items(), key=lambda kv: -kv[1]) if v >= 0.7][:2]
    limiting = [FACTOR_LABELS[k].lower() for k, v in sorted(means.items(), key=lambda kv: kv[1]) if v < 0.75][:2]
    if helping and limiting:
        return f"Helping: {' and '.join(helping)}. Limiting: {' and '.join(limiting)}."
    if helping:
        return f"Helping: {' and '.join(helping)}."
    if limiting:
        return f"Limiting: {' and '.join(limiting)}."
    return "Conditions are mixed across this session."


# ------------------------------------------------------------
# Score one hour
# ------------------------------------------------------------
def photography_score_breakdown(
    hour: HourlyConditions,
    shoot_type: str,
    sunset_unix: int | None = None,
    *,
    latitude: float | None = None,
    longitude: float | None = None,
    timezone_offset_seconds: int = 0,
) -> HourScore:
    """Score one forecast slot. sunset_unix is unused: we use sun height instead."""
    _ = sunset_unix
    _ = timezone_offset_seconds
    shoot_type = normalize_shoot_type(shoot_type)
    weights = dict(SHOOT_WEIGHTS[shoot_type])

    missing = (
        latitude is None
        or longitude is None
        or hour.visibility_m is None
    )
    if missing:
        return HourScore(
            hour=hour,
            score=None,
            shoot_type=shoot_type,
            status=STATUS_UNAVAILABLE,
            light=None,
            rain=None,
            wind=None,
            comfort=None,
            visibility=None,
            weights=weights,
        )

    sun_height, is_afternoon = sun_height_degrees(latitude, longitude, hour.timestamp_unix)
    feels_like = hour.feels_like_c if hour.feels_like_c is not None else hour.temperature_c
    light = light_suitability(shoot_type, hour.cloud_cover, sun_height, is_afternoon)
    rain = rain_suitability(hour.rain_probability, hour.rain_mm)
    wind = wind_suitability(hour.wind_speed, hour.wind_gust_ms)
    comfort = comfort_suitability(feels_like)
    visibility = visibility_suitability(hour.visibility_m)
    caps = factor_caps(light, rain, wind, comfort)

    base_score = 100.0 * (
        weights["light"] * light
        + weights["rain"] * rain
        + weights["wind"] * wind
        + weights["comfort"] * comfort
        + weights["visibility"] * visibility
    )
    final_score = min(base_score, caps["light"], caps["rain"], caps["wind"], caps["comfort"])
    final_score = clamp(final_score, 0.0, 100.0)
    status = STATUS_NOT_RECOMMENDED if is_hazard(hour.weather_id) else STATUS_OK

    return HourScore(
        hour=hour,
        score=final_score,
        shoot_type=shoot_type,
        status=status,
        light=light,
        rain=rain,
        wind=wind,
        comfort=comfort,
        visibility=visibility,
        weights=weights,
        caps=caps,
        sun_height=sun_height,
        is_afternoon=is_afternoon,
    )


def photography_score(
    hour: HourlyConditions,
    shoot_type: str,
    sunset_unix: int | None = None,
    *,
    latitude: float | None = None,
    longitude: float | None = None,
    timezone_offset_seconds: int = 0,
) -> float | None:
    """Photography Score 0–100, or None when data is missing."""
    return photography_score_breakdown(
        hour,
        shoot_type,
        sunset_unix,
        latitude=latitude,
        longitude=longitude,
        timezone_offset_seconds=timezone_offset_seconds,
    ).score


def hours_on_date(forecast: ForecastReport, shoot_date: str) -> list[HourlyConditions]:
    return [hour for hour in forecast.hours if hour.time_text.startswith(shoot_date)]


def score_forecast(
    forecast: ForecastReport,
    shoot_type: str,
    shoot_date: str,
) -> list[HourScore]:
    """Score every slot on the chosen date."""
    scored = []
    for hour in hours_on_date(forecast, shoot_date):
        scored.append(
            photography_score_breakdown(
                hour,
                shoot_type,
                forecast.sunset_unix,
                latitude=forecast.latitude,
                longitude=forecast.longitude,
                timezone_offset_seconds=forecast.timezone_offset_seconds,
            )
        )
    return scored


# ------------------------------------------------------------
# Full session (the whole booking, not only the best hour)
# ------------------------------------------------------------
def _slot_time(hour: HourlyConditions) -> datetime:
    return datetime.strptime(hour.time_text, "%Y-%m-%d %H:%M:%S")


def _slot_count(duration_hours: float) -> int:
    return max(1, int(round(duration_hours / SLOT_HOURS)))


def _percentile(values: list[float], percentile: float) -> float:
    """Simple percentile: sort, then pick the item at that fraction."""
    ordered = sorted(values)
    index = int(percentile * (len(ordered) - 1))
    return ordered[index]


def session_from_slots(group: list[HourScore]) -> SessionScore | None:
    """
    session_score = 0.60 × mean + 0.40 × 20th-percentile
    then limited by the lowest rain / wind / comfort cap in the group.
    """
    if not group:
        return None

    start_dt = _slot_time(group[0].hour)
    end_dt = start_dt + timedelta(hours=SLOT_HOURS * len(group))
    start = start_dt.strftime("%H:%M")
    end = end_dt.strftime("%H:%M")
    explanation = explain_session(group)

    if any(item.status == STATUS_UNAVAILABLE for item in group):
        return SessionScore(start, end, 0, 0.0, STATUS_UNAVAILABLE, explanation)

    scores = [float(item.score) for item in group if item.score is not None]
    if not scores:
        return None

    mean = sum(scores) / len(scores)
    weak = _percentile(scores, SESSION_WEAK_PERCENTILE)
    mixed = SESSION_MEAN_WEIGHT * mean + SESSION_WEAK_WEIGHT * weak

    rain_caps = [item.caps["rain"] for item in group if item.caps]
    wind_caps = [item.caps["wind"] for item in group if item.caps]
    comfort_caps = [item.caps["comfort"] for item in group if item.caps]
    if rain_caps:
        mixed = min(mixed, min(rain_caps))
    if wind_caps:
        mixed = min(mixed, min(wind_caps))
    if comfort_caps:
        mixed = min(mixed, min(comfort_caps))
    mixed = clamp(mixed, 0.0, 100.0)

    status = STATUS_OK
    if any(item.status == STATUS_NOT_RECOMMENDED for item in group):
        status = STATUS_NOT_RECOMMENDED

    return SessionScore(start, end, display_score(mixed), mixed, status, explanation)


def score_session(
    hour_scores: list[HourScore],
    session_start: datetime,
    *,
    duration_hours: float | None = None,
) -> SessionScore | None:
    """Score N consecutive slots starting at the slot that contains session_start."""
    duration = SESSION_HOURS if duration_hours is None else duration_hours
    n_slots = _slot_count(duration)
    containing = None
    first_after = None
    for i, item in enumerate(hour_scores):
        slot_start = _slot_time(item.hour)
        slot_end = slot_start + timedelta(hours=SLOT_HOURS)
        if slot_start <= session_start < slot_end:
            containing = i
            break
        if first_after is None and slot_start >= session_start:
            first_after = i
    start_index = containing if containing is not None else first_after
    if start_index is None:
        return None
    if start_index + n_slots > len(hour_scores):
        return None
    return session_from_slots(hour_scores[start_index:start_index + n_slots])


def starts_after_sunrise(item: HourScore) -> bool:
    """
    True when this slot is at/after sunrise that day.

    Pre-dawn (sun below horizon, still morning) → False.
    Daylight, or evening after sunset → True (sunset shoots need dusk).
    Unknown sun position → True (do not block synthetic / incomplete data).
    """
    if item.sun_height is None or item.is_afternoon is None:
        return True
    if item.sun_height >= 0.0:
        return True
    return bool(item.is_afternoon)


def best_shooting_window(
    scored_hours: list[HourScore],
    *,
    duration_hours: float | None = None,
) -> SessionScore | None:
    """Best complete run of consecutive slots — not the single highest hour.

    Only considers sessions that start at or after sunrise (skips pre-dawn).
    """
    if not scored_hours:
        return None
    duration = SESSION_HOURS if duration_hours is None else duration_hours
    n_slots = _slot_count(duration)
    best: SessionScore | None = None
    for i in range(len(scored_hours) - n_slots + 1):
        group = scored_hours[i:i + n_slots]
        if not starts_after_sunrise(group[0]):
            continue
        session = session_from_slots(group)
        if session is None or session.status == STATUS_UNAVAILABLE:
            continue
        if best is None:
            best = session
            continue
        this_ok = session.status == STATUS_OK
        best_ok = best.status == STATUS_OK
        if (this_ok, session.raw_score) > (best_ok, best.raw_score):
            best = session
    return best


def score_booked_interval(
    scored_hours: list[HourScore],
    shoot_date: str,
    preferred_time: str,
    *,
    duration_hours: float | None = None,
) -> SessionScore | None:
    """Score the photographer's booked clock time as a full session."""
    try:
        start = datetime.strptime(f"{shoot_date} {preferred_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None
    return score_session(scored_hours, start, duration_hours=duration_hours)
