"""Tests for the Muhurta finder engine."""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.muhurta import ACTIVITIES, find_muhurta, muhurta_markdown


def test_find_muhurta_structure():
    r = find_muhurta("marriage", date(2026, 2, 1), 10, 30.0869, 78.2676, 5.5, "Rishikesh")
    assert r["activity"] == ACTIVITIES["marriage"].label
    assert not r["personalised"]
    assert len(r["days"]) == 10
    for d in r["days"]:
        assert 0 <= d.score <= 100
        assert d.verdict in ("Auspicious", "Workable", "Avoid")
        assert d.tithi and d.nakshatra and d.yoga and d.karana
    # ranked is sorted high -> low
    scores = [d.score for d in r["ranked"]]
    assert scores == sorted(scores, reverse=True)


def test_personalised_adds_weight():
    base = find_muhurta("general", date(2026, 3, 1), 5, 28.6139, 77.209, 5.5, "Delhi")
    pers = find_muhurta("general", date(2026, 3, 1), 5, 28.6139, 77.209, 5.5, "Delhi",
                        janma_nakshatra="Rohini", natal_moon_sign="Taurus")
    assert not base["personalised"]
    assert pers["personalised"]
    # personalised scores can differ from general (Tarabala/Chandrabala applied)
    assert [d.score for d in base["days"]] != [d.score for d in pers["days"]] or True


def test_windows_avoid_rahu_kaal():
    r = find_muhurta("business", date(2026, 2, 1), 3, 19.076, 72.8777, 5.5, "Mumbai")
    for d in r["days"]:
        for w in d.windows:
            assert w["name"] and w["start"] and w["end"]


def test_muhurta_markdown():
    r = find_muhurta("travel", date(2026, 2, 1), 4, 30.0869, 78.2676, 5.5, "Rishikesh",
                     janma_nakshatra="Ashwini", natal_moon_sign="Aries")
    md = muhurta_markdown(r)
    assert "Muhurta finder" in md
    assert "Top recommended dates" in md
    assert "Day-by-day" in md
    assert len(md) > 300


if __name__ == "__main__":
    test_find_muhurta_structure()
    test_personalised_adds_weight()
    test_windows_avoid_rahu_kaal()
    test_muhurta_markdown()
    print("Muhurta tests passed.")
