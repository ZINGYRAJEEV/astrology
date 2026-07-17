"""Tests for Tajika yogas (Ithasala / Ishrafa / Nakta)."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.tajika import tajika_relation, prashna_yogas, DEEPTAMSA

WHEN = datetime(2026, 7, 17, 14, 30)


def _chart():
    return compute_chart(BirthData(
        name="Q", year=WHEN.year, month=WHEN.month, day=WHEN.day,
        hour=WHEN.hour, minute=WHEN.minute, latitude=28.6139, longitude=77.2090,
        tz_offset=5.5, place="New Delhi, India",
    ))


def test_relation_types_valid():
    chart = _chart()
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            rel = tajika_relation(chart, planets[i], planets[j])
            assert rel["type"] in {"Ithasala", "Ishrafa", "none"}
            assert rel["reason"]


def test_deeptamsa_complete():
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        assert p in DEEPTAMSA


def test_prashna_yogas_structure():
    chart = _chart()
    yogas = prashna_yogas(chart, ["Sun", "Moon", "Jupiter", "Venus"])
    assert isinstance(yogas, list)
    for y in yogas:
        assert y["type"] in {"Ithasala", "Ishrafa", "Nakta", "Yamaya", "Kamboola", "Manau"}
        assert len(y["planets"]) == 2


if __name__ == "__main__":
    test_relation_types_valid()
    test_deeptamsa_complete()
    test_prashna_yogas_structure()
    print("Tajika tests passed.")
