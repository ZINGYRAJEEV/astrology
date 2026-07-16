"""User-friendly report formatting (Hrishikesh Panchang style).

Rules: plain verdict first, inline term definitions, split data from interpretation,
reader-oriented grouping, explicit verdict scale, short non-redundant summary.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple

from . import prediction_data as pd
from . import reference as ref
from .interpret import HouseReport

SCOPE_NOTE = (
    "This report covers your birth chart profile and life-area predictions. "
    "Detailed remedies for weak planets are in **Horoscope & Reading → Phase 3**, "
    "not included in this download."
)

VERDICT_LEGEND = (
    "**How to read verdicts**\n"
    "- **Supported** — this area tends to work in your favor without much extra effort\n"
    "- **Mixed** — outcomes depend heavily on your choices and timing\n"
    "- **Challenged** — this area needs conscious effort, patience, or remedial practice\n"
    "- **Auspicious** — strongly favorable by Panchang birth-quality scoring (70%+ is strong)"
)

VERDICT_SHORT = {
    "Supported": "works in your favor",
    "Mixed": "depends on your choices",
    "Challenged": "needs conscious effort",
    "Auspicious": "strongly favorable",
}

DIGNITY_PLAIN = {
    "Exalted": "strongest possible sign placement",
    "Debilitated": "weakest possible sign placement",
    "Own Sign": "at home in its own sign",
    "Moolatrikona": "very comfortable and strong",
    "Friend's Sign": "supportive sign placement",
    "Enemy's Sign": "uncomfortable sign placement",
    "Neutral": "neutral sign placement",
}

HOUSE_FRIENDLY: Dict[int, Tuple[str, str]] = {
    1: ("Personality & Self", "Lagna"),
    2: ("Wealth & Income", "Dhana"),
    6: ("Health & Daily Life", "Ripu"),
    7: ("Marriage & Love", "Kalatra"),
    9: ("Spiritual Path", "Dharma"),
    10: ("Career & Public Life", "Karma"),
}


def _fmt_time(hour: int, minute: int) -> str:
    dt = datetime(2000, 1, 1, hour, minute)
    return dt.strftime("%I:%M %p").lstrip("0")


def _fmt_date(day: int, month: int, year: int) -> str:
    dt = datetime(year, month, day)
    return dt.strftime("%B %d, %Y")


def bindu_context(points: int) -> str:
    base = f"{points} bindus (strength points out of ~56 per house — higher is better)"
    if points >= 30:
        return f"{base}; **{points} is high**"
    if points >= 25:
        return f"{base}; **{points} is moderate**"
    return f"{base}; **{points} is low** — extra effort helps"


def navaratna_context(percent: float) -> str:
    return (
        f"Birth quality score: {percent}% "
        f"(scores **above 70%** are strongly favorable; 50–70% is mixed; below 50% needs attention)."
    )


def dignity_phrase(dignity: str) -> str:
    plain = DIGNITY_PLAIN.get(dignity, dignity.lower())
    return f"{dignity} ({plain})"


def birth_intro_lines(
    name: str, birth: dict, chart_lagna: str, moon_sign: str,
    moon_nak: str, moon_pada: int,
) -> List[str]:
    who = name or "You"
    return [
        f"{who} was born on {_fmt_date(birth['day'], birth['month'], birth['year'])} "
        f"at {_fmt_time(birth['hour'], birth['minute'])} in {birth.get('place') or 'your birthplace'}.",
        f"Your **Ascendant** (rising sign — shapes outward personality) is **{chart_lagna}**.",
        f"Your **Moon sign** (inner emotional nature) is **{moon_sign}**, "
        f"in the lunar mansion **{moon_nak}** (pada {moon_pada}).",
    ]


def format_house_section(
    area_name: str,
    house_num: int,
    report: HouseReport,
    extra_plain: str = "",
) -> Dict[str, str]:
    friendly, sanskrit = HOUSE_FRIENDLY.get(
        house_num, (area_name, ref.HOUSE_NAME.get(house_num, "")),
    )
    verdict = report.verdict
    vshort = VERDICT_SHORT.get(verdict, verdict.lower())
    plain_parts = [pd.VERDICT_PREDICTION[verdict]]
    if extra_plain:
        plain_parts.append(extra_plain.strip())
    plain = " ".join(plain_parts)
    technical = (
        f"House {house_num} ({sanskrit}): lord **{report.lord}** sits in house "
        f"{report.lord_house} ({dignity_phrase(report.lord_dignity)}). "
        f"Ashtakavarga: {bindu_context(report.sav_points)} ({report.sav_class})."
    )
    return {
        "area": area_name,
        "title": f"{friendly} — {vshort}",
        "friendly_name": friendly,
        "verdict": verdict,
        "verdict_short": vshort,
        "plain": plain,
        "technical": technical,
        "prediction": plain,
        "technical_basis": technical,
    }


def format_personality_section(
    nak: dict, av: dict, nav_percent: float,
    vaara_text: str, tithi_text: str, yoga_text: str, karana_text: str,
    lagna: str, lagna_lord: str, ll_dignity: str, ll_score: float,
    nav_verdict: str = "Mixed",
) -> Dict[str, str]:
    verdict = "Supported" if ll_score >= 0.5 else "Mixed"
    if nav_verdict == "Auspicious":
        verdict = "Supported"
    vshort = VERDICT_SHORT.get(verdict, verdict)
    plain = (
        f"{nak.get('nature', 'You have a distinctive nature')}. "
        f"{nak.get('prediction', '')} "
        f"You tend toward {av['varna'].lower()} temperament ({av['varna_meaning'].lower()}), "
        f"with a {av['gana'].lower()} spiritual style and {av['yoni'].lower()} yoni energy. "
        f"{navaratna_context(nav_percent)}"
    )
    technical = (
        f"Avakhada: Varna {av['varna']}, Gana {av['gana']}, Yoni {av['yoni']}, "
        f"Nadi {av['nadi']} (Ayurvedic constitution type). "
        f"Weekday: {vaara_text} Tithi: {tithi_text} Yoga: {yoga_text} Karana: {karana_text}. "
        f"Lagnesh {lagna_lord} ({dignity_phrase(ll_dignity)}) for {lagna} Ascendant."
    )
    return {
        "area": "Personality & nature",
        "title": f"Who you are — {vshort}",
        "friendly_name": "Who you are",
        "verdict": verdict,
        "verdict_short": vshort,
        "plain": plain.strip(),
        "technical": technical,
        "prediction": plain.strip(),
        "technical_basis": technical,
    }


def format_focus_line(house_num: int, report: HouseReport) -> Dict[str, str]:
    theme = ref.HOUSE_THEME[house_num].title()
    friendly, sanskrit = HOUSE_FRIENDLY.get(
        house_num, (theme, ref.HOUSE_NAME.get(house_num, "")),
    )
    return {
        "plain": (
            f"**{friendly}** — {VERDICT_SHORT.get(report.verdict, report.verdict)}. "
            f"{pd.VERDICT_PREDICTION[report.verdict]}"
        ),
        "technical": (
            f"House {house_num} ({sanskrit}): lord {report.lord} "
            f"({dignity_phrase(report.lord_dignity)})."
        ),
    }


def format_timing_plain(timing: dict) -> Dict[str, str]:
    plain_parts = []
    if timing.get("current_maha"):
        maha = timing["current_maha"]
        antar = timing.get("current_antar")
        plain_parts.append(
            f"You are in **{maha} Mahadasha**"
            + (f" with **{antar} Antardasha**" if antar else "")
            + " — a major life chapter shaped by that planet's themes."
        )
    if timing.get("year_ahead"):
        plain_parts.append(timing["year_ahead"])
    if timing.get("sade_sati") and "Not in" not in timing["sade_sati"]:
        plain_parts.append(
            f"Saturn's Sade Sati phase: {timing['sade_sati']} — a period of testing and maturity."
        )
    if timing.get("guru_gochar"):
        plain_parts.append(timing["guru_gochar"])
    technical = (
        f"Birth Nakshatra {timing.get('birth_nakshatra')} "
        f"(Dasha lord {timing.get('birth_nakshatra_lord')}). "
        f"Dasha balance at birth: {timing.get('dasha_balance_years', '—')} years."
    )
    return {
        "plain": " ".join(plain_parts) if plain_parts else "Timing data unavailable.",
        "technical": technical,
    }


def build_summary(name: str, life_predictions: List[Dict], nav_percent: float,
                  intent: str) -> str:
    who = name or "You"
    supported = sum(1 for lp in life_predictions if lp["verdict"] == "Supported")
    challenged = sum(1 for lp in life_predictions if lp["verdict"] == "Challenged")
    if supported > challenged:
        tone = "more areas work in your favor than need extra effort"
    elif challenged > supported:
        tone = "several areas ask for patience and conscious effort"
    else:
        tone = "strengths and challenges are fairly balanced"
    return (
        f"{who}, your chart shows {tone} for **{intent.lower()}**. "
        f"Birth quality is {nav_percent:.0f}% by Panchang scoring. "
        f"Each section below leads with plain meaning; technical details are optional."
    )


def group_predictions(life_predictions: List[Dict]) -> Dict[str, List[Dict]]:
    who = [lp for lp in life_predictions if "Personality" in lp["area"]]
    working = [lp for lp in life_predictions if lp["verdict"] == "Supported" and lp not in who]
    effort = [lp for lp in life_predictions if lp["verdict"] in ("Mixed", "Challenged") and lp not in who]
    return {"who_you_are": who, "working_well": working, "needs_effort": effort}


def enrich_prediction(pred: dict, birth_raw: dict) -> dict:
    pred = dict(pred)
    pred["scope_note"] = SCOPE_NOTE
    pred["verdict_legend"] = VERDICT_LEGEND
    pred["birth_intro"] = birth_intro_lines(
        pred["name"], birth_raw, pred["birth"]["lagna"],
        pred.get("moon_sign", ""), pred["panchang_at_birth"]["nakshatra"],
        pred["panchang_at_birth"]["nakshatra_pada"],
    )
    rk = pred.get("rishikesh", {})
    nav_pct = rk.get("navaratna", {}).get("percent", 0)
    pred["summary"] = build_summary(
        pred["name"], pred["life_predictions"], nav_pct, pred["focus_intent"],
    )
    pred["groups"] = group_predictions(pred["life_predictions"])
    pred["timing_friendly"] = format_timing_plain(pred.get("timing", {}))
    pred["remedies_note"] = (
        f"Open **Horoscope & Reading → Phase 3** for {pred.get('remedies_count', 0)} "
        "detailed remedial measures (Upaye) — not included in this download."
    )
    return pred
