"""Graha Drishti - planetary aspects.

Every planet aspects the 7th house from itself. Mars (4,7,8), Jupiter
(5,7,9) and Saturn (3,7,10) cast additional special full aspects. This
module computes, for any house, which planets are casting an aspect onto it.
"""

from __future__ import annotations

from typing import Dict, List

from . import reference as ref
from .chart_engine import Chart


def aspected_houses(from_house: int, planet: str) -> List[int]:
    """House numbers aspected by ``planet`` sitting in ``from_house``."""
    offsets = ref.SPECIAL_ASPECTS.get(planet, ref.DEFAULT_ASPECTS)
    return [((from_house - 1 + (off - 1)) % 12) + 1 for off in offsets]


def aspects_on_house(chart: Chart, house: int) -> List[Dict]:
    """Planets casting an aspect onto ``house`` (with where they sit)."""
    result = []
    for name, p in chart.planets.items():
        if house in aspected_houses(p.house, name):
            result.append({
                "planet": name,
                "from_house": p.house,
                "from_sign": p.sign,
                "is_benefic": name in ref.NATURAL_BENEFICS,
            })
    return result


def aspects_on_planet(chart: Chart, planet: str) -> List[Dict]:
    """Planets aspecting the house occupied by ``planet`` (excluding itself)."""
    target_house = chart.planets[planet].house
    return [a for a in aspects_on_house(chart, target_house) if a["planet"] != planet]


def aspect_summary(chart: Chart) -> Dict[int, List[Dict]]:
    return {h: aspects_on_house(chart, h) for h in range(1, 13)}
