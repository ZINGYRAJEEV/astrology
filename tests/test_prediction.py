"""Tests for astrology prediction engine."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.prediction import generate_prediction, predict_from_birth, prediction_markdown


BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)


def test_generate_prediction():
    chart = compute_chart(BIRTH)
    pred = generate_prediction(chart, "Career & success")
    assert pred["name"] == "Test Native"
    assert pred["panchang_at_birth"]["nakshatra"]
    assert pred["panchang_at_birth"]["tithi"]
    assert len(pred["life_predictions"]) >= 6
    assert pred["timing"]["birth_nakshatra_lord"]
    assert pred["opening"]
    print("Nakshatra:", pred["panchang_at_birth"]["nakshatra"])
    print("Areas:", len(pred["life_predictions"]))


def test_predict_from_birth():
    pred = predict_from_birth(BIRTH, "Marriage & relationships")
    assert pred["focus_intent"] == "Marriage & relationships"
    md = prediction_markdown(pred)
    assert "Astrology Prediction" in md
    assert len(md) > 500


if __name__ == "__main__":
    test_generate_prediction()
    test_predict_from_birth()
    print("\nPrediction tests passed.")
