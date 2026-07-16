"""Plain-talk narrative synthesis — a to-the-point reading framed around the native.

Turns the structured chart data into a conversational reading (like a good
astrologer explaining it in person): foundational placements, what's working,
what needs effort, current timing, planets to watch, plus per-area deep dives.
"""

from __future__ import annotations

from typing import Dict, List

from . import reference as ref
from .friendly_report import dignity_phrase, bindu_context

# Short outer/inner temperament per sign (kept tight and everyday).
SIGN_TRAIT = {
    "Aries": "bold, direct, action-first",
    "Taurus": "grounded, steady, comfort-loving",
    "Gemini": "curious, quick, communicative",
    "Cancer": "sensitive, nurturing, home-centred",
    "Leo": "confident, warm, leadership-driven",
    "Virgo": "practical, analytical, detail-focused",
    "Libra": "balanced, relational, harmony-seeking",
    "Scorpio": "intense, private, transformative",
    "Sagittarius": "philosophical, freedom-loving, big-picture",
    "Capricorn": "disciplined, ambitious, patient",
    "Aquarius": "independent, unconventional, idea-driven",
    "Pisces": "imaginative, compassionate, dreamy",
}

# What each planet governs, in plain words (for "planets to watch" + timing).
PLANET_DOMAIN = {
    "Sun": "authority, confidence, father and vitality",
    "Moon": "emotions, home, mother and mental peace",
    "Mars": "energy, drive, assertiveness, property and siblings",
    "Mercury": "communication, intellect, business and nerves",
    "Jupiter": "wisdom, fortune, children and growth",
    "Venus": "love, comfort, pleasure and relationships",
    "Saturn": "discipline, career, patience and long lessons",
    "Rahu": "ambition, foreign links and obsessive desire",
    "Ketu": "detachment, spirituality and letting go",
}

# Health-specific body/domain per planet (classical Vedic health astrology).
PLANET_HEALTH = {
    "Sun": "heart, eyes, bones and overall vitality",
    "Moon": "fluids, digestion, chest and emotional health",
    "Mars": "blood, inflammation, injuries and energy levels",
    "Mercury": "nervous system, skin and speech",
    "Jupiter": "liver, weight and fat metabolism",
    "Venus": "kidneys, reproductive health, skin and the pull toward indulgence",
    "Saturn": "bones, joints, teeth and chronic conditions",
    "Rahu": "hard-to-diagnose or unusual complaints",
    "Ketu": "mysterious, intermittent or karmic ailments",
}

DASHA_THEME = {
    "Sun": "authority, health and self-confidence",
    "Moon": "emotions, home and mental peace",
    "Mars": "energy, drive, property and bold action",
    "Mercury": "study, business and communication",
    "Jupiter": "wisdom, children, fortune and expansion",
    "Venus": "love, comfort, art and relationships",
    "Saturn": "discipline, career consolidation and karma",
    "Rahu": "ambition, foreign links and desire",
    "Ketu": "spirituality, detachment and research",
}

_WEAK_DIGNITIES = {"Debilitated", "Enemy's Sign"}


def _foundation(name, lagna, moon_sign, nak, pada, nav_percent, nav_verdict) -> str:
    lead = f"{name}, you are" if name and name != "Native" else "You are"
    asc = SIGN_TRAIT.get(lagna, "distinctive")
    inner = SIGN_TRAIT.get(moon_sign, "distinctive")
    scale = (
        "a strong baseline for resilience" if nav_percent >= 70
        else "a mixed baseline" if nav_percent >= 50
        else "a baseline that needs conscious support"
    )
    return (
        f"{lead} a **{lagna} Ascendant** with **Moon in {moon_sign}** "
        f"({nak} nakshatra, pada {pada}). That pairs a {asc} outer nature "
        f"with a {inner} inner drive. Your birth-quality score is "
        f"**{nav_percent:.0f}% ({nav_verdict})** — {scale} in this tradition, "
        f"where Moon strength (Chandrabala) is the single heaviest-weighted factor."
    )


def _area_line(area_name: str, house_num: int, houses) -> str:
    r = houses[house_num]
    lord = r.lord
    dom = PLANET_DOMAIN.get(lord, "its themes")
    return (
        f"**{area_name}** — {r.lord} rules this area and is {dignity_phrase(r.lord_dignity)}, "
        f"placed in house {r.lord_house} (support score {r.sav_points}/56)."
    )


def _timing(timing: dict) -> str:
    maha = timing.get("current_maha")
    antar = timing.get("current_antar")
    if not maha:
        return "Current planetary period (Dasha) data is unavailable."
    parts = [
        f"You are in a **{maha} Mahadasha**"
        + (f" with **{antar} Antardasha**" if antar else "")
        + "."
    ]
    parts.append(
        f"{maha} (the larger period) sets the broad theme of these years — "
        f"{DASHA_THEME.get(maha, 'karmic growth')}."
    )
    if antar and antar != maha:
        parts.append(
            f"{antar} (the current sub-period) is the flavour layered on top right now — "
            f"{DASHA_THEME.get(antar, 'inner change')}."
        )
    ss = timing.get("sade_sati", "")
    if ss and "Not in" in ss:
        parts.append(
            "Reassuringly, you are **not in Sade Sati** (the ~7.5-year Saturn pressure phase) currently."
        )
    elif ss:
        parts.append(f"Saturn's Sade Sati is a factor now: {ss}.")
    return " ".join(parts)


def _watch(weak_planets: List[str]) -> str:
    if not weak_planets:
        return (
            "No planets sit in their weakest sign, so there is no single dominant "
            "weak point to offset — keep your overall routine balanced."
        )
    lines = []
    for p in weak_planets:
        lines.append(f"**{p}** (debilitated — weakest sign placement), tied to {PLANET_DOMAIN.get(p, 'its themes')}")
    joined = "; ".join(lines)
    return (
        f"The chart points to {joined}. This tradition suggests planet-specific "
        f"remedies (gemstones, mantras or practices) in a later Phase 3 to offset these."
    )


def _deep_dive_health(houses, nadi, nadi_meaning, yoga_name, yoga_quality, yoga_note) -> str:
    r = houses[6]
    lord = r.lord
    health_dom = PLANET_HEALTH.get(lord, "its associated organs")
    weak = r.lord_dignity in _WEAK_DIGNITIES
    verdict_line = (
        f"Your health house (6th, Ripu) is ruled by **{lord}**, which is "
        f"{dignity_phrase(r.lord_dignity)} in house {r.lord_house}. "
    )
    if weak:
        verdict_line += (
            f"That weak placement is the main reason health reads as needing attention — "
            f"it isn't something that just runs on autopilot. "
        )
    else:
        verdict_line += "That gives your health house a reasonably steady ruler. "

    sav_line = (
        f"Its Ashtakavarga support is {bindu_context(r.sav_points)} — "
        + (
            "so the underlying constitution has strong backing even where the ruling planet is weak. "
            if r.sav_points >= 30 else
            "so underlying support is moderate to low; routine matters more here. "
        )
    )
    domain_line = (
        f"A stressed {lord} classically points to care around {health_dom}. "
    )
    const_line = (
        f"Your constitution is **{nadi} Nadi** — {nadi_meaning}. "
    )
    yoga_line = ""
    if yoga_quality != "Challenged":
        yoga_line = (
            f"On the plus side, your birth Yoga **{yoga_name}** supports vitality — "
            f"health tends to improve with steady routine. "
        )
    else:
        yoga_line = (
            f"Your birth Yoga **{yoga_name}** is flagged as a caution ({yoga_note}), "
            f"so disciplined self-care matters more. "
        )
    bottom = (
        "**Bottom line:** your health is more in your hands than automatic — "
        "regular sleep, meals and movement (and moderation around comfort/indulgence) "
        "are the specific levers, more than any inherent fragility."
    )
    return verdict_line + sav_line + domain_line + const_line + yoga_line + bottom


def _deep_dive_generic(title: str, house_num: int, houses, extra: str = "") -> str:
    r = houses[house_num]
    lord = r.lord
    dom = PLANET_DOMAIN.get(lord, "its themes")
    weak = r.lord_dignity in _WEAK_DIGNITIES
    strong = r.lord_dignity in ("Exalted", "Own Sign", "Moolatrikona")
    verdict = r.verdict
    line = (
        f"Your {title.lower()} area is **{verdict}**. It's ruled by **{lord}** "
        f"({dignity_phrase(r.lord_dignity)}) in house {r.lord_house}, "
        f"with {bindu_context(r.sav_points)} of support. "
    )
    if strong:
        line += f"{lord} is well placed, so this reads as a natural strength rather than a forced effort. "
    elif weak:
        line += (
            f"Because {lord} is weak, this area won't run on autopilot — "
            f"be realistic and consistent rather than assuming it will sort itself out. "
        )
    else:
        line += "The placement is workable; your choices and timing shape the outcome. "
    line += f"{lord} governs {dom}. "
    if extra:
        line += extra
    return line.strip()


def build_narrative(
    *,
    name: str,
    lagna: str,
    moon_sign: str,
    nakshatra: str,
    pada: int,
    nav_percent: float,
    nav_verdict: str,
    houses,
    timing: dict,
    weak_planets: List[str],
    nadi: str,
    nadi_meaning: str,
    yoga_name: str,
    yoga_quality: str,
    yoga_note: str,
    nak_data: dict,
) -> Dict:
    """Assemble the plain-talk narrative dict."""
    working, effort = [], []
    area_houses = [
        ("Wealth", 2), ("Career", 10), ("Marriage & love", 7),
        ("Health", 6), ("Spiritual path", 9),
    ]
    for area_name, hn in area_houses:
        line = _area_line(area_name, hn, houses)
        if houses[hn].verdict == "Supported":
            working.append(line)
        else:
            effort.append(line)

    overview = [
        ("Your foundational placements",
         _foundation(name, lagna, moon_sign, nakshatra, pada, nav_percent, nav_verdict)),
    ]
    if working:
        overview.append(("What's working in your favour", "\n\n".join(f"- {w}" for w in working)))
    if effort:
        overview.append(("What needs more conscious effort", "\n\n".join(f"- {e}" for e in effort)))
    overview.append(("Where you are right now (timing)", _timing(timing)))
    overview.append(("The planets to watch", _watch(weak_planets)))

    deep_dives = {
        "Health": _deep_dive_health(
            houses, nadi, nadi_meaning, yoga_name, yoga_quality, yoga_note,
        ),
        "Wealth": _deep_dive_generic("Wealth", 2, houses),
        "Career": _deep_dive_generic(
            "Career", 10, houses,
            extra=(f"Suited fields (from your birth star): {nak_data['career']}. "
                   if nak_data.get("career") else ""),
        ),
        "Marriage & love": _deep_dive_generic(
            "Marriage & love", 7, houses,
            extra=(f"Relationship tone (from your birth star): {nak_data['relationship']}. "
                   if nak_data.get("relationship") else ""),
        ),
        "Spiritual path": _deep_dive_generic("Spiritual path", 9, houses),
    }

    disclaimer = (
        "This is a traditional interpretive framework, not a predictive science — "
        "useful as a lens for reflection, not a fixed outcome."
    )
    return {"overview": overview, "deep_dives": deep_dives, "disclaimer": disclaimer}
