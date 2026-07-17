"""Gochara (transit) engine — current planetary transits vs the natal chart.

Computes every planet's live sidereal position and judges it relative to the
native's Janma Rashi (natal Moon sign) and Lagna, using the classical Gochara
benefic-house scheme. Flags the key life-timing transits:
  * Sade Sati (Saturn 12/1/2 from Moon)
  * Ashtama Shani (Saturn 8th) and Kantaka Shani (Saturn 4th)
  * Guru Gochar (Jupiter in 2/5/7/9/11 from Moon)
  * Rahu / Ketu axis houses from Moon
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

import swisseph as swe

from . import reference as ref
from .chart_engine import Chart

_FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL
_SWE_ID = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}

# Classical auspicious transit houses from the natal Moon (Gochara).
GOCHARA_GOOD_HOUSES: Dict[str, set] = {
    "Sun": {3, 6, 10, 11},
    "Moon": {1, 3, 6, 7, 10, 11},
    "Mars": {3, 6, 11},
    "Mercury": {2, 4, 6, 8, 10, 11},
    "Jupiter": {2, 5, 7, 9, 11},
    "Venus": {1, 2, 3, 4, 5, 8, 9, 11, 12},
    "Saturn": {3, 6, 11},
    "Rahu": {3, 6, 10, 11},
    "Ketu": {3, 6, 10, 11},
}


def _dignity(planet: str, sign: str) -> str:
    if planet in ref.EXALTATION and ref.EXALTATION[planet][0] == sign:
        return "Exalted"
    if planet in ref.DEBILITATION and ref.DEBILITATION[planet][0] == sign:
        return "Debilitated"
    if sign in ref.OWN_SIGNS.get(planet, set()):
        return "Own Sign"
    return ""


def transit_positions(when: Optional[datetime] = None) -> Dict[str, Dict]:
    """Current sidereal transit longitude / sign for all nine planets."""
    when = when or datetime.now()
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd = swe.julday(when.year, when.month, when.day, when.hour + when.minute / 60.0)
    out: Dict[str, Dict] = {}
    for name, body in _SWE_ID.items():
        xx = swe.calc_ut(jd, body, _FLAGS)[0]
        lon = xx[0] % 360.0
        speed = xx[3]
        sidx = int(lon // 30) % 12
        out[name] = {
            "longitude": lon,
            "sign_index": sidx,
            "sign": ref.SIGNS[sidx],
            "retrograde": (name == "Rahu") or (speed < 0),
        }
    # Ketu is exactly opposite Rahu.
    rahu = out["Rahu"]
    ketu_lon = (rahu["longitude"] + 180.0) % 360.0
    ketu_sidx = int(ketu_lon // 30) % 12
    out["Ketu"] = {
        "longitude": ketu_lon,
        "sign_index": ketu_sidx,
        "sign": ref.SIGNS[ketu_sidx],
        "retrograde": True,
    }
    return out


def _house_from(sign_index: int, ref_sign_index: int) -> int:
    return (sign_index - ref_sign_index) % 12 + 1


def gochar_report(chart: Chart, when: Optional[datetime] = None) -> Dict:
    """Full transit report relative to the native's Moon sign and Lagna."""
    when = when or datetime.now()
    pos = transit_positions(when)
    moon_sign_idx = chart.planets["Moon"].sign_index
    lagna_idx = chart.lagna_sign_index

    rows: List[Dict] = []
    for name in ref.PLANETS:
        p = pos[name]
        h_moon = _house_from(p["sign_index"], moon_sign_idx)
        h_lagna = _house_from(p["sign_index"], lagna_idx)
        favourable = h_moon in GOCHARA_GOOD_HOUSES.get(name, set())
        rows.append({
            "planet": name,
            "sign": p["sign"],
            "retrograde": p["retrograde"],
            "dignity": _dignity(name, p["sign"]),
            "house_from_moon": h_moon,
            "house_from_lagna": h_lagna,
            "favourable": favourable,
        })

    highlights: List[Dict] = []

    # Saturn transits.
    sat_h = _house_from(pos["Saturn"]["sign_index"], moon_sign_idx)
    if sat_h in (12, 1, 2):
        phase = {12: "Rising phase (12th)", 1: "Peak (over Moon)", 2: "Setting phase (2nd)"}[sat_h]
        highlights.append({
            "title": "Sade Sati active",
            "tone": "challenging",
            "detail": (
                f"Saturn transits {pos['Saturn']['sign']} — {phase} from your natal Moon. "
                "A ~7.5-year period of testing, maturation and restructuring."
            ),
        })
    elif sat_h == 8:
        highlights.append({
            "title": "Ashtama Shani",
            "tone": "challenging",
            "detail": (
                f"Saturn in the 8th ({pos['Saturn']['sign']}) from your Moon — a phase asking "
                "patience with health, obstacles and slow change."
            ),
        })
    elif sat_h == 4:
        highlights.append({
            "title": "Kantaka Shani (Ardhashtama)",
            "tone": "challenging",
            "detail": (
                f"Saturn in the 4th ({pos['Saturn']['sign']}) from your Moon — pressure around "
                "home, peace of mind and domestic matters."
            ),
        })
    else:
        highlights.append({
            "title": "Saturn transit",
            "tone": "favourable" if sat_h in GOCHARA_GOOD_HOUSES["Saturn"] else "neutral",
            "detail": (
                f"Saturn in the {sat_h}th ({pos['Saturn']['sign']}) from your Moon — "
                + ("a supportive Saturn phase for disciplined effort."
                   if sat_h in GOCHARA_GOOD_HOUSES["Saturn"]
                   else "a routine Saturn phase; steady effort is favoured.")
            ),
        })

    # Jupiter transit (Guru Gochar).
    jup_h = _house_from(pos["Jupiter"]["sign_index"], moon_sign_idx)
    jup_good = jup_h in ref_guru_houses()
    highlights.append({
        "title": "Guru Gochar (Jupiter)",
        "tone": "favourable" if jup_good else "neutral",
        "detail": (
            f"Jupiter in the {jup_h}th ({pos['Jupiter']['sign']}) from your Moon — "
            + ("auspicious for growth, marriage, children and fortune."
               if jup_good else "a quieter Jupiter phase; consolidate rather than expand.")
        ),
    })

    # Rahu / Ketu axis.
    rahu_h = _house_from(pos["Rahu"]["sign_index"], moon_sign_idx)
    ketu_h = _house_from(pos["Ketu"]["sign_index"], moon_sign_idx)
    highlights.append({
        "title": "Rahu–Ketu axis",
        "tone": "neutral",
        "detail": (
            f"Rahu in the {rahu_h}th ({pos['Rahu']['sign']}) and Ketu in the {ketu_h}th "
            f"({pos['Ketu']['sign']}) from your Moon — the axis of desire vs detachment "
            "for this ~18-month phase."
        ),
    })

    return {
        "when": when,
        "moon_sign": ref.SIGNS[moon_sign_idx],
        "lagna": chart.lagna_sign,
        "rows": rows,
        "highlights": highlights,
    }


def ref_guru_houses() -> set:
    """Auspicious Jupiter transit houses from natal Moon."""
    return {2, 5, 7, 9, 11}
