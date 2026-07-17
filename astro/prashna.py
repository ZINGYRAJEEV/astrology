"""Prashna (horary) engine — answer a question from the moment it is asked.

Casts a chart for the query time and place, then judges the relevant houses,
their lords, the Moon (the key significator of the querent's mind) and the
Ascendant lord to reach a Favourable / Mixed / Unfavourable verdict with
plain reasons and a rough timing hint.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple

from . import reference as ref
from .chart_engine import BirthData, Chart, compute_chart
from .strength_calc import all_strengths
from .aspects import aspects_on_house
from .tajika import prashna_yogas

_KENDRA_TRIKONA = {1, 4, 5, 7, 9, 10}
_UPACHAYA = {11}
_DUSTHANA = {6, 8, 12}
_GOOD_PLACEMENT = _KENDRA_TRIKONA | _UPACHAYA

_MOVABLE = {"Aries", "Cancer", "Libra", "Capricorn"}
_FIXED = {"Taurus", "Leo", "Scorpio", "Aquarius"}

_DIGNITY_VAL = {
    "Exalted": 2.0, "Moolatrikona": 1.5, "Own Sign": 1.5, "Friend's Sign": 0.75,
    "Neutral's Sign": 0.0, "Enemy's Sign": -0.75, "Debilitated": -1.5,
}

QUESTION_TYPES: Dict[str, Dict] = {
    "general": {"label": "General yes / no", "primary": 1, "mode": "standard"},
    "career": {"label": "Career / job / promotion", "primary": 10, "support": [11, 6], "mode": "standard"},
    "marriage": {"label": "Marriage / relationship", "primary": 7, "support": [5, 11], "mode": "standard"},
    "finance": {"label": "Money / finance / gains", "primary": 11, "support": [2, 5], "mode": "standard"},
    "education": {"label": "Education / exams", "primary": 5, "support": [4, 9], "mode": "standard"},
    "property": {"label": "Property / vehicle", "primary": 4, "support": [11], "mode": "standard"},
    "children": {"label": "Children / progeny", "primary": 5, "support": [9], "mode": "standard"},
    "travel": {"label": "Travel / relocation / foreign", "primary": 12, "support": [3, 9], "mode": "standard"},
    "health": {"label": "Health / recovery", "primary": 1, "mode": "health"},
    "litigation": {"label": "Dispute / litigation / competition", "primary": 1, "mode": "litigation"},
}


def _is_benefic(planet: str) -> bool:
    return planet in ref.NATURAL_BENEFICS


def _house_quality(chart: Chart, strengths, house: int) -> Tuple[float, List[str]]:
    reasons: List[str] = []
    lord = chart.house_lord(house)
    dig = strengths[lord].dignity
    score = _DIGNITY_VAL.get(dig, 0.0)
    reasons.append(f"{house}th lord {lord} is {dig.lower()}")

    lh = chart.planet_house(lord)
    if lh in _GOOD_PLACEMENT:
        score += 0.8
        reasons.append(f"{lord} is well placed in house {lh}")
    elif lh in _DUSTHANA:
        score -= 0.8
        reasons.append(f"{lord} is in a difficult house ({lh})")

    for occ in chart.occupants(house):
        if _is_benefic(occ):
            score += 0.6
            reasons.append(f"benefic {occ} occupies the {house}th")
        else:
            score -= 0.5
            reasons.append(f"malefic {occ} occupies the {house}th")

    for a in aspects_on_house(chart, house):
        if a["is_benefic"]:
            score += 0.35
        else:
            score -= 0.3

    return score, reasons


def _moon_quality(chart: Chart, strengths) -> Tuple[float, List[str]]:
    reasons: List[str] = []
    m = chart.planets["Moon"]
    dig = strengths["Moon"].dignity
    score = _DIGNITY_VAL.get(dig, 0.0)
    reasons.append(f"Moon (the mind) is {dig.lower()} in {m.sign}")
    if m.house in _GOOD_PLACEMENT:
        score += 0.7
        reasons.append(f"Moon is well placed in house {m.house}")
    elif m.house in _DUSTHANA:
        score -= 0.7
        reasons.append(f"Moon is in a difficult house ({m.house})")
    return score, reasons


def _timing_hint(chart: Chart, house: int) -> str:
    lord = chart.house_lord(house)
    sign = chart.planets[lord].sign
    if sign in _MOVABLE:
        return "Movable sign involved — a result is likely relatively soon."
    if sign in _FIXED:
        return "Fixed sign involved — expect delay; the matter matures slowly."
    return "Dual sign involved — moderate timing, possibly in stages."


def _find_yoga(yogas: List[Dict], a: str, b: str) -> Dict:
    for y in yogas:
        pair = set(y["planets"])
        if a in pair and b in pair:
            return y
    return {}


def _verdict(pct: float) -> str:
    if pct >= 62:
        return "Favourable"
    if pct >= 45:
        return "Mixed"
    return "Unfavourable"


def answer_prashna(
    question_type: str,
    when: datetime,
    latitude: float,
    longitude: float,
    tz_offset: float,
    place: str,
) -> Dict:
    """Cast the horary chart and judge the question."""
    cfg = QUESTION_TYPES.get(question_type, QUESTION_TYPES["general"])
    birth = BirthData(
        name="Prashna", year=when.year, month=when.month, day=when.day,
        hour=when.hour, minute=when.minute, latitude=latitude, longitude=longitude,
        tz_offset=tz_offset, place=place,
    )
    chart = compute_chart(birth)
    strengths = all_strengths(chart)

    reasons: List[str] = []
    lagna_lord = ref.SIGN_LORD[chart.lagna_sign]
    lagna_score = _DIGNITY_VAL.get(strengths[lagna_lord].dignity, 0.0)
    reasons.append(f"Ascendant lord {lagna_lord} (you) is {strengths[lagna_lord].dignity.lower()}")
    moon_score, moon_reasons = _moon_quality(chart, strengths)
    reasons += moon_reasons

    primary = cfg["primary"]
    mode = cfg["mode"]

    sixth_lord = chart.house_lord(6)
    if mode in ("health", "litigation"):
        q1, _ = _house_quality(chart, strengths, 1)
        q6, _ = _house_quality(chart, strengths, 6)
        if mode == "health":
            raw = 0.7 * q1 + moon_score + 0.6 * lagna_score - 0.8 * q6
            reasons.append("Health favours a strong 1st house/Moon and a weak 6th (disease) house")
        else:
            raw = q1 + moon_score + 0.5 * lagna_score - 0.9 * q6
            reasons.append("You (1st) vs the opponent (6th) — a stronger 1st favours you")
        significators = [lagna_lord, "Moon", sixth_lord]
        key_pair = (lagna_lord, sixth_lord)
        inverted = True  # a connection to the 6th (disease/opponent) is adverse
    else:
        ph_score, ph_reasons = _house_quality(chart, strengths, primary)
        reasons += ph_reasons
        support_score = 0.0
        for h in cfg.get("support", []):
            s, _ = _house_quality(chart, strengths, h)
            support_score += 0.4 * s
        raw = ph_score + 0.5 * support_score + 0.6 * moon_score + 0.4 * lagna_score
        matter_lord = chart.house_lord(primary)
        significators = [lagna_lord, matter_lord, "Moon"]
        # For a "general" question the matter lord == lagna lord; use the Moon.
        key_pair = (lagna_lord, matter_lord) if matter_lord != lagna_lord else (lagna_lord, "Moon")
        inverted = False

    # ---- Tajika yogas (Ithasala / Ishrafa / Nakta) -----------------------
    yogas = prashna_yogas(chart, list(dict.fromkeys(significators)))
    key = _find_yoga(yogas, key_pair[0], key_pair[1])
    if key.get("type") == "Ithasala":
        raw += -0.9 if inverted else 0.9
        reasons.append(key["reason"])
    elif key.get("type") == "Ishrafa":
        raw += 0.5 if inverted else -0.5
        reasons.append(key["reason"])
    elif key.get("type") == "Nakta":
        raw += -0.4 if inverted else 0.4
        reasons.append(key["reason"])

    pct = max(5.0, min(95.0, 50.0 + raw * 8.0))
    verdict = _verdict(pct)

    m = chart.planets["Moon"]
    return {
        "question_type": cfg["label"],
        "asked_at": when.strftime("%d %b %Y, %I:%M %p").lstrip("0"),
        "place": place,
        "lagna": chart.lagna_sign,
        "moon_sign": m.sign,
        "moon_nakshatra": m.nakshatra,
        "score": round(pct, 1),
        "verdict": verdict,
        "reasons": reasons,
        "yogas": yogas,
        "timing": _timing_hint(chart, primary),
        "chart": chart,
    }
