"""Tests for the Sahams (Tajika sensitive points) engine."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.sahams import SAHAMS, compute_sahams, is_day_birth, sahams_markdown, _saham_longitude
from astro import reference as ref

BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)


def test_sahams_structure():
    chart = compute_chart(BIRTH)
    sahams = compute_sahams(chart)
    assert len(sahams) == len(SAHAMS)
    for s in sahams:
        assert s["sign"] in ref.SIGNS
        assert 1 <= s["house"] <= 12
        assert 0 <= s["longitude"] < 360
        assert s["lord"] in ref.PLANETS


def test_day_night_reversal():
    chart = compute_chart(BIRTH)
    day = _saham_longitude(chart, "Moon", "Sun", True)
    night = _saham_longitude(chart, "Moon", "Sun", False)
    # Reversing operands gives a different point (unless Moon==Sun longitude).
    assert abs(day - night) > 1e-6


def test_deterministic_and_markdown():
    chart = compute_chart(BIRTH)
    a = compute_sahams(chart)
    b = compute_sahams(chart)
    assert [x["longitude"] for x in a] == [x["longitude"] for x in b]
    md = sahams_markdown(a, "Test Native", is_day_birth(chart))
    assert "Punya" in md


if __name__ == "__main__":
    test_sahams_structure()
    test_day_night_reversal()
    test_deterministic_and_markdown()
    print("Sahams tests passed.")
