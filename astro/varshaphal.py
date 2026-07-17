"""Varshaphal (Tajika annual horoscope) — solar-return chart for a given year.

Computes the Varsha Pravesh (the instant the transiting Sun returns to its
natal sidereal longitude), builds the annual chart, locates the Muntha
(progressed point), selects a simplified year-lord (Varshesh) from the Tajika
office-bearers, and gives a Sun-transit month-by-month outlook.

Note: the year-lord uses a simplified strength proxy rather than full
Panchavargeeya Bala; treat it as indicative.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

import swisseph as swe

from . import reference as ref
from .chart_engine import BirthData, Chart, compute_chart
from .strength_calc import all_strengths
from .panchavargeeya import panchavargeeya_bala, trirashi_pati

_FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL
_SUN_SPEED = 0.98565  # mean degrees/day

HOUSE_THEME = {
    1: "self, health & fresh initiative",
    2: "money, family & speech",
    3: "effort, courage, siblings & short trips",
    4: "home, property, mother & inner peace",
    5: "creativity, romance, children & speculation",
    6: "work, competition, health & debts",
    7: "partnerships, marriage & travel",
    8: "change, shared resources & research",
    9: "fortune, dharma, mentors & long journeys",
    10: "career, status & public life",
    11: "gains, networks & fulfilment of desires",
    12: "expenses, retreat, spirituality & foreign links",
}


def _sun_longitude(when_ut: datetime) -> float:
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd = swe.julday(when_ut.year, when_ut.month, when_ut.day,
                    when_ut.hour + when_ut.minute / 60.0 + when_ut.second / 3600.0)
    return swe.calc_ut(jd, swe.SUN, _FLAGS)[0][0] % 360.0


def solar_return(chart: Chart, year: int) -> datetime:
    """Local datetime when the transiting Sun returns to its natal longitude."""
    natal_sun = chart.planets["Sun"].longitude
    tz = chart.birth.tz_offset
    guess = datetime(year, chart.birth.month, chart.birth.day,
                     chart.birth.hour, chart.birth.minute)
    for _ in range(8):
        cur = _sun_longitude(guess - timedelta(hours=tz))
        diff = ((natal_sun - cur + 180.0) % 360.0) - 180.0
        if abs(diff) < 1e-4:
            break
        guess += timedelta(days=diff / _SUN_SPEED)
    return guess


def _annual_chart(chart: Chart, sr_local: datetime) -> Chart:
    b = chart.birth
    annual_birth = BirthData(
        name=b.name, year=sr_local.year, month=sr_local.month, day=sr_local.day,
        hour=sr_local.hour, minute=sr_local.minute,
        latitude=b.latitude, longitude=b.longitude, tz_offset=b.tz_offset, place=b.place,
    )
    return compute_chart(annual_birth)


def _aspects_lagna(annual: Chart, planet: str) -> bool:
    """True if the planet occupies or casts a full aspect on the annual Lagna."""
    from .aspects import aspects_on_house
    if annual.planet_house(planet) == 1:
        return True
    return any(a["planet"] == planet for a in aspects_on_house(annual, 1))


def _select_year_lord(annual: Chart, candidates: List[Dict]) -> Dict:
    """Varshesh = the office-bearer with the greatest Panchavargeeya Bala.

    Tradition prefers a candidate related to the annual Lagna, so a lord that
    aspects/occupies the Lagna wins ties and is noted.
    """
    for c in candidates:
        bala = panchavargeeya_bala(c["planet"], annual)
        c["bala"] = bala
        c["total"] = bala["total"]
        c["aspects_lagna"] = _aspects_lagna(annual, c["planet"])
        c["dignity"] = all_strengths(annual)[c["planet"]].dignity

    best = max(
        candidates,
        key=lambda c: (c["total"], c["aspects_lagna"]),
    )
    return best


def varshaphal(chart: Chart, year: int) -> Dict:
    """Full Tajika annual horoscope for the solar year beginning in ``year``."""
    sr = solar_return(chart, year)
    annual = _annual_chart(chart, sr)
    annual_lagna_idx = annual.lagna_sign_index

    age = year - chart.birth.year
    muntha_idx = (chart.lagna_sign_index + age) % 12
    muntha_sign = ref.SIGNS[muntha_idx]
    muntha_house = (muntha_idx - annual_lagna_idx) % 12 + 1
    muntha_lord = ref.SIGN_LORD[muntha_sign]

    sun_house = annual.planets["Sun"].house
    is_day = sun_house in {7, 8, 9, 10, 11, 12}
    luminary = "Sun" if is_day else "Moon"

    trirashi = trirashi_pati(annual.lagna_sign, is_day)
    candidates = [
        {"role": "Muntha lord (Munthesh)", "planet": muntha_lord},
        {"role": "Annual-Ascendant lord (Varsha Lagnesh)", "planet": ref.SIGN_LORD[annual.lagna_sign]},
        {"role": "Birth-Ascendant lord (Janma Lagnesh)", "planet": ref.SIGN_LORD[chart.lagna_sign]},
        {"role": f"Triplicity lord (Trirashi-pati, {'day' if is_day else 'night'})", "planet": trirashi},
        {"role": f"Day/Night lord (Dinaratri-pati, {'day' if is_day else 'night'})", "planet": luminary},
    ]
    # De-duplicate planets, keeping the highest-priority role.
    seen, uniq = {}, []
    for c in candidates:
        if c["planet"] in seen:
            continue
        seen[c["planet"]] = True
        uniq.append(c)
    year_lord = _select_year_lord(annual, uniq)

    strengths = all_strengths(annual)
    annual_planets = []
    for name in ref.PLANETS:
        p = annual.planets[name]
        annual_planets.append({
            "planet": name,
            "sign": p.sign,
            "house": p.house,
            "dignity": strengths[name].dignity,
            "retrograde": p.retrograde,
        })

    highlights: List[str] = [
        f"Muntha in house {muntha_house} ({muntha_sign}) — the year emphasises "
        f"{HOUSE_THEME[muntha_house]}.",
        f"Year lord (Varshesh): {year_lord['planet']} as {year_lord['role']} — "
        f"strongest office-bearer with {year_lord['total']} virupas of "
        f"Panchavargeeya Bala"
        + (", and it aspects the annual Ascendant."
           if year_lord["aspects_lagna"] else "."),
    ]
    benefics_kendra = [
        p["planet"] for p in annual_planets
        if p["house"] in {1, 4, 7, 10} and p["planet"] in ref.NATURAL_BENEFICS
    ]
    if benefics_kendra:
        highlights.append(
            f"Benefic(s) {', '.join(benefics_kendra)} in an angle (kendra) — "
            "supportive backbone for the year."
        )

    monthly = _monthly_outlook(chart, sr, annual_lagna_idx)

    return {
        "year": year,
        "age": age,
        "solar_return": sr.strftime("%d %b %Y, %I:%M %p").lstrip("0"),
        "place": chart.birth.place,
        "annual_lagna": annual.lagna_sign,
        "annual_lagna_lord": ref.SIGN_LORD[annual.lagna_sign],
        "muntha_sign": muntha_sign,
        "muntha_house": muntha_house,
        "muntha_lord": muntha_lord,
        "year_lord": year_lord["planet"],
        "year_lord_role": year_lord["role"],
        "year_lord_dignity": year_lord["dignity"],
        "year_lord_bala": year_lord["total"],
        "office_bearers": uniq,
        "annual_planets": annual_planets,
        "highlights": highlights,
        "monthly": monthly,
    }


def _monthly_outlook(chart: Chart, sr_local: datetime, annual_lagna_idx: int) -> List[Dict]:
    tz = chart.birth.tz_offset
    seg = 365.25 / 12.0
    out: List[Dict] = []
    for k in range(12):
        start_local = sr_local + timedelta(days=seg * k)
        sun_lon = _sun_longitude(start_local - timedelta(hours=tz))
        sun_sign_idx = int(sun_lon // 30) % 12
        house = (sun_sign_idx - annual_lagna_idx) % 12 + 1
        out.append({
            "month": k + 1,
            "from_date": start_local.strftime("%d %b %Y"),
            "sun_sign": ref.SIGNS[sun_sign_idx],
            "house": house,
            "theme": HOUSE_THEME[house],
        })
    return out


def varshaphal_markdown(vp: Dict, native: str) -> str:
    lines = [
        f"# Varshaphal {vp['year']} — {native} (age {vp['age']})",
        "",
        f"Solar return (Varsha Pravesh): {vp['solar_return']} · {vp['place']}",
        f"Annual Ascendant: {vp['annual_lagna']} (lord {vp['annual_lagna_lord']})",
        f"Muntha: {vp['muntha_sign']} in house {vp['muntha_house']} (lord {vp['muntha_lord']})",
        f"Year lord (Varshesh): {vp['year_lord']} — {vp['year_lord_role']} "
        f"({vp['year_lord_bala']} virupas)",
        "",
        "## Office-bearers (Panchavargeeya Bala)",
        "",
        "| Role | Planet | Kshetra | Uchcha | Hadda | Drekkana | Navamsha | Total |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for c in vp["office_bearers"]:
        b = c["bala"]
        lines.append(
            f"| {c['role']} | {c['planet']} | {b['kshetra']} | {b['uchcha']} | "
            f"{b['hadda']} | {b['drekkana']} | {b['navamsha']} | **{b['total']}** |"
        )
    lines += ["", "## Highlights"]
    for h in vp["highlights"]:
        lines.append(f"- {h}")
    lines += ["", "## Month-by-month (Sun transit)"]
    for m in vp["monthly"]:
        lines.append(f"- **From {m['from_date']}** — Sun in {m['sun_sign']} "
                     f"(house {m['house']}): {m['theme']}")
    return "\n".join(lines)
