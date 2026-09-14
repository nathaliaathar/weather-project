# Pair playbook — Nathalia and Dafna

Use this file as the shared plan: what you are building, how the page should look, who owns which file, and in which order to work.

The live board (tabs, mockup charts, clickable tasks) is the Cursor canvas **Shoot Window — pair playbook**. The file-connection tree is the canvas **Shoot Window — file flow**.

Printed copies to hand to each other:

- [playbook-role-a.pdf](playbook-role-a.pdf) — Role A: data + Photography Score
- [playbook-role-b.pdf](playbook-role-b.pdf) — Role B: page + charts
- [shoot-window-pair-playbook.html](shoot-window-pair-playbook.html) — same board in the browser (send this file on WhatsApp / Drive)

Each PDF has your files, your functions, your checklist, and a gold **TOGETHER** section (the meetings you do as a pair). Keep this markdown in sync when you work on GitHub without Cursor.

---

## What you are building

A decision tool for professional photographers who do outdoor sessions in Israel.

Someone is not asking "what is the weather in Tel Aviv?". They are asking:

> I have a portrait session tomorrow in Tel Aviv at 17:00. Should I shoot then — and is there a better window?

The page should collect:

- location (Tel Aviv, Haifa, ...)
- date
- preferred time
- photography type (portrait / sunset / landscape)

Then it should:

1. fetch a **forecast** (many hours, not only "now")
2. score each hour like a photographer would
3. show a **Photography Score** (0–100)
4. recommend a **Best Shooting Window**
5. show interactive charts (score, temperature, clouds/rain)

If the city does not exist, the page shows a clear error instead of crashing.

Weather is the input. The product is the score and the recommendation.

Build **one page** in Streamlit. Target the mockup below. Do not invent extra screens.

---

## Page mockup (what to build)

This is the UX target. It is meant to look calm and professional, and to be easy for juniors: **one page, Streamlit widgets only, no custom CSS, no extra pages, no login.**

`.streamlit/config.toml` already sets a warm light theme. Leave it. Do not fight Streamlit with HTML.

Copy is example text. Your real numbers will come from `scoring.py`.

### Design rules (keep these)

1. **Decision first, weather second.** The photographer should see the score and the window before any chart.
2. **One screen.** Inputs at the top, result below. No sidebar menu, no tabs for the MVP.
3. **Three charts is enough.** Score during the day (main), then temperature, then clouds/rain.
4. **Do not dump JSON** or ten weather numbers in a table. A few `st.metric` values are enough to trust the score.
5. **Empty and error states are part of the product.** Before the click, explain the app. On failure, one `st.error` sentence.

### Too hard — skip for the university MVP

- custom CSS / HTML / React
- a map of Israel
- login, user accounts, saved shoots
- comparing three cities on one screen (that is Phase 2)
- minute-perfect windows like 17:50–19:05 (the free API is every 3 hours)

If it is not on the mockup, do not build it yet.

### 1 — Before the photographer clicks (empty state)

`app.py` already has the four inputs. Keep that row.

```text
Shoot Window
A decision tool for outdoor photographers in Israel.
Weather is the input. The Photography Score is the product.

Plan a session
+--------------+----------------+------------------+--------------------+
| Location     | Date           | Preferred time   | Photography type   |
| Tel Aviv   v | 2026-09-04     | 17:00            | portrait         v |
+--------------+----------------+------------------+--------------------+

                         [  Plan shoot  ]

Choose a location in Israel, a date, a time, and a photography type,
then press Plan shoot.

What this app is
Weather Data → Analysis → Photography Score → Recommendation → Decision
```

**Streamlit pieces (already started in `app.py`):**

| Block | Widget |
| --- | --- |
| Title | `st.title` + `st.caption` |
| Four inputs | `st.columns(4)` with `selectbox`, `date_input`, `time_input`, `selectbox` |
| Button | `st.button("Plan shoot", type="primary")` |
| Empty text | `st.write` + a short `st.markdown` |

### 2 — After a successful plan (the page that matters)

This is the layout Person B should recreate, top to bottom.

```text
Shoot Window
A decision tool for outdoor photographers in Israel.

Plan a session
+--------------+----------------+------------------+--------------------+
| Location     | Date           | Preferred time   | Photography type   |
| Tel Aviv   v | 2026-09-04     | 17:00            | portrait         v |
+--------------+----------------+------------------+--------------------+
                         [  Plan shoot  ]

Tel Aviv  ·  4 Sep 2026  ·  portrait

+----------------------+  +----------------------+  +----------------------+
| Photography Score    |  | Best shooting window |  | Your booked time     |
|                      |  |                      |  |                      |
|      87 / 100        |  |   18:00 – 21:00      |  | 17:00  ·  score 83   |
|      Excellent       |  |   Strongest slot     |  | Close to the window  |
+----------------------+  +----------------------+  +----------------------+

Conditions look excellent for a portrait session. Rain chance is low and
the wind eases after 18:00. If you can move the booking, prefer 18:00–21:00
over 17:00.

Photography Score during the day
+------------------------------------------------------------------+
| 100|                                                             |
|  90|                         * 94                                  |
|  80|              * 83              * 91 (optional)                |
|  70|     * 72                              * 70                    |
|    +---------+---------+---------+---------+                     |
|      12:00     15:00     18:00     21:00                         |
+------------------------------------------------------------------+
Mark the highest point. That chart is the product.

Temperature (°C)                    Cloud cover (%) and rain chance
+---------------------------+       +---------------------------+
| 31                         |       | clouds  ----               |
| 29                         |       | rain   ....               |
| 26         *               |       |                           |
| 24                         |       | 12:00  15:00  18:00  21:00|
+---------------------------+       +---------------------------+

Why this hour?   (click to open — optional expander)
  Temperature 26.4 °C     Wind 3.1 m/s     Clouds 24%     Rain 2%
```

**Streamlit pieces (build in this order):**

| Block on the mockup | Widget to use | Notes |
| --- | --- | --- |
| City · date · type | `st.caption` or `st.write` | One line under the button |
| Three big numbers | `st.columns(3)` + `st.metric` | Score, window, booked time |
| Recommendation sentence | `st.success(...)` | One or two sentences, not a paragraph |
| Score chart | `st.plotly_chart(photography_score_chart(scored))` | Full width. Do this before the other charts |
| Two smaller charts | `st.columns(2)` + two `st.plotly_chart` | Temperature left, clouds/rain right |
| Supporting weather | `st.expander("Why this hour?")` | Optional. Four `st.metric` inside |

`st.metric` example for the score:

```python
st.metric("Photography Score", "87 / 100", "Excellent")
```

`st.success` example for the sentence:

```python
st.success(
    "Conditions look excellent for a portrait session. "
    "Best shooting window: 18:00–21:00."
)
```

You do not need to copy these strings. Use your real `score` and `window` variables.

### 3 — If something goes wrong

One red box. No traceback on the page.

```text
Something went wrong

City not found. Check the location name and try again.
```

**Streamlit piece:** `except WeatherError as err:` then `st.error(str(err))`.

Same pattern for a missing API key: `st.error("Missing API key. Copy .env.example to .env.")`.

### Visual tone

- Warm light page (already in `config.toml`).
- Plenty of space. Do not pack ten metrics in one row.
- Charts: default Plotly is fine. A simple **line** is more professional here than a 3D gauge.
- Words: short, calm, for a photographer (“excellent”, “windy for portrait”, “prefer 18:00”). Not “payload keys” or “status 200”.

### How this maps to files

```text
Inputs on the mockup     →  already in app.py
Score / window numbers   →  scoring.py (Person A), displayed in app.py (Person B)
Recommendation sentence  →  app.py (Person B) using the score
Three charts             →  charts.py (Person B), shown with st.plotly_chart
Error box                →  app.py catches WeatherError
```

Person B: follow this mockup in Step 8. Do not parse JSON to invent extra widgets.

## Words you will see

| Word | What it means here |
| --- | --- |
| API | A way for your Python program to ask OpenWeatherMap for data |
| API key | A secret password the weather service gives you. Never put it on GitHub. |
| Endpoint | The specific URL you call: `/data/2.5/forecast` (5-day / 3-hour) |
| JSON | The nested dictionary the API sends back |
| Streamlit | The library that turns `app.py` into a web page |
| HourlyConditions | Weather for one 3-hour slot (temp, wind, clouds, rain chance) |
| ForecastReport | City info + a list of HourlyConditions + sunrise/sunset |
| Photography Score | Your 0–100 rating of how good that hour is for this shoot type |
| Best Shooting Window | The time range you recommend, based on the scores |

## How to use this file

1. Read **What you are building** and the **Page mockup**.
2. Fill **Who is who** (10 minutes).
3. Do **one task** from the checklist. Each task says what to do, how, and when it is done.
4. Do not start Streamlit on day 1. First get status **200** in the notebook.
5. Do not write `scoring.py` until you can parse the sample JSON.
6. Person B: do not invent a new layout. Recreate the mockup with Streamlit widgets only.

## Work in this order

### Step 1 — Get a free key and install libraries

**Your task:** make your computer ready to talk to OpenWeatherMap.

**How:** create a key at https://home.openweathermap.org/api_keys. Copy `.env.example` to `.env` and paste the key. Then run `pip install -r requirements.txt` inside `weather-project/`.

**Done when:** you have a `.env` file and pip finished without errors. **Who:** both.

### Step 2 — In the notebook, get status 200 from the FORECAST endpoint

**Your task:** send one request for a real city and see that it worked.

**How:** open `notebooks/01_forecast_api_colab.ipynb`. Fill in `requests.get` to  
`https://api.openweathermap.org/data/2.5/forecast`  
(params: `q`, `appid`, `units=metric`). Print `response.status_code`.

**Done when:** you see `200`. **Who:** both. Do not build the Streamlit page yet.

### Step 3 — Read photographer-useful fields out of the JSON

**Your task:** find the numbers a photographer would care about.

**How:** after a 200, look at `payload["list"][0]` and `payload["city"]`. Print temperature, wind, `clouds.all`, `pop`, and sunset. You can also practice on `data/sample_forecast.json` offline.

**Done when:** you can print city, one slot time, temperature, wind, clouds, rain chance, sunset. **Who:** both.

### Step 4 — Role A: fill `models.py` (sample JSON)

**Your task:** copy the notebook mapping into `HourlyConditions.from_slot_json` and `ForecastReport.from_api_json`.

**How:** open `photo_planner/models.py` and `data/sample_forecast.json` side by side. Fill every field. Then remove skip on the matching tests.

**Who:** Role A. Role B waits until field names are frozen.

### Step 5 — Role A: `validation.py` then `client.py`

**Your task:** clean the city name and shoot type, then send the live forecast from Python files (not the notebook).

**How:** fill `normalize_city_name` and `normalize_shoot_type`, then `get_forecast` in `client.py` (`requests.get`, check status codes, return a `ForecastReport`).

**Done when:** `pytest` for models/validation passes and `get_forecast` works for Tel Aviv. **Who:** Role A.

### Step 6 — Together: decide score weights on paper

**Your task:** agree what "good weather" means for each shoot type. There is no single correct formula.

**How:** for portrait, sunset, and landscape, write four numbers (rain, wind, temperature, clouds) that add up to 1.0. Ask: "What would cancel this shoot first?" Put those numbers into `SHOOT_WEIGHTS` in `scoring.py`.

**Done when:** both of you can explain why portrait weights wind more (or less) than landscape. **Who:** both. Do this before coding the formula.

### Step 7 — Role A: `scoring.py`

**Your task:** turn weather into a 0–100 score and a recommended window.

**How:** fill `photography_score`, `hours_on_date`, `score_forecast`, `best_shooting_window`. Use the sample forecast date `2026-09-04` in tests. MVP window = the single best 3-hour slot.

**Done when:** scoring tests pass (range 0–100, four hours on 2026-09-04). **Who:** Role A. Role B can start charts with fake `(hour, score)` pairs if needed.

### Step 8 — Role B: charts, then the page (follow the mockup)

**Your task:** make the successful-result screen match the mockup above.

**How:** fill `photography_score_chart` in `charts.py` (do not call the API there). In `app.py`, after the button click, call `get_forecast` and `score_forecast`. Then build the page **in this order**:

1. three `st.metric` (score, best window, booked time)
2. one `st.success` sentence
3. `st.plotly_chart` for the score
4. two charts in `st.columns(2)`
5. optional `st.expander` with wind / rain / clouds
6. `except WeatherError` → `st.error`

**Who:** Role B. Do not parse JSON in `app.py`. Do not add CSS.

### Step 9 — Test on your computer

**Your task:** use the app like a real photographer, including mistakes.

**How:** `streamlit run app.py`. Try Tel Aviv portrait tomorrow 17:00, a sunset session, an empty flow, and a city you type wrongly if you add a custom-city box.

**Who:** B leads, A watches the error messages and whether the scores make photographic sense.

### Step 10 — GitHub (no secrets)

**Your task:** share the code without sharing the API key.

**How:** follow `docs/DEPLOY.md`. Check `git status` before every push. Never commit `.env` or `.streamlit/secrets.toml`.

### Step 11 — Deploy and screenshot

**Your task:** put the app on Streamlit Community Cloud and prove it works.

**How:** [share.streamlit.io](https://share.streamlit.io/) → this repo → `app.py` → add `OPENWEATHER_API_KEY` in Secrets. Open the URL, plan a shoot, save screenshots of the score and the charts.

### Step 12 — OPTIONAL Phase 2

Compare Tel Aviv, Haifa, and Herzliya for the same sunset. Skip until the one-city app is solid.

---

## Who is who

- **Role A — data + score:** `client.py`, `models.py`, `validation.py`, `errors.py`, `scoring.py`, `tests/`
- **Role B — the web page:** `charts.py`, `app.py`, `.streamlit/config.toml`, README usage
- **Both:** notebook, **Photography Score weights**, GitHub, secrets, deploy

Write the names here after a 10-minute decision:

- Role A:
- Role B:

Pair: **Nathalia** and **Dafna**.

### Why the files are split this way

```text
Person A produces a ForecastReport, then a list of (hour, score)
        ↓
Person B only displays that decision
```

Person B does **not** parse JSON in `app.py`. If the score needs a new field (for example visibility), Person A adds it on `HourlyConditions` first.

### Model contract

`app.py` receives a `ForecastReport` with:

- city, country, latitude, longitude
- timezone_offset_seconds, sunrise_unix, sunset_unix
- hours: a list of `HourlyConditions`

Each `HourlyConditions` has:

- time_text, timestamp_unix
- temperature_c, feels_like_c, humidity
- wind_speed, cloud_cover, rain_probability, rain_mm
- description, icon

Then `app.py` also receives scored pairs: `(HourlyConditions, float)`.

### Working in parallel — you will not wait all week

The **names** of fields and functions are already written (`HourlyConditions.temperature_c`, `get_forecast`, `score_forecast`, `photography_score_chart`). Role A fills how those functions work. Role B can already use the names.

**Role A does not need Role B.** Sample JSON + `pytest` are enough. You can finish models, validation, client, scoring, and tests with Streamlit still empty.

**Role B does not wait for the live API.** Build charts with a tiny fake list, for example two `HourlyConditions(...)` plus made-up scores `72` and `94`. The Streamlit layout (metrics, `st.success`, `st.plotly_chart`) can be written the same way. When Role A finishes, you only replace the fake list with `score_forecast(...)`.

**Three short meetings, not a lock:**

1. Together: notebook until status `200`.
2. Together: 20 minutes on paper for `SHOOT_WEIGHTS` (before Role A codes `photography_score`).
3. Together: plug `app.py` into the real `get_forecast` + `score_forecast` (one afternoon).

Do **not** change field names in `models.py` without telling Role B. That is the only way one of you actually blocks the other.

---

## Checklist (tick as you go)

Each line is one job. Do them in order. One at a time.

### Both

- [ ] **Task:** Decide who is Role A and who is Role B. **How:** talk for 10 minutes, write the names above. **Done when:** each person knows which files they own.
- [ ] **Task:** Practice talking to the forecast API together. **How:** open the notebook, add the API key (do not commit it), request Tel Aviv, print `status_code`. **Done when:** you see 200.
- [ ] **Task:** Agree Photography Score weights on paper. **How:** for each shoot type, decide rain / wind / temperature / clouds weights that add to 1.0. Write why. **Done when:** both can explain portrait vs sunset.
- [ ] **Task:** Read each other’s files out loud. **How:** A opens `app.py` / `charts.py`. B opens `client.py` / `scoring.py`. Ask: can I explain this file in my own words?
- [ ] **Task:** Put the project on GitHub without the secret key. **How:** follow `docs/DEPLOY.md`. Before you push, `git status` must not show `.env`.
- [ ] **Task:** Publish the app. **How:** Streamlit Community Cloud, entry file `app.py`, secret name `OPENWEATHER_API_KEY`. **Done when:** you have a public URL.
- [ ] **Task:** Prove the live app works. **How:** plan a real Israel shoot, then trigger an error. Save both screenshots.

### Role A — data + score

- [ ] **Task:** Get a free API key and keep it only on your computer. **How:** create a key → copy `.env.example` to `.env` → paste the key. Never commit `.env`.
- [ ] **Task:** Look at the raw forecast JSON. **How:** after status 200, print `payload["city"]["name"]`, `len(payload["list"])`, and one slot's `temp`, `pop`, `clouds`.
- [ ] **Task:** Turn the sample JSON into models (no internet). **How:** fill `from_slot_json` and `from_api_json` using `data/sample_forecast.json`.
- [ ] **Task:** Stop empty city names and unknown shoot types. **How:** fill both functions in `validation.py`.
- [ ] **Task:** Write the live forecast request. **How:** fill `get_forecast` in `client.py`. Clean the name, `requests.get`, return `ForecastReport.from_api_json(...)`.
- [ ] **Task:** Turn failed requests into clear errors. **How:** 401 → `InvalidApiKeyError`, 404 → `CityNotFoundError`, other failures → `WeatherRequestError`.
- [ ] **Task:** Filter hours to the booked date. **How:** fill `hours_on_date` (sample date `2026-09-04` should keep 4 slots).
- [ ] **Task:** Write `photography_score`. **How:** convert each weather field to a 0–100 goodness, then combine with `SHOOT_WEIGHTS`.
- [ ] **Task:** Write `score_forecast` and `best_shooting_window`. **How:** implement them in `scoring.py`. MVP = best single 3-hour slot.
- [ ] **Task:** Turn tests on and make them pass. **How:** delete `@pytest.mark.skip` after each function works, then run `pytest` from `weather-project/`.

### Role B — the web page

- [ ] **Task:** In the notebook, pull out the numbers the page will show. **How:** time, temperature, wind, clouds, rain chance, sunset (notebook section 3).
- [ ] **Task:** Make the Photography Score chart. **How:** fill `photography_score_chart` in `charts.py`. Do not call the API in that file.
- [ ] **Task:** Show the decision after the button click. **How:** match mockup section 2: three `st.metric`, then `st.success`. Catch `WeatherError` with `st.error` (mockup section 3).
- [ ] **Task:** Put the score chart on the page. **How:** full-width `st.plotly_chart(photography_score_chart(scored))`. Mark the best hour if you can.
- [ ] **Task:** Add temperature and clouds/rain charts. **How:** `st.columns(2)` + the other two functions in `charts.py`.
- [ ] **Task:** Try the app on your computer. **How:** `streamlit run app.py`. Portrait in Tel Aviv, sunset in Haifa, missing key if you temporarily rename `.env`.
- [ ] **Task:** Write how a classmate can run the project. **How:** update `README.md` (install, `.env`, `streamlit run app.py`, never commit the key).
- [ ] **Optional:** Highlight the photographer's preferred time on the score chart. Skip until the main chart works.

---

## Rules

- Do not commit `.env` or `.streamlit/secrets.toml`
- Do not copy a finished weather app — your product is a photography decision tool
- Follow the page mockup; do not add screens that are not on it
- One owner per file
- Decide score weights together; do not download a "perfect" formula
- Write the core logic yourselves — do not copy a finished weather app
