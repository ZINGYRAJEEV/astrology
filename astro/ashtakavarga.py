"""Ashtakavarga - the numerical 'math of opportunity'.

Implements the classical Prastarashtakavarga benefic-point (bindu) tables to
compute each planet's Bhinnashtakavarga (BAV) and the combined
Sarvashtakavarga (SAV) per sign / house. The seven planetary BAV totals sum
to 337 bindus across the chart (average 28 per house), exactly as described
in the source material.

Interpretation thresholds (per the briefing):
  * 30+ points  -> highly auspicious (themes manifest powerfully/easily)
  * 25-30       -> middling / stable (standard effort, expected outcome)
  * below 25    -> challenging (meagre results, more struggle)
"""

from __future__ import annotations

from typing import Dict, List

from . import reference as ref
from .chart_engine import Chart

# Order of the eight contributors (seven planets + the Ascendant/Lagna).
CONTRIBUTORS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"]

# Benefic houses (counted inclusively from each contributor's sign, 1 = same
# sign) where the planet being evaluated receives a bindu. These are the
# standard Parashari tables; each planet's grand total is noted.
BENEFIC_PLACES: Dict[str, Dict[str, List[int]]] = {
    "Sun": {  # total 48
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {  # total 49
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [3, 6, 10, 11],
    },
    "Mars": {  # total 39
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 3, 6, 10, 11],
    },
    "Mercury": {  # total 54
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {  # total 56
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {  # total 52
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Lagna": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {  # total 39
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [1, 3, 4, 6, 10, 11],
    },
}

# Planets that own a Bhinnashtakavarga (the luminaries + five taras).
BAV_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _contributor_sign(chart: Chart, contributor: str) -> int:
    if contributor == "Lagna":
        return chart.lagna_sign_index
    return chart.planets[contributor].sign_index


def compute_bav(chart: Chart) -> Dict[str, List[int]]:
    """Bhinnashtakavarga: per-planet bindus indexed by sign (0=Aries..11)."""
    bav: Dict[str, List[int]] = {}
    for planet in BAV_PLANETS:
        points = [0] * 12
        table = BENEFIC_PLACES[planet]
        for contributor in CONTRIBUTORS:
            csign = _contributor_sign(chart, contributor)
            for house in table[contributor]:
                sign_idx = (csign + house - 1) % 12
                points[sign_idx] += 1
        bav[planet] = points
    return bav


def classify(points: int) -> str:
    if points >= 30:
        return "Highly auspicious"
    if points >= 25:
        return "Stable"
    return "Challenging"


def compute_sav(chart: Chart) -> Dict:
    """Sarvashtakavarga: combined bindus per sign and per house (+ class)."""
    bav = compute_bav(chart)
    per_sign = [0] * 12
    for planet in BAV_PLANETS:
        for s in range(12):
            per_sign[s] += bav[planet][s]

    lagna = chart.lagna_sign_index
    per_house = {}
    for h in range(1, 13):
        sign_idx = (lagna + h - 1) % 12
        pts = per_sign[sign_idx]
        per_house[h] = {
            "house": h,
            "sign": ref.SIGNS[sign_idx],
            "points": pts,
            "class": classify(pts),
        }

    total = sum(per_sign)
    return {
        "bav": bav,
        "per_sign": per_sign,                 # indexed by sign 0..11
        "per_house": per_house,               # keyed by house 1..12
        "total": total,                        # should be 337
        "average": total / 12.0,
        "bav_totals": {p: sum(bav[p]) for p in BAV_PLANETS},
    }


def house_points(chart: Chart, house: int) -> int:
    sav = compute_sav(chart)
    return sav["per_house"][house]["points"]
