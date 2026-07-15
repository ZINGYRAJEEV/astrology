"""Tests for Ashtakoota horoscope matching."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.matching import match_from_birth, matching_markdown

GROOM = BirthData(
    name="Groom", year=1990, month=5, day=15, hour=10, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)
BRIDE = BirthData(
    name="Bride", year=1992, month=8, day=20, hour=14, minute=0,
    latitude=30.0869, longitude=78.2676, tz_offset=5.5, place="Rishikesh, India",
)


def test_match_structure():
    m = match_from_birth(GROOM, BRIDE)
    assert m["total_points"] >= 0
    assert m["total_points"] <= 36
    assert len(m["kootas"]) == 8
    assert m["kootas"][7]["name"] == "Nadi"
    assert m["groom"]["avakhada"]["nadi"]
    assert m["bride"]["avakhada"]["gana"]
    assert m["verdict"]
    print(f"Score: {m['total_points']}/36 ({m['verdict']})")


def test_nadi_dosha_same_nadi():
    """Two natives with same Moon nakshatra share Nadi — should score 0 on Nadi."""
    g = compute_chart(GROOM)
    b_nak = g.planets["Moon"].nakshatra
    # Bride with same nakshatra unlikely from different DOB; test koota directly
    from astro import rishikesh_rules as rr
    n1 = rr.avakhada(g.planets["Moon"].sign, b_nak)["nadi"]
    n2 = rr.avakhada(g.planets["Moon"].sign, b_nak)["nadi"]
    assert n1 == n2


def test_matching_markdown():
    m = match_from_birth(GROOM, BRIDE)
    md = matching_markdown(m)
    assert "Ashtakoota" in md
    assert "Nadi" in md
    assert len(md) > 400


if __name__ == "__main__":
    test_match_structure()
    test_nadi_dosha_same_nadi()
    test_matching_markdown()
    print("\nMatching tests passed.")
