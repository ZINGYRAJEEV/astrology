"""Mundane AI / technology themes — Lahiri Prashna overlay.

Adds plain-language Mercury · Rahu · Saturn notes and short horizon cues
on top of a tech-focused horary verdict. Symbolic guidance only — not a
product roadmap or market prediction.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from . import reference as ref
from .prashna import QUESTION_TYPES, answer_prashna
from .strength_calc import all_strengths

AI_PRESETS = [
    {
        "key": "ai_future",
        "title": "Future of AI (collective themes)",
        "question": "What themes will shape artificial intelligence in the coming years?",
    },
    {
        "key": "ai_career",
        "title": "AI career / product launch",
        "question": "Is this a favourable window to build or launch an AI product or career path?",
    },
    {
        "key": "ai_risk",
        "title": "AI risk & regulation",
        "question": "Where do disruption, ethics, and regulatory pressure sit for AI right now?",
    },
]

_HOUSE_AI = {
    1: "public face / adoption of AI identity",
    2: "data value, speech models, monetisation of knowledge",
    3: "media, skills, short-cycle tools, developer culture",
    4: "infrastructure at home / cloud foundations",
    5: "creativity, generative models, education use",
    6: "competition, compliance labour, system bugs / debt",
    7: "partnerships, platforms, public contracts",
    8: "sudden shocks, shared risk, deep research / opacity",
    9: "ethics, law, higher learning, cross-border norms",
    10: "industry status, big tech authority, careers",
    11: "networks, gains, open ecosystems, scale",
    12: "foreign labs, retreat, cost of compute / loss themes",
}


def _planet_theme(chart, strengths, name: str, role: str) -> Dict:
    p = chart.planets[name]
    dig = strengths[name].dignity
    return {
        "planet": ref.planet_label(name),
        "role": role,
        "sign": ref.sign_label(p.sign),
        "house": p.house,
        "dignity": dig,
        "house_theme": _HOUSE_AI.get(p.house, "mixed themes"),
        "line": (
            f"{ref.planet_label(name)} ({role}) in {ref.sign_label(p.sign)} "
            f"{p.house}th — {dig}; theme: {_HOUSE_AI.get(p.house, 'mixed')}."
        ),
    }


def _horizon_bands(verdict: str, timing: str) -> List[str]:
    """Short near / mid symbolic bands (not calendar prophecy)."""
    if verdict == "Favourable":
        return [
            "Near term: openings for tools, skills, and network-led gains — move with clarity.",
            "Mid term: structure (Saturn themes) decides who scales; favour durable systems over hype.",
            f"Pace cue: {timing}",
        ]
    if verdict == "Unfavourable":
        return [
            "Near term: friction, compliance, or over-promise risk — slow big bets.",
            "Mid term: rebuild on ethics, testing, and clearer rules before chasing scale.",
            f"Pace cue: {timing}",
        ]
    return [
        "Near term: mixed signals — pilot small, measure, avoid all-or-nothing launches.",
        "Mid term: winners pair Mercury skills with Saturn discipline and Rahu reach.",
        f"Pace cue: {timing}",
    ]


def analyze_ai_themes(
    question_type: str,
    when: datetime,
    latitude: float,
    longitude: float,
    tz_offset: float,
    place: str,
    question_text: str = "",
) -> Dict:
    """Prashna tech verdict + Mercury/Rahu/Saturn thematic overlay (Lahiri)."""
    if question_type not in QUESTION_TYPES or QUESTION_TYPES[question_type].get("mode") != "tech":
        question_type = "ai_future"

    base = answer_prashna(question_type, when, latitude, longitude, tz_offset, place)
    chart = base["chart"]
    strengths = all_strengths(chart)

    significators = [
        _planet_theme(chart, strengths, "Mercury", "intellect / code / systems"),
        _planet_theme(chart, strengths, "Rahu", "disruption / foreign tech / scale"),
        _planet_theme(chart, strengths, "Saturn", "regulation / durability / limits"),
    ]

    working, watch = [], []
    for s in significators:
        dig = s["dignity"]
        h = s["house"]
        if dig in ("Exalted", "Own Sign", "Moolatrikona") or h in (3, 10, 11):
            working.append(s["line"])
        if dig in ("Debilitated", "Enemy's Sign") or h in (6, 8, 12):
            watch.append(s["line"])

    summary = (
        f"**{base['verdict']}** ({base['score']}%) for “{QUESTION_TYPES[question_type]['label']}” "
        f"at {base['asked_at']} · {place} (Lahiri). "
        f"Ascendant {base['lagna']}; Moon in {base['moon_sign']} ({base['moon_nakshatra']})."
    )

    return {
        **{k: v for k, v in base.items() if k != "chart"},
        "question_text": question_text,
        "method": "Lahiri sidereal Prashna + Mercury/Rahu/Saturn mundane overlay",
        "summary": summary,
        "significators": significators,
        "working": working[:4],
        "watch": watch[:4],
        "horizon": _horizon_bands(base["verdict"], base["timing"]),
        "disclaimer": (
            "Symbolic Jyotish guidance for reflection — not a technical, legal, or investment forecast."
        ),
    }
