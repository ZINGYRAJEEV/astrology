"""Tests for the Varshaphal (annual horoscope) engine."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.varshaphal import solar_return, varshaphal, varshaphal_markdown
from astro import reference as ref

BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)


def test_solar_return_near_birthday():
    chart = compute_chart(BIRTH)
    sr = solar_return(chart, 2026)
    # Solar return lands around the birthday (mid-May).
    assert sr.year == 2026
    assert sr.month == 5
    assert 13 <= sr.day <= 17


def test_varshaphal_structure():
    chart = compute_chart(BIRTH)
    vp = varshaphal(chart, 2026)
    assert vp["age"] == 2026 - 1990
    assert vp["annual_lagna"] in ref.SIGNS
    assert vp["muntha_sign"] in ref.SIGNS
    assert 1 <= vp["muntha_house"] <= 12
    assert vp["year_lord"] in ref.PLANETS
    assert len(vp["annual_planets"]) == 9
    assert len(vp["monthly"]) == 12
    for m in vp["monthly"]:
        assert 1 <= m["house"] <= 12
        assert m["sun_sign"] in ref.SIGNS


def test_muntha_advances_one_sign_per_year():
    chart = compute_chart(BIRTH)
    v1 = varshaphal(chart, 2025)
    v2 = varshaphal(chart, 2026)
    i1 = ref.SIGNS.index(v1["muntha_sign"])
    i2 = ref.SIGNS.index(v2["muntha_sign"])
    assert (i2 - i1) % 12 == 1


def test_varshaphal_markdown():
    chart = compute_chart(BIRTH)
    md = varshaphal_markdown(varshaphal(chart, 2026), "Test Native")
    assert "Varshaphal 2026" in md
    assert "Month-by-month" in md


if __name__ == "__main__":
    test_solar_return_near_birthday()
    test_varshaphal_structure()
    test_muntha_advances_one_sign_per_year()
    test_varshaphal_markdown()
    print("Varshaphal tests passed.")
