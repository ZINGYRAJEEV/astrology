"""Nature & behaviour portrait from birth-chart placements.

Builds a layman-friendly description of the native's outer/inner nature and
how each planet-in-house placement colours day-to-day behaviour.
"""

from __future__ import annotations

from typing import Dict, List

from . import reference as ref
from .chart_engine import Chart
from .combinations import planet_in_house
from .narrative import SIGN_TRAIT, PLANET_DOMAIN
from .strength_calc import all_strengths

_HOUSE_BEHAVIOUR = {
    1: "how you present yourself and your core personality",
    2: "speech, values, family tone and money habits",
    3: "courage, initiative and how you communicate",
    4: "emotional comfort, home life and inner peace",
    5: "creativity, romance, children and risk-taking",
    6: "daily routine, service, health habits and conflict style",
    7: "how you behave in partnerships and with the public",
    8: "depth, privacy, shared resources and transformation",
    9: "beliefs, luck, ethics and higher learning",
    10: "public image, ambition and work behaviour",
    11: "friendships, gains and social networking style",
    12: "solitude, spending, foreign links and letting go",
}


def build_nature_profile(chart: Chart) -> Dict:
    """Portrait + per-planet nature/behaviour from house placements."""
    strengths = all_strengths(chart)
    moon = chart.planets["Moon"]
    lagna = chart.lagna_sign
    lagna_lord = ref.SIGN_LORD[lagna]
    ll = chart.planets[lagna_lord]
    outer = SIGN_TRAIT.get(lagna, "distinctive")
    inner = SIGN_TRAIT.get(moon.sign, "distinctive")
    name = chart.birth.name or "You"
    lead = name if name != "Native" else "You"

    portrait = (
        f"{lead} shows a **{ref.sign_label(lagna)} Ascendant** — outwardly "
        f"{outer} — with **{ref.planet_label('Moon')} in {ref.sign_label(moon.sign)}** "
        f"({moon.nakshatra}, pada {moon.nakshatra_pada}), so the inner emotional style "
        f"is {inner}. Your chart ruler "
        f"**{ref.planet_label(lagna_lord)}** sits in the "
        f"**{ll.house}th house** ({_HOUSE_BEHAVIOUR.get(ll.house, 'that life area')}) "
        f"in {ref.sign_label(ll.sign)}, which strongly colours how these traits "
        f"play out in daily life."
    )

    # Short trait bullets from Ascendant, Moon and key angular placements.
    traits: List[str] = [
        f"Outer nature (Lagna): {outer}.",
        f"Inner / emotional nature (Moon): {inner}.",
        f"Chart ruler {ref.planet_label(lagna_lord)} in house {ll.house} steers "
        f"{_HOUSE_BEHAVIOUR.get(ll.house, 'life direction')}.",
    ]

    placements: List[Dict] = []
    for pname in ref.PLANETS:
        p = chart.planets[pname]
        info = planet_in_house(pname, p.house) or {}
        dignity = strengths[pname].dignity
        house_theme = _HOUSE_BEHAVIOUR.get(p.house, "this area of life")
        effect = info.get("effect") or (
            f"{pname} in the {p.house}th house colours {house_theme}."
        )
        nature_line = (
            f"{ref.planet_label(pname)} in the **{p.house}th house** "
            f"({ref.sign_label(p.sign)}, {dignity}) — governs "
            f"{PLANET_DOMAIN.get(pname, 'its themes')}. {effect}"
        )
        placements.append({
            "planet": pname,
            "label": ref.planet_label(pname),
            "house": p.house,
            "sign": p.sign,
            "sign_label": ref.sign_label(p.sign),
            "dignity": dignity,
            "retrograde": p.retrograde,
            "nature": nature_line,
            "behaviour_strengths": info.get("merits", ""),
            "behaviour_cautions": info.get("demerits", ""),
            "house_theme": house_theme,
        })
        # Highlight 1st-house planets as especially behavioural.
        if p.house == 1 and pname != lagna_lord:
            traits.append(
                f"{ref.planet_label(pname)} in the 1st house stamps your personality "
                f"with {PLANET_DOMAIN.get(pname, 'its flavour')}."
            )

    return {
        "portrait": portrait,
        "traits": traits,
        "placements": placements,
    }
