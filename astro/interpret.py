"""Interpretation & synthesis engine (Phases 2-3 of the 12-step framework).

Brings together placement, dignity and aspect data into:
  * functional benefic/malefic classification per ascendant,
  * a house-by-house assessment (ruler + occupants + aspects),
  * "repeating pattern" detection (confidence rises when several
    independent indicators agree),
  * remedial measures gated by the "Do No Harm" rule, and
  * a written synthesis tailored to the seeker's stated focus.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from . import reference as ref
from .chart_engine import Chart
from .strength_calc import all_strengths, PlanetStrength
from .aspects import aspects_on_house

# Which houses to emphasise per client intent (Phase 1, step 5).
INTENT_HOUSES = {
    "Health & vitality": [1, 6, 8],
    "Career & success": [10, 6, 11, 2],
    "Wealth & finances": [2, 11, 5, 9],
    "Marriage & relationships": [7, 5, 2, 8],
    "Spiritual growth": [9, 12, 5, 8],
    "Family & home": [4, 2, 3, 11],
    "General reading": [1, 4, 7, 10, 5, 9],
}


# ---------------------------------------------------------------------------
# Functional nature (relative to the ascendant)
# ---------------------------------------------------------------------------
def ruled_houses(chart: Chart, planet: str) -> List[int]:
    """House numbers ruled by ``planet`` in this chart (whole-sign)."""
    owned = ref.OWN_SIGNS.get(planet, set())
    return [h for h, sign in chart.house_signs.items() if sign in owned]


def functional_nature(chart: Chart) -> Dict[str, Dict]:
    """Classify each planet as functional benefic/malefic/neutral for the lagna."""
    result: Dict[str, Dict] = {}
    for planet in ref.PLANETS:
        houses = ruled_houses(chart, planet)
        score = 0
        for h in houses:
            if h in ref.TRIKONA:
                score += 2          # trikona lords are the best
            if h in ref.KENDRA and h != 1:
                # natural benefics ruling a kendra suffer kendradhipati dosha;
                # natural malefics ruling a kendra gain benefic power.
                score += -1 if planet in ref.NATURAL_BENEFICS else 1
            if h in {3, 11}:
                score -= 1
            if h in {6, 8, 12}:
                score -= 2
        # Yogakaraka: rules both a kendra and a trikona.
        if any(h in ref.KENDRA for h in houses) and any(h in ref.TRIKONA for h in houses):
            score += 2
        if not houses:               # nodes
            nature = "Neutral"
        elif score > 1:
            nature = "Benefic"
        elif score < 0:
            nature = "Malefic"
        else:
            nature = "Neutral"
        result[planet] = {
            "nature": nature,
            "ruled_houses": houses,
            "score": score,
            "yogakaraka": any(h in ref.KENDRA for h in houses) and any(h in ref.TRIKONA for h in houses),
        }
    return result


# ---------------------------------------------------------------------------
# House-by-house analysis
# ---------------------------------------------------------------------------
@dataclass
class HouseReport:
    house: int
    name: str
    sign: str
    signification: str
    category: str
    lord: str
    lord_house: int
    lord_dignity: str
    lord_strength: int
    occupants: List[str]
    aspecting: List[str]
    signals: List[str]
    verdict: str         # "Supported" / "Mixed" / "Challenged"


def analyse_house(chart: Chart, house: int, strengths: Dict[str, PlanetStrength]) -> HouseReport:
    sign = chart.house_signs[house]
    lord = ref.SIGN_LORD[sign]
    lord_pos = chart.planets[lord]
    lord_strength = strengths[lord]
    occupants = chart.occupants(house)
    aspecting = [a["planet"] for a in aspects_on_house(chart, house)]

    signals: List[str] = []
    pos, neg = 0, 0

    # 1) Lord's dignity.
    if lord_strength.dignity in ("Exalted", "Own Sign", "Moolatrikona"):
        signals.append(f"Lord {lord} is strong ({lord_strength.dignity}).")
        pos += 1
    elif lord_strength.dignity in ("Debilitated", "Enemy's Sign"):
        signals.append(f"Lord {lord} is weak ({lord_strength.dignity}).")
        neg += 1

    # 2) Lord's placement (dusthana weakens the house).
    if lord_pos.house in ref.DUSTHANA:
        signals.append(f"Lord {lord} sits in dusthana house {lord_pos.house}.")
        neg += 1
    elif lord_pos.house in (ref.KENDRA | ref.TRIKONA):
        signals.append(f"Lord {lord} sits in supportive house {lord_pos.house}.")
        pos += 1

    # 3) Occupants.
    for occ in occupants:
        if occ in ref.NATURAL_BENEFICS:
            signals.append(f"Benefic {occ} occupies the house.")
            pos += 1
        else:
            signals.append(f"Malefic {occ} occupies the house.")
            neg += 1

    # 4) Aspects.
    for a in aspects_on_house(chart, house):
        if a["planet"] in occupants:
            continue
        if a["is_benefic"]:
            signals.append(f"Benefic {a['planet']} aspects from house {a['from_house']}.")
            pos += 1
        else:
            signals.append(f"Malefic {a['planet']} aspects from house {a['from_house']}.")
            neg += 1

    if pos - neg >= 1:
        verdict = "Supported"
    elif neg - pos >= 1:
        verdict = "Challenged"
    else:
        verdict = "Mixed"

    return HouseReport(
        house=house,
        name=ref.HOUSE_NAME[house],
        sign=sign,
        signification=ref.HOUSE_SIGNIFICATION[house],
        category=ref.house_category(house),
        lord=lord,
        lord_house=lord_pos.house,
        lord_dignity=lord_strength.dignity,
        lord_strength=lord_strength.percent,
        occupants=occupants,
        aspecting=aspecting,
        signals=signals,
        verdict=verdict,
    )


def analyse_all_houses(chart: Chart) -> Dict[int, HouseReport]:
    strengths = all_strengths(chart)
    return {h: analyse_house(chart, h, strengths) for h in range(1, 13)}


# ---------------------------------------------------------------------------
# Repeating patterns (confidence through agreement)
# ---------------------------------------------------------------------------
def repeating_patterns(chart: Chart) -> List[Dict]:
    """Flag houses where ruler, occupants and aspects all point the same way."""
    reports = analyse_all_houses(chart)
    patterns = []
    for h, r in reports.items():
        # count agreeing indicators
        good = sum(1 for s in r.signals if "strong" in s or "Benefic" in s or "supportive" in s)
        bad = sum(1 for s in r.signals if "weak" in s or "Malefic" in s or "dusthana" in s)
        # Need at least 2 independent indicators in agreement to be "repeating".
        if good >= 2 and bad == 0:
            patterns.append({
                "house": h,
                "theme": ref.HOUSE_THEME[h],
                "direction": "favourable",
                "count": good,
                "detail": f"{good} indicators agree that {ref.HOUSE_THEME[h]} is well supported.",
            })
        elif bad >= 2 and good == 0:
            patterns.append({
                "house": h,
                "theme": ref.HOUSE_THEME[h],
                "direction": "challenging",
                "count": bad,
                "detail": f"{bad} indicators agree that {ref.HOUSE_THEME[h]} needs attention.",
            })
    patterns.sort(key=lambda p: p["count"], reverse=True)
    return patterns


# ---------------------------------------------------------------------------
# Remedies (Do No Harm)
# ---------------------------------------------------------------------------
def recommend_remedies(chart: Chart) -> List[Dict]:
    """Suggest remedies, only strengthening *functional benefics*.

    Per the briefing's caution, strengthening a functional malefic with a
    gemstone can cause harm, so for malefics we recommend pacifying measures
    (mantra / charity) instead of gemstones.
    """
    strengths = all_strengths(chart)
    nature = functional_nature(chart)
    recs = []
    for planet in ref.PLANETS:
        nat = nature[planet]["nature"]
        s = strengths[planet]
        rem = ref.REMEDIES[planet]
        if nat == "Benefic" and s.score < 0.6:
            recs.append({
                "planet": planet,
                "rationale": f"Functional benefic but weak ({s.dignity}). Safe to strengthen.",
                "gemstone": rem["gemstone"],
                "mantra": rem["mantra"],
                "charity": rem["charity"],
                "strengthen": True,
            })
        elif nat == "Malefic" and s.score < 0.45:
            recs.append({
                "planet": planet,
                "rationale": "Functional malefic - PACIFY only (no gemstone). Do No Harm.",
                "gemstone": "- (avoid strengthening)",
                "mantra": rem["mantra"],
                "charity": rem["charity"],
                "strengthen": False,
            })
    return recs


# ---------------------------------------------------------------------------
# Written synthesis
# ---------------------------------------------------------------------------
def synthesize(chart: Chart, intent: str = "General reading") -> Dict:
    """Phase 3: synthesise findings into a structured, readable report."""
    from .strength_calc import chart_foundation_score
    from .dasha_calc import compute_vimshottari, current_dasha, starting_nakshatra

    strengths = all_strengths(chart)
    foundation = chart_foundation_score(chart)
    reports = analyse_all_houses(chart)
    patterns = repeating_patterns(chart)
    nature = functional_nature(chart)

    nak = starting_nakshatra(chart)
    periods = compute_vimshottari(chart)
    maha, antar = current_dasha(periods)

    lagna_lord = ref.SIGN_LORD[chart.lagna_sign]
    lagnesh = strengths[lagna_lord]

    emphasis = INTENT_HOUSES.get(intent, INTENT_HOUSES["General reading"])

    paragraphs: List[str] = []

    # Lagna paragraph.
    vargottama = " It is Vargottama (same sign in D-1 and D-9), giving exceptional stability." \
        if lagnesh.vargottama else ""
    paragraphs.append(
        f"The Ascendant (Lagna) is {chart.lagna_sign} "
        f"({ref.SIGN_SANSKRIT[chart.lagna_sign]}), making {lagna_lord} the chart ruler "
        f"(Lagnesh). The Lagnesh is {lagnesh.dignity} at {lagnesh.percent}% dignity, "
        f"placed in house {chart.planet_house(lagna_lord)}. A "
        f"{'strong' if lagnesh.score >= 0.6 else 'weaker'} Lagnesh indicates "
        f"{'resilience and the ability to sail through adversity' if lagnesh.score >= 0.6 else 'a need to consciously build vitality and confidence'}.{vargottama}"
    )

    # Foundation paragraph.
    parts = [f"Overall chart foundation scores {foundation['average_percent']}%."]
    if foundation["exalted"]:
        parts.append("Exalted: " + ", ".join(foundation["exalted"]) + ".")
    if foundation["own"]:
        parts.append("In own sign: " + ", ".join(foundation["own"]) + ".")
    if foundation["debilitated"]:
        parts.append("Debilitated (needs care): " + ", ".join(foundation["debilitated"]) + ".")
    if foundation["vargottama"]:
        parts.append("Vargottama: " + ", ".join(foundation["vargottama"]) + ".")
    paragraphs.append(" ".join(parts))

    # Focus paragraph.
    focus_lines = []
    for h in emphasis:
        r = reports[h]
        focus_lines.append(
            f"House {h} ({r.name} - {ref.HOUSE_THEME[h]}): {r.verdict}. "
            f"Lord {r.lord} ({r.lord_dignity}) in house {r.lord_house}."
        )
    paragraphs.append(
        f"For your focus on '{intent}', the most relevant houses are: "
        + " ".join(focus_lines)
    )

    # Pattern paragraph.
    if patterns:
        fav = [p for p in patterns if p["direction"] == "favourable"]
        chal = [p for p in patterns if p["direction"] == "challenging"]
        line = "Repeating patterns (high confidence): "
        if fav:
            line += "Strengths in " + ", ".join(ref.HOUSE_THEME[p["house"]] for p in fav) + ". "
        if chal:
            line += "Attention needed in " + ", ".join(ref.HOUSE_THEME[p["house"]] for p in chal) + "."
        paragraphs.append(line)

    # Timing paragraph.
    if maha:
        timing = (
            f"Timing (Vimshottari Dasha): birth Nakshatra is {nak['nakshatra']} "
            f"(lord {nak['lord']}). The currently running Mahadasha is {maha.lord}"
        )
        if antar:
            timing += f", with {antar.lord} Antardasha"
        timing += (
            f". This activates {maha.lord}-related themes; '{maha.lord}' governs "
            f"houses {', '.join(map(str, ruled_houses(chart, maha.lord))) or 'shadow/karmic'} in your chart."
        )
        paragraphs.append(timing)

    return {
        "intent": intent,
        "paragraphs": paragraphs,
        "foundation": foundation,
        "patterns": patterns,
        "functional_nature": nature,
        "current_maha": maha.lord if maha else None,
        "current_antar": antar.lord if antar else None,
        "nakshatra": nak,
    }


# ---------------------------------------------------------------------------
# Plain-language reading (for people new to astrology)
# ---------------------------------------------------------------------------
# Everyday meanings so a beginner can understand the chart without jargon.
PLANET_PLAIN = {
    "Sun": "confidence, vitality and your sense of self",
    "Moon": "emotions, peace of mind and your inner world",
    "Mars": "energy, courage and drive to take action",
    "Mercury": "thinking, communication, learning and business sense",
    "Jupiter": "wisdom, growth, optimism and good fortune",
    "Venus": "love, relationships, comfort and enjoyment of life",
    "Saturn": "discipline, patience, hard work and life's longer lessons",
    "Rahu": "ambition, big desires and unconventional paths",
    "Ketu": "detachment, spirituality and letting go",
}

DIGNITY_PLAIN = {
    "Exalted": "is very strong here and can give its best",
    "Moolatrikona": "is very comfortable and strong here",
    "Own Sign": "is at home and stable here",
    "Friend's Sign": "is reasonably well supported here",
    "Neutral's Sign": "is average here \u2014 neither helped nor hindered",
    "Enemy's Sign": "is a bit strained and less effective here",
    "Debilitated": "is weakened here and needs conscious support",
}

VERDICT_PLAIN = {
    "Supported": ("Favourable", "This area has natural support in your chart."),
    "Mixed": ("Mixed", "This area has both helpful and challenging influences \u2014 your choices tip the balance."),
    "Challenged": ("Needs effort", "This area asks for conscious attention and steady effort."),
}

# Friendly framing per focus area.
INTENT_PLAIN = {
    "Health & vitality": {
        "title": "Health & Vitality",
        "intro": "how strong and resilient your body and energy tend to be",
        "good": "You generally carry good reserves of energy; steady routines keep you well.",
        "work": "Prioritise rest, balanced food and stress management \u2014 small daily habits help most.",
    },
    "Career & success": {
        "title": "Career & Success",
        "intro": "your work, public standing and the way you build a career",
        "good": "You have real momentum for growth and recognition \u2014 keep aiming higher.",
        "work": "Progress comes through persistence and skill-building rather than shortcuts.",
    },
    "Wealth & finances": {
        "title": "Wealth & Finances",
        "intro": "how money comes to you, your savings and overall prosperity",
        "good": "Money tends to flow and accumulate when you stay consistent.",
        "work": "Be deliberate with budgeting and avoid impulsive risks; wealth builds gradually.",
    },
    "Marriage & relationships": {
        "title": "Marriage & Relationships",
        "intro": "your partnerships, marriage and how you relate to others closely",
        "good": "You are well set up for warm, committed partnership.",
        "work": "Patience, honest communication and the right timing matter for harmony.",
    },
    "Spiritual growth": {
        "title": "Spiritual Growth",
        "intro": "your inner life, meaning, wisdom and the path toward peace",
        "good": "You have a natural pull toward growth, wisdom and inner peace.",
        "work": "Regular practice (meditation, study, service) steadily opens this path.",
    },
    "Family & home": {
        "title": "Family & Home",
        "intro": "your home life, mother, comfort and emotional foundation",
        "good": "Home and family are a source of strength and comfort for you.",
        "work": "Nurturing your roots and emotional security pays off over time.",
    },
    "General reading": {
        "title": "Life Overview",
        "intro": "the main pillars of your life \u2014 self, home, relationships and career",
        "good": "Your core life areas have solid support to build on.",
        "work": "A few areas need conscious effort; awareness is the first step.",
    },
}


def plain_language_reading(chart: Chart, intent: str = "General reading") -> Dict:
    """Beginner-friendly reading focused on the chosen life area.

    Translates dignity / house-lord / dasha findings into everyday language
    and gives concrete, supportive guidance for the selected ``intent``.
    """
    from .dasha_calc import compute_vimshottari, current_dasha

    strengths = all_strengths(chart)
    reports = analyse_all_houses(chart)
    info = INTENT_PLAIN.get(intent, INTENT_PLAIN["General reading"])
    emphasis = INTENT_HOUSES.get(intent, INTENT_HOUSES["General reading"])

    # ---- headline -------------------------------------------------------
    verdicts = [reports[h].verdict for h in emphasis]
    n_good = verdicts.count("Supported")
    n_bad = verdicts.count("Challenged")
    if n_good > n_bad:
        tone = "mostly favourable"
        headline = (
            f"Your chart looks {tone} for {info['title'].lower()}. {info['good']}"
        )
    elif n_bad > n_good:
        tone = "challenging but workable"
        headline = (
            f"Your chart is {tone} for {info['title'].lower()}. {info['work']}"
        )
    else:
        tone = "balanced"
        headline = (
            f"Your chart is {tone} for {info['title'].lower()}: real strengths "
            f"alongside areas that reward effort."
        )

    # ---- intro about ascendant in plain words ---------------------------
    lagna_lord = ref.SIGN_LORD[chart.lagna_sign]
    ll = strengths[lagna_lord]
    overview = (
        f"Think of your Ascendant ({chart.lagna_sign}) as your starting point in life "
        f"\u2014 your personality and vitality. Its 'ruler' is {lagna_lord}, the planet of "
        f"{PLANET_PLAIN[lagna_lord]}. In your chart {lagna_lord} {DIGNITY_PLAIN[ll.dignity]}, "
        f"which means your overall foundation is "
        f"{'strong and resilient' if ll.score >= 0.6 else 'something to consciously build up'}."
    )

    # ---- key areas for this intent --------------------------------------
    key_areas = []
    for h in emphasis:
        r = reports[h]
        label, meaning = VERDICT_PLAIN[r.verdict]
        lord = r.lord
        lord_strength = strengths[lord]
        # Build a plain explanation.
        why = (
            f"This part of life is guided by {lord} (the planet of {PLANET_PLAIN[lord]}), "
            f"which {DIGNITY_PLAIN[lord_strength.dignity]}."
        )
        if r.occupants:
            occ_plain = ", ".join(
                f"{o} ({PLANET_PLAIN[o].split(',')[0]})" for o in r.occupants
            )
            why += f" Planets sitting here: {occ_plain}."
        # Simple advice.
        if r.verdict == "Supported":
            advice = "Lean into this \u2014 it's a natural strength you can rely on."
        elif r.verdict == "Challenged":
            advice = "Go gently and stay consistent here; effort and patience pay off."
        else:
            advice = "Stay aware here \u2014 your habits and choices decide the outcome."

        key_areas.append({
            "house": h,
            "title": ref.HOUSE_THEME[h].title(),
            "label": label,
            "verdict": r.verdict,
            "meaning": meaning,
            "explanation": why,
            "advice": advice,
        })

    # ---- current life period (dasha) in plain words ---------------------
    periods = compute_vimshottari(chart)
    maha, antar = current_dasha(periods)
    timing = None
    if maha:
        ml = maha.lord
        sub = f" Within it runs a {antar.lord} sub-period, colouring the next months with {PLANET_PLAIN[antar.lord].split(',')[0]}." if antar else ""
        timing = (
            f"Right now you are in a {ml} life-period (Dasha). This tends to bring "
            f"{PLANET_PLAIN[ml]} to the foreground for several years.{sub} "
            f"For your focus on {info['title'].lower()}, this is the energy currently "
            f"shaping your experience \u2014 work with it rather than against it."
        )

    # ---- simple action steps -------------------------------------------
    actions = []
    good_houses = [a for a in key_areas if a["verdict"] == "Supported"]
    weak_houses = [a for a in key_areas if a["verdict"] == "Challenged"]
    if good_houses:
        actions.append(
            "Build on your strengths: " +
            ", ".join(a["title"].lower() for a in good_houses) + "."
        )
    if weak_houses:
        actions.append(
            "Give extra care to: " +
            ", ".join(a["title"].lower() for a in weak_houses) + "."
        )
    actions.append(info["good"] if n_good >= n_bad else info["work"])

    return {
        "intent": intent,
        "title": info["title"],
        "intro": info["intro"],
        "headline": headline,
        "tone": tone,
        "overview": overview,
        "key_areas": key_areas,
        "timing": timing,
        "actions": actions,
    }
