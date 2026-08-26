"""Tests for concise planetary-position brief."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.position_brief import build_position_brief
from astro.prediction import generate_prediction, prediction_markdown


BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)


def test_position_brief_structure():
    brief = build_position_brief(compute_chart(BIRTH))
    assert brief["insight"]
    assert brief["summary"]
    names = [a["name"] for a in brief["areas"]]
    assert names == ["Career", "Wealth", "Family", "Health"]
    for area in brief["areas"]:
        assert area["bullets"]
        assert area["bullets"][0]["lead"]
    assert brief["gochara"]
    assert brief["key_positions"]


def test_prediction_includes_brief_and_markdown():
    pred = generate_prediction(compute_chart(BIRTH))
    assert pred["position_brief"]["areas"]
    md = prediction_markdown(pred)
    assert "Clear picture by life area" in md
    assert "### Career" in md
    assert "Gochara (transit) overlay" in md


if __name__ == "__main__":
    test_position_brief_structure()
    test_prediction_includes_brief_and_markdown()
    print("Position brief tests passed.")
