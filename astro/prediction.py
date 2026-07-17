"""Astrology prediction engine — birth chart + Panchang at birth.

Combines:
  * Janam Kundli (sidereal chart from date, time, place, name)
  * Panchang at the exact birth moment (Tithi, Nakshatra, Yoga, Karana, Vaara)
  * House analysis, Dasha timing, and repeating patterns

Produces plain-language life predictions suitable for end users.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional

from . import reference as ref
from .chart_engine import Chart, BirthData, compute_chart
from .panchang import compute_panchang, format_time
from . import prediction_data as pd
from .strength_calc import all_strengths, chart_foundation_score
from .interpret import (
    analyse_all_houses, repeating_patterns, functional_nature,
    recommend_remedies, ruled_houses, INTENT_HOUSES,
)
from .dasha_calc import compute_vimshottari, current_dasha, starting_nakshatra, sade_sati_status
from .rishikesh_prediction import analyze_rishikesh_birth
from . import friendly_report as fr
from .narrative import build_narrative
from .yogas import detect_yogas
from .vargas import reading_highlights
from .combinations import layman_outcomes


def _birth_datetime(chart: Chart) -> datetime:
    b = chart.birth
    return datetime(b.year, b.month, b.day, b.hour, b.minute)


def birth_panchang(chart: Chart):
    """Panchang computed at the exact birth date/time (not sunrise)."""
    b = chart.birth
    return compute_panchang(
        date(b.year, b.month, b.day),
        latitude=b.latitude,
        longitude=b.longitude,
        tz_offset=b.tz_offset,
        place=b.place or "Birth place",
        place_hindi=b.place.split(",")[0] if b.place else "Birth place",
        at_time=_birth_datetime(chart),
    )


def _year_ahead(maha_lord: str, antar_lord: Optional[str]) -> str:
    themes = {
        "Sun": "authority, health, father and self-confidence",
        "Moon": "emotions, home, mother and mental peace",
        "Mars": "energy, property, siblings and bold action",
        "Mercury": "study, business, communication and skills",
        "Jupiter": "wisdom, children, fortune and expansion",
        "Venus": "love, comfort, art and relationships",
        "Saturn": "discipline, delays, career consolidation and karma",
        "Rahu": "ambition, foreign links, technology and desire",
        "Ketu": "spirituality, detachment, research and letting go",
    }
    base = themes.get(maha_lord, "karmic growth")
    line = f"The coming period emphasises {base}."
    if antar_lord and antar_lord != maha_lord:
        line += f" Right now the sub-theme is {themes.get(antar_lord, 'inner change')}."
    return line


def generate_prediction(
    chart: Chart,
    intent: str = "General reading",
    horizon_years: int = 5,
) -> Dict:
    """Full personalised prediction from birth data + Panchang + chart."""
    b = chart.birth
    panch = birth_panchang(chart)
    birth_dt = _birth_datetime(chart)
    rishikesh = analyze_rishikesh_birth(chart, panch, birth_dt)
    strengths = all_strengths(chart)
    houses = analyse_all_houses(chart)
    foundation = chart_foundation_score(chart)
    patterns = repeating_patterns(chart)
    nature = functional_nature(chart)
    remedies = recommend_remedies(chart)
    nak_info = starting_nakshatra(chart)
    periods = compute_vimshottari(chart)
    maha, antar = current_dasha(periods)
    ss = sade_sati_status(chart)

    moon = chart.planets["Moon"]
    lagna_lord = ref.SIGN_LORD[chart.lagna_sign]
    ll = strengths[lagna_lord]

    # Panchang-based personality block.
    nak = pd.NAKSHATRA_PREDICTION.get(moon.nakshatra, {})
    tithi_pos = panch.tithi.index if panch.tithi.index <= 15 else panch.tithi.index - 15
    tithi_text = pd.TITHI_PREDICTION.get(tithi_pos, "")
    if panch.tithi.index > 15:
        tithi_text = "Krishna Paksha tone: " + tithi_text + " Inward and reflective energy."
    yoga_text = pd.YOGA_PREDICTION.get(panch.yoga.name, "")
    karana_text = pd.KARANA_PREDICTION.get(panch.karana.name, "")
    vaara_text = pd.VAARA_PREDICTION.get(panch.vaara.name, "")

    panchang_block = {
        "vaara": panch.vaara.name,
        "tithi": f"{panch.tithi.name} ({panch.paksha})",
        "nakshatra": moon.nakshatra,
        "nakshatra_pada": moon.nakshatra_pada,
        "nakshatra_lord": nak_info["lord"],
        "yoga": panch.yoga.name,
        "karana": panch.karana.name,
        "hindu_month": panch.hindu_month,
        "summary": nak.get("prediction", "Your birth star shapes your inner nature."),
    }

    # Short summary placeholder — rebuilt after life_predictions exist (Rule 10).
    opening = ""

    # Life-area predictions — plain verdict first, technical basis separate.
    life_predictions: List[Dict] = []
    av = rishikesh["avakhada"]
    nav = rishikesh["navaratna"]

    life_predictions.append(fr.format_personality_section(
        nak, av, nav["percent"], vaara_text, tithi_text, yoga_text, karana_text,
        chart.lagna_sign, lagna_lord, ll.dignity, ll.score, nav["verdict"],
    ))

    for area_name, house_num, _subtitle in pd.LIFE_AREAS[1:]:
        r = houses[house_num]
        extra = ""
        if house_num == 10:
            extra = nak.get("career", "")
        elif house_num == 7:
            extra = nak.get("relationship", "")
        life_predictions.append(fr.format_house_section(area_name, house_num, r, extra))

    focus_houses = INTENT_HOUSES.get(intent, INTENT_HOUSES["General reading"])
    focus_lines = [fr.format_focus_line(h, houses[h]) for h in focus_houses]

    # Timing / year ahead.
    timing = {
        "birth_nakshatra": nak_info["nakshatra"],
        "birth_nakshatra_lord": nak_info["lord"],
        "dasha_balance_years": round(nak_info["balance_years"], 2),
        "current_maha": maha.lord if maha else None,
        "current_antar": antar.lord if antar else None,
        "maha_until": format_time(maha.end) if maha else None,
        "year_ahead": _year_ahead(maha.lord, antar.lord if antar else None) if maha else "",
        "sade_sati": ss["phase"],
        "guru_gochar": rishikesh["guru_gochar"]["phase"],
    }

    # Lucky elements from chart + panchang.
    lucky = {
        "day": panch.vaara.name_hindi or panch.vaara.name,
        "nakshatra": moon.nakshatra,
        "nakshatra_lord": nak_info["lord"],
        "lucky_direction": ref.SIGN_ELEMENT.get(chart.lagna_sign, "—"),
        "gemstone_hint": ref.REMEDIES.get(lagna_lord, {}).get("gemstone", "—")
        if nature.get(lagna_lord, {}).get("nature") == "Benefic" else "Consult astrologer",
        "mantra_hint": ref.REMEDIES.get(lagna_lord, {}).get("mantra", ""),
    }

    # High-confidence patterns.
    pattern_texts = [p["detail"] for p in patterns[:3]]

    cautions = list(rishikesh["spoil_notes"])
    if ss["active"]:
        cautions.append(f"Sade Sati active: {ss['phase']} — period of Saturnian refinement.")
    if foundation["debilitated"]:
        cautions.append(
            "Some planets are in weak placements and may need support — "
            "see Horoscope & Reading → Phase 3 for remedies (not in this download)."
        )
    if panch.karana.name == "Vishti":
        cautions.append("Birth Karana Vishti (Bhadra) — avoid impulsive starts; plan carefully.")
    if rishikesh["limbs"]["yoga"]["quality"] == "Challenged":
        cautions.append(rishikesh["limbs"]["yoga"]["note"])

    result = {
        "name": b.name or "Native",
        "moon_sign": moon.sign,
        "birth": {
            "date": f"{b.day:02d}/{b.month:02d}/{b.year}",
            "time": f"{b.hour:02d}:{b.minute:02d}",
            "place": b.place,
            "lagna": chart.lagna_sign,
            "day": b.day, "month": b.month, "year": b.year,
            "hour": b.hour, "minute": b.minute,
        },
        "panchang_at_birth": panchang_block,
        "rishikesh": rishikesh,
        "opening": opening,
        "life_predictions": life_predictions,
        "focus_intent": intent,
        "focus_detail": [fl["plain"] for fl in focus_lines],
        "focus_friendly": focus_lines,
        "timing": timing,
        "lucky": lucky,
        "patterns": pattern_texts,
        "cautions": cautions,
        "remedies_count": len(remedies),
        "remedies_summary": [
            {"planet": r["planet"], "strengthen": r["strengthen"],
             "rationale": r["rationale"][:120]}
            for r in remedies[:4]
        ],
        "weak_planets": foundation["debilitated"],
        "yogas": detect_yogas(chart),
        "divisional": reading_highlights(chart),
        "combinations_reading": layman_outcomes(chart),
    }
    # Rebuild summary now that life_predictions exist.
    result["summary"] = fr.build_summary(
        result["name"], life_predictions, rishikesh["navaratna"]["percent"], intent,
    )
    result["opening"] = result["summary"]
    # Plain-talk narrative (to-the-point synthesis + per-area deep dives).
    result["narrative"] = build_narrative(
        name=result["name"],
        lagna=chart.lagna_sign,
        moon_sign=moon.sign,
        nakshatra=moon.nakshatra,
        pada=moon.nakshatra_pada,
        nav_percent=rishikesh["navaratna"]["percent"],
        nav_verdict=rishikesh["navaratna"]["verdict"],
        houses=houses,
        timing=timing,
        weak_planets=foundation["debilitated"],
        nadi=av["nadi"],
        nadi_meaning=av.get("nadi_meaning", ""),
        yoga_name=panch.yoga.name,
        yoga_quality=rishikesh["limbs"]["yoga"]["quality"],
        yoga_note=rishikesh["limbs"]["yoga"]["note"],
        nak_data=nak,
    )
    return fr.enrich_prediction(result, {
        "day": b.day, "month": b.month, "year": b.year,
        "hour": b.hour, "minute": b.minute, "place": b.place,
    })


def predict_from_birth(birth: BirthData, intent: str = "General reading") -> Dict:
    """One-call API: birth inputs -> prediction dict."""
    chart = compute_chart(birth)
    return generate_prediction(chart, intent)


def prediction_markdown(pred: Dict) -> str:
    """Export user-friendly prediction as Markdown."""
    lines = [
        f"# Life Prediction — {pred['name']}",
        "",
        f"> {pred.get('scope_note', fr.SCOPE_NOTE)}",
        "",
        pred.get("verdict_legend", fr.VERDICT_LEGEND),
        "",
        "## At a glance",
        pred.get("summary", pred.get("opening", "")),
        "",
    ]
    for line in pred.get("birth_intro", []):
        lines.append(f"- {line}")
    lines.append("")

    yogas = pred.get("yogas")
    if yogas:
        lines.append("## Notable yogas in your chart")
        for y in yogas:
            lines.append(f"- **{y['name']}** ({y['category']}) — {y['detail']}")
        lines.append("")

    divisional = pred.get("divisional")
    if divisional:
        lines.append("## Divisional charts (Vargas)")
        for d in divisional:
            vg = (f" · vargottama: {', '.join(d['vargottama'])}"
                  if d["vargottama"] else "")
            lines.append(f"- **{d['name']}** — {d['theme']}. Ascendant "
                         f"{d['lagna_sign']}{vg}. {d['note']}")
        lines.append("")

    combos = pred.get("combinations_reading")
    if combos:
        lines.append("## What your planetary combinations mean (in plain words)")
        for block in combos:
            lines.append(f"### {block['area']}")
            for ln in block["lines"]:
                mark = {"good": "\u2705", "caution": "\u26a0\ufe0f"}.get(ln["tone"], "\u2022")
                lines.append(f"- {mark} {ln['text']}")
            lines.append("")

    narrative = pred.get("narrative")
    if narrative:
        lines.append("## Your reading in plain words")
        for heading, text in narrative["overview"]:
            lines += [f"### {heading}", text, ""]
        lines.append("## Ask about a specific area")
        for area, text in narrative["deep_dives"].items():
            lines += [f"### {area}", text, ""]
        lines += [f"> {narrative['disclaimer']}", ""]

    groups = pred.get("groups", fr.group_predictions(pred["life_predictions"]))
    section_map = [
        ("Who you are", groups.get("who_you_are", [])),
        ("What's working well", groups.get("working_well", [])),
        ("What needs effort", groups.get("needs_effort", [])),
    ]
    for section_title, items in section_map:
        if not items:
            continue
        lines.append(f"## {section_title}")
        for lp in items:
            lines += [
                f"### {lp.get('title', lp['area'])}",
                lp.get("plain", lp.get("prediction", "")),
                "",
                f"> Technical basis: {lp.get('technical', lp.get('technical_basis', ''))}",
                "",
            ]

    lines.append(f"## Your focus: {pred['focus_intent']}")
    for fl in pred.get("focus_friendly", []):
        if isinstance(fl, dict):
            lines.append(f"- {fl['plain']}")
            if fl.get("technical"):
                lines.append(f"  > {fl['technical']}")
        else:
            lines.append(f"- {fl}")
    lines.append("")

    tf = pred.get("timing_friendly", fr.format_timing_plain(pred.get("timing", {})))
    lines += ["## What's happening now (timing)", tf["plain"], "", f"> {tf['technical']}", ""]

    if pred.get("cautions"):
        lines.append("## Watch points")
        for c in pred["cautions"]:
            lines.append(f"- {c}")
        lines.append("")

    lk = pred["lucky"]
    lines += [
        "## Favourable elements",
        f"- Weekday energy: {lk['day']}",
        f"- Birth star: {lk['nakshatra']} (lord {lk['nakshatra_lord']})",
        f"- Gemstone hint: {lk['gemstone_hint']}",
        "",
        pred.get("remedies_note", ""),
        "",
        "_Hrishikesh Panchang tradition · Lahiri sidereal · For guidance, not deterministic fate._",
    ]
    return "\n".join(lines)
