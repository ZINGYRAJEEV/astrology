"""'Today for You' dashboard — personalised daily guidance for a saved chart.

Combines, for a given native and day/location:
  * today's Panchang (Tithi, Nakshatra, Yoga, Karana, Vaara + sun/moon times)
  * personal day-quality score (Tarabala + Chandrabala + limb weighting)
  * auspicious windows (Choghadiya + Abhijit) and inauspicious windows
    (Rahu Kaal, Yamaganda, Gulika Kaal)
  * current Vimshottari Dasha (Maha / Antar) with a plain-language theme
  * Sade Sati status and Guru Gochar (Jupiter transit) relative to natal Moon
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Dict

from . import reference as ref
from .chart_engine import Chart
from .panchang import compute_panchang, format_time
from .dasha_calc import compute_vimshottari, current_dasha, sade_sati_status
from .rishikesh_prediction import _guru_gochar
from .muhurta import ACTIVITIES, evaluate_day
from .narrative import DASHA_THEME


def _dasha_line(maha_lord, antar_lord) -> str:
    if not maha_lord:
        return "Dasha timing unavailable."
    line = (
        f"You are in a **{maha_lord} Mahadasha**"
        + (f" with **{antar_lord} Antardasha**" if antar_lord else "")
        + f". The broad theme is {DASHA_THEME.get(maha_lord, 'karmic growth')}"
    )
    if antar_lord and antar_lord != maha_lord:
        line += f", coloured right now by {DASHA_THEME.get(antar_lord, 'inner change')}"
    return line + "."


def build_dashboard(
    chart: Chart,
    target_date: date,
    latitude: float,
    longitude: float,
    tz_offset: float,
    place: str,
) -> Dict:
    """Assemble the personalised daily dashboard for ``chart`` on ``target_date``."""
    moon = chart.planets["Moon"]
    janma_nak = moon.nakshatra
    moon_sign = moon.sign
    janma_nak_idx = ref.NAKSHATRAS.index(janma_nak) if janma_nak in ref.NAKSHATRAS else None
    moon_sign_idx = ref.SIGNS.index(moon_sign) if moon_sign in ref.SIGNS else None

    day = evaluate_day(
        target_date, ACTIVITIES["general"], latitude, longitude, tz_offset, place,
        janma_nak_idx, moon_sign_idx,
    )
    panch = compute_panchang(
        target_date, latitude=latitude, longitude=longitude, tz_offset=tz_offset,
        place=place, place_hindi="", altitude_m=0.0,
    )

    when = datetime.combine(target_date, time(12, 0))
    periods = compute_vimshottari(chart)
    maha, antar = current_dasha(periods, when)
    ss = sade_sati_status(chart, when)
    guru = _guru_gochar(chart, when)

    inauspicious = [
        {"name": w.name, "start": format_time(w.start), "end": format_time(w.end)}
        for w in (panch.rahu_kaal, panch.yamaganda, panch.gulika_kaal)
    ]

    if day.verdict == "Auspicious":
        headline = "A favourable day for you — good energy for meaningful action."
    elif day.verdict == "Workable":
        headline = "A workable day — pick your windows and avoid the flagged times."
    else:
        headline = "A low day for you — keep to routine; defer important launches."

    return {
        "name": chart.birth.name or "Native",
        "date": target_date,
        "place": place,
        "janma_nakshatra": janma_nak,
        "moon_sign": moon_sign,
        "score": day.score,
        "verdict": day.verdict,
        "headline": headline,
        "weekday": day.weekday,
        "panchang": {
            "tithi": f"{panch.tithi.name} ({panch.paksha})",
            "nakshatra": panch.nakshatra.name,
            "yoga": panch.yoga.name,
            "karana": panch.karana.name,
            "sunrise": format_time(panch.sunrise),
            "sunset": format_time(panch.sunset),
            "abhijit": {
                "start": format_time(panch.abhijit_muhurta.start),
                "end": format_time(panch.abhijit_muhurta.end),
            },
            "brahma_muhurta": {
                "start": format_time(panch.brahma_muhurta.start),
                "end": format_time(panch.brahma_muhurta.end),
            },
        },
        "good_windows": day.windows,
        "avoid_windows": inauspicious,
        "positives": day.positives,
        "warnings": day.warnings,
        "dasha": {
            "maha": maha.lord if maha else None,
            "antar": antar.lord if antar else None,
            "line": _dasha_line(maha.lord if maha else None, antar.lord if antar else None),
        },
        "sade_sati": {
            "active": ss["active"],
            "phase": ss["phase"],
            "note": (
                f"Sade Sati active — {ss['phase']}." if ss["active"]
                else "Not in Sade Sati — that Saturn pressure phase is not active for you."
            ),
        },
        "guru_gochar": guru["phase"],
    }
