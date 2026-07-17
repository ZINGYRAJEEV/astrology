"""Panchavargeeya Bala — Tajika five-fold strength of a planet.

Used to select the Varshesh (year lord) in Varshaphal by comparing the
office-bearers. The five components (in virupas) are:

    Kshetra (sign)     max 30
    Uchcha  (exalt)    max 20
    Hadda   (bounds)   max 15
    Drekkana (decan)   max 10
    Navamsha (D-9)     max  5
                       ------
    total              max 80

The Hadda uses the Egyptian bounds; Kshetra/Hadda/Drekkana/Navamsha grade by
planetary friendship where a planet does not itself rule the division.
"""

from __future__ import annotations

from typing import Dict

from . import reference as ref
from .chart_engine import Chart

# Egyptian bounds (Hadda): per sign, list of (upper_degree, lord).
_HADDA: Dict[str, list] = {
    "Aries": [(6, "Jupiter"), (12, "Venus"), (20, "Mercury"), (25, "Mars"), (30, "Saturn")],
    "Taurus": [(8, "Venus"), (14, "Mercury"), (22, "Jupiter"), (27, "Saturn"), (30, "Mars")],
    "Gemini": [(6, "Mercury"), (12, "Jupiter"), (17, "Venus"), (24, "Mars"), (30, "Saturn")],
    "Cancer": [(7, "Mars"), (13, "Venus"), (19, "Mercury"), (26, "Jupiter"), (30, "Saturn")],
    "Leo": [(6, "Jupiter"), (11, "Venus"), (18, "Saturn"), (24, "Mercury"), (30, "Mars")],
    "Virgo": [(7, "Mercury"), (17, "Venus"), (21, "Jupiter"), (28, "Mars"), (30, "Saturn")],
    "Libra": [(6, "Saturn"), (14, "Mercury"), (21, "Jupiter"), (28, "Venus"), (30, "Mars")],
    "Scorpio": [(7, "Mars"), (11, "Venus"), (19, "Mercury"), (24, "Jupiter"), (30, "Saturn")],
    "Sagittarius": [(12, "Jupiter"), (17, "Venus"), (21, "Mercury"), (26, "Saturn"), (30, "Mars")],
    "Capricorn": [(7, "Mercury"), (14, "Jupiter"), (22, "Venus"), (26, "Saturn"), (30, "Mars")],
    "Aquarius": [(7, "Mercury"), (13, "Venus"), (20, "Jupiter"), (25, "Mars"), (30, "Saturn")],
    "Pisces": [(12, "Venus"), (16, "Jupiter"), (19, "Mercury"), (28, "Mars"), (30, "Saturn")],
}


def _relation_grade(planet: str, lord: str, own: float, friend: float,
                    neutral: float, enemy: float) -> float:
    if planet == lord:
        return own
    rel = ref.relationship(planet, lord)
    return {"Friend": friend, "Neutral": neutral, "Enemy": enemy}[rel]


def _kshetra_bala(planet: str, sign: str, degree: float) -> float:
    if ref.EXALTATION.get(planet, ("", 0))[0] == sign:
        return 30.0
    mt = ref.MOOLATRIKONA.get(planet)
    if mt and mt[0] == sign and mt[1] <= degree < mt[2]:
        return 30.0
    if sign in ref.OWN_SIGNS.get(planet, set()):
        return 30.0
    lord = ref.SIGN_LORD[sign]
    return _relation_grade(planet, lord, 30.0, 15.0, 7.5, 3.75)


def _uchcha_bala(planet: str, longitude: float) -> float:
    exalt = ref.EXALTATION.get(planet)
    if not exalt:
        return 0.0
    exalt_long = ref.SIGNS.index(exalt[0]) * 30 + exalt[1]
    deb_long = (exalt_long + 180) % 360
    diff = abs(longitude - deb_long) % 360
    if diff > 180:
        diff = 360 - diff
    return diff / 9.0  # 0 at debilitation, 20 at exaltation


def _hadda_bala(planet: str, sign: str, degree: float) -> float:
    for upper, lord in _HADDA[sign]:
        if degree < upper:
            return _relation_grade(planet, lord, 15.0, 11.25, 7.5, 3.75)
    return _relation_grade(planet, _HADDA[sign][-1][1], 15.0, 11.25, 7.5, 3.75)


def _drekkana_bala(planet: str, sign_index: int, degree: float) -> float:
    third = int(degree // 10)  # 0,1,2
    offset = [0, 4, 8][third]  # 1st, 5th, 9th sign
    lord = ref.SIGN_LORD[ref.SIGNS[(sign_index + offset) % 12]]
    return _relation_grade(planet, lord, 10.0, 7.5, 5.0, 2.5)


def _navamsha_bala(planet: str, navamsha_sign: str) -> float:
    lord = ref.SIGN_LORD[navamsha_sign]
    return _relation_grade(planet, lord, 5.0, 3.75, 2.5, 1.25)


def panchavargeeya_bala(planet: str, chart: Chart) -> Dict[str, float]:
    """Five-fold Tajika strength for ``planet`` in ``chart`` (virupas)."""
    p = chart.planets[planet]
    kshetra = _kshetra_bala(planet, p.sign, p.degree_in_sign)
    uchcha = _uchcha_bala(planet, p.longitude)
    hadda = _hadda_bala(planet, p.sign, p.degree_in_sign)
    drekkana = _drekkana_bala(planet, p.sign_index, p.degree_in_sign)
    navamsha = _navamsha_bala(planet, p.navamsha_sign)
    total = kshetra + uchcha + hadda + drekkana + navamsha
    return {
        "kshetra": round(kshetra, 2),
        "uchcha": round(uchcha, 2),
        "hadda": round(hadda, 2),
        "drekkana": round(drekkana, 2),
        "navamsha": round(navamsha, 2),
        "total": round(total, 2),
    }


def _element(sign: str) -> str:
    return ref.SIGN_ELEMENT[sign]


# Tajika triplicity (Trirashi) lords: (day lord, night lord).
_TRIRASHI = {
    "Fire": ("Sun", "Jupiter"),
    "Earth": ("Venus", "Moon"),
    "Air": ("Saturn", "Mercury"),
    "Water": ("Mars", "Mars"),
}


def trirashi_pati(annual_lagna_sign: str, is_day: bool) -> str:
    """Triplicity lord of the annual ascendant's element (day/night)."""
    day_lord, night_lord = _TRIRASHI[_element(annual_lagna_sign)]
    return day_lord if is_day else night_lord
