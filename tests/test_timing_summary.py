"""Tests for visual timing summary (Mahadasha / Antardasha impact map)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from astro.chart_engine import BirthData, compute_chart
from astro.timing_summary import build_timing_summary, timing_summary_markdown
from astro.timing_viz import timing_d3_html
from astro.prediction import generate_prediction


BIRTH = BirthData(
    name="Neev", year=2015, month=8, day=15, hour=10, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi",
)


def test_timing_summary_structure():
    chart = compute_chart(BIRTH)
    when = datetime(2025, 9, 1, 12, 0)
    summary = build_timing_summary(chart, when=when, horizon_years=6)
    assert summary["areas"] == ["Career", "Wealth", "Family", "Health", "Spiritual"]
    assert summary["current"]["maha"]
    assert summary["current"]["antar"]
    assert summary["chapters"], "expected upcoming antardasha chapters"
    ch = summary["chapters"][0]
    assert set(ch["scores"]) == set(summary["areas"])
    for area, row in ch["scores"].items():
        assert 5 <= row["score"] <= 95
        assert row["tone"] in ("good", "mixed", "bad")
        assert row["note"]
    assert ch["phases"] and len(ch["phases"]) == 3
    assert summary["years"], "expected year risk/opportunity map"
    y = summary["years"][0]
    assert "tag" in y and y["risks"] is not None and y["opportunities"] is not None


def test_timing_d3_html_embeds_data():
    chart = compute_chart(BIRTH)
    summary = build_timing_summary(chart, when=datetime(2025, 9, 1), horizon_years=4)
    from astro.timing_viz import timeline_figure, impact_figure, timing_d3_html
    assert timeline_figure(summary) is not None
    assert impact_figure(summary) is not None
    html = timing_d3_html(summary)
    assert "d3@7" in html
    assert summary["chapters"][0]["label"].split(" / ")[0] in html


def test_prediction_includes_timing_summary():
    chart = compute_chart(BIRTH)
    pred = generate_prediction(chart, horizon_years=5)
    assert "timing_summary" in pred
    assert pred["timing_summary"]["chapters"]
    md = timing_summary_markdown(pred["timing_summary"])
    assert "Timing map" in md
    assert "Year risk" in md


if __name__ == "__main__":
    test_timing_summary_structure()
    test_timing_d3_html_embeds_data()
    test_prediction_includes_timing_summary()
    print("timing summary tests OK")
