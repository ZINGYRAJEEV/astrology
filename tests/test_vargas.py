"""Tests for the divisional-chart (Varga) engine."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.vargas import VARGAS, build_varga_chart, varga_sign_index, all_vargas, varga_markdown

BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)


def test_varga_sign_index_range():
    for varga in VARGAS:
        for i in range(0, 360, 3):
            idx = varga_sign_index(float(i), varga)
            assert 0 <= idx <= 11


def test_d1_identity():
    # D-1 returns the natal sign.
    assert varga_sign_index(45.0, 1) == 1  # 45° -> Taurus


def test_d9_matches_engine_navamsha():
    chart = compute_chart(BIRTH)
    vc = build_varga_chart(chart, 9)
    # Divisional Ascendant should match the engine's navamsha lagna.
    assert vc["lagna_sign"] == chart.navamsha_lagna_sign
    # Each planet's D-9 sign should match the engine's stored navamsha sign.
    for p in vc["planets"]:
        assert p["sign"] == chart.planets[p["planet"]].navamsha_sign


def test_build_varga_structure():
    chart = compute_chart(BIRTH)
    for varga in VARGAS:
        vc = build_varga_chart(chart, varga)
        assert len(vc["planets"]) == 9
        for p in vc["planets"]:
            assert 1 <= p["house"] <= 12
            assert p["sign"]


def test_all_vargas_and_markdown():
    chart = compute_chart(BIRTH)
    everything = all_vargas(chart)
    assert set(everything.keys()) == set(VARGAS.keys())
    md = varga_markdown(everything[9], "Test Native")
    assert "Navamsha" in md


if __name__ == "__main__":
    test_varga_sign_index_range()
    test_d1_identity()
    test_d9_matches_engine_navamsha()
    test_build_varga_structure()
    test_all_vargas_and_markdown()
    print("Varga tests passed.")
