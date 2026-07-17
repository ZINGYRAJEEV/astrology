"""Tests for the Prashna (horary) engine."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.prashna import QUESTION_TYPES, answer_prashna
from astro import reference as ref

WHEN = datetime(2026, 7, 17, 14, 30)
LAT, LON, TZ, PLACE = 28.6139, 77.2090, 5.5, "New Delhi, India"


def test_all_question_types_run():
    for qtype in QUESTION_TYPES:
        res = answer_prashna(qtype, WHEN, LAT, LON, TZ, PLACE)
        assert 5.0 <= res["score"] <= 95.0
        assert res["verdict"] in {"Favourable", "Mixed", "Unfavourable"}
        assert res["lagna"] in ref.SIGNS
        assert res["moon_sign"] in ref.SIGNS
        assert res["reasons"]
        assert res["timing"]
        assert isinstance(res["yogas"], list)


def test_deterministic():
    a = answer_prashna("career", WHEN, LAT, LON, TZ, PLACE)
    b = answer_prashna("career", WHEN, LAT, LON, TZ, PLACE)
    assert a["score"] == b["score"]
    assert a["verdict"] == b["verdict"]


def test_verdict_matches_score():
    res = answer_prashna("marriage", WHEN, LAT, LON, TZ, PLACE)
    s = res["score"]
    if s >= 62:
        assert res["verdict"] == "Favourable"
    elif s >= 45:
        assert res["verdict"] == "Mixed"
    else:
        assert res["verdict"] == "Unfavourable"


if __name__ == "__main__":
    test_all_question_types_run()
    test_deterministic()
    test_verdict_matches_score()
    print("Prashna tests passed.")
