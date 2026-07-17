"""Tests for the planetary-combinations reference and detector."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.combinations import (
    CONJUNCTIONS, NAKSHATRA_TRAIT, PLANET_IN_HOUSE, THREE_PLANET, chart_combinations,
    combinations_markdown, conjunction, house_lord_generic, layman_outcomes,
    outcome_balance, planet_in_house, three_planet,
)
from astro import reference as ref

BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)


def test_all_planet_house_entries_complete():
    for planet in ref.PLANETS:
        assert planet in PLANET_IN_HOUSE, planet
        for house in range(1, 13):
            info = PLANET_IN_HOUSE[planet][house]
            assert info["effect"] and info["merits"] and info["demerits"], (planet, house)


def test_conjunction_lookup_is_order_independent():
    for (a, b) in CONJUNCTIONS:
        assert conjunction(a, b) is not None
        assert conjunction(b, a) == conjunction(a, b)


def test_conjunction_keys_sorted():
    for key in CONJUNCTIONS:
        assert list(key) == sorted(key), key


def test_planet_in_house_lookup():
    info = planet_in_house("Sun", 10)
    assert info and "career" in info["effect"].lower()


def test_chart_combinations_structure():
    chart = compute_chart(BIRTH)
    data = chart_combinations(chart)
    assert len(data["placements"]) == 9
    for p in data["placements"]:
        assert 1 <= p["house"] <= 12
        assert p["effect"]
        assert p["dignity"] and p["dignity_state"] and p["dignity_note"]
        assert p["nakshatra"] in ref.NAKSHATRAS
        assert p["nakshatra_note"] and p["aspect_note"]
        assert isinstance(p["aspects"], list)
    for c in data["conjunctions"]:
        assert len(c["planets"]) == 2
        assert c["significance"]
        assert c["planets"][0] != c["planets"][1]
    for s in data["stelliums"]:
        assert len(s["planets"]) >= 3
        assert s["significance"]


def test_house_lords_complete():
    chart = compute_chart(BIRTH)
    lords = chart_combinations(chart)["house_lords"]
    assert len(lords) == 12
    for d in lords:
        assert 1 <= d["from_house"] <= 12
        assert 1 <= d["to_house"] <= 12
        assert d["lord"] in ref.PLANETS
        assert d["quality"] and d["meaning"]


def test_three_planet_lookup_and_keys():
    for key in THREE_PLANET:
        assert list(key) == sorted(key), key
        assert three_planet(*key) is not None
    # Order independence.
    assert three_planet("Venus", "Sun", "Mercury") == three_planet("Sun", "Mercury", "Venus")


def test_house_lord_generic():
    d = house_lord_generic(5, 10)
    assert d["from_house"] == 5 and d["to_house"] == 10
    assert d["quality"] and d["meaning"]


def test_nakshatra_traits_complete():
    for nak in ref.NAKSHATRAS:
        assert nak in NAKSHATRA_TRAIT and NAKSHATRA_TRAIT[nak]


def test_combinations_markdown():
    chart = compute_chart(BIRTH)
    md = combinations_markdown(chart, "Test Native")
    assert "Planetary Combinations Report" in md
    assert "Planet placements" in md
    assert "House-lord placements" in md


def test_layman_outcomes_and_balance():
    chart = compute_chart(BIRTH)
    reading = layman_outcomes(chart)
    assert reading["nutshell"] and reading["areas"]
    for block in reading["areas"]:
        for ln in block["lines"]:
            assert ln["text"] and ln["reason"]
            assert ln["tone"] in {"good", "caution", "neutral"}
    bal = outcome_balance(reading)
    assert 0 <= bal["score"] <= 100
    counted = bal["good"] + bal["caution"] + bal["neutral"]
    total = sum(len(b["lines"]) for b in reading["areas"])
    assert counted == total


if __name__ == "__main__":
    test_all_planet_house_entries_complete()
    test_conjunction_lookup_is_order_independent()
    test_conjunction_keys_sorted()
    test_planet_in_house_lookup()
    test_chart_combinations_structure()
    test_house_lords_complete()
    test_three_planet_lookup_and_keys()
    test_house_lord_generic()
    test_nakshatra_traits_complete()
    test_combinations_markdown()
    test_layman_outcomes_and_balance()
    print("Combinations tests passed.")
