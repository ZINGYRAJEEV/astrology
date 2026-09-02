"""Copilot-style structured chart + timing explanations.

Produces scannable sections (identity, life-area verdicts, phase breakdowns,
“why this period behaves this way”, year risk/opportunity) — short bullets,
not essay walls. Designed to sit beside the D3 timing graphs.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional

from . import reference as ref
from .chart_engine import Chart
from .dasha_calc import sade_sati_status
from .gochar import gochar_report
from .interpret import analyse_all_houses
from .narrative import DASHA_THEME, PLANET_DOMAIN, SIGN_TRAIT
from .panchang import compute_panchang
from .rishikesh_prediction import analyze_rishikesh_birth
from .strength_calc import all_strengths
from .timing_summary import TIMING_AREAS, build_timing_summary

_STRONG = {"Exalted", "Own Sign", "Moolatrikona"}
_WEAK = {"Debilitated", "Enemy's Sign"}

_HOUSE_THEME_SHORT = {
    1: "self & vitality", 2: "income & speech", 3: "effort & siblings",
    4: "home & peace", 5: "creativity & children", 6: "health & competition",
    7: "partnership & public", 8: "sudden change & depth", 9: "fortune & dharma",
    10: "career & status", 11: "gains & network", 12: "loss & foreign links",
}

_GOCHARA_EFFECTS = {
    1: ["Identity pressure", "Fresh starts"],
    2: ["Money themes", "Family speech"],
    3: ["Effort & courage", "Short travel"],
    4: ["Home & property", "Emotional comfort"],
    5: ["Creativity", "Children / romance"],
    6: ["Competition", "Health routine"],
    7: ["Partnerships", "Public image"],
    8: ["Sudden shifts", "Hidden obstacles"],
    9: ["Guidance", "Luck"],
    10: ["Career visibility", "Authority"],
    11: ["Gains", "Network support"],
    12: ["Expenses", "Foreign links"],
}

_PHASE_THEMES = {
    "Open": ("Acceleration + openings", "Soft start + setup"),
    "Peak": ("Peak pressure / peak expression", "Full expression of the sub-period"),
    "Settle": ("Stabilisation + skill growth", "Cooling-down and clarity"),
}


def _pl(name: str) -> str:
    return ref.planet_label(name)


def _mid(iso_a: str, iso_b: str) -> datetime:
    a, b = datetime.fromisoformat(iso_a), datetime.fromisoformat(iso_b)
    return a + (b - a) / 2


def _months(start: datetime, end: datetime) -> float:
    return max((end - start).days / 30.44, 0.1)


def _area_verdict_block(area: str, house: int, report, strengths) -> Dict:
    lord = report.lord
    dig = report.lord_dignity
    theme = _HOUSE_THEME_SHORT.get(report.lord_house, "this area")
    bullets: List[str] = [
        f"{_pl(lord)} rules this area and is {dig} in the {report.lord_house}th "
        f"({theme})."
    ]
    if report.verdict == "Challenged":
        bullets.append("Needs patience and conscious effort.")
        if report.lord_house in (6, 8, 12):
            bullets.append(
                "Risk of slowdown, pressure, or foreign/remote themes when this house is active."
            )
    elif report.verdict == "Supported":
        bullets.append("Themes tend to flow with less friction.")
    else:
        bullets.append("Choices and timing matter.")

    if area == "Health" and dig in _STRONG and report.lord_house == 6:
        bullets.append("Good discipline potential — routine and sleep still matter.")
    if area == "Spiritual" and dig in _STRONG:
        bullets.append("Excellent window for dharma, ethics, and higher learning when activated.")
    if area == "Wealth" and dig in _STRONG:
        bullets.append("Strong earning potential through the lord’s natural skills.")

    tone = (
        "good" if report.verdict == "Supported"
        else "bad" if report.verdict == "Challenged"
        else "mixed"
    )
    label = (
        "Strong" if report.verdict == "Supported"
        else "Challenged" if report.verdict == "Challenged"
        else "Mixed"
    )
    return {
        "name": area if area != "Family" else "Family / Marriage",
        "verdict": label,
        "tone": tone,
        "bullets": bullets[:4],
    }


def _planet_snapshot(chart: Chart, strengths) -> Dict:
    strong, challenged = [], []
    for name in ref.PLANETS:
        dig = strengths[name].dignity
        p = chart.planets[name]
        line = (
            f"{_pl(name)} in {dig} ({p.house}th) → "
            f"{ref.HOUSE_THEME.get(p.house, 'life themes')}"
        )
        if dig in _STRONG:
            strong.append(line)
        elif dig in _WEAK:
            challenged.append(line)
    return {"strong": strong[:5], "challenged": challenged[:4]}


def _gochara_lines(chart: Chart, when: datetime) -> List[str]:
    report = gochar_report(chart, when)
    lines = []
    for row in report.get("rows", []):
        if row["planet"] not in ("Sun", "Mars", "Jupiter", "Saturn", "Rahu"):
            continue
        h = row["house_from_moon"]
        effects = _GOCHARA_EFFECTS.get(h, ["Mixed results"])
        lines.append(
            f"{_pl(row['planet'])} in {h}th from Moon: "
            + ", ".join(e.lower() for e in effects[:2])
        )
    return lines[:5]


def _phase_area_lines(
    chart: Chart, houses, strengths, maha: str, antar: str, area: str, house: int,
    phase_name: str, gochara_mid: List[str],
) -> List[str]:
    """Short practical bullets for one area inside one phase."""
    r = houses[house]
    score_tone = r.verdict
    dig_a = strengths[antar].dignity
    dig_m = strengths[maha].dignity
    p_a, p_m = chart.planets[antar], chart.planets[maha]
    out: List[str] = []

    if area == "Career":
        if r.verdict == "Challenged" or dig_a in _WEAK or p_a.house in (6, 8, 12):
            out.append("Pressure or role uncertainty — avoid impulsive job jumps.")
        elif dig_a in _STRONG or p_m.house in (10, 11):
            out.append("Openings via skill, networks, or foreign/remote links.")
        else:
            out.append("Steady effort pays; visibility comes in waves.")
        if phase_name == "Peak" and r.verdict != "Supported":
            out.append("Work pressure peaks — pace yourself.")
        if phase_name == "Settle":
            out.append("Stabilisation begins; skill upgrades help.")

    elif area == "Wealth":
        if dig_a in _STRONG and p_a.house in (2, 11):
            out.append("Stronger earning window — speech, trade, skills bring money.")
        elif p_a.house == 12 or any("expenses" in g.lower() for g in gochara_mid):
            out.append("Income may hold, but expenses rise — budget tightly.")
        else:
            out.append("Skill-based income is safer than speculation.")
        if phase_name == "Open":
            out.append("Often the clearer money window of this chapter.")

    elif area == "Family":
        if r.verdict == "Challenged" or houses[7].lord_house in (6, 8, 12):
            out.append("Friction or misunderstandings — communicate slowly.")
        else:
            out.append("Bonding improves with conscious time together.")
        if phase_name == "Peak":
            out.append("Most sensitive stretch for close bonds.")
        if phase_name == "Settle":
            out.append("Communication softens compared with the peak.")

    elif area == "Health":
        out.append(
            f"Sleep and routine matter more under {_pl(maha)}/{_pl(antar)} pace."
        )
        if phase_name == "Peak":
            out.append("Stress-related dips more likely — protect rest.")
        if phase_name == "Settle":
            out.append("Energy tends to return if routine is kept.")

    else:  # Spiritual
        if dig_m in _STRONG or maha in ("Ketu", "Jupiter") or antar in ("Ketu", "Jupiter"):
            out.append("Strong window for mantra, study, and inner clarity.")
        else:
            out.append("Quiet practice steadies the outer dasha noise.")

    # One natal anchor line.
    out.append(
        f"Natal cue: {_pl(r.lord)} ({r.lord_dignity}) in {r.lord_house}th colours {area.lower()}."
    )
    return out[:4]


def _phase_theme(phase_name: str, scores: Dict) -> str:
    mean = sum(s["score"] for s in scores.values()) / max(len(scores), 1)
    hard = sum(1 for s in scores.values() if s["tone"] == "bad")
    soft, hard_label = _PHASE_THEMES[phase_name]
    if phase_name == "Peak" and (hard >= 2 or mean < 45):
        return "Overload + adjustment"
    if phase_name == "Open" and mean >= 58:
        return soft
    if phase_name == "Settle":
        return "Stabilisation + skill growth"
    return soft if mean >= 50 else hard_label


def _why_layers(chart: Chart, strengths, maha: str, antar: str) -> Dict:
    pm, pa = chart.planets[maha], chart.planets[antar]
    return {
        "maha": {
            "title": f"{_pl(maha)} Mahadasha — background theme",
            "placement": (
                f"{_pl(maha)} sits in your {pm.house}th house "
                f"({ref.sign_label(pm.sign)}, {strengths[maha].dignity})."
            ),
            "brings": [
                t.strip() for t in DASHA_THEME.get(maha, "karmic growth").split(",")
            ] + [
                ref.HOUSE_THEME.get(pm.house, "life themes"),
            ],
            "quote": (
                f"{_pl(maha)} in the {pm.house}th colours the whole chapter — "
                f"{ref.HOUSE_SIGNIFICATION[pm.house].split('.')[0].lower()}."
            ),
        },
        "antar": {
            "title": f"{_pl(antar)} Antardasha — active flavour",
            "placement": (
                f"{_pl(antar)} is {strengths[antar].dignity} in your {pa.house}th "
                f"({ref.sign_label(pa.sign)})."
            ),
            "activates": [
                t.strip() for t in DASHA_THEME.get(antar, "inner change").split(",")
            ] + [
                PLANET_DOMAIN.get(antar, "its natural themes"),
            ],
            "quote": (
                f"{_pl(antar)} in the {pa.house}th activates "
                f"{ref.HOUSE_THEME.get(pa.house, 'these themes')} during the sub-period."
            ),
        },
        "fluctuation": (
            "Month-to-month ups and downs come from Gochara (transits) interacting with "
            "these natal placements — especially Jupiter and Saturn from the Moon."
        ),
    }


def _explain_chapter(
    chart: Chart, houses, strengths, chapter: Dict, when: datetime,
) -> Dict:
    maha, antar = chapter["maha"], chapter["antar"]
    start = datetime.fromisoformat(chapter["full_start"])
    end = datetime.fromisoformat(chapter["full_end"])
    length = _months(start, end)
    why = _why_layers(chart, strengths, maha, antar)

    phases = []
    for i, p in enumerate(chapter.get("phases") or []):
        mid = _mid(p["start"], p["end"])
        g_lines = _gochara_lines(chart, mid)
        theme = _phase_theme(p["name"], p["scores"])
        # Why this phase
        why_bits = []
        if i == 0:
            why_bits.append(
                f"{_pl(antar)} ({strengths[antar].dignity}) sets the opening pace; "
                f"{_pl(maha)} in {chart.planets[maha].house}th supplies the background drive."
            )
        elif i == 1:
            why_bits.append(
                "Peak of the sub-period — natal pressure points and harder transits show most."
            )
            hard_g = [g for g in g_lines if any(
                w in g.lower() for w in ("expense", "sudden", "pressure", "obstacle", "competition")
            )]
            if hard_g:
                why_bits.append("Key transit pressure: " + hard_g[0])
        else:
            why_bits.append(
                "Cooling phase — after peak intensity, clarity and skill growth tend to return."
            )
            soft_g = [g for g in g_lines if any(
                w in g.lower() for w in ("gain", "guidance", "luck", "network", "fresh")
            )]
            if soft_g:
                why_bits.append("Supportive transit cue: " + soft_g[0])

        area_blocks = {}
        for area, h in TIMING_AREAS:
            area_blocks[area] = _phase_area_lines(
                chart, houses, strengths, maha, antar, area, h, p["name"], g_lines,
            )
        ps = datetime.fromisoformat(p["start"])
        pe = datetime.fromisoformat(p["end"])
        phases.append({
            "name": f"Phase {i + 1} — {p['name']}",
            "theme": theme,
            "dates": f"{ps.strftime('%b %Y')} to {pe.strftime('%b %Y')}",
            "why": why_bits,
            "gochara": g_lines[:3],
            "areas": area_blocks,
            "scores": p["scores"],
        })

    # Key takeaways from chapter scores
    takeaways = {}
    for area, row in chapter["scores"].items():
        if row["tone"] == "bad":
            takeaways[area] = (
                f"Challenged through this chapter — most sensitive around the Peak phase. "
                f"({row['note']})"
            )
        elif row["tone"] == "good":
            takeaways[area] = (
                f"Favourable overall — lean into openings in the Open and Settle phases. "
                f"({row['note']})"
            )
        else:
            takeaways[area] = (
                f"Mixed — timing and choices decide outcomes. ({row['note']})"
            )

    return {
        "label": chapter["label"],
        "maha": maha,
        "antar": antar,
        "dates": f"{start.strftime('%d %b %Y')} – {end.strftime('%d %b %Y')}",
        "length_months": round(length, 1),
        "intro": (
            f"This period is about {length:.0f} months long. "
            f"{_pl(maha)} sets the tone ({DASHA_THEME.get(maha, 'growth')}); "
            f"{_pl(antar)} adds {DASHA_THEME.get(antar, 'change')}."
        ),
        "why": why,
        "phases": phases,
        "risks": chapter.get("risks", []),
        "opportunities": chapter.get("opportunities", []),
        "takeaways": takeaways,
        "is_current": chapter.get("is_current", False),
    }


def build_chart_explain(
    chart: Chart,
    when: Optional[datetime] = None,
    horizon_years: float = 6.0,
    timing: Optional[Dict] = None,
    remedies_count: int = 0,
) -> Dict:
    """Full structured explanation for summary page + prediction report."""
    when = when or datetime.now()
    timing = timing or build_timing_summary(chart, when=when, horizon_years=horizon_years)
    houses = analyse_all_houses(chart)
    strengths = all_strengths(chart)
    b = chart.birth
    name = b.name or "Native"
    moon = chart.planets["Moon"]
    lagna_lord = ref.SIGN_LORD[chart.lagna_sign]
    ll = chart.planets[lagna_lord]

    # Birth quality via Rishikesh navaratna when possible.
    try:
        panch = compute_panchang(
            date(b.year, b.month, b.day),
            latitude=b.latitude, longitude=b.longitude, tz_offset=b.tz_offset,
            place=b.place or "Birth", place_hindi="Birth",
            at_time=datetime(b.year, b.month, b.day, b.hour, b.minute),
        )
        rk = analyze_rishikesh_birth(
            chart, panch, datetime(b.year, b.month, b.day, b.hour, b.minute),
        )
        nav = rk["navaratna"]
        quality_pct, quality_verdict = nav["percent"], nav["verdict"]
    except Exception:
        quality_pct, quality_verdict = 50, "Mixed"

    if quality_pct >= 70:
        quality_quote = "a strong baseline for resilience"
    elif quality_pct >= 50:
        quality_quote = "a mixed baseline — strengths and challenges balance"
    else:
        quality_quote = "a baseline that needs conscious support"

    cur = timing.get("current") or {}
    ss = sade_sati_status(chart, when)

    life_areas = [
        _area_verdict_block(area, h, houses[h], strengths) for area, h in TIMING_AREAS
    ]
    snapshot = _planet_snapshot(chart, strengths)
    gochara = _gochara_lines(chart, when)

    working = [a["name"] for a in life_areas if a["tone"] == "good"]
    for line in snapshot["strong"][:2]:
        working.append(line.split(" → ")[-1])
    effort = [a["name"] for a in life_areas if a["tone"] == "bad"]
    if moon.house == 3:
        effort.append("Emotional restlessness (Moon in 3rd)")
    for line in snapshot["challenged"][:1]:
        effort.append(line.split(" → ")[0] + " pressure")

    # Favourable elements
    try:
        panch_now = compute_panchang(
            date(b.year, b.month, b.day),
            latitude=b.latitude, longitude=b.longitude, tz_offset=b.tz_offset,
            place=b.place or "Birth", place_hindi="Birth",
            at_time=datetime(b.year, b.month, b.day, b.hour, b.minute),
        )
        weekday = panch_now.vaara.name_hindi or panch_now.vaara.name
    except Exception:
        weekday = "—"
    gem = ref.REMEDIES.get(lagna_lord, {}).get("gemstone", "Consult astrologer")

    # Timing chapter explanations — current + next few
    chapters_src = timing.get("chapters") or []
    explained = [
        _explain_chapter(chart, houses, strengths, ch, when)
        for ch in chapters_src[:5]
    ]
    for i, ex in enumerate(explained):
        if i + 1 < len(explained):
            nxt = explained[i + 1]
            ex["next_teaser"] = (
                f"After this you enter {nxt['label']} ({nxt['dates']}) — "
                f"{DASHA_THEME.get(nxt['antar'], 'a new flavour')}."
            )
        else:
            ex["next_teaser"] = ""

    # Year maps with short prose
    year_maps = []
    for y in timing.get("years") or []:
        year_maps.append({
            "year": y["year"],
            "tag": y["tag"],
            "headline": f"{y['year']} — {y['tag']}",
            "chapters": y.get("chapters", []),
            "risks": y.get("risks", []),
            "opportunities": y.get("opportunities", []),
            "summary": (
                f"{y['tag']}: watch {', '.join(a for a, s in y['scores'].items() if s['tone'] == 'bad') or 'impulse moves'}; "
                f"lean into {', '.join(a for a, s in y['scores'].items() if s['tone'] == 'good') or 'steady skill work'}."
            ),
        })

    return {
        "title": f"{name} — Birth Chart Summary",
        "overall": {
            "score": int(round(quality_pct)),
            "verdict": quality_verdict,
            "quote": quality_quote,
            "balance": (
                "Strengths and challenges are balanced."
                if 45 <= quality_pct <= 75
                else "Overall tone leans supportive."
                if quality_pct > 75
                else "Overall tone asks for more conscious support."
            ),
        },
        "identity": {
            "ascendant": f"{ref.sign_label(chart.lagna_sign)} — {SIGN_TRAIT.get(chart.lagna_sign, 'distinctive')}",
            "moon": (
                f"{ref.sign_label(moon.sign)} ({moon.nakshatra}, pada {moon.nakshatra_pada}) — "
                f"{SIGN_TRAIT.get(moon.sign, 'distinctive')}"
            ),
            "chart_ruler": (
                f"{_pl(lagna_lord)} in {ll.house}th "
                f"({strengths[lagna_lord].dignity}) → "
                f"{ref.HOUSE_THEME.get(ll.house, 'daily life themes')}"
            ),
            "quote": (
                f"Your chart ruler {_pl(lagna_lord)} sits in the {ll.house}th house, "
                f"which strongly colours how these traits play out in daily life."
            ),
        },
        "current_chapter": {
            "maha": cur.get("maha"),
            "antar": cur.get("antar"),
            "antar_until": cur.get("antar_until"),
            "maha_theme": cur.get("maha_theme"),
            "antar_theme": cur.get("antar_theme"),
            "themes": [
                f"{_pl(cur['maha'])} → {cur.get('maha_theme')}" if cur.get("maha") else "",
                f"{_pl(cur['antar'])} → {cur.get('antar_theme')}" if cur.get("antar") else "",
            ],
            "quote": (
                f"You are in a {_pl(cur['maha']) if cur.get('maha') else '—'} / "
                f"{_pl(cur['antar']) if cur.get('antar') else '—'} chapter — "
                f"scan Career and Family first on the impact graph."
            ),
            "sade_sati": ss["phase"],
            "sade_sati_active": ss["active"],
        },
        "life_areas": life_areas,
        "planet_snapshot": snapshot,
        "gochara": gochara,
        "working_vs_effort": {
            "working": list(dict.fromkeys(working))[:6],
            "effort": list(dict.fromkeys(effort))[:6],
        },
        "favourable": {
            "weekday": weekday,
            "birth_star": f"{moon.nakshatra} ({_pl(ref.NAKSHATRA_LORD.get(moon.nakshatra, ''))})",
            "gemstone_hint": gem,
        },
        "remedies_note": (
            f"Open Horoscope & Reading → Phase 3 for detailed remedial measures (Upaye)"
            + (f" — about {remedies_count} suggested." if remedies_count else
               " — not always included in the download.")
        ),
        "timing_chapters": explained,
        "year_maps": year_maps,
    }


def chart_explain_markdown(ex: Dict) -> str:
    """Compact markdown twin of the structured explanation."""
    if not ex:
        return ""
    o, idn, cur = ex["overall"], ex["identity"], ex["current_chapter"]
    lines = [
        f"# {ex['title']}",
        "",
        "## Overall quality",
        f"Birth quality score: **{o['score']}% ({o['verdict']})** — “{o['quote']}”.",
        o["balance"],
        "",
        "## Core identity",
        f"- Ascendant: {idn['ascendant']}",
        f"- Moon: {idn['moon']}",
        f"- Chart ruler: {idn['chart_ruler']}",
        f"> {idn['quote']}",
        "",
        "## Current life chapter",
        f"- Mahadasha: **{cur.get('maha') or '—'}**",
        f"- Antardasha: **{cur.get('antar') or '—'}** (until {cur.get('antar_until') or '—'})",
    ]
    for t in cur.get("themes") or []:
        if t:
            lines.append(f"- {t}")
    lines += [
        f"> {cur.get('quote', '')}",
        f"Sade Sati: {cur.get('sade_sati') or '—'}",
        "",
        "## Life areas — quick verdicts",
    ]
    for a in ex.get("life_areas", []):
        lines.append(f"### {a['name']} — {a['verdict']}")
        for b in a["bullets"]:
            lines.append(f"- {b}")
        lines.append("")

    snap = ex.get("planet_snapshot") or {}
    lines.append("## Planet-by-planet snapshot")
    if snap.get("strong"):
        lines.append("### Strongest placements")
        for s in snap["strong"]:
            lines.append(f"- {s}")
    if snap.get("challenged"):
        lines.append("### Challenged placements")
        for s in snap["challenged"]:
            lines.append(f"- {s}")
    lines += ["", "## Transits (Gochara) — current pressures"]
    for g in ex.get("gochara", []):
        lines.append(f"- {g}")

    wve = ex.get("working_vs_effort") or {}
    lines += ["", "## What’s working vs what needs effort", "### Working well"]
    for x in wve.get("working", []):
        lines.append(f"- {x}")
    lines.append("### Needs effort")
    for x in wve.get("effort", []):
        lines.append(f"- {x}")

    fav = ex.get("favourable") or {}
    lines += [
        "",
        "## Favourable elements",
        f"- Weekday: {fav.get('weekday', '—')}",
        f"- Birth star: {fav.get('birth_star', '—')}",
        f"- Gemstone hint: {fav.get('gemstone_hint', '—')}",
        "",
        "## Remedies",
        ex.get("remedies_note", ""),
        "",
        "## Timing breakdowns (with why)",
    ]
    for ch in ex.get("timing_chapters", []):
        lines += [
            f"### {ch['label']} ({ch['dates']})",
            ch["intro"],
            "",
            f"**Why — Mahadasha:** {ch['why']['maha']['placement']}",
            f"> {ch['why']['maha']['quote']}",
            f"**Why — Antardasha:** {ch['why']['antar']['placement']}",
            f"> {ch['why']['antar']['quote']}",
            ch["why"]["fluctuation"],
            "",
        ]
        for ph in ch.get("phases", []):
            lines.append(f"#### {ph['name']} — {ph['theme']} ({ph['dates']})")
            for w in ph.get("why", []):
                lines.append(f"- Why: {w}")
            for area, bullets in (ph.get("areas") or {}).items():
                lines.append(f"- **{area}:** " + "; ".join(bullets[:2]))
            lines.append("")
        lines.append("**Key takeaways**")
        for area, text in (ch.get("takeaways") or {}).items():
            lines.append(f"- {area}: {text}")
        if ch.get("next_teaser"):
            lines += ["", f"*{ch['next_teaser']}*", ""]

    lines += ["", "## Year risk & opportunity map"]
    for y in ex.get("year_maps", []):
        lines.append(f"### {y['headline']}")
        lines.append(y.get("summary", ""))
        if y.get("risks"):
            lines.append("**Risks:** " + "; ".join(y["risks"]))
        if y.get("opportunities"):
            lines.append("**Opportunities:** " + "; ".join(y["opportunities"]))
        lines.append("")
    return "\n".join(lines)
