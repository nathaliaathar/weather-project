# ============================================================
# WHAT THIS FILE DOES
# ============================================================
# This file marks photo_planner/ as a Python package
# (a folder you can import from).
#
# WHY THIS EXISTS:
# Without it, `from photo_planner.models import ForecastReport`
# would not work as a package import on some setups.
#
# You do not put assignment logic here.
# Person A owns client, models, validation, errors, scoring.
# Person B owns charts and the Streamlit UI in app.py.
# ============================================================

# WHY THIS EXISTS:
# Re-exporting these names lets other files write:
#     from photo_planner import ForecastReport, WeatherError
from photo_planner.errors import WeatherError  # KEEP
from photo_planner.models import ForecastReport, HourlyConditions  # KEEP

__all__ = ["WeatherError", "ForecastReport", "HourlyConditions"]  # KEEP
