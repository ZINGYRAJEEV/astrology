"""Strength & dignity engine (Step 3 of the build plan).

Scores each planet's dignity (exalted / own / friendly / neutral / enemy /
debilitated) from the reference tables and flags Vargottama planets (same
sign in D-1 and D-9). This feeds Phase 2 of the 12-step interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from . import reference as ref
from .chart_engine import Chart, PlanetPosition

# Dignity -> a normalised 0..1 strength score and a human label.
DIGNITY_SCORE = {
    "Exalted": 1.0,
    "Moolatrikona": 0.85,
    "Own Sign": 0.75,
    "Friend's Sign": 0.6,
    "Neutral's Sign": 0.45,
    "Enemy's Sign": 0.25,
    "Debilitated": 0.0,
}


@dataclass
class PlanetStrength:
    planet: str
    sign: str
    dignity: str
    score: float            # 0..1 dignity score
    vargottama: bool        # same sign in D-1 and D-9
    retrograde: bool
    is_benefic: bool        # natural benefic
    naisargika: float = 0.0  # natural strength in virupas
    notes: str = ""

    @property
    def percent(self) -> int:
        return round(self.score * 100)


def _dignity_of(planet: str, sign: str, degree: float = None) -> str:
    """Classify a planet's dignity in a given sign.

    If ``degree`` (0-30 within the sign) is provided, the Moolatrikona
    degree-range is honoured (it ranks just below exaltation).
    """
    if planet in ref.EXALTATION and ref.EXALTATION[planet][0] == sign:
        return "Exalted"
    if planet in ref.DEBILITATION and ref.DEBILITATION[planet][0] == sign:
        return "Debilitated"
    if planet in ref.MOOLATRIKONA and degree is not None:
        mt_sign, mt_lo, mt_hi = ref.MOOLATRIKONA[planet]
        if sign == mt_sign and mt_lo <= degree < mt_hi:
            return "Moolatrikona"
    if sign in ref.OWN_SIGNS.get(planet, set()):
        return "Own Sign"

    # Nodes have no rulership; fall back to relationship with the sign lord.
    sign_lord = ref.SIGN_LORD[sign]
    if planet == sign_lord:
        return "Own Sign"
    rel = ref.relationship(planet, sign_lord)
    return {"Friend": "Friend's Sign", "Enemy": "Enemy's Sign"}.get(rel, "Neutral's Sign")


def planet_strength(chart: Chart, planet: str) -> PlanetStrength:
    p: PlanetPosition = chart.planets[planet]
    dignity = _dignity_of(planet, p.sign, p.degree_in_sign)
    vargottama = p.sign_index == p.navamsha_sign_index

    notes = []
    # Navamsha cross-check: exalted in D-1 but weak in D-9 struggles to deliver.
    nav_dignity = _dignity_of(planet, p.navamsha_sign)
    if dignity in ("Exalted", "Own Sign") and nav_dignity in ("Debilitated", "Enemy's Sign"):
        notes.append(
            f"Strong in D-1 but {nav_dignity.lower()} in Navamsha (D-9) - "
            "promised benefits may be diluted."
        )
    if dignity == "Debilitated" and nav_dignity in ("Exalted", "Own Sign"):
        notes.append("Debilitated in D-1 but strong in Navamsha - hidden resilience (Neecha Bhanga tendency).")
    if vargottama:
        notes.append("Vargottama: same sign in D-1 and D-9 - exceptional, dependable strength.")

    return PlanetStrength(
        planet=planet,
        sign=p.sign,
        dignity=dignity,
        score=DIGNITY_SCORE[dignity],
        vargottama=vargottama,
        retrograde=p.retrograde,
        is_benefic=planet in ref.NATURAL_BENEFICS,
        naisargika=ref.NAISARGIKA_VIRUPAS.get(planet, 0.0),
        notes=" ".join(notes),
    )


def all_strengths(chart: Chart) -> Dict[str, PlanetStrength]:
    return {name: planet_strength(chart, name) for name in ref.PLANETS}


def chart_foundation_score(chart: Chart) -> dict:
    """Overall 'foundations' summary (Phase 2, step 6 of the framework)."""
    strengths = all_strengths(chart)
    exalted = [s.planet for s in strengths.values() if s.dignity == "Exalted"]
    debilitated = [s.planet for s in strengths.values() if s.dignity == "Debilitated"]
    own = [s.planet for s in strengths.values() if s.dignity == "Own Sign"]
    vargottama = [s.planet for s in strengths.values() if s.vargottama]
    avg = sum(s.score for s in strengths.values()) / len(strengths)
    return {
        "average_score": avg,
        "average_percent": round(avg * 100),
        "exalted": exalted,
        "own": own,
        "debilitated": debilitated,
        "vargottama": vargottama,
    }
