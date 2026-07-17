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
    rk = pred["rishikesh"]
    assert rk["ishtakal"]["formatted"]
    assert rk["navaratna"]["percent"] > 0
    assert rk["avakhada"]["varna"] in ("Brahmin", "Kshatriya", "Vaishya", "Shudra")
    assert rk["avakhada"]["gana"] in ("Deva", "Manushya", "Rakshasa")
    assert len(rk["navaratna"]["breakdown"]) == 7
    assert pred["timing"]["guru_gochar"]
    nar = pred["narrative"]
    assert nar["overview"] and len(nar["overview"]) >= 4
    assert "Health" in nar["deep_dives"]
    assert nar["deep_dives"]["Health"]
    assert "weak_planets" in pred
    assert "yogas" in pred and isinstance(pred["yogas"], list)
    assert "divisional" in pred and len(pred["divisional"]) == 3
    for d in pred["divisional"]:
        assert d["lagna_sign"] and d["note"]
    combos = pred["combinations_reading"]
    assert combos["nutshell"] and combos["areas"]
    for block in combos["areas"]:
        assert block["area"] and block["lines"]
        for ln in block["lines"]:
            assert ln["text"] and ln["tone"] in {"good", "caution", "neutral"}
            assert ln["reason"]
    print("Nakshatra:", pred["panchang_at_birth"]["nakshatra"])
    print("Navaratna:", rk["navaratna"]["verdict"], rk["navaratna"]["percent"])
    print("Areas:", len(pred["life_predictions"]))


def test_predict_from_birth():
    pred = predict_from_birth(BIRTH, "Marriage & relationships")
    assert pred["focus_intent"] == "Marriage & relationships"
    md = prediction_markdown(pred)
    assert "Life Prediction" in md
    assert "At a glance" in md
    assert "Technical basis" in md
    assert "How to read verdicts" in md or "Supported" in md
    assert "Your reading in plain words" in md
    assert "Ask about a specific area" in md
    assert len(md) > 500


if __name__ == "__main__":
    test_generate_prediction()
    test_predict_from_birth()
    print("\nPrediction tests passed.")
