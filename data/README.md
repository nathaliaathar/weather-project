# Sample forecast JSON

This file is a **practice** copy of what OpenWeatherMap's 5-day / 3-hour forecast returns for Tel Aviv.

It is smaller than a real response (5 slots instead of ~40) so you can read it.

## Why it exists

You can implement `HourlyConditions.from_slot_json` and `ForecastReport.from_api_json` in `models.py` **without** calling the live API. The tests in `tests/test_models.py` load this file.

JSON is nested dictionaries and lists. Follow the keys:

- `city.name` → city
- `city.country` → country
- `city.coord.lat` / `lon`
- `city.timezone`, `city.sunrise`, `city.sunset`
- `list` → many 3-hour slots
- For one slot:
  - `dt_txt`, `dt`
  - `main.temp` / `feels_like` / `humidity`
  - `wind.speed`
  - `clouds.all`
  - `pop` (rain chance, 0 to 1)
  - `rain.3h` (only present when it rains)
  - `weather[0].description` / `icon`

This is **not** a file you edit for the assignment. Use it as a map while you write the parsers.

The last slot is on **2026-09-05** so you can test `hours_on_date` (it should drop that slot when the shoot date is 2026-09-04).
