"""Tests for Hindi planet labels and nature/behaviour profile."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro import reference as ref
from astro.chart_engine import BirthData, compute_chart
from astro.nature_profile import build_nature_profile
from astro.prediction import generate_prediction


BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)


def test_planet_and_sign_hindi_labels():
    assert ref.planet_label("Sun") == "Sun (सूर्य)"
    assert ref.planet_label("Jupiter") == "Jupiter (गुरु)"
    assert ref.sign_label("Aries") == "Aries (मेष)"
    assert "सूर्य" in ref.with_hindi_planets("The Sun and Moon are strong.")
    assert "चंद्रमा" in ref.with_hindi_planets("The Sun and Moon are strong.")
    # Do not double-annotate.
    once = ref.with_hindi_planets("Sun (सूर्य) is bright")
    assert once.count("सूर्य") == 1


def test_nature_profile_structure():
    chart = compute_chart(BIRTH)
    profile = build_nature_profile(chart)
    assert profile["portrait"]
    assert profile["traits"]
    assert len(profile["placements"]) == 9
    for pl in profile["placements"]:
        assert "(" in pl["label"] and pl["nature"]
        assert 1 <= pl["house"] <= 12


def test_prediction_includes_hindi_and_nature():
    pred = generate_prediction(compute_chart(BIRTH))
    assert pred["nature_profile"]["placements"]
    assert "सूर्य" in pred["narrative"]["overview"][0][1] or "Moon (चंद्रमा)" in pred["narrative"]["overview"][0][1]


if __name__ == "__main__":
    test_planet_and_sign_hindi_labels()
    test_nature_profile_structure()
    test_prediction_includes_hindi_and_nature()
    print("Nature profile tests passed.")
