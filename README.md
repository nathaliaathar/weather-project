# Shoot Window — photography decision tool

Weather is the **input**. The **product** is a decision tool for outdoor photographers in Israel.

A photographer enters location, date, time, and shoot type. The app fetches a forecast, scores each hour for that shoot type, and recommends the best shooting window.

```text
Weather Data → Analysis → Photography Score → Recommendation → Decision
```

## Project layout

```text
weather-project/
│
├── app.py
│   └── Home page: location, date, time, shoot type → opens results.
│
├── pages/results.py
│   └── Photography Score, best window, booked time, and charts.
│
├── photo_planner/
│   ├── client.py      — HTTP request to the forecast API
│   ├── models.py      — JSON → HourlyConditions / ForecastReport
│   ├── scoring.py     — Photography Score + best shooting window
│   ├── validation.py  — city name and shoot type checks
│   ├── charts.py      — Plotly figures from scored hours
│   ├── errors.py      — named errors for the UI
│   └── __init__.py
│
├── notebooks/01_forecast_api_colab.ipynb
│   └── Practice notebook for the forecast API
│
├── data/sample_forecast.json
│   └── Sample forecast for offline parsing tests
│
├── tests/
│   └── pytest suite for models, validation, scoring, charts
│
├── docs/
│   ├── PAIR.md     — pair roles and checklist
│   └── DEPLOY.md   — local run + Streamlit Cloud
│
├── requirements.txt
├── .env.example
└── README.md
```

## How data moves

```text
Photographer chooses: Tel Aviv, tomorrow, 17:00, portrait
        ↓
app.py → OpenWeatherClient.get_forecast(city)
        ↓
validation.py → client.py → OpenWeatherMap /data/2.5/forecast
        ↓
models.py → ForecastReport
        ↓
scoring.py → Photography Score + best_shooting_window
        ↓
pages/results.py + charts.py → decision on screen
```

## Pair roles

See [docs/PAIR.md](docs/PAIR.md).

| Person | Owns |
| --- | --- |
| A (data + score) | API client, JSON model, validation, Photography Score, tests |
| B (UI) | Plotly charts, Streamlit layout, recommendation text |
| Both | Notebook, score weights, GitHub, secrets, Cloud deploy |

## Quick start

1. Create a free API key: https://home.openweathermap.org/api_keys
2. Copy `.env.example` → `.env` and paste the key.
3. Create a venv, then `pip install -r requirements.txt`
4. Run tests: `pytest`
5. Start the app: `streamlit run app.py`
6. Deploy: [docs/DEPLOY.md](docs/DEPLOY.md)

## What the app shows

- Inputs: location in Israel, date, preferred time, photography type
- A **Photography Score** (0–100) and a short recommendation
- **Best Shooting Window** for the chosen day
- Charts: score over time, temperature, rain, city comparison heatmap
- Clear errors for a missing API key or an unknown city

The free OpenWeatherMap forecast is every **3 hours** (12:00, 15:00, 18:00...), not every minute.

## Secrets

Never commit:

- `.env`
- `.streamlit/secrets.toml`

On Streamlit Community Cloud, add `OPENWEATHER_API_KEY` in the app Secrets panel.
