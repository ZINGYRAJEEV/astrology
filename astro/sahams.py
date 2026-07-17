"""Sahams — Tajika sensitive points (Vedic analogues of Arabic Parts).

Each Saham is a longitude derived from two significators and the Ascendant:

    day birth   : Saham = A - B + Ascendant
    night birth : Saham = B - A + Ascendant   (operands reversed)

The sign/house a Saham falls in, and the strength of its lord, show how that
area of life fares. Day/night is judged by whether the Sun is above the
horizon. Traditions vary in the exact operands and in which Sahams reverse at
night; the common day-formula with night reversal is used here.
"""

from __future__ import annotations

from typing import Dict, List

from . import reference as ref
from .chart_engine import Chart

# key: (label, significance, planet A, planet B)
SAHAMS: List[Dict] = [
    {"key": "punya", "label": "Punya (Fortune)", "a": "Moon", "b": "Sun",
     "signifies": "merit, fortune & overall well-being"},
    {"key": "vidya", "label": "Vidya (Learning)", "a": "Sun", "b": "Moon",
     "signifies": "education, knowledge & intellect"},
    {"key": "vivaha", "label": "Vivaha (Marriage)", "a": "Venus", "b": "Saturn",
     "signifies": "marriage & partnership"},
    {"key": "santana", "label": "Santana (Children)", "a": "Jupiter", "b": "Moon",
     "signifies": "progeny & children"},
    {"key": "karma", "label": "Karma (Career)", "a": "Mars", "b": "Mercury",
     "signifies": "work, action & profession"},
    {"key": "pitri", "label": "Pitri (Father)", "a": "Sun", "b": "Saturn",
     "signifies": "father & paternal matters"},
    {"key": "matri", "label": "Matri (Mother)", "a": "Moon", "b": "Venus",
     "signifies": "mother & maternal matters"},
    {"key": "gaurava", "label": "Gaurava (Respect)", "a": "Jupiter", "b": "Sun",
     "signifies": "honour, dignity & respect"},
    {"key": "jaya", "label": "Jaya (Victory)", "a": "Jupiter", "b": "Mars",
     "signifies": "success over rivals & competition"},
    {"key": "roga", "label": "Roga (Illness)", "a": "Saturn", "b": "Moon",
     "signifies": "health challenges & ailments"},
]


def is_day_birth(chart: Chart) -> bool:
    """True if the Sun is above the horizon (houses 7-12) in the chart."""
    return chart.planets["Sun"].house in {7, 8, 9, 10, 11, 12}


def _saham_longitude(chart: Chart, a: str, b: str, day: bool) -> float:
    asc = chart.ascendant_longitude
    la, lb = chart.planets[a].longitude, chart.planets[b].longitude
    value = (la - lb + asc) if day else (lb - la + asc)
    return value % 360.0


def compute_sahams(chart: Chart) -> List[Dict]:
    """All Sahams for a chart with sign, house-from-Lagna and lord."""
    day = is_day_birth(chart)
    lagna_idx = chart.lagna_sign_index
    out: List[Dict] = []
    for s in SAHAMS:
        lon = _saham_longitude(chart, s["a"], s["b"], day)
        sign_idx = int(lon // 30) % 12
        sign = ref.SIGNS[sign_idx]
        house = (sign_idx - lagna_idx) % 12 + 1
        out.append({
            "label": s["label"],
            "signifies": s["signifies"],
            "longitude": round(lon, 2),
            "sign": sign,
            "degree": round(lon - sign_idx * 30, 2),
            "house": house,
            "lord": ref.SIGN_LORD[sign],
            "occupants": chart.occupants(house),
        })
    return out


def sahams_markdown(sahams: List[Dict], native: str, day: bool) -> str:
    lines = [
        f"# Sahams (Tajika sensitive points) — {native}",
        "",
        f"Chart type: {'day' if day else 'night'} birth",
        "",
        "| Saham | Sign | House | Lord | Signifies |",
        "| --- | --- | --- | --- | --- |",
    ]
    for s in sahams:
        lines.append(
            f"| {s['label']} | {s['sign']} {s['degree']}° | {s['house']} | "
            f"{s['lord']} | {s['signifies']} |"
        )
    lines += ["", "> Day-formula with night reversal; operand traditions vary. "
              "Read each Saham's house and its lord's strength."]
    return "\n".join(lines)
