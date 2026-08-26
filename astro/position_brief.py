"""Concise planetary-position brief — Copilot-style clear bullets.

Turns house lords, placements, current Dasha and Gochara into short,
scannable sections (Career / Wealth / Family / Health) with bold leads,
plus a transit overlay and a one-line summary. Avoids mixing everything
into long paragraphs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from . import reference as ref
from .chart_engine import Chart
from .dasha_calc import compute_vimshottari, current_dasha
from .gochar import gochar_report
from .interpret import analyse_all_houses
from .strength_calc import all_strengths

# Life-area → house used for the brief.
_AREA_HOUSES = [
    ("Career", 10),
    ("Wealth", 2),
    ("Family", 7),
    ("Health", 6),
]

_HOUSE_THEME_SHORT = {
    1: "self & vitality",
    2: "income & speech",
    3: "effort & siblings",
    4: "home & peace",
    5: "creativity & children",
    6: "health & competition",
    7: "partnership & public",
    8: "sudden change & depth",
    9: "fortune & dharma",
    10: "career & status",
    11: "gains & network",
    12: "loss & foreign links",
}

_GOCHARA_EFFECTS = {
    1: ["Identity pressure", "Fresh starts", "Body focus"],
    2: ["Money themes", "Family speech", "Food / values"],
    3: ["Effort & courage", "Short travel", "Sibling matters"],
    4: ["Home & property", "Emotional comfort", "Mother themes"],
    5: ["Creativity", "Children / romance", "Speculation"],
    6: ["Competition", "Enemies", "Legal / work pressure", "Health routine"],
    7: ["Partnerships", "Public image", "Agreements"],
    8: ["Sudden shifts", "Shared money", "Hidden obstacles"],
    9: ["Guidance", "Travel", "Higher learning", "Luck"],
    10: ["Career visibility", "Authority", "Reputation"],
    11: ["Gains", "Network support", "Wish fulfilment"],
    12: ["Expenses", "Foreign links", "Retreat / closure"],
}

_WEAK = {"Debilitated", "Enemy's Sign"}
_STRONG = {"Exalted", "Own Sign", "Moolatrikona"}


def _bullet(lead: str, detail: str = "") -> Dict[str, str]:
    return {"lead": lead.strip(), "detail": detail.strip()}


def _area_bullets(area: str, house: int, report, chart: Chart, strengths) -> List[Dict]:
    """Short bullets for one life area from lord placement + occupants."""
    lord = report.lord
    lord_h = report.lord_house
    dig = report.lord_dignity
    theme = _HOUSE_THEME_SHORT.get(lord_h, "this area")
    bullets: List[Dict] = []

    # Verdict lead.
    if report.verdict == "Supported":
        bullets.append(_bullet(
            f"{area} support is strong",
            f"{ref.planet_label(lord)} rules this house and is {dig} in the {lord_h}th "
            f"({theme}).",
        ))
    elif report.verdict == "Challenged":
        bullets.append(_bullet(
            f"{area} needs conscious effort",
            f"{ref.planet_label(lord)} ({dig}) in the {lord_h}th — {theme} colours results.",
        ))
    else:
        bullets.append(_bullet(
            f"{area} is mixed — choices matter",
            f"Lord {ref.planet_label(lord)} in the {lord_h}th ({dig}).",
        ))

    # Area-specific leads from classical house meaning + lord house.
    if area == "Career":
        if lord_h in (10, 11, 2, 9):
            bullets.append(_bullet("Career visibility", f"Lord links work to {theme}."))
        elif lord_h in (6, 8, 12):
            bullets.append(_bullet(
                "Work pressure or role shifts",
                f"Career lord in {lord_h}th can bring competition, change, or foreign/remote work.",
            ))
        if dig in _STRONG:
            bullets.append(_bullet("Authority potential", "Strong career lord favours leadership roles."))
        if dig in _WEAK:
            bullets.append(_bullet("Career slowdown risk", "Weak lord — avoid impulsive job jumps."))

    elif area == "Wealth":
        if lord_h in (2, 11, 5, 9):
            bullets.append(_bullet("Income pathways open", f"Wealth lord supports {theme}."))
        elif lord_h in (6, 8, 12):
            bullets.append(_bullet(
                "High volatility: gains + losses",
                "Wealth lord in a dusthana — plan, don't gamble.",
            ))
        if dig in _WEAK:
            bullets.append(_bullet("Must avoid impulsive financial decisions", ""))
        occ = report.occupants
        if "Rahu" in occ or "Mars" in occ:
            bullets.append(_bullet(
                "Rahu/Mars often triggers",
                "real estate moves · business partnerships · high-risk investments",
            ))

    elif area == "Family":
        if lord_h == 7:
            bullets.append(_bullet("Partnership focus", "7th themes stay central in relationships."))
        if lord_h in (6, 8, 12) or dig in _WEAK:
            bullets.append(_bullet(
                "Stress in marriage / close bonds",
                f"{ref.planet_label(lord)} rules the 7th and sits under pressure.",
            ))
        if "Rahu" in report.occupants:
            bullets.append(_bullet(
                "Misunderstandings",
                "Rahu's illusion-creating nature can cloud clarity with partners.",
            ))
        if chart.planets["Mars"].house in (1, 2, 4, 7, 8, 12):
            bullets.append(_bullet(
                "Sibling / in-law karmas may activate",
                f"Mars in {chart.planets['Mars'].house}th can heat family dynamics.",
            ))

    elif area == "Health":
        health_hits = []
        for p in ("Mars", "Saturn", "Rahu", "Moon", "Sun"):
            if chart.planets[p].house in (1, 6, 8) or dig in _WEAK and lord == p:
                pass
        if dig in _WEAK or lord_h in (6, 8, 12):
            bullets.append(_bullet("Health fluctuations", "routine and sleep matter more than usual"))
        # Classic Mars/Rahu combo notes when both afflict 1/6/8
        mars_h = chart.planets["Mars"].house
        rahu_h = chart.planets["Rahu"].house
        if mars_h in (1, 6, 8) or rahu_h in (1, 6, 8):
            bullets.append(_bullet("Inflammation / blood pressure watch", "Mars themes"))
        if mars_h in (1, 8) and rahu_h in (1, 6, 8):
            bullets.append(_bullet("Accidents (Mars + Rahu combination)", "extra care with speed & travel"))
        if chart.planets["Moon"].house in (6, 8, 12) or strengths["Moon"].dignity in _WEAK:
            bullets.append(_bullet("Mental agitation", "sleep, mood, and digestion need pacing"))

    # Occupants of the house as short bullets.
    for occ in report.occupants[:3]:
        bullets.append(_bullet(
            f"{ref.planet_label(occ)} in the {house}th",
            f"colours {area.lower()} with {ref.PLANET_SANSKRIT.get(occ, occ)} themes.",
        ))

    return bullets[:6]  # keep scannable


def _key_positions(chart: Chart, houses) -> List[Dict[str, str]]:
    """One-liners like: Moon is 8th lord → placed in Aries (7th)."""
    lines = []
    lagna = chart.lagna_sign
    for name in ("Sun", "Moon", "Mars", "Jupiter", "Saturn", "Rahu"):
        p = chart.planets[name]
        ruled = [h for h in range(1, 13) if ref.SIGN_LORD[ref.SIGNS[(chart.lagna_sign_index + h - 1) % 12]] == name]
        # Simpler: which houses does this planet lord from lagna?
        ruled = []
        for h in range(1, 13):
            sign = ref.SIGNS[(chart.lagna_sign_index + h - 1) % 12]
            if ref.SIGN_LORD[sign] == name:
                ruled.append(h)
        if not ruled and name in ("Rahu", "Ketu"):
            lines.append({
                "planet": name,
                "text": (
                    f"{ref.planet_label(name)} in **{ref.sign_label(p.sign)}** "
                    f"({p.house}th) → {_HOUSE_THEME_SHORT.get(p.house, '')}."
                ),
            })
            continue
        if not ruled:
            continue
        lords = " & ".join(f"{h}th" for h in ruled[:2])
        lines.append({
            "planet": name,
            "text": (
                f"{ref.planet_label(name)} is **{lords} lord** for {ref.sign_label(lagna)} Lagna "
                f"→ placed in {ref.sign_label(p.sign)} ({p.house}th)."
            ),
        })
    return lines[:5]


def _gochara_overlay(chart: Chart) -> List[Dict]:
    """Saturn / Jupiter / Rahu style: Planet in Sign (house) → effect bullets."""
    report = gochar_report(chart)
    overlay = []
    for row in report.get("rows", []):
        if row["planet"] not in ("Saturn", "Jupiter", "Rahu", "Mars", "Sun"):
            continue
        h = row["house_from_lagna"]
        effects = _GOCHARA_EFFECTS.get(h, ["Mixed results"])
        overlay.append({
            "line": (
                f"{ref.planet_label(row['planet'])} in {ref.sign_label(row['sign'])} "
                f"({h}th) →"
            ),
            "effects": effects[:4],
            "favourable": row["favourable"],
        })
    return overlay[:4]


def _dasha_heading(chart: Chart) -> Dict:
    periods = compute_vimshottari(chart)
    maha, antar = current_dasha(periods)
    if not maha:
        return {"title": "Current period", "subtitle": "", "bullets": []}
    title = f"{ref.planet_label(maha.lord)}"
    if antar:
        title += f" / {ref.planet_label(antar.lord)}"
    subtitle = f"{maha.start:%b %Y} – {maha.end:%b %Y}"
    if antar:
        subtitle = f"Antardasha {antar.start:%b %Y} – {antar.end:%b %Y}"
    bullets = [
        _bullet("Mahadasha theme", ref.PLANET_SANSKRIT.get(maha.lord, maha.lord) + " chapter is running"),
    ]
    if antar:
        bullets.append(_bullet(
            "Current flavour",
            f"{ref.planet_label(antar.lord)} sub-period colours the next stretch",
        ))
    return {"title": title, "subtitle": subtitle, "bullets": bullets}


def _summary(areas: List[Dict], gochara: List[Dict], dasha: Dict) -> str:
    challenged = [a["name"] for a in areas if a.get("tone") == "challenged"]
    supported = [a["name"] for a in areas if a.get("tone") == "supported"]
    bits = []
    if dasha.get("title"):
        bits.append(f"You are in a **{dasha['title']}** chapter")
    if supported:
        bits.append(f"**strength** shows in {', '.join(supported).lower()}")
    if challenged:
        bits.append(f"**watch points** in {', '.join(challenged).lower()}")
    hard_go = [g for g in gochara if not g.get("favourable")]
    if hard_go:
        bits.append("transits currently **reshape pressure and timing**")
    else:
        bits.append("transits offer **usable support** if you stay consistent")
    if not bits:
        return "This chart period asks for **clear priorities** and steady effort."
    text = ". ".join(bits)
    if not text.endswith("."):
        text += "."
    return text[0].upper() + text[1:] if text else text


def build_position_brief(chart: Chart) -> Dict:
    """Full Copilot-style planetary brief for the prediction report."""
    houses = analyse_all_houses(chart)
    strengths = all_strengths(chart)
    areas = []
    for name, h in _AREA_HOUSES:
        r = houses[h]
        tone = (
            "supported" if r.verdict == "Supported"
            else "challenged" if r.verdict == "Challenged"
            else "mixed"
        )
        areas.append({
            "name": name,
            "house": h,
            "verdict": r.verdict,
            "tone": tone,
            "bullets": _area_bullets(name, h, r, chart, strengths),
        })

    positions = _key_positions(chart, houses)
    gochara = _gochara_overlay(chart)
    dasha = _dasha_heading(chart)
    summary = _summary(areas, gochara, dasha)

    # Non-obvious insight: lagna lord + nodes.
    lagna_lord = ref.SIGN_LORD[chart.lagna_sign]
    ll = chart.planets[lagna_lord]
    insight = (
        f"{ref.planet_label(lagna_lord)} rules your **{ref.sign_label(chart.lagna_sign)} Lagna** "
        f"and sits in the **{ll.house}th** ({ref.sign_label(ll.sign)}). "
        f"That placement is the **theme of how life opens for you** — "
        f"{_HOUSE_THEME_SHORT.get(ll.house, 'core direction')}."
    )

    return {
        "title": "Lahiri chart interpretation",
        "insight": insight,
        "dasha": dasha,
        "key_positions": positions,
        "areas": areas,
        "gochara": gochara,
        "summary": summary,
        "when": datetime.now().strftime("%Y-%m-%d"),
    }
