"""Tests for Panchavargeeya Bala and triplicity lord."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.panchavargeeya import panchavargeeya_bala, trirashi_pati
from astro import reference as ref

BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)

_MAX = {"kshetra": 30, "uchcha": 20, "hadda": 15, "drekkana": 10, "navamsha": 5}


def test_bala_components_within_range():
    chart = compute_chart(BIRTH)
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        b = panchavargeeya_bala(planet, chart)
        for comp, mx in _MAX.items():
            assert 0.0 <= b[comp] <= mx + 1e-6, (planet, comp, b[comp])
        assert abs(b["total"] - sum(b[c] for c in _MAX)) < 1e-6
        assert b["total"] <= 80 + 1e-6


def test_exalted_planet_high_uchcha():
    # A planet exactly at exaltation gets ~20 uchcha bala.
    from astro.panchavargeeya import _uchcha_bala
    exalt_long = ref.SIGNS.index("Cancer") * 30 + 5  # Jupiter exalts Cancer 5
    assert abs(_uchcha_bala("Jupiter", exalt_long) - 20.0) < 0.2


def test_trirashi_pati():
    # Fire sign, day -> Sun; night -> Jupiter.
    assert trirashi_pati("Aries", True) == "Sun"
    assert trirashi_pati("Leo", False) == "Jupiter"
    assert trirashi_pati("Gemini", True) == "Saturn"
    assert trirashi_pati("Cancer", False) == "Mars"


if __name__ == "__main__":
    test_bala_components_within_range()
    test_exalted_planet_high_uchcha()
    test_trirashi_pati()
    print("Panchavargeeya tests passed.")
