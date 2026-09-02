"""Visual timing summary — Mahadasha / Antardasha impact by life area.

Builds a compact, graph-ready timeline (scores + short risk/opportunity notes)
so readers can scan good vs challenged stretches without a wall of text.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from . import reference as ref
from .chart_engine import Chart
from .dasha_calc import compute_vimshottari, current_dasha, sade_sati_status
from .interpret import analyse_all_houses
from .narrative import DASHA_THEME, PLANET_DOMAIN
from .strength_calc import all_strengths

# Areas shown on the impact graph (house → short label).
TIMING_AREAS: List[Tuple[str, int]] = [
    ("Career", 10),
    ("Wealth", 2),
    ("Family", 7),
    ("Health", 6),
    ("Spiritual", 9),
]

_AREA_KEYS = [a[0] for a in TIMING_AREAS]

_DIGNITY_DELTA = {
    "Exalted": 18,
    "Moolatrikona": 15,
    "Own Sign": 12,
    "Friend's Sign": 5,
    "Neutral's Sign": 0,
    "Enemy's Sign": -12,
    "Debilitated": -18,
}

_HOUSE_BASE = {"Supported": 72, "Mixed": 50, "Challenged": 30}


def _clamp(n: float, lo: float = 5.0, hi: float = 95.0) -> int:
    return int(round(max(lo, min(hi, n))))


def _tone(score: int) -> str:
    if score >= 65:
        return "good"
    if score <= 38:
        return "bad"
    return "mixed"


def _tone_label(tone: str) -> str:
    return {"good": "Favourable", "bad": "Challenged", "mixed": "Mixed"}.get(tone, "Mixed")


def _lord_delta(chart: Chart, strengths, lord: str, area_house: int) -> Tuple[float, str]:
    """How strongly a dasha lord supports / pressures one life area."""
    p = chart.planets[lord]
    dig = strengths[lord].dignity
    delta = float(_DIGNITY_DELTA.get(dig, 0))
    notes: List[str] = []

    # Rules the life-area house → personal stake in results.
    if ref.SIGN_LORD[chart.house_signs[area_house]] == lord:
        delta += 10
        notes.append(f"{lord} rules this area")

    # Occupies the life-area house → activates themes directly.
    if p.house == area_house:
        delta += 8
        notes.append(f"{lord} sits in house {area_house}")

    # Dusthana occupancy: hard for most areas; Health (6) can still discipline.
    if p.house in ref.DUSTHANA:
        if area_house == 6 and p.house == 6:
            delta += 4
            notes.append(f"{lord} in 6th — endurance with effort")
        elif area_house in (2, 7, 10) and dig in ("Debilitated", "Enemy's Sign"):
            delta -= 10
            notes.append(f"{lord} in house {p.house} under strain")
        elif area_house in (2, 7, 10):
            delta -= 6
            notes.append(f"{lord} from dusthana house {p.house}")
        elif area_house == 9 and lord in ("Ketu", "Jupiter", "Saturn"):
            delta += 6
            notes.append(f"{lord} in {p.house} — inner / spiritual turn")
        else:
            delta -= 3

    # Kendra / trikona of the lord — freer expression.
    if p.house in (ref.KENDRA | ref.TRIKONA) and dig not in ("Debilitated", "Enemy's Sign"):
        delta += 5

    # Nodes: sharper swings.
    if lord == "Rahu":
        if area_house in (10, 11, 2):
            delta += 4
        if area_house in (7, 4):
            delta -= 3
    if lord == "Ketu":
        if area_house == 9:
            delta += 8
        if area_house in (2, 7, 10):
            delta -= 5

    note = notes[0] if notes else f"{lord}: {DASHA_THEME.get(lord, 'karmic growth')}"
    return delta, note


def _score_area(
    chart: Chart, houses, strengths, maha: str, antar: str, area: str, house: int,
) -> Dict:
    base = float(_HOUSE_BASE.get(houses[house].verdict, 50))
    # Antar is the active flavour (heavier weight).
    d_maha, n_maha = _lord_delta(chart, strengths, maha, house)
    d_antar, n_antar = _lord_delta(chart, strengths, antar, house)
    score = _clamp(base + 0.35 * d_maha + 0.65 * d_antar)
    tone = _tone(score)
    # Prefer the more specific antar note when tones diverge.
    note = n_antar if abs(d_antar) >= abs(d_maha) else n_maha
    return {
        "area": area,
        "house": house,
        "score": score,
        "tone": tone,
        "label": _tone_label(tone),
        "note": note,
    }


def _risks_opps(scores: Dict[str, Dict], maha: str, antar: str) -> Tuple[List[str], List[str]]:
    risks: List[str] = []
    opps: List[str] = []
    for area, row in scores.items():
        if row["tone"] == "bad":
            risks.append(f"{area}: {row['note']}")
        elif row["tone"] == "good":
            opps.append(f"{area}: {row['note']}")
    # Always seed one thematic line from lords.
    theme = (
        f"{maha}/{antar}: {DASHA_THEME.get(antar, 'change')} "
        f"(background: {DASHA_THEME.get(maha, 'growth')})"
    )
    if not opps:
        opps.append(theme)
    if len(risks) < 1 and any(s["tone"] == "mixed" for s in scores.values()):
        risks.append(f"Mixed stretch — pace {PLANET_DOMAIN.get(antar, 'this period')} carefully")
    return risks[:4], opps[:4]


def _phase_points(start: datetime, end: datetime, scores: Dict[str, Dict]) -> List[Dict]:
    """Three equal phases: open → peak → settle (small score modulation)."""
    span = max((end - start).total_seconds(), 1.0)
    thirds = [
        ("Open", 0.00, 0.33, +4),
        ("Peak", 0.33, 0.67, 0),
        ("Settle", 0.67, 1.00, +3),
    ]
    out = []
    for name, a, b, bump in thirds:
        ps = start + timedelta(seconds=span * a)
        pe = start + timedelta(seconds=span * b)
        phase_scores = {}
        for area, row in scores.items():
            # Peak shows natal effect raw; open/settle slightly softer toward mid.
            s = _clamp(row["score"] + (bump if row["tone"] != "bad" else -abs(bump) // 2))
            if name == "Peak" and row["tone"] == "bad":
                s = _clamp(row["score"] - 4)
            phase_scores[area] = {
                "score": s,
                "tone": _tone(s),
                "label": _tone_label(_tone(s)),
            }
        out.append({
            "name": name,
            "start": ps.isoformat(timespec="seconds"),
            "end": pe.isoformat(timespec="seconds"),
            "scores": phase_scores,
        })
    return out


def _iter_antars(periods, start: datetime, end: datetime):
    for maha in periods:
        if maha.end <= start or maha.start >= end:
            continue
        for antar in maha.antardashas:
            if antar.end <= start or antar.start >= end:
                continue
            yield maha, antar


def build_timing_summary(
    chart: Chart,
    when: Optional[datetime] = None,
    horizon_years: float = 6.0,
) -> Dict:
    """Graph-ready dasha impact summary from ``when`` forward ``horizon_years``."""
    when = when or datetime.now()
    horizon_end = when + timedelta(days=horizon_years * 365.2425)

    periods = compute_vimshottari(chart, antardashas=True)
    houses = analyse_all_houses(chart)
    strengths = all_strengths(chart)
    maha_now, antar_now = current_dasha(periods, when)
    ss = sade_sati_status(chart, when)

    chapters: List[Dict] = []
    for maha, antar in _iter_antars(periods, when, horizon_end):
        scores = {
            area: _score_area(chart, houses, strengths, maha.lord, antar.lord, area, h)
            for area, h in TIMING_AREAS
        }
        risks, opps = _risks_opps(scores, maha.lord, antar.lord)
        clip_start = max(antar.start, when)
        clip_end = min(antar.end, horizon_end)
        chapters.append({
            "maha": maha.lord,
            "antar": antar.lord,
            "label": f"{maha.lord} / {antar.lord}",
            "maha_theme": DASHA_THEME.get(maha.lord, "karmic growth"),
            "antar_theme": DASHA_THEME.get(antar.lord, "inner change"),
            "start": clip_start.isoformat(timespec="seconds"),
            "end": clip_end.isoformat(timespec="seconds"),
            "start_label": clip_start.strftime("%b %Y"),
            "end_label": clip_end.strftime("%b %Y"),
            "full_start": antar.start.isoformat(timespec="seconds"),
            "full_end": antar.end.isoformat(timespec="seconds"),
            "scores": scores,
            "risks": risks,
            "opportunities": opps,
            "phases": _phase_points(clip_start, clip_end, scores),
            "is_current": bool(
                maha_now and antar_now
                and maha.lord == maha_now.lord
                and antar.lord == antar_now.lord
                and antar.start <= when < antar.end
            ),
        })

    # Year risk / opportunity map.
    years: List[Dict] = []
    y0, y1 = when.year, horizon_end.year
    for year in range(y0, y1 + 1):
        y_start = datetime(year, 1, 1)
        y_end = datetime(year + 1, 1, 1)
        overlapping = [
            c for c in chapters
            if datetime.fromisoformat(c["start"]) < y_end
            and datetime.fromisoformat(c["end"]) > y_start
        ]
        if not overlapping:
            continue
        avg = {area: 0.0 for area in _AREA_KEYS}
        for c in overlapping:
            for area in _AREA_KEYS:
                avg[area] += c["scores"][area]["score"]
        n = len(overlapping)
        year_scores = {
            area: {
                "score": _clamp(avg[area] / n),
                "tone": _tone(_clamp(avg[area] / n)),
                "label": _tone_label(_tone(_clamp(avg[area] / n))),
            }
            for area in _AREA_KEYS
        }
        risks, opps = [], []
        for c in overlapping:
            risks.extend(c["risks"][:2])
            opps.extend(c["opportunities"][:2])
        # Dedupe preserving order.
        def _uniq(xs):
            seen, out = set(), []
            for x in xs:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out[:4]

        # One-word year tag from average score.
        mean = sum(v["score"] for v in year_scores.values()) / len(year_scores)
        if mean >= 65:
            tag = "Growth year"
        elif mean <= 42:
            tag = "Pressure year"
        else:
            tag = "Mixed year"
        years.append({
            "year": year,
            "tag": tag,
            "scores": year_scores,
            "risks": _uniq(risks),
            "opportunities": _uniq(opps),
            "chapters": [c["label"] for c in overlapping],
        })

    current = next((c for c in chapters if c["is_current"]), chapters[0] if chapters else None)

    natal_baseline = {
        area: {
            "verdict": houses[h].verdict,
            "score": _HOUSE_BASE.get(houses[h].verdict, 50),
            "lord": houses[h].lord,
            "lord_dignity": houses[h].lord_dignity,
            "lord_house": houses[h].lord_house,
        }
        for area, h in TIMING_AREAS
    }

    return {
        "as_of": when.isoformat(timespec="seconds"),
        "horizon_years": horizon_years,
        "areas": _AREA_KEYS,
        "current": {
            "maha": maha_now.lord if maha_now else None,
            "antar": antar_now.lord if antar_now else None,
            "maha_until": maha_now.end.strftime("%d %b %Y") if maha_now else None,
            "antar_until": antar_now.end.strftime("%d %b %Y") if antar_now else None,
            "maha_theme": DASHA_THEME.get(maha_now.lord, "") if maha_now else "",
            "antar_theme": DASHA_THEME.get(antar_now.lord, "") if antar_now else "",
            "sade_sati": ss["phase"],
            "sade_sati_active": ss["active"],
        },
        "natal_baseline": natal_baseline,
        "chapters": chapters,
        "years": years,
        "legend": {
            "good": "Favourable — themes tend to flow with less friction",
            "mixed": "Mixed — results depend on timing and effort",
            "bad": "Challenged — patience and conscious choices matter most",
        },
    }


def timing_summary_markdown(summary: Dict) -> str:
    """Compact markdown for downloads — tables, not essay walls."""
    if not summary:
        return ""
    cur = summary.get("current") or {}
    lines = [
        "## Timing map (Mahadasha / Antardasha)",
        "",
        f"**Now:** {cur.get('maha') or '—'} / {cur.get('antar') or '—'} "
        f"(Antar until {cur.get('antar_until') or '—'}).",
        f"Sade Sati: {cur.get('sade_sati') or '—'}.",
        "",
        "### Antardasha impact (score 0–100)",
        "",
        "| Period | Dates | " + " | ".join(summary.get("areas", [])) + " |",
        "|---|---|" + "|".join(["---"] * len(summary.get("areas", []))) + "|",
    ]
    for c in summary.get("chapters", []):
        cells = [str(c["scores"][a]["score"]) for a in summary["areas"]]
        lines.append(
            f"| **{c['label']}** | {c['start_label']} → {c['end_label']} | "
            + " | ".join(cells) + " |"
        )
    lines += ["", "### Year risk / opportunity map", ""]
    for y in summary.get("years", []):
        lines.append(f"#### {y['year']} — {y['tag']}")
        lines.append("**Watch:** " + ("; ".join(y["risks"]) or "—"))
        lines.append("**Lean into:** " + ("; ".join(y["opportunities"]) or "—"))
        lines.append("")
    return "\n".join(lines)
