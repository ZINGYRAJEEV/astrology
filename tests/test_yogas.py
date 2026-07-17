"""Tests for the yoga detector."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.yogas import detect_yogas, yogas_markdown

BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)

_VALID_CATEGORIES = {
    "Pancha Mahapurusha", "Lunar", "Conjunction", "Raj Yoga", "Wealth",
    "Vipreet Raja", "Reputation", "Cancellation",
}


def test_detect_yogas_structure():
    chart = compute_chart(BIRTH)
    yogas = detect_yogas(chart)
    assert isinstance(yogas, list)
    for y in yogas:
        assert y["name"] and y["detail"]
        assert y["category"] in _VALID_CATEGORIES
        assert y["tone"] in ("benefic", "malefic", "mixed")


def test_yogas_deterministic():
    chart = compute_chart(BIRTH)
    assert [y["name"] for y in detect_yogas(chart)] == [y["name"] for y in detect_yogas(chart)]


def test_yogas_markdown():
    chart = compute_chart(BIRTH)
    md = yogas_markdown(detect_yogas(chart), "Test Native")
    assert "Yogas in the chart" in md


def test_multiple_charts_run():
    # a spread of birth data should all detect without error
    for year in (1975, 1985, 1995, 2005):
        b = BirthData(name="X", year=year, month=8, day=20, hour=10, minute=0,
                      latitude=19.076, longitude=72.8777, tz_offset=5.5, place="Mumbai")
        detect_yogas(compute_chart(b))


if __name__ == "__main__":
    test_detect_yogas_structure()
    test_yogas_deterministic()
    test_yogas_markdown()
    test_multiple_charts_run()
    print("Yoga tests passed.")
