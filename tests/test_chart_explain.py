"""Tests for Copilot-style chart explanation."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from astro.chart_engine import BirthData, compute_chart
from astro.chart_explain import build_chart_explain, chart_explain_markdown
from astro.prediction import generate_prediction


BIRTH = BirthData(
    name="Neev Kumar", year=2015, month=8, day=15, hour=10, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi",
)


def test_chart_explain_structure():
    chart = compute_chart(BIRTH)
    ex = build_chart_explain(chart, when=datetime(2025, 9, 1), horizon_years=6)
    assert "Neev" in ex["title"]
    assert ex["overall"]["score"] >= 5
    assert ex["identity"]["ascendant"]
    assert ex["current_chapter"]["maha"]
    assert len(ex["life_areas"]) == 5
    assert ex["timing_chapters"], "expected explained chapters"
    ch = ex["timing_chapters"][0]
    assert ch["why"]["maha"]["placement"]
    assert ch["why"]["antar"]["placement"]
    assert len(ch["phases"]) == 3
    assert "Career" in ch["phases"][0]["areas"]
    assert ch["takeaways"]
    assert ex["year_maps"]
    md = chart_explain_markdown(ex)
    assert "Core identity" in md
    assert "Timing breakdowns" in md
    assert "Year risk" in md


def test_prediction_includes_chart_explain():
    pred = generate_prediction(compute_chart(BIRTH), horizon_years=5)
    assert pred.get("chart_explain")
    assert pred["chart_explain"]["timing_chapters"]


if __name__ == "__main__":
    test_chart_explain_structure()
    test_prediction_includes_chart_explain()
    print("chart explain tests OK")
