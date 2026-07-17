"""Tests for the festival & vrat calendar engine."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.festivals import compute_festivals, festivals_markdown


def test_compute_festivals_structure():
    events = compute_festivals(2026, 3, 30.0869, 78.2676, 5.5, "Rishikesh")
    assert isinstance(events, list)
    assert events, "March should contain observances (Holi/Ekadashi/etc.)"
    for e in events:
        assert e["type"] in ("festival", "vrat", "sankranti")
        assert e["name"] and e["note"]
        assert e["tithi"] and e["nakshatra"]


def test_ekadashi_present_each_month():
    events = compute_festivals(2026, 6, 28.6139, 77.209, 5.5, "Delhi")
    ekadashis = [e for e in events if e["name"].startswith("Ekadashi")]
    # Two Ekadashis per lunar month; at least one should land in a civil month.
    assert len(ekadashis) >= 1


def test_sankranti_detected():
    # The Sun changes sign once per ~month, so a full month should catch one.
    events = compute_festivals(2026, 1, 30.0869, 78.2676, 5.5, "Rishikesh")
    sankrantis = [e for e in events if e["type"] == "sankranti"]
    assert len(sankrantis) >= 1
    # January should include Makar Sankranti (Sun into Capricorn).
    assert any("Makar" in e["name"] for e in sankrantis)


def test_festivals_markdown():
    events = compute_festivals(2026, 3, 30.0869, 78.2676, 5.5, "Rishikesh")
    md = festivals_markdown(events, 2026, 3)
    assert "Festivals & Vrats" in md
    assert len(md) > 100


if __name__ == "__main__":
    test_compute_festivals_structure()
    test_ekadashi_present_each_month()
    test_sankranti_detected()
    test_festivals_markdown()
    print("Festival tests passed.")
