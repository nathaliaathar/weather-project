# Shoot Window — photography decision tool

**Start here.** This folder is a **starter structure** for a university pair project (Nathalia and Dafna). Fill in the `# TODO (STUDENT)` sections — do not replace the project with a copied repository, and do not expect the app to work until you write those parts.

This is **not** a weather app. Weather is the **input**. The **product** is a decision tool for professional photographers who shoot outdoors in Israel.

A photographer enters: Tel Aviv, tomorrow, 17:00, portrait. Python fetches a forecast, scores each hour the way a photographer would, and recommends the best shooting window.

```text
Weather Data → Analysis → Photography Score → Recommendation → Decision
```

## Project roadmap

Work in this order. Tick items as you finish them.

```text
PROJECT ROADMAP

[ ]  1. Create a free OpenWeatherMap API key and copy .env.example → .env
[ ]  2. Install libraries: pip install -r requirements.txt
[ ]  3. In the notebook: send a FORECAST request and print status_code (200)
[ ]  4. In the notebook: extract temp, wind, clouds, pop, sunrise/sunset from JSON
[ ]  5. Person A: parse data/sample_forecast.json in models.py
[ ]  6. Person A: validate city + shoot type in validation.py
[ ]  7. Person A: implement client.py get_forecast — then pytest for models/validation
[ ]  8. Together: agree Photography Score weights on paper (portrait / sunset / landscape)
[ ]  9. Person A: scoring.py (score each hour + best window)
[ ] 10. Person B: Photography Score chart in charts.py
[ ] 11. Person B: app.py shows score, recommendation, best window, charts
[ ] 12. Handle invalid cities / missing key with st.error
[ ] 13. GitHub repo (no secrets) + Streamlit Community Cloud — docs/DEPLOY.md
[ ] 14. OPTIONAL later: compare Tel Aviv vs Haifa vs Herzliya
[ ] 15. Delete educational comments marked DELETE LATER, then update this README
```

## What each file is for

```text
weather-project/
│
├── app.py
│   └── Starts the web page. Asks for location, date, time, shoot type.
│       Calls the client and scoring, then shows the decision.
│
├── photo_planner/
│   ├── client.py
│   │   └── Sends the HTTP request to the forecast API and returns a ForecastReport.
│   ├── models.py
│   │   └── Turns forecast JSON into HourlyConditions + ForecastReport.
│   ├── scoring.py
│   │   └── THE PRODUCT: Photography Score + best shooting window.
│   ├── validation.py
│   │   └── Cleans / rejects city name and shoot type before scoring.
│   ├── charts.py
│   │   └── Builds Plotly figures from scored hours (no API calls).
│   ├── errors.py
│   │   └── Named errors the UI can catch (404, bad key, empty city).
│   └── __init__.py
│       └── Makes this folder importable as photo_planner.
│
├── notebooks/01_forecast_api_colab.ipynb
│   └── Phase 1 lab: practice the forecast request before the app.
│
├── data/sample_forecast.json
│   └── Fake forecast so you can parse JSON without using the internet.
│
├── tests/
│   └── Checks models, validation, and scoring. Run with: pytest
│
├── docs/PAIR.md
│   └── Pair playbook: roles, mockup, checklist (same content as the live canvas).
│
├── docs/DEPLOY.md
│   └── How to run locally and publish on Streamlit Cloud.
│
├── requirements.txt
│   └── Libraries to install (not Python code).
│
├── .env.example
│   └── Template for your secret API key. Copy to .env — never commit .env.
│
└── README.md
    └── This file — how to start and what the project should become.
```

## How data moves (input → output)

```text
Photographer chooses: Tel Aviv, tomorrow, 17:00, portrait
        ↓
app.py
        ↓
calls OpenWeatherClient.get_forecast(city)
        ↓
validation.py  (clean the name, or raise InvalidCityError)
        ↓
client.py  sends HTTP GET to OpenWeatherMap /data/2.5/forecast
        ↓
JSON response (city info + list of 3-hour slots)
        ↓
models.py  ForecastReport.from_api_json(...)
        ↓
returns ForecastReport to app.py
        ↓
app.py calls score_forecast(...) in scoring.py
        ↓
each hour gets a Photography Score (0–100)
        ↓
best_shooting_window(...) → "18:00–21:00"
        ↓
app.py shows the recommendation
        ↓
charts.py  (Plotly figures)  →  st.plotly_chart on the page
```

`get_forecast` is written in `photo_planner/client.py`. The import in `app.py` is what lets the web page use that function.

`from_api_json` is written in `photo_planner/models.py`. The client calls it so `app.py` never has to parse JSON.

`photography_score` is written in `photo_planner/scoring.py`. That is the analysis step. Weather in, decision out.

## Pair roles

See [docs/PAIR.md](docs/PAIR.md) for the pair playbook, the **page mockup**, and the task checklist.

| Person | Owns |
| --- | --- |
| A (data + score) | API client, JSON model, validation, Photography Score, tests |
| B (UI) | Plotly charts, Streamlit layout, recommendation text, README polish |
| Both | Colab notebook, score **weights** (decide together), GitHub, secrets, Cloud deploy |

## Quick start

1. Create a free API key: https://home.openweathermap.org/api_keys
2. Copy `.env.example` → `.env` and paste the key.
3. Create a venv, then `pip install -r requirements.txt`
4. Start in `notebooks/01_forecast_api_colab.ipynb` (Colab or local Jupyter).
5. Implement the `# TODO (STUDENT)` sections in `photo_planner/` until `pytest` skips can be removed.
6. `streamlit run app.py`
7. Follow [docs/DEPLOY.md](docs/DEPLOY.md) for GitHub + Streamlit Cloud.

## What the finished app should show

- Photographer inputs: location in Israel, date, preferred time, photography type
- A **Photography Score** (for example 87/100) and a short recommendation
- **Best Shooting Window** (the best 3-hour slot, or a merged window)
- Interactive charts: score over time, temperature, clouds and/or rain
- Clear errors for a missing API key or an unknown city

The free OpenWeatherMap forecast is every **3 hours** (12:00, 15:00, 18:00...), not every minute. That is enough for the MVP. Exact times like 17:50–19:05 would need extra interpolation — treat that as optional.

## Phase 2 (later)

Compare cities (Tel Aviv vs Haifa vs Herzliya) for the same sunset shoot. Do this only after the one-city flow works. There is a commented stub in `scoring.py`.

## Secrets

Never commit:

- `.env`
- `.streamlit/secrets.toml`

On Streamlit Community Cloud, add `OPENWEATHER_API_KEY` in the app Secrets panel. Same name as in `.env.example`.

## Comments you will see in the code

| Label | Meaning |
| --- | --- |
| `# KEEP` | Setup that should stay in the final project |
| `# TODO (STUDENT)` | Work you (or your pair) must write |
| `# HINT` | A small idea, not the finished solution |
| `# DELETE LATER` | Learning comments to remove before submission |
| `# OPTIONAL` | Useful, not required for the MVP |
