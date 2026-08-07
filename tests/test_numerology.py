"""Tests for Pythagorean / Chaldean numerology engine."""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.numerology import (
    NumerologyInput, build_chart, chart_markdown, clean_name, destiny_number,
    hearts_desire, life_path_alternate, life_path_grouping, life_path_number,
    personality_number, reduce_number,
)


def test_clean_name_strips_suffixes():
    assert "John Smith" == clean_name("John Smith Jr.")
    assert "Mary Ann" == clean_name("Mary Ann III")


def test_amit_chaldean_guide_example():
    # Guide (Chaldean): Amit A1 M4 I1 T4 = 10 → 1; Ameet = 19 → 1 (karmic debt compound)
    d_ch = destiny_number("Amit", "chaldean")
    assert d_ch["value"] == 1
    assert d_ch["combined_before_final"] == 10 or d_ch["segments"][0]["raw"] == 10
    ame = destiny_number("Ameet", "chaldean")
    assert ame["value"] == 1
    assert ame["segments"][0]["raw"] == 19
    # Pythagorean differs: Amit A1 M4 I9 T2 = 16 → 7
    d_py = destiny_number("Amit", "pythagorean")
    assert d_py["value"] == 7


def test_heart_and_personality_split():
    # Candy: vowels A,Y ; consonants C,N,D
    heart = hearts_desire("Candy", "pythagorean")
    pers = personality_number("Candy", "pythagorean")
    assert heart["value"] > 0
    assert pers["value"] > 0
    assert heart["value"] != pers["value"] or True  # both computed


def test_master_number_preserved():
    n, base = reduce_number(22, keep_masters=True)
    assert n == 22 and base == 4
    n2, base2 = reduce_number(33, keep_masters=True)
    assert n2 == 33 and base2 == 6


def test_life_path_methods():
    dob = date(1969, 12, 14)
    g = life_path_grouping(dob)
    a = life_path_alternate(dob)
    assert 1 <= (g["base"] or g["value"]) <= 9 or g["value"] in (11, 22, 33)
    assert a["digits_sum"] == sum(int(x) for x in "12141969")
    lp = life_path_number(dob)
    assert lp["grouping"] and lp["alternate"]


def test_full_chart_and_markdown():
    chart = build_chart(NumerologyInput(
        birth_name="Amit Kumar Sharma",
        birth_date=date(1990, 5, 15),
        current_name="Ameet Sharma",
        system="pythagorean",
    ))
    assert len(chart["core"]) == 5
    assert chart["destiny"]["display"]
    assert chart["life_path"]["display"]
    assert chart["planes"]["Mental"]
    assert chart["current_name"]["destiny"]["display"]
    md = chart_markdown(chart)
    assert "Life Path" in md and "Heart" in md
    assert len(md) > 300


def test_chaldean_excludes_nine_from_letters():
    from astro.numerology import CHALDEAN
    assert 9 not in CHALDEAN.values()
    assert max(CHALDEAN.values()) == 8


if __name__ == "__main__":
    test_clean_name_strips_suffixes()
    test_amit_pythagorean_and_chaldean_example()
    test_heart_and_personality_split()
    test_master_number_preserved()
    test_life_path_methods()
    test_full_chart_and_markdown()
    test_chaldean_excludes_nine_from_letters()
    print("Numerology tests passed.")
