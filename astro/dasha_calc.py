"""Vimshottari Dasha timing engine (Step 5 of the build plan).

Implements the 120-year Vimshottari system based on the Moon's Nakshatra at
birth: it finds the starting dasha balance, then generates the full
Mahadasha sequence with Antardasha sub-periods. Also provides a simple
Sade Sati detector (Saturn transiting the 12th/1st/2nd sign from natal Moon).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

import swisseph as swe

from . import reference as ref
from .chart_engine import Chart

# Mean tropical year length used to convert dasha "years" to days.
_YEAR_DAYS = 365.2425


@dataclass
class DashaPeriod:
    lord: str
    start: datetime
    end: datetime
    level: int                      # 1 = Maha, 2 = Antar
    antardashas: List["DashaPeriod"] = field(default_factory=list)

    @property
    def years(self) -> float:
        return (self.end - self.start).days / _YEAR_DAYS


def _jd_to_datetime(jd: float) -> datetime:
    y, mo, d, h = swe.revjul(jd)
    hh = int(h)
    mm = int((h - hh) * 60)
    ss = int((((h - hh) * 60) - mm) * 60)
    return datetime(y, mo, d, hh, mm, ss)


def _add_years(dt: datetime, years: float) -> datetime:
    return dt + timedelta(days=years * _YEAR_DAYS)


def _moon_nakshatra_fraction(moon_long: float):
    """Return (nakshatra name, lord, fraction elapsed within the nakshatra)."""
    idx = int(moon_long // ref.NAKSHATRA_SPAN) % 27
    pos_in_nak = moon_long - idx * ref.NAKSHATRA_SPAN
    fraction = pos_in_nak / ref.NAKSHATRA_SPAN
    name = ref.NAKSHATRAS[idx]
    return name, ref.NAKSHATRA_LORD[name], fraction


def compute_vimshottari(chart: Chart, antardashas: bool = True) -> List[DashaPeriod]:
    """Full Mahadasha timeline (and Antardashas) from birth to birth+120y."""
    moon = chart.planets["Moon"]
    nak_name, start_lord, fraction = _moon_nakshatra_fraction(moon.longitude)

    birth_dt = _jd_to_datetime(chart.julian_day_ut) + timedelta(hours=chart.birth.tz_offset)

    # Balance of the first (running-at-birth) mahadasha.
    start_index = ref.VIMSHOTTARI_ORDER.index(start_lord)
    full_first = ref.VIMSHOTTARI_YEARS[start_lord]
    remaining_first = full_first * (1.0 - fraction)

    periods: List[DashaPeriod] = []
    cursor = birth_dt
    for i in range(9):
        lord = ref.VIMSHOTTARI_ORDER[(start_index + i) % 9]
        span = remaining_first if i == 0 else ref.VIMSHOTTARI_YEARS[lord]
        end = _add_years(cursor, span)
        period = DashaPeriod(lord=lord, start=cursor, end=end, level=1)
        if antardashas:
            period.antardashas = _antardashas(lord, cursor, span)
        periods.append(period)
        cursor = end
    return periods


def _antardashas(maha_lord: str, start: datetime, maha_years: float) -> List[DashaPeriod]:
    """Sub-periods within a mahadasha, starting from the mahadasha lord."""
    start_index = ref.VIMSHOTTARI_ORDER.index(maha_lord)
    subs: List[DashaPeriod] = []
    cursor = start
    for i in range(9):
        lord = ref.VIMSHOTTARI_ORDER[(start_index + i) % 9]
        # Antardasha length proportional to lord's years out of 120.
        sub_years = maha_years * ref.VIMSHOTTARI_YEARS[lord] / 120.0
        end = _add_years(cursor, sub_years)
        subs.append(DashaPeriod(lord=lord, start=cursor, end=end, level=2))
        cursor = end
    return subs


def current_dasha(periods: List[DashaPeriod], when: Optional[datetime] = None):
    """Return (mahadasha, antardasha) active at ``when`` (default: now)."""
    when = when or datetime.now()
    for maha in periods:
        if maha.start <= when < maha.end:
            antar = None
            for a in maha.antardashas:
                if a.start <= when < a.end:
                    antar = a
                    break
            return maha, antar
    return None, None


def starting_nakshatra(chart: Chart) -> dict:
    moon = chart.planets["Moon"]
    name, lord, fraction = _moon_nakshatra_fraction(moon.longitude)
    return {
        "nakshatra": name,
        "lord": lord,
        "fraction_elapsed": fraction,
        "balance_years": ref.VIMSHOTTARI_YEARS[lord] * (1 - fraction),
    }


# ---------------------------------------------------------------------------
# Gochara (transit) helpers - Sade Sati
# ---------------------------------------------------------------------------
def sade_sati_status(chart: Chart, when: Optional[datetime] = None) -> dict:
    """Detect Sade Sati: Saturn transiting 12th/1st/2nd sign from natal Moon."""
    when = when or datetime.now()
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ut = when  # treat as UT for a coarse transit check
    jd = swe.julday(ut.year, ut.month, ut.day,
                    ut.hour + ut.minute / 60.0)
    xx, _ = swe.calc_ut(jd, swe.SATURN, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)
    sat_sign = int(xx[0] // 30) % 12

    moon_sign = chart.planets["Moon"].sign_index
    diff = (sat_sign - moon_sign) % 12
    phases = {11: "Rising (12th from Moon)", 0: "Peak (over Moon)", 1: "Setting (2nd from Moon)"}
    active = diff in phases
    return {
        "active": active,
        "phase": phases.get(diff, "Not in Sade Sati"),
        "saturn_sign": ref.SIGNS[sat_sign],
        "moon_sign": ref.SIGNS[moon_sign],
    }
