"""Rishikesh Panchang life-prediction analysis.

Applies the Kashi / Hrishikesh computational tradition:
  1. Ishtakal (Ghati-Pala from local sunrise)
  2. Five-limb evaluation with Phalita Navaratna weighting
  3. Tarabala & Chandrabala (priority for natal prediction)
  4. Avakhada Chakra personality matrix
  5. Gochar hints (Guru Gochar alongside existing Sade Sati)
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from . import reference as ref
from . import rishikesh_rules as rr
from .chart_engine import Chart
from .panchang import Panchang


def _ishtakal(sunrise: datetime, birth: datetime) -> Dict:
    """Birth time as Ghati & Pala from local sunrise (Rishikesh Ishtakal step)."""
    if birth < sunrise:
        delta_min = 0.0
    else:
        delta_min = (birth - sunrise).total_seconds() / 60.0
    ghati = int(delta_min // 24)
    rem_min = delta_min - ghati * 24
    pala = int(rem_min * 2.5)  # 60 palas per ghati -> 1 pala = 24 sec
    return {
        "ghati": ghati,
        "pala": min(pala, 59),
        "formatted": f"{ghati} Ghati {pala} Pala",
        "minutes_after_sunrise": round(delta_min, 1),
    }


def _tithi_number(tithi_index: int) -> int:
    """1..15 within paksha."""
    return tithi_index if tithi_index <= 15 else tithi_index - 15


def _evaluate_tithi(panch: Panchang) -> Tuple[str, float, str]:
    """Water element — emotional constitution & wealth potential."""
    num = _tithi_number(panch.tithi.index)
    paksha = panch.paksha
    if paksha == "Shukla Paksha":
        score, quality = 0.85, "Auspicious"
        note = "Shukla Paksha birth — growth-oriented lunar phase (Lakshmi favour)."
    elif num == 10 and paksha == "Krishna Paksha":
        score, quality = 0.80, "Auspicious"
        note = "Krishna Dashami — traditionally auspicious waning-phase birth."
    elif panch.tithi.name == "Amavasya":
        score, quality = 0.25, "Challenged"
        note = "Amavasya birth — introspective path; material struggles possible without remedies."
    elif num in rr.RIKTA_TITHI_NUMBERS:
        score, quality = 0.35, "Challenged"
        note = f"Rikta Tithi ({panch.tithi.name}) — avoid impulsive new ventures; plan with care."
    elif paksha == "Krishna Paksha":
        score, quality = 0.55, "Mixed"
        note = "Krishna Paksha — reflective, inward energy; growth through release."
    else:
        score, quality = 0.70, "Mixed"
        note = f"{panch.tithi.name} — balanced lunar-day influence."
    return quality, score, note


def _evaluate_vara(panch: Panchang) -> Tuple[str, float, str]:
    """Fire element — vitality & Ayus."""
    name = panch.vaara.name
    if name in rr.BENEFIC_VAARA:
        return "Auspicious", 0.90, (
            f"{name} — benefic weekday; Jupiter/Venus protection for vitality."
        )
    if name in rr.MALEFIC_VAARA:
        return "Challenged", 0.40, (
            f"{name} — Saturn-ruled day; life asks endurance, discipline and steady labour."
        )
    return "Mixed", 0.65, f"{name} — moderate fiery vitality; habits shape longevity."


def _evaluate_nakshatra(nak: str) -> Tuple[str, float, str]:
    """Air element — destiny & Janma Rashi talents."""
    if nak in rr.GANDANTA_NAKSHATRAS:
        return "Challenged", 0.35, (
            f"{nak} — Gandanta Nakshatra; critical early-life transitions; "
            "Vedic remedies traditionally advised."
        )
    return "Auspicious", 0.80, (
        f"{nak} — birth star shapes inherent talents and naming syllables (Padas)."
    )


def _evaluate_yoga(yoga: str) -> Tuple[str, float, str]:
    """Ether element — health & spiritual character (heavily weighted)."""
    if yoga in rr.MAHA_YOGA_DOSHAS:
        return "Challenged", 0.20, (
            f"{yoga} — Maha Yoga Dosha; can mar otherwise auspicious limbs. "
            "Rishikesh tradition weights Yoga highest (32 pts) as a 'spoiling' agent."
        )
    auspicious = {
        "Preeti", "Ayushman", "Saubhagya", "Shobhana", "Sukarma", "Dhriti",
        "Vriddhi", "Dhruva", "Harshana", "Siddhi", "Shiva", "Siddha",
        "Sadhya", "Shubha", "Shukla", "Brahma", "Indra",
    }
    if yoga in auspicious:
        return "Auspicious", 0.90, f"{yoga} — supportive Yoga for immunity and spiritual character."
    return "Mixed", 0.55, f"{yoga} — moderate Yoga influence; awareness of health rhythms helps."


def _evaluate_karana(karana: str) -> Tuple[str, float, str]:
    """Earth element — execution & career capability."""
    if karana == "Vishti":
        return "Challenged", 0.30, (
            "Vishti (Bhadra) Karana — caution in new starts; introspective planning favoured."
        )
    if karana in rr.FIXED_KARANAS:
        return "Challenged", 0.45, (
            f"{karana} — fixed Karana; worldly climb may need extra persistence."
        )
    return "Auspicious", 0.80, (
        f"{karana} — moving Karana; versatility in business and practical affairs."
    )


def _tarabala_at_birth() -> Tuple[str, float, str]:
    """Tarabala at birth instant — Janma star (position 1)."""
    name = rr.TARABALA_NAMES[0]
    score = 0.45
    note = (
        "Janma Tarabala — birth in one's own Nakshatra; self-knowledge is the lesson. "
        "Rishikesh tradition prioritises Tarabala (60 pts) for life prediction."
    )
    return name, score, note


def _chandrabala_at_birth(moon_sign_idx: int) -> Tuple[str, float, str]:
    """Chandrabala — Moon in own sign at birth = 1st house transit."""
    house = 1
    good = house in rr.CHANDRA_BALA_GOOD_HOUSES
    score = 0.95 if good else 0.40
    quality = "Strong" if good else "Weak"
    note = (
        f"Chandrabala {quality} — natal Moon in {ref.SIGNS[moon_sign_idx]} "
        f"(house {house} from Janma Rashi). Highest weight (100 pts) in Phalita hierarchy."
    )
    return quality, score, note


def _avakhada(moon_sign: str, nakshatra: str) -> Dict:
    varna = rr.VARNA_BY_SIGN[moon_sign]
    vashya = rr.VASHYA_BY_SIGN[moon_sign]
    yoni = rr.YONI_BY_NAKSHATRA[nakshatra]
    gana = rr.GANA_BY_NAKSHATRA[nakshatra]
    nadi = rr.NADI_BY_NAKSHATRA[nakshatra]
    return {
        "varna": varna,
        "varna_meaning": rr.VARNA_MEANING[varna],
        "vashya": vashya,
        "vashya_meaning": rr.VASHYA_MEANING[vashya],
        "yoni": yoni,
        "yoni_meaning": rr.YONI_MEANING[yoni],
        "gana": gana,
        "gana_meaning": rr.GANA_MEANING[gana],
        "nadi": nadi,
        "nadi_meaning": rr.NADI_MEANING[nadi],
        "nadi_dosha_note": (
            "Nadi matching is the critical filter in Ashtakoota Milan — "
            "same Nadi between partners is traditionally avoided."
        ),
    }


def _guru_gochar(chart: Chart, when: Optional[datetime] = None) -> Dict:
    """Jupiter transit relative to natal Moon (Gochar)."""
    when = when or datetime.now()
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd = swe.julday(when.year, when.month, when.day, when.hour + when.minute / 60.0)
    xx = swe.calc_ut(jd, swe.JUPITER, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)[0]
    jup_sign = int(xx[0] // 30) % 12
    moon_sign = chart.planets["Moon"].sign_index
    house = (jup_sign - moon_sign) % 12 + 1
    auspicious = house in rr.GURU_GOCHAR_GOOD_HOUSES
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(house, "th")
    return {
        "jupiter_sign": ref.SIGNS[jup_sign],
        "house_from_moon": house,
        "auspicious": auspicious,
        "phase": (
            f"Guru in {house}{suffix} house from natal Moon — "
            + ("auspicious for marriage, progeny, fortune."
               if auspicious else "neutral/challenging; patience in expansion.")
        ),
    }


def _navaratna_score(limbs: Dict) -> Dict:
    """Weighted Phalita Navaratna Samgraha score."""
    total_weight = 0
    weighted_sum = 0.0
    breakdown = []
    for key, weight in rr.LIMB_WEIGHTS.items():
        if key not in limbs:
            continue
        entry = limbs[key]
        total_weight += weight
        contrib = entry["score"] * weight
        weighted_sum += contrib
        breakdown.append({
            "limb": key,
            "weight": weight,
            "quality": entry["quality"],
            "score_pct": round(entry["score"] * 100),
            "weighted": round(contrib, 1),
        })
    pct = round(weighted_sum / total_weight * 100, 1) if total_weight else 0
    if pct >= 70:
        verdict = "Auspicious"
    elif pct >= 50:
        verdict = "Mixed"
    else:
        verdict = "Challenged"
    return {
        "percent": pct,
        "verdict": verdict,
        "breakdown": breakdown,
        "priority_note": (
            "Chandrabala (100) and Tarabala (60) carry highest weight for life prediction. "
            "A malefic Yoga (32 pts) can nullify an auspicious Nakshatra."
        ),
    }


def analyze_rishikesh_birth(
    chart: Chart,
    panch: Panchang,
    birth_dt: datetime,
) -> Dict:
    """Full Rishikesh Panchang analysis for natal life prediction."""
    moon = chart.planets["Moon"]
    moon_sign = moon.sign
    nak = moon.nakshatra

    ishtakal = _ishtakal(panch.sunrise, birth_dt)

    t_q, t_s, t_n = _evaluate_tithi(panch)
    v_q, v_s, v_n = _evaluate_vara(panch)
    n_q, n_s, n_n = _evaluate_nakshatra(nak)
    y_q, y_s, y_n = _evaluate_yoga(panch.yoga.name)
    k_q, k_s, k_n = _evaluate_karana(panch.karana.name)
    tb_name, tb_s, tb_n = _tarabala_at_birth()
    cb_q, cb_s, cb_n = _chandrabala_at_birth(moon.sign_index)

    limbs = {
        "tithi": {"quality": t_q, "score": t_s, "note": t_n, "element": rr.LIMB_ELEMENT["tithi"]},
        "vara": {"quality": v_q, "score": v_s, "note": v_n, "element": rr.LIMB_ELEMENT["vara"]},
        "nakshatra": {"quality": n_q, "score": n_s, "note": n_n, "element": rr.LIMB_ELEMENT["nakshatra"]},
        "yoga": {"quality": y_q, "score": y_s, "note": y_n, "element": rr.LIMB_ELEMENT["yoga"]},
        "karana": {"quality": k_q, "score": k_s, "note": k_n, "element": rr.LIMB_ELEMENT["karana"]},
        "tarabala": {"quality": tb_name, "score": tb_s, "note": tb_n, "element": "Star strength (Tarabala)"},
        "chandrabala": {"quality": cb_q, "score": cb_s, "note": cb_n, "element": "Natal Moon strength (Chandrabala)"},
    }

    navaratna = _navaratna_score(limbs)
    avakhada = _avakhada(moon_sign, nak)
    guru = _guru_gochar(chart)

    spoil_notes: List[str] = []
    if y_q == "Challenged" and n_q == "Auspicious":
        spoil_notes.append(
            "Malefic Yoga overrides auspicious Nakshatra — remedies for Yoga Dosha are prioritised."
        )
    if nak in rr.GANDANTA_NAKSHATRAS:
        spoil_notes.append("Gandanta birth — traditional Sandhi Shanti and Nakshatra remedies advised.")
    if panch.tithi.name == "Amavasya":
        spoil_notes.append("Amavasya birth — deep spiritual potential; material caution in early ventures.")

    synthesis = (
        f"Hrishikesh Panchang evaluation: {navaratna['verdict']} ({navaratna['percent']}%). "
        f"Born {ishtakal['formatted']} after sunrise at {chart.birth.place or 'birthplace'}. "
        f"Janma Rashi {moon_sign}, {nak} Nakshatra. "
        f"Avakhada: {avakhada['varna']} Varna, {avakhada['gana']} Gana, {avakhada['nadi']} Nadi. "
    )
    if spoil_notes:
        synthesis += " " + " ".join(spoil_notes)

    return {
        "tradition": "Shri Kashi Vishwanath Hrishikesh Panchang (Lahiri / North-Indian)",
        "ishtakal": ishtakal,
        "sunrise_at_birth": panch.sunrise.strftime("%I:%M %p").lstrip("0"),
        "limbs": limbs,
        "navaratna": navaratna,
        "avakhada": avakhada,
        "guru_gochar": guru,
        "spoil_notes": spoil_notes,
        "synthesis": synthesis,
    }
