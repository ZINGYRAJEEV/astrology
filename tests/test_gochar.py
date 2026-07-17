"""Tests for the Gochar (transit) engine and Pratyantardasha timing."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.gochar import gochar_report, transit_positions
from astro.dasha_calc import (
    compute_vimshottari, current_dasha_full, upcoming_changes,
)
from astro import reference as ref

BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)


def test_transit_positions():
    pos = transit_positions(datetime(2026, 3, 10, 12, 0))
    for name in ref.PLANETS:
        assert name in pos
        assert pos[name]["sign"] in ref.SIGNS
        assert 0 <= pos[name]["longitude"] < 360
    # Ketu is opposite Rahu.
    diff = abs(pos["Rahu"]["longitude"] - pos["Ketu"]["longitude"]) % 360
    assert abs(diff - 180.0) < 1e-6


def test_gochar_report():
    chart = compute_chart(BIRTH)
    rep = gochar_report(chart, datetime(2026, 3, 10, 12, 0))
    assert rep["moon_sign"] in ref.SIGNS
    assert rep["lagna"] in ref.SIGNS
    assert len(rep["rows"]) == len(ref.PLANETS)
    for r in rep["rows"]:
        assert 1 <= r["house_from_moon"] <= 12
        assert 1 <= r["house_from_lagna"] <= 12
    # highlights always include Saturn, Jupiter and the nodes
    titles = " ".join(h["title"] for h in rep["highlights"])
    assert "Jupiter" in titles or "Guru" in titles
    assert "Rahu" in titles


def test_pratyantardasha():
    chart = compute_chart(BIRTH)
    periods = compute_vimshottari(chart, pratyantardashas=True)
    when = datetime(2026, 3, 10, 12, 0)
    maha, antar, prat = current_dasha_full(periods, when)
    assert maha is not None
    assert antar is not None
    assert prat is not None
    # nesting is time-consistent
    assert maha.start <= antar.start <= prat.start <= when < prat.end <= antar.end <= maha.end
    changes = upcoming_changes(periods, when, count=5)
    assert changes
    assert all(c["start"] >= when for c in changes)


if __name__ == "__main__":
    test_transit_positions()
    test_gochar_report()
    test_pratyantardasha()
    print("Gochar & Pratyantardasha tests passed.")
