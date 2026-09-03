"""Generate colorful Role A / Role B PDF playbooks. Run from weather-project/: python docs/generate_role_playbooks.py"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT_DIR = Path(__file__).resolve().parent

NAVY = HexColor("#12323C")
GOLD = HexColor("#C47B2B")
CREAM = HexColor("#FFF8F0")
SAND = HexColor("#F4ECE1")
TEAL = HexColor("#1F7A6C")
CORAL = HexColor("#C45C3E")
INK = HexColor("#1B1F24")
MUTED = HexColor("#5C656C")
A_BANNER = HexColor("#1B4F63")
B_BANNER = HexColor("#8A4A16")
CHECK = HexColor("#E8D5B5")


def register_fonts() -> tuple[str, str]:
    segoe = Path(r"C:\Windows\Fonts\segoeui.ttf")
    segoe_b = Path(r"C:\Windows\Fonts\segoeuib.ttf")
    if segoe.exists() and segoe_b.exists():
        pdfmetrics.registerFont(TTFont("Playbook", str(segoe)))
        pdfmetrics.registerFont(TTFont("Playbook-Bold", str(segoe_b)))
        return "Playbook", "Playbook-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_B = register_fonts()


class Banner(Flowable):
    def __init__(self, text: str, color: Color, height: float = 18 * mm):
        super().__init__()
        self.text = text
        self.color = color
        self.height = height
        self.width = 0

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.height

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=0)
        self.canv.setFillColor(white)
        self.canv.setFont(FONT_B, 13)
        self.canv.drawString(8 * mm, self.height / 2 - 4, self.text)


class ColorCard(Flowable):
    def __init__(self, title: str, body: str, fill: Color, title_color: Color, width_hint: float | None = None):
        super().__init__()
        self.title = title
        self.body = body
        self.fill = fill
        self.title_color = title_color
        self._width = width_hint or 170 * mm
        self._body = Paragraph(
            body,
            ParagraphStyle(
                "cardbody",
                fontName=FONT,
                fontSize=9.5,
                leading=13,
                textColor=INK,
            ),
        )
        self._title_h = 16
        pad = 10
        bw, bh = self._body.wrap(self._width - 2 * pad, 800)
        self._bh = bh
        self.height = pad + self._title_h + 6 + bh + pad
        self.width = self._width

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        pad = 10
        self._body.wrap(availWidth - 2 * pad, 800)
        self.height = pad + self._title_h + 6 + self._bh + pad
        return availWidth, self.height

    def draw(self):
        self.canv.setFillColor(self.fill)
        self.canv.roundRect(0, 0, self.width, self.height, 8, fill=1, stroke=0)
        self.canv.setFillColor(self.title_color)
        self.canv.setFont(FONT_B, 11)
        self.canv.drawString(10, self.height - 18, self.title)
        self._body.drawOn(self.canv, 10, 10)


class FooterCanvas:
    def __init__(self, role_label: str, banner: Color):
        self.role_label = role_label
        self.banner = banner

    def __call__(self, canv, doc):
        canv.saveState()
        canv.setFillColor(self.banner)
        canv.rect(0, 0, A4[0], 12 * mm, fill=1, stroke=0)
        canv.setFillColor(white)
        canv.setFont(FONT, 8)
        canv.drawString(16 * mm, 5 * mm, f"Shoot Window  ·  {self.role_label}  ·  Nathalia & Dafna")
        canv.drawRightString(A4[0] - 16 * mm, 5 * mm, f"Page {doc.page}")
        canv.setFillColor(GOLD)
        canv.rect(0, A4[1] - 6 * mm, A4[0], 6 * mm, fill=1, stroke=0)
        canv.restoreState()


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("H1c", fontName=FONT_B, fontSize=22, leading=26, textColor=NAVY, spaceAfter=6, alignment=TA_CENTER))
    s.add(ParagraphStyle("H2", fontName=FONT_B, fontSize=14, leading=18, textColor=NAVY, spaceBefore=10, spaceAfter=6))
    s.add(ParagraphStyle("H3", fontName=FONT_B, fontSize=11.5, leading=15, textColor=GOLD, spaceBefore=8, spaceAfter=4))
    s.add(ParagraphStyle("Body", fontName=FONT, fontSize=10, leading=14, textColor=INK, spaceAfter=6))
    s.add(ParagraphStyle("Small", fontName=FONT, fontSize=9, leading=12.5, textColor=MUTED, spaceAfter=4))
    s.add(ParagraphStyle("Center", fontName=FONT, fontSize=10.5, leading=14.5, textColor=INK, alignment=TA_CENTER, spaceAfter=6))
    s.add(ParagraphStyle("Tag", fontName=FONT_B, fontSize=9, leading=12, textColor=GOLD, alignment=TA_CENTER, spaceAfter=2))
    s.add(ParagraphStyle("Task", fontName=FONT, fontSize=9.5, leading=13, textColor=INK))
    s.add(ParagraphStyle("TaskB", fontName=FONT_B, fontSize=9.5, leading=13, textColor=NAVY))
    s.add(ParagraphStyle("WhiteC", fontName=FONT_B, fontSize=11, leading=14, textColor=white, alignment=TA_CENTER))
    s.add(ParagraphStyle("Cell", fontName=FONT, fontSize=8.5, leading=11.5, textColor=INK))
    s.add(ParagraphStyle("CellB", fontName=FONT_B, fontSize=8.5, leading=11.5, textColor=NAVY))
    s.add(ParagraphStyle("Check", fontName=FONT, fontSize=9.5, leading=13, textColor=INK, leftIndent=4))
    return s


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def section_table(headers: list[str], rows: list[list[str]], header_bg: Color, S) -> Table:
    data = [[p(h, S["CellB"]) for h in headers]]
    for row in rows:
        data.append([p(c, S["Cell"]) for c in row])
    col_w = (A4[0] - 36 * mm) / len(headers)
    t = Table(data, colWidths=[col_w] * len(headers))
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("BACKGROUND", (0, 1), (-1, -1), CREAM),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, SAND]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#E0D4C4")),
                ("BOX", (0, 0), (-1, -1), 1, header_bg),
            ]
        )
    )
    return t


def checkbox_block(items: list[tuple[str, str]], S) -> list:
    flow = []
    for title, how in items:
        inner = Table(
            [[p(f"☐   <b>{title}</b><br/>{how}", S["Check"])]],
            colWidths=[A4[0] - 36 * mm],
        )
        inner.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), CHECK),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("BOX", (0, 0), (-1, -1), 0.6, GOLD),
                ]
            )
        )
        flow.append(KeepTogether([inner, Spacer(1, 3.5 * mm)]))
    return flow


def together_block(S) -> list:
    return [
        Banner("TOGETHER — you both do these (do not split)", GOLD, 14 * mm),
        Spacer(1, 4 * mm),
        p(
            "These are the only times you must sit together. The rest of the week you can work in parallel.",
            S["Body"],
        ),
        section_table(
            ["When", "What you do together", "Done when"],
            [
                [
                    "Meeting 1 · start",
                    "Decide Role A / Role B (10 min). Copy <b>.env.example → .env</b>, paste the API key. Install with <b>pip install -r requirements.txt</b>.",
                    "Each person knows her files. .env exists. Never commit it.",
                ],
                [
                    "Meeting 2 · notebook",
                    "Open <b>notebooks/01_forecast_api_colab.ipynb</b>. GET <b>/data/2.5/forecast</b> for Tel Aviv. Print <b>status_code</b>, then temp, wind, clouds, pop, sunset.",
                    "You see <b>200</b>. Do not open Streamlit yet.",
                ],
                [
                    "Meeting 3 · weights",
                    "On paper: for portrait, sunset, landscape write rain / wind / temperature / clouds weights that add to <b>1.0</b>. Ask: what would cancel this shoot first?",
                    "Both can explain portrait vs sunset. Put numbers in <b>SHOOT_WEIGHTS</b>.",
                ],
                [
                    "Meeting 4 · plug in",
                    "Connect <b>app.py</b> to real <b>get_forecast</b> + <b>score_forecast</b>. Try Tel Aviv portrait tomorrow 17:00. Try an error case.",
                    "The page shows a Photography Score. Mistakes show <b>st.error</b>, not a traceback.",
                ],
                [
                    "Meeting 5 · ship",
                    "GitHub without secrets (<b>docs/DEPLOY.md</b>). Streamlit Cloud, secret name <b>OPENWEATHER_API_KEY</b>. Screenshots of score + error.",
                    "Public URL works. <b>.env</b> is not on GitHub.",
                ],
            ],
            TEAL,
            S,
        ),
        Spacer(1, 4 * mm),
        ColorCard(
            "You will NOT wait all week",
            "Field names and function names are already in the starter files. "
            "Role A fills how they work. Role B can already use the names. "
            "The only way to block each other is changing a field name in models.py without saying so.",
            HexColor("#D8F3EF"),
            TEAL,
        ),
    ]


def cover(role: str, subtitle: str, banner: Color, S) -> list:
    tag = "ROLE A PLAYBOOK" if role == "A" else "ROLE B PLAYBOOK"
    return [
        Spacer(1, 8 * mm),
        p("SHOOT WINDOW", S["Tag"]),
        p(tag, S["H1c"]),
        p(subtitle, S["Center"]),
        Spacer(1, 3 * mm),
        Banner(f"Pair project  ·  Nathalia & Dafna  ·  Role {role}", banner, 12 * mm),
        Spacer(1, 5 * mm),
        p(
            "<b>This is not a weather app.</b> Weather is the input. The product is a decision tool "
            "for outdoor photographers in Israel.",
            S["Center"],
        ),
        p(
            "Photographer asks: <i>I have a portrait in Tel Aviv tomorrow at 17:00. "
            "Should I shoot then — and is there a better window?</i>",
            S["Center"],
        ),
        Spacer(1, 2 * mm),
        ColorCard(
            "The product formula",
            "Weather Data  →  Analysis  →  Photography Score  →  Recommendation  →  Decision",
            SAND,
            GOLD,
        ),
        Spacer(1, 3 * mm),
        p(
            "Fill the <b># TODO (STUDENT)</b> comments. Do not copy a finished weather app. "
            "One owner per file.",
            S["Small"],
        ),
    ]


def build_role_a(path: Path) -> None:
    S = styles()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="Shoot Window — Role A playbook",
        author="Nathalia & Dafna",
    )
    story: list = []
    story += cover("A", "Data + Photography Score", A_BANNER, S)

    story.append(p("Your job in one sentence", S["H2"]))
    story.append(
        p(
            "You turn forecast JSON into a <b>ForecastReport</b>, then into a <b>Photography Score (0–100)</b> "
            "and a <b>best shooting window</b>. Role B only displays what you return. She does not parse JSON.",
            S["Body"],
        )
    )

    story.append(p("Your files — what each one is for", S["H2"]))
    story.append(
        section_table(
            ["File", "Function (what you write)", "Who calls it"],
            [
                [
                    "<b>photo_planner/models.py</b>",
                    "<b>HourlyConditions.from_slot_json</b> — one 3-hour slot.<br/>"
                    "<b>ForecastReport.from_api_json</b> — city + list of hours + sunrise/sunset.",
                    "client.py and tests (sample JSON, no internet)",
                ],
                [
                    "<b>photo_planner/validation.py</b>",
                    "<b>normalize_city_name</b> — strip spaces, reject empty.<br/>"
                    "<b>normalize_shoot_type</b> — portrait / sunset / landscape only.",
                    "client.py and scoring.py",
                ],
                [
                    "<b>photo_planner/errors.py</b>",
                    "Already written (KEEP). You <b>raise</b> these errors. Do not invent new classes unless you need a new case.",
                    "app.py catches WeatherError",
                ],
                [
                    "<b>photo_planner/client.py</b>",
                    "<b>OpenWeatherClient.get_forecast</b> — GET the 5-day / 3-hour forecast.<br/>"
                    "<b>_params</b> — dict with q, appid, units.",
                    "app.py after Plan shoot",
                ],
                [
                    "<b>photo_planner/scoring.py</b>",
                    "<b>THE PRODUCT.</b> photography_score, hours_on_date, score_forecast, best_shooting_window.<br/>"
                    "Agree <b>SHOOT_WEIGHTS</b> with Role B on paper first.",
                    "app.py · tests/test_scoring.py",
                ],
                [
                    "<b>tests/</b>",
                    "Remove <b>@pytest.mark.skip</b> after each function works. Run <b>pytest</b> from weather-project/.",
                    "You, after each step",
                ],
                [
                    "<b>data/sample_forecast.json</b>",
                    "Do not edit. Use it as a map while you write from_slot_json. Date <b>2026-09-04</b> has 4 slots (+ 1 extra day to test the filter).",
                    "models.py and tests",
                ],
            ],
            A_BANNER,
            S,
        )
    )

    story.append(p("Your functions — fill these TODOs", S["H2"]))
    story.append(
        section_table(
            ["Function", "Receives", "Must return"],
            [
                ["from_slot_json", "one dict from payload[\"list\"]", "HourlyConditions (all fields)"],
                ["from_api_json", "full forecast JSON", "ForecastReport (city + hours list)"],
                ["normalize_city_name", "whatever the user typed", "clean name or InvalidCityError"],
                ["normalize_shoot_type", "\"Portrait\" etc.", "\"portrait\" or InvalidShootTypeError"],
                ["get_forecast", "city name", "ForecastReport, or 401/404 named errors"],
                ["photography_score", "one hour + shoot type", "float 0–100"],
                ["hours_on_date", "ForecastReport + \"YYYY-MM-DD\"", "only hours that day"],
                ["score_forecast", "forecast + type + date", "list of (hour, score)"],
                ["best_shooting_window", "scored hours", "(start, end, score) — MVP = best 3-hour slot"],
            ],
            TEAL,
            S,
        )
    )

    story.append(PageBreak())
    story += together_block(S)

    story.append(p("Your solo path (Role B is not blocked)", S["H2"]))
    story.append(
        p(
            "You do <b>not</b> need Streamlit. Sample JSON + pytest are enough until Meeting 4.",
            S["Body"],
        )
    )
    story.append(
        ColorCard(
            "Order — one file at a time",
            "1. Notebook with Role B until 200.<br/>"
            "2. models.py using sample_forecast.json (freeze field names — they are already KEEP).<br/>"
            "3. validation.py<br/>"
            "4. client.py get_forecast for Tel Aviv<br/>"
            "5. Meeting 3: weights on paper with Role B<br/>"
            "6. scoring.py (the product)<br/>"
            "7. Turn tests on, run pytest<br/>"
            "8. Meeting 4: help Role B plug app.py into your functions",
            HexColor("#E4F0F5"),
            A_BANNER,
        )
    )

    story.append(p("Contract — do not rename these fields", S["H2"]))
    story.append(
        p(
            "Role B already builds charts from these names. If the UI needs a new field, add it here first and tell her.",
            S["Small"],
        )
    )
    story.append(
        section_table(
            ["Object", "Fields Role B will read"],
            [
                [
                    "HourlyConditions",
                    "time_text, timestamp_unix, temperature_c, feels_like_c, humidity, wind_speed, cloud_cover, rain_probability, rain_mm, description, icon",
                ],
                [
                    "ForecastReport",
                    "city, country, latitude, longitude, timezone_offset_seconds, sunrise_unix, sunset_unix, hours",
                ],
            ],
            CORAL,
            S,
        )
    )
    story.append(
        p(
            "Hints: <b>pop</b> is 0–1 (0.4 = 40% rain). The key <b>\"3h\"</b> is a string. "
            "<b>rain</b> is often missing — use .get. Endpoint is <b>/data/2.5/forecast</b>, not current weather.",
            S["Small"],
        )
    )

    story.append(p("Your checklist", S["H2"]))
    story += checkbox_block(
        [
            ("API key only on your computer", "Create key → copy .env.example to .env → paste. Never commit .env."),
            ("Read one raw forecast slot", "After 200, print city name, len(list), temp, pop, clouds."),
            ("Parse sample JSON in models.py", "from_slot_json + from_api_json with data/sample_forecast.json."),
            ("Validate city and shoot type", "Both functions in validation.py."),
            ("Live request in client.py", "Clean name, requests.get, return ForecastReport.from_api_json(...)."),
            ("Map HTTP failures to errors", "401 InvalidApiKeyError · 404 CityNotFoundError · else WeatherRequestError."),
            ("Filter hours to the booked date", "hours_on_date — 2026-09-04 keeps 4 slots."),
            ("Write photography_score", "Each weather field → 0–100 goodness, then SHOOT_WEIGHTS."),
            ("score_forecast + best_shooting_window", "MVP = the single best 3-hour slot."),
            ("pytest passes", "Delete @pytest.mark.skip as you go. Run pytest from weather-project/."),
        ],
        S,
    )

    story.append(p("Rules", S["H2"]))
    story.append(
        p(
            "Do not commit secrets. Do not copy a weather app. Do not download a “perfect” score formula — "
            "you and Role B decide the weights. Fill TODOs yourself.",
            S["Body"],
        )
    )

    doc.build(story, onFirstPage=FooterCanvas("Role A · Data + Score", A_BANNER), onLaterPages=FooterCanvas("Role A · Data + Score", A_BANNER))


def build_role_b(path: Path) -> None:
    S = styles()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="Shoot Window — Role B playbook",
        author="Nathalia & Dafna",
    )
    story: list = []
    story += cover("B", "Page + charts  ·  the photographer’s screen", B_BANNER, S)

    story.append(p("Your job in one sentence", S["H2"]))
    story.append(
        p(
            "You show a <b>decision</b>, not a weather dump. After Plan shoot the photographer must see: "
            "Photography Score, best shooting window, one calm sentence, then charts. "
            "You never parse JSON in <b>app.py</b> — you only display what Role A returns.",
            S["Body"],
        )
    )

    story.append(p("Your files — what each one is for", S["H2"]))
    story.append(
        section_table(
            ["File", "Function (what you write)", "Notes"],
            [
                [
                    "<b>photo_planner/charts.py</b>",
                    "<b>photography_score_chart</b> — score vs time (the product chart).<br/>"
                    "<b>temperature_chart</b> · <b>clouds_and_rain_chart</b>.",
                    "No API calls. Return Plotly figures only.",
                ],
                [
                    "<b>app.py</b>",
                    "Coordinator. Inputs are already KEEP. After the button: call client + scoring, then layout.",
                    "Catch WeatherError with st.error. No CSS. No extra pages.",
                ],
                [
                    "<b>.streamlit/config.toml</b>",
                    "Warm theme already set. You may tweak later. Not required to learn the API.",
                    "Leave it for the MVP.",
                ],
                [
                    "<b>README.md</b>",
                    "How a classmate runs the project: install, .env, streamlit run app.py, never commit the key.",
                    "Last polish before GitHub.",
                ],
            ],
            B_BANNER,
            S,
        )
    )

    story.append(p("Your functions", S["H2"]))
    story.append(
        section_table(
            ["Function", "Receives", "Must return"],
            [
                ["photography_score_chart", "list of (HourlyConditions, score)", "Plotly figure, score 0–100 vs clock time"],
                ["temperature_chart", "same list", "Plotly figure of temperature_c"],
                ["clouds_and_rain_chart", "same list", "Plotly figure of clouds and/or rain (pop × 100 if you want % )"],
            ],
            TEAL,
            S,
        )
    )

    story.append(p("Page mockup — build this, nothing extra", S["H2"]))
    story.append(
        p(
            "One Streamlit page. Decision first, weather second. Skip: custom CSS, maps, login, comparing 3 cities, minute-perfect windows.",
            S["Small"],
        )
    )
    story.append(
        section_table(
            ["Order", "What the photographer sees", "Streamlit widget"],
            [
                ["0 · already done", "Location, date, 17:00, photography type, Plan shoot", "st.columns(4) + st.button (KEEP)"],
                ["1", "Tel Aviv · date · portrait", "st.caption"],
                ["2", "87/100 · 18:00–21:00 · booked 17:00 score 83", "st.columns(3) + st.metric"],
                ["3", "One or two recommendation sentences", "st.success(...)"],
                ["4", "Photography Score during the day (mark the peak)", "st.plotly_chart — full width"],
                ["5", "Temperature  |  clouds &amp; rain", "st.columns(2) + two charts"],
                ["6 optional", "Why this hour? wind / rain / clouds", "st.expander"],
                ["Error", "One red sentence, no traceback", "except WeatherError: st.error(...)"],
            ],
            GOLD,
            S,
        )
    )

    story.append(PageBreak())
    story += together_block(S)

    story.append(p("Your solo path (Role A is not a blocker)", S["H2"]))
    story.append(
        ColorCard(
            "Use fake scores until Meeting 4",
            "Build two fake HourlyConditions (copy the field names from models.py) and pair them with scores 72 and 94. "
            "Draw the three charts and the metric layout with that list. "
            "When Role A finishes, replace the fake list with score_forecast(forecast, shoot_type, date). "
            "Do not wait for the live API to start charts.py.",
            HexColor("#FDE8D0"),
            B_BANNER,
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(
        ColorCard(
            "Order — one step at a time",
            "1. Notebook with Role A until 200. Note photographer fields: time, temp, wind, clouds, pop, sunset.<br/>"
            "2. Wait only for field names (already KEEP in models.py).<br/>"
            "3. Meeting 3: weights on paper (you help decide; Role A codes them).<br/>"
            "4. charts.py — score chart first, then the other two.<br/>"
            "5. app.py layout with fake data matching the mockup.<br/>"
            "6. Meeting 4: wire get_forecast + score_forecast, catch WeatherError.<br/>"
            "7. Test locally, then README, then help deploy.",
            HexColor("#F8E6D2"),
            CORAL,
        )
    )

    story.append(p("What you read from Role A (do not parse JSON)", S["H2"]))
    story.append(
        p(
            "hour.time_text · hour.temperature_c · hour.wind_speed · hour.cloud_cover · hour.rain_probability<br/>"
            "scored_hours is a list of (hour, float). window is (start, end, best_score).",
            S["Body"],
        )
    )
    story.append(
        p(
            "If you need a new field (for example visibility), Role A adds it on HourlyConditions first.",
            S["Small"],
        )
    )

    story.append(p("Your checklist", S["H2"]))
    story += checkbox_block(
        [
            ("Notebook: photographer fields", "Time, temperature, wind, clouds, rain chance, sunset."),
            ("Photography Score chart", "Fill photography_score_chart. X = clock, Y = 0–100. No API in charts.py."),
            ("Decision row after Plan shoot", "Three st.metric then st.success. Catch WeatherError with st.error."),
            ("Score chart on the page", "Full-width st.plotly_chart. Mark the best hour if you can."),
            ("Temperature + clouds/rain", "st.columns(2) and the other two chart functions."),
            ("Try the app locally", "streamlit run app.py. Portrait Tel Aviv 17:00, sunset Haifa, missing-key error."),
            ("README for a classmate", "Install, .env, streamlit run app.py, never commit the key."),
            ("Optional: mark preferred time", "Highlight 17:00 on the score chart. Skip until the main chart works."),
        ],
        S,
    )

    story.append(p("Tone of the page", S["H2"]))
    story.append(
        p(
            "Words for a photographer: “excellent”, “windy for portrait”, “prefer 18:00”. "
            "Not “payload keys” or “status 200”. Default Plotly line charts — not 3D gauges. "
            "Theme is already in config.toml.",
            S["Body"],
        )
    )
    story.append(
        p(
            "Rules: no secrets on GitHub, no copied weather app, no extra screens, one owner per file, "
            "weights decided together, fill TODOs yourself.",
            S["Small"],
        )
    )

    doc.build(story, onFirstPage=FooterCanvas("Role B · Page + Charts", B_BANNER), onLaterPages=FooterCanvas("Role B · Page + Charts", B_BANNER))


def main() -> None:
    a = OUT_DIR / "playbook-role-a.pdf"
    b = OUT_DIR / "playbook-role-b.pdf"
    build_role_a(a)
    build_role_b(b)
    print(a)
    print(b)


if __name__ == "__main__":
    main()
