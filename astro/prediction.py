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

    # Opening prediction — Rishikesh Panchang synthesis + chart foundation.
    opening = (
        f"{b.name or 'Dear native'}, born on {b.day:02d}/{b.month:02d}/{b.year} at "
        f"{b.hour:02d}:{b.minute:02d} in {b.place or 'your birthplace'} "
        f"({rishikesh['ishtakal']['formatted']} after sunrise at {rishikesh['sunrise_at_birth']}), "
        f"you carry {chart.lagna_sign} Ascendant with Moon in {moon.nakshatra} "
        f"(pada {moon.nakshatra_pada}, Janma Rashi {moon.sign}). "
        f"Birth Panchang: {panch.vaara.name}, {panch.tithi.name} ({panch.paksha}), "
        f"Yoga {panch.yoga.name}, Karana {panch.karana.name}. "
        f"{rishikesh['synthesis']} "
        f"{nak.get('prediction', '')} "
        f"Chart foundation scores {foundation['average_percent']}% overall dignity."
    )

    # Life-area predictions (chart + panchang blend).
    life_predictions: List[Dict] = []

    rk = rishikesh
    av = rk["avakhada"]
    nav = rk["navaratna"]

    # Personality (always) — Avakhada + five limbs per Rishikesh tradition.
    life_predictions.append({
        "area": "Personality & nature",
        "verdict": nav["verdict"] if nav["verdict"] != "Auspicious" else (
            "Supported" if ll.score >= 0.5 else "Mixed"
        ),
        "prediction": (
            f"{nak.get('nature', 'Unique nature')}. "
            f"Avakhada: {av['varna']} Varna ({av['varna_meaning']}), "
            f"{av['gana']} Gana ({av['gana_meaning']}), "
            f"{av['yoni']} Yoni, {av['nadi']} Nadi ({av['nadi_meaning']}). "
            f"{vaara_text} Birth Tithi: {tithi_text} "
            f"Yoga: {yoga_text} Karana: {karana_text} "
            f"Navaratna birth quality: {nav['verdict']} ({nav['percent']}%)."
        ),
        "panchang_factor": f"{moon.nakshatra} Nakshatra, {panch.tithi.name}",
        "chart_factor": f"{chart.lagna_sign} Lagna, Lagnesh {lagna_lord} ({ll.dignity})",
    })

    for area_name, house_num, subtitle in pd.LIFE_AREAS[1:]:
        r = houses[house_num]
        verdict = r.verdict
        nak_career = nak.get("career", "") if house_num == 10 else ""
        nak_rel = nak.get("relationship", "") if house_num == 7 else ""
        extra = nak_career or nak_rel or ""
        life_predictions.append({
            "area": area_name,
            "verdict": verdict,
            "prediction": (
                f"{pd.VERDICT_PREDICTION[verdict]} "
                f"House {house_num} ({r.name}): lord {r.lord} in house {r.lord_house} "
                f"({r.lord_dignity}). Ashtakavarga {r.sav_points} bindus ({r.sav_class}). "
                f"{extra}"
            ).strip(),
            "panchang_factor": panchang_block["summary"] if house_num in (9, 7) else "",
            "chart_factor": "; ".join(r.signals[:2]) if r.signals else r.verdict,
        })

    # Focus area (user intent).
    focus_houses = INTENT_HOUSES.get(intent, INTENT_HOUSES["General reading"])
    focus_lines = []
    for h in focus_houses:
        r = houses[h]
        focus_lines.append(
            f"**{ref.HOUSE_THEME[h].title()}** ({r.verdict}): lord {r.lord} "
            f"({r.lord_dignity}) — {pd.VERDICT_PREDICTION[r.verdict]}"
        )

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
        "guru_gochar": rk["guru_gochar"]["phase"],
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

    cautions = list(rk["spoil_notes"])
    if ss["active"]:
        cautions.append(f"Sade Sati active: {ss['phase']} — period of Saturnian refinement.")
    if foundation["debilitated"]:
        cautions.append(
            "Planets needing care: " + ", ".join(foundation["debilitated"]) +
            " — remedies in Phase 3 may help."
        )
    if panch.karana.name == "Vishti":
        cautions.append("Birth Karana Vishti (Bhadra) — avoid impulsive starts; plan carefully.")
    if rk["limbs"]["yoga"]["quality"] == "Challenged":
        cautions.append(rk["limbs"]["yoga"]["note"])

    return {
        "name": b.name or "Native",
        "birth": {
            "date": f"{b.day:02d}/{b.month:02d}/{b.year}",
            "time": f"{b.hour:02d}:{b.minute:02d}",
            "place": b.place,
            "lagna": chart.lagna_sign,
        },
        "panchang_at_birth": panchang_block,
        "rishikesh": rishikesh,
        "opening": opening,
        "life_predictions": life_predictions,
        "focus_intent": intent,
        "focus_detail": focus_lines,
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
    }


def predict_from_birth(birth: BirthData, intent: str = "General reading") -> Dict:
    """One-call API: birth inputs -> prediction dict."""
    chart = compute_chart(birth)
    return generate_prediction(chart, intent)


def prediction_markdown(pred: Dict) -> str:
    """Export prediction as Markdown."""
    lines = [
        f"# Astrology Prediction — {pred['name']}",
        "",
        f"**Birth:** {pred['birth']['date']} {pred['birth']['time']} · {pred['birth']['place']}",
        f"**Lagna:** {pred['birth']['lagna']}",
        "",
        "## Birth Panchang",
        f"- Vaara: {pred['panchang_at_birth']['vaara']}",
        f"- Tithi: {pred['panchang_at_birth']['tithi']}",
        f"- Nakshatra: {pred['panchang_at_birth']['nakshatra']} "
        f"(pada {pred['panchang_at_birth']['nakshatra_pada']}, "
        f"lord {pred['panchang_at_birth']['nakshatra_lord']})",
        f"- Yoga: {pred['panchang_at_birth']['yoga']}",
        f"- Karana: {pred['panchang_at_birth']['karana']}",
        "",
        "## Overview",
        pred["opening"],
        "",
    ]
    rk = pred.get("rishikesh", {})
    if rk:
        lines += [
            "## Rishikesh Panchang Evaluation",
            f"- Tradition: {rk['tradition']}",
            f"- Ishtakal: {rk['ishtakal']['formatted']} after sunrise ({rk['sunrise_at_birth']})",
            f"- Navaratna score: {rk['navaratna']['verdict']} ({rk['navaratna']['percent']}%)",
            "",
            "### Avakhada Chakra",
            f"- Varna: {rk['avakhada']['varna']} — {rk['avakhada']['varna_meaning']}",
            f"- Vashya: {rk['avakhada']['vashya']} — {rk['avakhada']['vashya_meaning']}",
            f"- Yoni: {rk['avakhada']['yoni']} — {rk['avakhada']['yoni_meaning']}",
            f"- Gana: {rk['avakhada']['gana']} — {rk['avakhada']['gana_meaning']}",
            f"- Nadi: {rk['avakhada']['nadi']} — {rk['avakhada']['nadi_meaning']}",
            "",
            "### Five Limbs (weighted)",
        ]
        for item in rk["navaratna"]["breakdown"]:
            limb = rk["limbs"][item["limb"]]
            lines.append(
                f"- **{item['limb'].title()}** (wt {item['weight']}): "
                f"{item['quality']} — {limb['note']}"
            )
        lines += ["", "### Gochar", f"- {rk['guru_gochar']['phase']}", ""]

    lines += ["## Life Predictions"]
    for lp in pred["life_predictions"]:
        lines.append(f"### {lp['area']} ({lp['verdict']})")
        lines.append(lp["prediction"])
        lines.append("")

    lines.append(f"## Focus: {pred['focus_intent']}")
    for fl in pred["focus_detail"]:
        lines.append(f"- {fl}")
    lines.append("")

    t = pred["timing"]
    lines.append("## Timing")
    lines.append(
        f"- Birth Nakshatra dasha lord: {t['birth_nakshatra_lord']} "
        f"({t['birth_nakshatra']})"
    )
    if t["current_maha"]:
        lines.append(
            f"- Current period: {t['current_maha']} Mahadasha"
            + (f" / {t['current_antar']} Antardasha" if t["current_antar"] else "")
        )
        lines.append(f"- {t['year_ahead']}")
    lines.append(f"- Sade Sati: {t['sade_sati']}")
    if t.get("guru_gochar"):
        lines.append(f"- Guru Gochar: {t['guru_gochar']}")
    if t.get("dasha_balance_years"):
        lines.append(f"- Dasha balance at birth: {t['dasha_balance_years']} years")
    lines.append("")

    if pred["patterns"]:
        lines.append("## High-confidence patterns")
        for p in pred["patterns"]:
            lines.append(f"- {p}")
        lines.append("")

    if pred["cautions"]:
        lines.append("## Cautions")
        for c in pred["cautions"]:
            lines.append(f"- {c}")
        lines.append("")

    lines.append("## Lucky elements")
    lk = pred["lucky"]
    lines.append(f"- Favourable weekday energy: {lk['day']}")
    lines.append(f"- Birth star: {lk['nakshatra']} (lord {lk['nakshatra_lord']})")
    lines.append(f"- Gemstone hint (Lagnesh): {lk['gemstone_hint']}")
    lines.append("")
    lines.append(
        "_Prediction follows the Shri Kashi Vishwanath Hrishikesh Panchang tradition "
        "(Lahiri sidereal, Phalita Navaratna weighting). "
        "For guidance and self-reflection, not deterministic fate._"
    )
    return "\n".join(lines)
