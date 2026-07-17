"""Tests for the planetary-combinations reference and detector."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.combinations import (
    CONJUNCTIONS, PLANET_IN_HOUSE, chart_combinations, conjunction, planet_in_house,
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
    for c in data["conjunctions"]:
        assert len(c["planets"]) == 2
        assert c["significance"]
        assert c["planets"][0] != c["planets"][1]


if __name__ == "__main__":
    test_all_planet_house_entries_complete()
    test_conjunction_lookup_is_order_independent()
    test_conjunction_keys_sorted()
    test_planet_in_house_lookup()
    test_chart_combinations_structure()
    print("Combinations tests passed.")
