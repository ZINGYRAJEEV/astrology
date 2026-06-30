"""Smoke + correctness tests for the astrology engine.

Run with:  python -m pytest -q   (or)   python tests/test_engine.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro import reference as ref
from astro.strength_calc import all_strengths, _dignity_of
from astro.dasha_calc import compute_vimshottari, current_dasha, starting_nakshatra
from astro.aspects import aspected_houses
from astro.interpret import functional_nature, analyse_all_houses, synthesize


# A well-known reference birth (M. K. Gandhi: 2 Oct 1869, 07:11, Porbandar).
GANDHI = BirthData(
    name="Test Native", year=1869, month=10, day=2, hour=7, minute=11,
    latitude=21.6417, longitude=69.6293, tz_offset=5.5, place="Porbandar",
)


def test_chart_basic():
    c = compute_chart(GANDHI)
    assert len(c.planets) == 9
    # Rahu and Ketu are exactly opposite.
    rahu = c.planets["Rahu"].longitude
    ketu = c.planets["Ketu"].longitude
    assert abs(((rahu - ketu) % 360) - 180) < 1e-6
    # Every planet has a valid house 1..12.
    for p in c.planets.values():
        assert 1 <= p.house <= 12
        assert 0 <= p.sign_index <= 11
    # House signs are 12 consecutive signs from the lagna.
    assert c.house_signs[1] == c.lagna_sign
    print("Lagna:", c.lagna_sign, "| Moon:", c.planets["Moon"].sign,
          "| Sun:", c.planets["Sun"].sign)


def test_dignity_logic():
    # Sun exalted in Aries, debilitated in Libra.
    assert _dignity_of("Sun", "Aries") == "Exalted"
    assert _dignity_of("Sun", "Libra") == "Debilitated"
    assert _dignity_of("Sun", "Leo") == "Own Sign"
    assert _dignity_of("Saturn", "Libra") == "Exalted"


def test_aspects():
    # A planet in house 1: Mars aspects 4,7,8; default planet aspects 7.
    assert sorted(aspected_houses(1, "Mars")) == [4, 7, 8]
    assert sorted(aspected_houses(1, "Jupiter")) == [5, 7, 9]
    assert sorted(aspected_houses(1, "Saturn")) == [3, 7, 10]
    assert aspected_houses(1, "Sun") == [7]


def test_vimshottari():
    c = compute_chart(GANDHI)
    periods = compute_vimshottari(c)
    # Nine mahadashas starting from the one running at birth (partial first).
    assert len(periods) == 9
    nak = starting_nakshatra(c)
    # First (running) period equals the remaining balance of its lord's dasha.
    assert abs(periods[0].years - nak["balance_years"]) < 0.1
    # Subsequent eight periods are full-length.
    for p in periods[1:]:
        assert abs(p.years - ref.VIMSHOTTARI_YEARS[p.lord]) < 0.1
    # Each mahadasha has nine antardashas whose spans sum to the maha span.
    for p in periods:
        assert len(p.antardashas) == 9
        sub_total = sum(a.years for a in p.antardashas)
        assert abs(sub_total - p.years) < 0.05
    nak = starting_nakshatra(c)
    assert nak["nakshatra"] in ref.NAKSHATRAS
    print("Birth Nakshatra:", nak["nakshatra"], "lord", nak["lord"])


def test_functional_and_synthesis():
    c = compute_chart(GANDHI)
    nature = functional_nature(c)
    assert set(nature.keys()) == set(ref.PLANETS)
    houses = analyse_all_houses(c)
    assert len(houses) == 12
    syn = synthesize(c, "Career & success")
    assert syn["paragraphs"]
    print("Synthesis paragraphs:", len(syn["paragraphs"]))


def test_ashtakavarga():
    from astro.ashtakavarga import compute_sav, BAV_PLANETS, BENEFIC_PLACES
    # Each planet's benefic-place table sums to its classical total.
    expected = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
                "Jupiter": 56, "Venus": 52, "Saturn": 39}
    for p in BAV_PLANETS:
        total = sum(len(v) for v in BENEFIC_PLACES[p].values())
        assert total == expected[p], f"{p} table sums to {total}, expected {expected[p]}"
    c = compute_chart(GANDHI)
    sav = compute_sav(c)
    assert sav["total"] == 337, f"SAV total {sav['total']} != 337"
    assert sav["bav_totals"] == expected
    # Each house has a sane bindu count.
    for h in range(1, 13):
        assert 0 <= sav["per_house"][h]["points"] <= 56
    print("SAV total:", sav["total"], "avg:", round(sav["average"], 1))


def test_moolatrikona_and_naisargika():
    # Sun in early Leo -> Moolatrikona; Sun deep in Leo (>20) -> Own Sign.
    assert _dignity_of("Sun", "Leo", 10) == "Moolatrikona"
    assert _dignity_of("Sun", "Leo", 25) == "Own Sign"
    assert ref.NAISARGIKA_VIRUPAS["Sun"] == 60.00


def test_witness_reading():
    from astro.wisdom import witness_reading, PLANET_WITNESS
    c = compute_chart(GANDHI)
    wr = witness_reading(c)
    assert wr["reflections"]
    assert set(PLANET_WITNESS.keys()) == set(ref.PLANETS)
    print("Witness reflections:", len(wr["reflections"]))


if __name__ == "__main__":
    test_chart_basic()
    test_dignity_logic()
    test_aspects()
    test_vimshottari()
    test_functional_and_synthesis()
    test_ashtakavarga()
    test_moolatrikona_and_naisargika()
    test_witness_reading()
    print("\nAll tests passed.")
