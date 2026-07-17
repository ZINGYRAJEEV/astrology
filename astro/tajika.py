"""Tajika yogas for Prashna (horary) — Ithasala, Ishrafa, Nakta, Yamaya.

These describe how two significators "connect":

* **Ithasala** (applying aspect): the faster planet is *behind* the slower in
  degrees within a valid Tajika aspect and their orbs (deeptamsa) overlap —
  the matter is forming and tends to complete. A promise of "yes".
* **Ishrafa** (separating aspect): they are in aspect within orb but the
  faster planet has already passed — the moment has slipped; "was close".
* **Nakta / Yamaya**: no direct aspect, but a third fast planet transfers or
  collects the light between them — help comes via an intermediary.

Tajika uses five aspects (unlike Parashari full aspects): conjunction (same
sign), sextile (3rd/11th), trine (5th/9th) and opposition (7th). The 4th/10th
(square) are treated as inimical and do not form Ithasala.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from . import reference as ref
from .chart_engine import Chart

# Deeptamsa (orb, degrees) for each planet.
DEEPTAMSA = {
    "Sun": 15.0, "Moon": 12.0, "Mars": 8.0, "Mercury": 7.0,
    "Jupiter": 9.0, "Venus": 7.0, "Saturn": 9.0, "Rahu": 9.0, "Ketu": 9.0,
}

# Mean daily motion (deg/day) — used to decide which planet is "faster".
_MEAN_SPEED = {
    "Moon": 13.18, "Mercury": 1.38, "Venus": 1.20, "Sun": 0.99,
    "Mars": 0.52, "Jupiter": 0.083, "Saturn": 0.034, "Rahu": 0.053, "Ketu": 0.053,
}

# Valid Tajika aspecting sign-distances (0-based difference).
_ASPECT_DIFFS = {0, 2, 4, 6, 8, 10}  # conjunction, sextile, trine, opposition


def _faster(a: str, b: str) -> str:
    return a if _MEAN_SPEED[a] >= _MEAN_SPEED[b] else b


def _sign_diff(chart: Chart, a: str, b: str) -> int:
    return (chart.planets[a].sign_index - chart.planets[b].sign_index) % 12


def tajika_relation(chart: Chart, a: str, b: str) -> Dict:
    """Classify the Tajika connection between significators ``a`` and ``b``."""
    pa, pb = chart.planets[a], chart.planets[b]
    diff = _sign_diff(chart, a, b)
    aspecting = diff in _ASPECT_DIFFS
    orb = (DEEPTAMSA[a] + DEEPTAMSA[b]) / 2.0

    if not aspecting:
        return {"type": "none", "planets": (a, b), "reason":
                f"{a} and {b} are not in a Tajika aspect (they cannot connect directly)."}

    # Degree gap: within orb?
    da, db = pa.degree_in_sign, pb.degree_in_sign
    within = abs(da - db) <= orb

    faster = _faster(a, b)
    slower = b if faster == a else a
    # Applying (Ithasala) if the faster planet has fewer degrees than the slower.
    applying = chart.planets[faster].degree_in_sign < chart.planets[slower].degree_in_sign

    if not within:
        return {"type": "none", "planets": (a, b), "reason":
                f"{a} and {b} aspect each other but are outside orb "
                f"({abs(da - db):.1f}° apart, orb {orb:.1f}°) — no firm connection."}

    if applying:
        return {"type": "Ithasala", "planets": (a, b), "faster": faster, "slower": slower,
                "reason": f"Ithasala: {faster} (faster) is applying to {slower} within orb "
                          "— the matter is forming and tends to complete."}
    return {"type": "Ishrafa", "planets": (a, b), "faster": faster, "slower": slower,
            "reason": f"Ishrafa: {faster} has already separated from {slower} — the "
                      "opportunity was close but is slipping past."}


def _aspects_both(chart: Chart, m: str, a: str, b: str) -> bool:
    return (_sign_diff(chart, m, a) in _ASPECT_DIFFS
            and _sign_diff(chart, m, b) in _ASPECT_DIFFS)


def transfer_of_light(chart: Chart, a: str, b: str) -> Optional[Dict]:
    """Nakta yoga — a third *faster* planet aspecting both significators."""
    if _sign_diff(chart, a, b) in _ASPECT_DIFFS:
        return None
    for m in ref.PLANETS:
        if m in (a, b) or not _aspects_both(chart, m, a, b):
            continue
        if _MEAN_SPEED[m] >= _MEAN_SPEED[a] and _MEAN_SPEED[m] >= _MEAN_SPEED[b]:
            return {"type": "Nakta", "planets": (a, b), "via": m,
                    "reason": f"Nakta (transfer of light): {m} aspects both {a} and {b} "
                              "— help arrives through a quick intermediary."}
    return None


def collection_of_light(chart: Chart, a: str, b: str) -> Optional[Dict]:
    """Yamaya yoga — a third *slower* planet aspected by both significators."""
    if _sign_diff(chart, a, b) in _ASPECT_DIFFS:
        return None
    for m in ref.PLANETS:
        if m in (a, b) or not _aspects_both(chart, m, a, b):
            continue
        if _MEAN_SPEED[m] <= _MEAN_SPEED[a] and _MEAN_SPEED[m] <= _MEAN_SPEED[b]:
            return {"type": "Yamaya", "planets": (a, b), "via": m,
                    "reason": f"Yamaya (collection of light): the slower {m} gathers both "
                              f"{a} and {b} — the matter resolves through a weighty third party."}
    return None


def kamboola(chart: Chart, a: str, b: str) -> Optional[Dict]:
    """Kamboola — the Moon reinforces an existing Ithasala between a and b."""
    if "Moon" in (a, b):
        return None
    if tajika_relation(chart, a, b).get("type") != "Ithasala":
        return None
    moon_deg = chart.planets["Moon"].degree_in_sign
    for other in (a, b):
        if _sign_diff(chart, "Moon", other) not in _ASPECT_DIFFS:
            continue
        orb = (DEEPTAMSA["Moon"] + DEEPTAMSA[other]) / 2.0
        if abs(moon_deg - chart.planets[other].degree_in_sign) <= orb:
            return {"type": "Kamboola", "planets": (a, b), "via": "Moon",
                    "reason": f"Kamboola: the Moon supports the {a}-{b} Ithasala — "
                              "a strong blessing that helps the matter succeed."}
    return None


def manau(chart: Chart, a: str, b: str) -> Optional[Dict]:
    """Manau — a malefic (Mars/Saturn) obstructs an existing Ithasala."""
    if tajika_relation(chart, a, b).get("type") != "Ithasala":
        return None
    for m in ("Saturn", "Mars"):
        if m in (a, b):
            continue
        if _aspects_both(chart, m, a, b):
            return {"type": "Manau", "planets": (a, b), "via": m,
                    "reason": f"Manau (obstruction): {m} intervenes in the {a}-{b} Ithasala "
                              "— expect a hurdle or delay before completion."}
    return None


def prashna_yogas(chart: Chart, significators: List[str]) -> List[Dict]:
    """All meaningful Tajika connections among the given significators."""
    yogas: List[Dict] = []
    seen = set()
    for i in range(len(significators)):
        for j in range(i + 1, len(significators)):
            a, b = significators[i], significators[j]
            if a == b or (a, b) in seen:
                continue
            seen.add((a, b))
            rel = tajika_relation(chart, a, b)
            if rel["type"] == "Ithasala":
                yogas.append(rel)
                for extra in (kamboola(chart, a, b), manau(chart, a, b)):
                    if extra:
                        yogas.append(extra)
            elif rel["type"] == "Ishrafa":
                yogas.append(rel)
            elif rel["type"] == "none":
                bridge = transfer_of_light(chart, a, b) or collection_of_light(chart, a, b)
                if bridge:
                    yogas.append(bridge)
    return yogas
