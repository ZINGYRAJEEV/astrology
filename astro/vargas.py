"""Divisional charts (Varga) engine — D3, D7, D9, D10, D12, D30.

Each divisional chart maps a planet's sidereal longitude into a finer sign
using the classical Parashari rules, then judges it from the divisional
Ascendant (whole-sign). Divisional charts reveal specific life areas:
Navamsha for marriage/dharma, Dasamsa for career, Saptamsa for children, etc.
"""

from __future__ import annotations

from typing import Dict, List

from . import reference as ref
from .chart_engine import Chart

VARGAS: Dict[int, Dict[str, str]] = {
    2: {"name": "Hora (D-2)", "signifies": "Wealth & resources"},
    3: {"name": "Drekkana (D-3)", "signifies": "Siblings, courage & initiative"},
    4: {"name": "Chaturthamsa (D-4)", "signifies": "Fortune, property & home"},
    7: {"name": "Saptamsa (D-7)", "signifies": "Children & progeny"},
    9: {"name": "Navamsha (D-9)", "signifies": "Marriage, dharma & inner strength"},
    10: {"name": "Dasamsa (D-10)", "signifies": "Career, profession & status"},
    12: {"name": "Dvadasamsa (D-12)", "signifies": "Parents & ancestry"},
    16: {"name": "Shodasamsa (D-16)", "signifies": "Vehicles, luxuries & comforts"},
    24: {"name": "Chaturvimsamsa (D-24)", "signifies": "Education & learning"},
    27: {"name": "Bhamsa (D-27)", "signifies": "Strengths, stamina & weaknesses"},
    30: {"name": "Trimsamsa (D-30)", "signifies": "Adversity, character & morals"},
    60: {"name": "Shashtiamsa (D-60)", "signifies": "Past karma & fine detail (overall)"},
}

# Trimsamsa (D-30) degree boundaries -> target sign index.
_TRIMSAMSA_ODD = [(5, 0), (10, 10), (18, 8), (25, 2), (30, 6)]     # Ar, Aq, Sg, Ge, Li
_TRIMSAMSA_EVEN = [(5, 1), (12, 5), (20, 11), (25, 9), (30, 7)]    # Ta, Vi, Pi, Cp, Sc


def varga_sign_index(longitude: float, varga: int) -> int:
    """Divisional-chart sign index (0-11) for a sidereal ``longitude``."""
    longitude = longitude % 360.0
    sign = int(longitude // 30) % 12
    deg = longitude - sign * 30.0
    is_odd = (sign % 2 == 0)  # 0-based even == 1-based odd sign

    if varga == 1:
        return sign
    if varga == 2:
        # Hora: odd sign 0-15 -> Leo, 15-30 -> Cancer; even sign reversed.
        first_half = deg < 15.0
        if is_odd:
            return 4 if first_half else 3   # Leo / Cancer
        return 3 if first_half else 4       # Cancer / Leo
    if varga == 3:
        part = int(deg // 10.0)
        return (sign + part * 4) % 12
    if varga == 4:
        part = int(deg // 7.5)
        return (sign + part * 3) % 12
    if varga == 7:
        part = int(deg // (30.0 / 7.0))
        start = sign if is_odd else (sign + 6) % 12
        return (start + part) % 12
    if varga == 9:
        return int(longitude // (30.0 / 9.0)) % 12
    if varga == 10:
        part = int(deg // 3.0)
        start = sign if is_odd else (sign + 8) % 12
        return (start + part) % 12
    if varga == 12:
        part = int(deg // 2.5)
        return (sign + part) % 12
    if varga == 16:
        part = int(deg // (30.0 / 16.0))
        start = (sign % 3) * 4          # movable->Aries, fixed->Leo, dual->Sagittarius
        return (start + part) % 12
    if varga == 24:
        part = int(deg // 1.25)
        start = 4 if is_odd else 3      # Leo (odd) / Cancer (even)
        return (start + part) % 12
    if varga == 27:
        part = int(deg // (30.0 / 27.0))
        start = (sign % 4) * 3          # fire->Aries, earth->Cancer, air->Libra, water->Cap
        return (start + part) % 12
    if varga == 30:
        table = _TRIMSAMSA_ODD if is_odd else _TRIMSAMSA_EVEN
        for upper, target in table:
            if deg < upper:
                return target
        return table[-1][1]
    if varga == 60:
        part = int(deg * 2.0)          # 0.5 deg each, 0-59
        return (sign + part) % 12
    raise ValueError(f"Unsupported varga D-{varga}")


def _dignity(planet: str, sign: str) -> str:
    if planet in ref.EXALTATION and ref.EXALTATION[planet][0] == sign:
        return "Exalted"
    if planet in ref.DEBILITATION and ref.DEBILITATION[planet][0] == sign:
        return "Debilitated"
    if sign in ref.OWN_SIGNS.get(planet, set()):
        return "Own Sign"
    return ""


def build_varga_chart(chart: Chart, varga: int) -> Dict:
    """Compute a divisional chart: divisional Ascendant + planet placements."""
    info = VARGAS.get(varga, {"name": f"D-{varga}", "signifies": ""})
    lagna_sign_idx = varga_sign_index(chart.ascendant_longitude, varga)

    planets: List[Dict] = []
    vargottama: List[str] = []
    for name in ref.PLANETS:
        p = chart.planets[name]
        v_sign_idx = varga_sign_index(p.longitude, varga)
        v_sign = ref.SIGNS[v_sign_idx]
        house = (v_sign_idx - lagna_sign_idx) % 12 + 1
        is_vargottama = (v_sign_idx == p.sign_index)
        if is_vargottama:
            vargottama.append(name)
        planets.append({
            "planet": name,
            "sign": v_sign,
            "house": house,
            "dignity": _dignity(name, v_sign),
            "retrograde": p.retrograde,
            "vargottama": is_vargottama,
            "d1_sign": p.sign,
        })

    return {
        "varga": varga,
        "name": info["name"],
        "signifies": info["signifies"],
        "lagna_sign": ref.SIGNS[lagna_sign_idx],
        "lagna_lord": ref.SIGN_LORD[ref.SIGNS[lagna_sign_idx]],
        "planets": planets,
        "vargottama": vargottama,
    }


def all_vargas(chart: Chart) -> Dict[int, Dict]:
    """Every supported divisional chart for a natal chart."""
    return {v: build_varga_chart(chart, v) for v in VARGAS}


def varga_markdown(vc: Dict, native: str) -> str:
    lines = [
        f"# {vc['name']} — {native}",
        "",
        f"> {vc['signifies']}",
        "",
        f"**Divisional Ascendant:** {vc['lagna_sign']} (lord {vc['lagna_lord']})",
        "",
        "| Planet | Sign | House | Dignity | Vargottama |",
        "| --- | --- | --- | --- | --- |",
    ]
    for p in vc["planets"]:
        lines.append(
            f"| {p['planet']}{' (R)' if p['retrograde'] else ''} | {p['sign']} | "
            f"{p['house']} | {p['dignity'] or '—'} | {'Yes' if p['vargottama'] else ''} |"
        )
    if vc["vargottama"]:
        lines += ["", f"**Vargottama planets:** {', '.join(vc['vargottama'])} "
                  "(same sign in D-1 and this varga — a strength)."]
    return "\n".join(lines)
