"""Tests for the 'Today for You' daily dashboard."""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.daily_dashboard import build_dashboard

BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)


def test_build_dashboard():
    chart = compute_chart(BIRTH)
    db = build_dashboard(chart, date(2026, 3, 10), 28.6139, 77.209, 5.5, "New Delhi")
    assert db["name"] == "Test Native"
    assert 0 <= db["score"] <= 100
    assert db["verdict"] in ("Auspicious", "Workable", "Avoid")
    assert db["headline"]
    assert db["panchang"]["tithi"] and db["panchang"]["nakshatra"]
    assert db["panchang"]["sunrise"] and db["panchang"]["sunset"]
    # three inauspicious windows: Rahu, Yamaganda, Gulika
    assert len(db["avoid_windows"]) == 3
    assert db["dasha"]["line"]
    assert "sade_sati" in db and "note" in db["sade_sati"]
    assert db["guru_gochar"]
    assert db["janma_nakshatra"] and db["moon_sign"]


def test_dashboard_personalised_notes():
    chart = compute_chart(BIRTH)
    db = build_dashboard(chart, date(2026, 3, 10), 28.6139, 77.209, 5.5, "New Delhi")
    # personalised scan includes Tarabala + Chandrabala notes among positives
    joined = " ".join(db["positives"])
    assert "Tarabala" in joined
    assert "Chandrabala" in joined


if __name__ == "__main__":
    test_build_dashboard()
    test_dashboard_personalised_notes()
    print("Dashboard tests passed.")
