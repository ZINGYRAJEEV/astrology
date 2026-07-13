"""Tests for Panchang (Rishikesh style) calculations."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date

from astro.panchang import compute_panchang, _tithi_index, _karana_name
from astro.panchang_data import RISHIKESH


def test_panchang_basic():
    p = compute_panchang(date(2026, 7, 13))
    assert p.place == RISHIKESH["name"]
    assert p.vaara.name == "Somavara"  # Monday
    assert 1 <= p.tithi.index <= 30
    assert p.nakshatra.name
    assert p.yoga.name
    assert p.karana.name
    assert p.sunrise < p.sunset
    assert len(p.day_choghadiya) == 8
    assert len(p.night_choghadiya) == 8
    assert p.vikram_samvat >= 2080
    print("Tithi:", p.tithi.name, p.paksha)
    print("Sunrise-Sunset:", p.sunrise.time(), p.sunset.time())


def test_tithi_karana_ranges():
    assert _tithi_index(0) == 1
    assert _tithi_index(11.9) == 1
    assert _tithi_index(12) == 2
    assert _karana_name(0) == "Kimstughna"
    assert _karana_name(1) in ("Bava", "Balava")


def test_inauspicious_ordering():
    p = compute_panchang(date(2026, 7, 13))
    assert p.rahu_kaal.start >= p.sunrise
    assert p.rahu_kaal.end <= p.sunset
    assert p.brahma_muhurta.end <= p.sunrise


if __name__ == "__main__":
    test_panchang_basic()
    test_tithi_karana_ranges()
    test_inauspicious_ordering()
    print("\nPanchang tests passed.")
