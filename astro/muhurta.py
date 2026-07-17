"""Muhurta finder — auspicious electional timing (Rishikesh / Kashi tradition).

Scans a date range for a chosen activity and scores each day using the
Phalita Navaratna Samgraha limb weighting (Tithi 1, Nakshatra 4, Vara 8,
Karana 16, Yoga 32) plus optional personalised Tarabala (60) and Chandrabala
(100) when the native's Janma Nakshatra and Moon sign are supplied.

Within each qualifying day it recommends concrete time windows (auspicious
Choghadiya + Abhijit Muhurta) and vetoes Rahu Kaal / Yamaganda / Gulika Kaal,
Rikta Tithis, Vishti (Bhadra) Karana, Amavasya and Maha Yoga Doshas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

from . import reference as ref
from . import rishikesh_rules as rr
from . import panchang_data as pd
from .panchang import Panchang, compute_panchang, format_time

# ---------------------------------------------------------------------------
# Tithi groups (by number 1..15 within a paksha)
# ---------------------------------------------------------------------------
_NANDA = {1, 6, 11}
_BHADRA = {2, 7, 12}
_JAYA = {3, 8, 13}
_RIKTA = {4, 9, 14}
_POORNA = {5, 10, 15}

_AUSPICIOUS_YOGAS = {
    "Preeti", "Ayushman", "Saubhagya", "Shobhana", "Sukarma", "Dhriti",
    "Vriddhi", "Dhruva", "Harshana", "Siddhi", "Shiva", "Siddha",
    "Sadhya", "Shubha", "Shukla", "Brahma", "Indra",
}

_UTTARA = {"Uttara Phalguni", "Uttara Ashadha", "Uttara Bhadrapada"}


@dataclass
class Activity:
    key: str
    label: str
    good_nakshatras: Set[str]
    good_varas: Set[str]
    avoid_rikta: bool = True
    include_char: bool = False   # count "Char" (travel) Choghadiya as good
    allow_abhijit: bool = True
    note: str = ""


ACTIVITIES: Dict[str, Activity] = {
    "general": Activity(
        "general", "General auspicious work",
        {"Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
         "Chitra", "Swati", "Anuradha", "Shravana", "Dhanishta", "Shatabhisha",
         "Revati", *_UTTARA},
        {"Somavara", "Budhavara", "Guruvara", "Shukravara"},
        note="Broadly favourable windows for any positive undertaking.",
    ),
    "marriage": Activity(
        "marriage", "Marriage / engagement (Vivah)",
        {"Rohini", "Mrigashira", "Magha", "Uttara Phalguni", "Hasta", "Swati",
         "Anuradha", "Mula", "Uttara Ashadha", "Uttara Bhadrapada", "Revati"},
        {"Somavara", "Budhavara", "Guruvara", "Shukravara"},
        note="Classical marriage stars; Venus/Jupiter days favoured, Tue/Sat avoided.",
    ),
    "griha_pravesh": Activity(
        "griha_pravesh", "Housewarming (Griha Pravesh)",
        {"Rohini", "Mrigashira", "Chitra", "Anuradha", "Uttara Phalguni",
         "Uttara Ashadha", "Uttara Bhadrapada", "Revati", "Shatabhisha", "Dhanishta"},
        {"Somavara", "Budhavara", "Guruvara", "Shukravara"},
        note="Fixed & gentle stars for entering a new home.",
    ),
    "business": Activity(
        "business", "New business / venture (Vyapar Arambh)",
        {"Ashwini", "Pushya", "Hasta", "Chitra", "Swati", "Anuradha", "Shravana",
         "Dhanishta", "Shatabhisha", "Revati", *_UTTARA},
        {"Budhavara", "Guruvara", "Shukravara"},
        note="Mercury/Jupiter/Venus days for commerce; Rikta Tithis avoided.",
    ),
    "travel": Activity(
        "travel", "Journey / travel (Yatra)",
        {"Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Anuradha",
         "Shravana", "Dhanishta", "Revati"},
        {"Somavara", "Budhavara", "Guruvara", "Shukravara"},
        include_char=True,
        note="Light, movable stars; 'Char' Choghadiya is favourable for journeys.",
    ),
    "education": Activity(
        "education", "Study / learning start (Vidyarambha)",
        {"Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Chitra",
         "Swati", "Anuradha", "Shravana", "Dhanishta", "Shatabhisha", "Revati",
         "Mula", *_UTTARA},
        {"Somavara", "Budhavara", "Guruvara", "Shukravara"},
        note="Mercury/Jupiter days ideal for beginning studies.",
    ),
    "naming": Activity(
        "naming", "Naming ceremony (Namakaran)",
        {"Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
         "Chitra", "Swati", "Anuradha", "Shravana", "Dhanishta", "Shatabhisha",
         "Revati", *_UTTARA},
        {"Somavara", "Budhavara", "Guruvara", "Shukravara"},
        note="Gentle, auspicious stars for a child's naming.",
    ),
    "purchase": Activity(
        "purchase", "Vehicle / property purchase",
        {"Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
         "Chitra", "Swati", "Anuradha", "Shravana", "Dhanishta", "Shatabhisha",
         "Revati", *_UTTARA},
        {"Somavara", "Budhavara", "Guruvara", "Shukravara"},
        note="Favourable stars for acquiring vehicles or property.",
    ),
}


def _tithi_num(idx: int) -> int:
    return idx if idx <= 15 else idx - 15


def _score_tithi(panch: Panchang, act: Activity) -> Tuple[float, str, Optional[str]]:
    num = _tithi_num(panch.tithi.index)
    name = panch.tithi.name
    if name == "Amavasya":
        return 0.20, f"{name} (new moon) — avoid new beginnings.", \
            "Amavasya — inauspicious for new ventures."
    if num in _RIKTA and act.avoid_rikta:
        return 0.30, f"Rikta Tithi ({name}) — traditionally avoided for new work.", \
            f"Rikta Tithi ({name}) — avoid starting ventures."
    if num in _POORNA:
        return 0.90, f"Poorna Tithi ({name}) — full, completing energy.", None
    if num in _JAYA:
        return 0.85, f"Jaya Tithi ({name}) — victory-giving.", None
    if num in _BHADRA:
        return 0.80, f"Bhadra Tithi ({name}) — supportive.", None
    if num in _NANDA:
        return 0.72, f"Nanda Tithi ({name}) — joyful.", None
    return 0.55, f"{name} — neutral lunar day.", None


def _score_vara(panch: Panchang, act: Activity) -> Tuple[float, str, Optional[str]]:
    name = panch.vaara.name
    if name in act.good_varas:
        return 0.90, f"{panch.vaara.name_hindi or name} — favourable weekday.", None
    if name in rr.MALEFIC_VAARA:
        return 0.40, f"{name} (Saturn) — restrictive weekday.", \
            f"{name} is Saturn-ruled — better for endurance tasks than new starts."
    if name == "Mangalavara":
        return 0.45, "Mangalavara (Mars) — energetic but harsh weekday.", \
            "Tuesday (Mars) — avoid for gentle undertakings like marriage."
    return 0.62, f"{name} — neutral weekday.", None


def _score_nakshatra(panch: Panchang, act: Activity) -> Tuple[float, str, Optional[str]]:
    nak = panch.nakshatra.name
    if nak in rr.GANDANTA_NAKSHATRAS:
        return 0.30, f"{nak} — Gandanta star; sensitive junction.", \
            f"{nak} is Gandanta — traditionally avoided; remedies advised."
    if nak in act.good_nakshatras:
        return 0.95, f"{nak} — ideal star for this activity.", None
    return 0.55, f"{nak} — workable but not a preferred star for this activity.", None


def _score_yoga(panch: Panchang) -> Tuple[float, str, Optional[str]]:
    y = panch.yoga.name
    if y in rr.MAHA_YOGA_DOSHAS:
        return 0.20, f"{y} — Maha Yoga Dosha; can spoil other limbs.", \
            f"{y} Yoga is a Maha Dosha — heavily weighted against; avoid if possible."
    if y in _AUSPICIOUS_YOGAS:
        return 0.90, f"{y} — auspicious Yoga.", None
    return 0.58, f"{y} — neutral Yoga.", None


def _score_karana(panch: Panchang) -> Tuple[float, str, Optional[str]]:
    k = panch.karana.name
    if k == "Vishti":
        return 0.25, "Vishti (Bhadra) Karana — avoid new starts.", \
            "Vishti (Bhadra) Karana active — inauspicious for beginnings."
    if k in rr.FIXED_KARANAS:
        return 0.50, f"{k} — fixed Karana; slower worldly progress.", None
    return 0.85, f"{k} — moving Karana; good for action.", None


def _score_tarabala(day_nak_idx: int, janma_nak_idx: int) -> Tuple[float, str, Optional[str]]:
    count = (day_nak_idx - janma_nak_idx) % 27 + 1
    tara = (count - 1) % 9
    name = rr.TARABALA_NAMES[tara]
    if name in rr.TARABALA_AUSPICIOUS:
        return 0.92, f"Tarabala {name} — favourable star-strength for you.", None
    if tara in (2, 4, 6):  # Vipat, Pratyak, Naidhana
        return 0.20, f"Tarabala {name} — weak star-strength for you.", \
            f"Tarabala {name} — inauspicious relative to your birth star."
    return 0.55, f"Tarabala {name} — neutral for you.", None


def _score_chandrabala(day_moon_sign_idx: int, natal_moon_sign_idx: int) -> Tuple[float, str, Optional[str]]:
    house = (day_moon_sign_idx - natal_moon_sign_idx) % 12 + 1
    if house in rr.CHANDRA_BALA_GOOD_HOUSES:
        return 0.92, f"Chandrabala strong — Moon in house {house} from your natal Moon.", None
    if house in {4, 8, 12}:
        return 0.30, f"Chandrabala weak — Moon in house {house} from your natal Moon.", \
            f"Chandrabala weak (Moon {house}th from your Janma Rashi) — the heaviest-weighted factor."
    return 0.58, f"Chandrabala moderate — Moon in house {house} from your natal Moon.", None


@dataclass
class DayResult:
    d: date
    weekday: str
    score: float
    verdict: str
    tithi: str
    nakshatra: str
    yoga: str
    karana: str
    positives: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    windows: List[Dict] = field(default_factory=list)
    best_window: Optional[Dict] = None


def _verdict(pct: float) -> str:
    if pct >= 70:
        return "Auspicious"
    if pct >= 55:
        return "Workable"
    return "Avoid"


def _overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and b_start < a_end


def _recommend_windows(panch: Panchang, act: Activity) -> List[Dict]:
    good_natures = {"Auspicious", "Highly auspicious"}
    if act.include_char:
        good_natures.add("Good for travel")
    blocked = [
        (panch.rahu_kaal.start, panch.rahu_kaal.end),
        (panch.yamaganda.start, panch.yamaganda.end),
        (panch.gulika_kaal.start, panch.gulika_kaal.end),
    ]
    windows: List[Dict] = []
    for w in list(panch.day_choghadiya) + list(panch.night_choghadiya):
        if w.nature not in good_natures:
            continue
        if any(_overlaps(w.start, w.end, bs, be) for bs, be in blocked):
            continue
        windows.append({
            "name": w.name,
            "start": format_time(w.start),
            "end": format_time(w.end),
            "nature": w.nature,
            "_start": w.start,
        })
    if act.allow_abhijit:
        ab = panch.abhijit_muhurta
        if not any(_overlaps(ab.start, ab.end, bs, be) for bs, be in blocked):
            windows.append({
                "name": "Abhijit Muhurta",
                "start": format_time(ab.start),
                "end": format_time(ab.end),
                "nature": "Auspicious (universal)",
                "_start": ab.start,
            })
    windows.sort(key=lambda x: x["_start"])
    for w in windows:
        w.pop("_start", None)
    return windows


def evaluate_day(
    d: date,
    act: Activity,
    latitude: float,
    longitude: float,
    tz_offset: float,
    place: str,
    janma_nak_idx: Optional[int] = None,
    natal_moon_sign_idx: Optional[int] = None,
) -> DayResult:
    """Score a single day for the given activity."""
    panch = compute_panchang(
        d, latitude=latitude, longitude=longitude, tz_offset=tz_offset,
        place=place, place_hindi="", altitude_m=0.0,
    )
    scores: List[Tuple[str, int, float]] = []
    positives: List[str] = []
    warnings: List[str] = []

    for key, fn in (
        ("tithi", _score_tithi), ("vara", _score_vara),
        ("nakshatra", _score_nakshatra),
    ):
        s, note, warn = fn(panch, act)
        scores.append((key, rr.LIMB_WEIGHTS[key], s))
        positives.append(note)
        if warn:
            warnings.append(warn)
    for key, fn in (("yoga", _score_yoga), ("karana", _score_karana)):
        s, note, warn = fn(panch)
        scores.append((key, rr.LIMB_WEIGHTS[key], s))
        positives.append(note)
        if warn:
            warnings.append(warn)

    personalised = janma_nak_idx is not None and natal_moon_sign_idx is not None
    if personalised:
        day_moon_sign_idx = int(panch.moon_longitude // 30) % 12
        ts, tnote, twarn = _score_tarabala(panch.nakshatra.index, janma_nak_idx)
        cs, cnote, cwarn = _score_chandrabala(day_moon_sign_idx, natal_moon_sign_idx)
        scores.append(("tarabala", rr.LIMB_WEIGHTS["tarabala"], ts))
        scores.append(("chandrabala", rr.LIMB_WEIGHTS["chandrabala"], cs))
        positives.append(tnote)
        positives.append(cnote)
        if twarn:
            warnings.append(twarn)
        if cwarn:
            warnings.append(cwarn)

    total_w = sum(w for _, w, _ in scores)
    weighted = sum(w * s for _, w, s in scores)
    pct = round(weighted / total_w * 100, 1) if total_w else 0.0

    windows = _recommend_windows(panch, act)
    if not windows:
        warnings.append("No clear auspicious window today (Rahu/Yamaganda/Gulika crowd the day).")

    return DayResult(
        d=d,
        weekday=panch.vaara.name_hindi or panch.vaara.name,
        score=pct,
        verdict=_verdict(pct),
        tithi=f"{panch.tithi.name} ({panch.paksha})",
        nakshatra=panch.nakshatra.name,
        yoga=panch.yoga.name,
        karana=panch.karana.name,
        positives=positives,
        warnings=warnings,
        windows=windows,
        best_window=windows[0] if windows else None,
    )


def find_muhurta(
    activity_key: str,
    start: date,
    num_days: int,
    latitude: float,
    longitude: float,
    tz_offset: float,
    place: str,
    janma_nakshatra: Optional[str] = None,
    natal_moon_sign: Optional[str] = None,
) -> Dict:
    """Scan ``num_days`` from ``start`` and rank auspicious days for an activity."""
    act = ACTIVITIES.get(activity_key, ACTIVITIES["general"])
    janma_nak_idx = (
        ref.NAKSHATRAS.index(janma_nakshatra) if janma_nakshatra in ref.NAKSHATRAS else None
    )
    natal_moon_sign_idx = (
        ref.SIGNS.index(natal_moon_sign) if natal_moon_sign in ref.SIGNS else None
    )
    personalised = janma_nak_idx is not None and natal_moon_sign_idx is not None

    days: List[DayResult] = []
    for i in range(max(1, num_days)):
        d = start + timedelta(days=i)
        days.append(evaluate_day(
            d, act, latitude, longitude, tz_offset, place,
            janma_nak_idx, natal_moon_sign_idx,
        ))

    ranked = sorted(days, key=lambda r: r.score, reverse=True)
    top = [r for r in ranked if r.verdict != "Avoid" and r.windows][:5]

    return {
        "activity": act.label,
        "activity_note": act.note,
        "place": place,
        "start": start,
        "num_days": num_days,
        "personalised": personalised,
        "days": days,
        "ranked": ranked,
        "top": top,
    }


def muhurta_markdown(result: Dict) -> str:
    """Export the muhurta scan as Markdown."""
    lines = [
        f"# Muhurta finder — {result['activity']}",
        "",
        f"> {result['activity_note']}",
        "",
        f"Location: {result['place']} · "
        f"{result['start'].strftime('%d %b %Y')} for {result['num_days']} day(s) · "
        + ("personalised (Tarabala + Chandrabala included)" if result["personalised"]
           else "general (no birth-star personalisation)"),
        "",
        "## Top recommended dates",
    ]
    if not result["top"]:
        lines.append("_No clearly auspicious dates in this range — try widening the range._")
    for r in result["top"]:
        bw = r.best_window
        when = f" — best window: {bw['name']} {bw['start']}–{bw['end']}" if bw else ""
        lines.append(
            f"- **{r.d.strftime('%a %d %b %Y')}** · {r.score:.0f}% ({r.verdict}) · "
            f"{r.nakshatra} nakshatra{when}"
        )
    lines += ["", "## Day-by-day"]
    for r in result["days"]:
        lines += [
            f"### {r.d.strftime('%a %d %b %Y')} — {r.score:.0f}% ({r.verdict})",
            f"Tithi {r.tithi} · Nakshatra {r.nakshatra} · Yoga {r.yoga} · Karana {r.karana}",
            "",
        ]
        if r.windows:
            lines.append("Auspicious windows:")
            for w in r.windows:
                lines.append(f"- {w['name']}: {w['start']}–{w['end']} ({w['nature']})")
        if r.warnings:
            lines.append("")
            lines.append("Cautions:")
            for w in r.warnings:
                lines.append(f"- {w}")
        lines.append("")
    return "\n".join(lines)
