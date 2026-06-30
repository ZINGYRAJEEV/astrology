"""Chart calculation engine (Steps 1 & 4 of the build plan).

Pure computation, no UI. Given birth date/time/place it computes the nine
planetary longitudes in the sidereal zodiac (Lahiri Ayanamsha), the
Ascendant (Lagna), assigns each planet to a sign and a whole-sign house,
and computes the Navamsha (D-9) divisional chart used for "true" strength
and marriage analysis.

Swiss Ephemeris (``pyswisseph``) is used with the built-in Moshier model so
no external ephemeris data files are required and everything works offline.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import swisseph as swe

from . import reference as ref

# Map our planet names to Swiss Ephemeris body ids. Rahu uses the Mean Node;
# Ketu is derived as exactly 180 degrees from Rahu.
_SWE_ID = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}

# Moshier ephemeris + sidereal zodiac + speed (to detect retrograde).
_FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

_NAVAMSHA_ARC = 30.0 / 9.0  # 3 deg 20 min


@dataclass
class PlanetPosition:
    name: str
    longitude: float          # sidereal longitude 0-360
    sign: str
    sign_index: int           # 0-11
    degree_in_sign: float     # 0-30
    house: int                # 1-12 (whole-sign from Lagna)
    nakshatra: str
    nakshatra_pada: int       # 1-4
    retrograde: bool
    navamsha_sign: str
    navamsha_sign_index: int
    navamsha_house: int = 0   # filled once navamsha lagna known


@dataclass
class BirthData:
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    tz_offset: float          # hours east of UTC (e.g. India = 5.5)
    place: str = ""


@dataclass
class Chart:
    birth: BirthData
    julian_day_ut: float
    ayanamsha: float
    ascendant_longitude: float
    lagna_sign: str
    lagna_sign_index: int
    navamsha_lagna_sign: str
    navamsha_lagna_index: int
    planets: Dict[str, PlanetPosition] = field(default_factory=dict)
    # sign occupying each house number 1..12 (whole sign)
    house_signs: Dict[int, str] = field(default_factory=dict)

    # ---- convenience accessors -------------------------------------------
    def house_lord(self, house: int) -> str:
        """Ruling planet of the sign occupying ``house``."""
        return ref.SIGN_LORD[self.house_signs[house]]

    def occupants(self, house: int) -> List[str]:
        return [p.name for p in self.planets.values() if p.house == house]

    def planet_house(self, planet: str) -> int:
        return self.planets[planet].house

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _norm360(x: float) -> float:
    return x % 360.0


def _sign_index(longitude: float) -> int:
    return int(longitude // 30) % 12


def _navamsha_sign_index(longitude: float) -> int:
    """Continuous Navamsha (D-9) sign index for a sidereal longitude.

    Each sign is split into nine 3°20' parts; counting these parts
    continuously from Aries 0° and taking modulo 12 yields the correct
    navamsha sign for movable/fixed/dual signs alike.
    """
    return int(longitude // _NAVAMSHA_ARC) % 12


def _nakshatra(longitude: float):
    idx = int(longitude // ref.NAKSHATRA_SPAN) % 27
    pos_in_nak = longitude - idx * ref.NAKSHATRA_SPAN
    pada = int(pos_in_nak // (ref.NAKSHATRA_SPAN / 4)) + 1
    return ref.NAKSHATRAS[idx], pada


def _whole_sign_house(planet_sign_index: int, lagna_sign_index: int) -> int:
    return (planet_sign_index - lagna_sign_index) % 12 + 1


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def compute_chart(birth: BirthData) -> Chart:
    """Compute a full natal chart (D-1) plus Navamsha (D-9) placements."""
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

    # Local civil time -> UTC -> Julian day.
    local_dt = datetime(birth.year, birth.month, birth.day, birth.hour, birth.minute)
    ut_dt = local_dt - timedelta(hours=birth.tz_offset)
    ut_hour = ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0
    jd_ut = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_hour)

    ayanamsha = swe.get_ayanamsa_ut(jd_ut)

    # Ascendant via Placidus cusps in sidereal mode; ascmc[0] = Ascendant.
    # Index by position so we work with both ``pyswisseph`` (returns
    # (cusps, ascmc)) and the ``pysweph`` fork (which may append an error
    # string). ``ascmc[0]`` is the Ascendant in either case.
    houses_result = swe.houses_ex(
        jd_ut, birth.latitude, birth.longitude, b"P", swe.FLG_SIDEREAL
    )
    ascmc = houses_result[1]
    asc_long = _norm360(ascmc[0])
    lagna_idx = _sign_index(asc_long)
    nav_lagna_idx = _navamsha_sign_index(asc_long)

    chart = Chart(
        birth=birth,
        julian_day_ut=jd_ut,
        ayanamsha=ayanamsha,
        ascendant_longitude=asc_long,
        lagna_sign=ref.SIGNS[lagna_idx],
        lagna_sign_index=lagna_idx,
        navamsha_lagna_sign=ref.SIGNS[nav_lagna_idx],
        navamsha_lagna_index=nav_lagna_idx,
    )

    # Whole-sign house -> sign mapping.
    for h in range(1, 13):
        chart.house_signs[h] = ref.SIGNS[(lagna_idx + h - 1) % 12]

    # Planets.
    for name in ref.PLANETS:
        if name == "Ketu":
            rahu = chart.planets["Rahu"]
            lon = _norm360(rahu.longitude + 180.0)
            speed = -1.0  # nodes are always retrograde
        else:
            # ``[0]`` = position tuple; later return items (retflags / error
            # string) differ between pyswisseph and the pysweph fork.
            xx = swe.calc_ut(jd_ut, _SWE_ID[name], _FLAGS)[0]
            lon = _norm360(xx[0])
            speed = xx[3]

        sidx = _sign_index(lon)
        nak, pada = _nakshatra(lon)
        nav_idx = _navamsha_sign_index(lon)
        # Rahu/Ketu are treated as perpetually retrograde.
        retro = (name in ("Rahu", "Ketu")) or (speed < 0)

        chart.planets[name] = PlanetPosition(
            name=name,
            longitude=lon,
            sign=ref.SIGNS[sidx],
            sign_index=sidx,
            degree_in_sign=lon - sidx * 30.0,
            house=_whole_sign_house(sidx, lagna_idx),
            nakshatra=nak,
            nakshatra_pada=pada,
            retrograde=retro,
            navamsha_sign=ref.SIGNS[nav_idx],
            navamsha_sign_index=nav_idx,
        )

    # Navamsha whole-sign houses (relative to navamsha lagna).
    for p in chart.planets.values():
        p.navamsha_house = _whole_sign_house(p.navamsha_sign_index, nav_lagna_idx)

    return chart


def format_dms(degree_in_sign: float) -> str:
    """Format a 0-30 degree value as D°M'S\"."""
    d = int(degree_in_sign)
    m_full = (degree_in_sign - d) * 60
    m = int(m_full)
    s = int((m_full - m) * 60)
    return f"{d:02d}\u00b0{m:02d}'{s:02d}\""
