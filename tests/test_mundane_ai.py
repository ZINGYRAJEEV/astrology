"""Tests for AI / tech mundane Prashna overlay (Lahiri)."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.mundane_ai import AI_PRESETS, analyze_ai_themes
from astro.prashna import QUESTION_TYPES, answer_prashna


WHEN = datetime(2026, 9, 16, 22, 30)
LAT, LON, TZ, PLACE = 28.6139, 77.2090, 5.5, "New Delhi, India"


def test_tech_question_types_exist():
    for key in ("ai_future", "ai_career", "ai_risk"):
        assert key in QUESTION_TYPES
        assert QUESTION_TYPES[key]["mode"] == "tech"


def test_analyze_ai_themes():
    for p in AI_PRESETS:
        res = analyze_ai_themes(p["key"], WHEN, LAT, LON, TZ, PLACE, question_text=p["question"])
        assert res["verdict"] in {"Favourable", "Mixed", "Unfavourable"}
        assert 5 <= res["score"] <= 95
        assert len(res["significators"]) == 3
        assert res["horizon"]
        assert "Lahiri" in res["method"]
        assert "chart" not in res


def test_tech_prashna_direct():
    res = answer_prashna("ai_future", WHEN, LAT, LON, TZ, PLACE)
    assert res["reasons"]
    assert any("Mercury" in r or "Rahu" in r or "Saturn" in r for r in res["reasons"])


if __name__ == "__main__":
    test_tech_question_types_exist()
    test_analyze_ai_themes()
    test_tech_prashna_direct()
    print("mundane AI tests OK")
