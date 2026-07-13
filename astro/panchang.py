"""Panchang calculation engine (ऋषिकेश / Lahiri sidereal).

Computes the five limbs (Tithi, Nakshatra, Yoga, Karana, Vaara) plus
sunrise/sunset, Brahma Muhurta, Abhijit, Rahu/Gulika/Yamaganda, and
Choghadiya for any date and geographic location. Uses Swiss Ephemeris with
the same Lahiri Ayanamsha as the horoscope module.

Traditional North-Indian panchangs (including Rishikesh) take the *sunrise*
instant as the primary reference for the day's Panchang; we also compute
end-times for each limb and optional 'current' values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from . import reference as ref
from . import panchang_data as pd
from .chart_engine import _norm360

_FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL
_TITHI_ARC = 12.0
_KARANA_ARC = 6.0
_YOGA_ARC = ref.NAKSHATRA_SPAN


@dataclass
class LimbInfo:
    """One Panchang limb with Sanskrit name and end time."""
    name: str
    name_hindi: str = ""
    index: int = 0
    end_time: Optional[datetime] = None
    extra: str = ""


@dataclass
class TimeWindow:
    name: str
    start: datetime
    end: datetime
    nature: str = ""


@dataclass
class Panchang:
    place: str
    place_hindi: str
    date: date
    latitude: float
    longitude: float
    tz_offset: float
    ayanamsha: float

    sunrise: datetime
    sunset: datetime
    moonrise: Optional[datetime] = None
    moonset: Optional[datetime] = None

    vaara: LimbInfo = None
    paksha: str = ""
    tithi: LimbInfo = None
    nakshatra: LimbInfo = None
    yoga: LimbInfo = None
    karana: LimbInfo = None

    hindu_month: str = ""
    hindu_month_hindi: str = ""
    vikram_samvat: int = 0
    shaka_samvat: int = 0

    rahu_kaal: TimeWindow = None
    gulika_kaal: TimeWindow = None
    yamaganda: TimeWindow = None
    abhijit_muhurta: TimeWindow = None
    brahma_muhurta: TimeWindow = None

    day_choghadiya: List[TimeWindow] = field(default_factory=list)
    night_choghadiya: List[TimeWindow] = field(default_factory=list)

    sun_longitude: float = 0.0
    moon_longitude: float = 0.0


def _jd_to_local(jd: float, tz_offset: float) -> datetime:
    y, mo, d, h = swe.revjul(jd)
    hh = int(h)
    mm = int((h - hh) * 60)
    ss = int((((h - hh) * 60) - mm) * 60)
    ut = datetime(y, mo, d, hh, mm, ss)
    return ut + timedelta(hours=tz_offset)


def _local_to_jd(dt: datetime, tz_offset: float) -> float:
    ut = dt - timedelta(hours=tz_offset)
    return swe.julday(ut.year, ut.month, ut.day, ut.hour + ut.minute / 60.0 + ut.second / 3600.0)


def _rise_set(jd_start: float, body: int, lat: float, lon: float, alt_m: float,
              rsmi: int) -> Optional[float]:
    geo = (lon, lat, alt_m)
    try:
        res, tret = swe.rise_trans(
            jd_start, body, rsmi, geo, 1013.25, 15.0, _FLAGS,
        )
        if res >= 0:
            return tret[0]
    except Exception:
        pass
    return None


def _sun_moon_longitudes(jd_ut: float) -> Tuple[float, float]:
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    sun = swe.calc_ut(jd_ut, swe.SUN, _FLAGS)[0][0]
    moon = swe.calc_ut(jd_ut, swe.MOON, _FLAGS)[0][0]
    return _norm360(sun), _norm360(moon)


def _elongation(sun: float, moon: float) -> float:
    return (moon - sun) % 360.0


def _tithi_index(elong: float) -> int:
    return int(elong // _TITHI_ARC) + 1  # 1..30


def _tithi_name(idx: int) -> Tuple[str, str]:
    paksha = "Shukla" if idx <= 15 else "Krishna"
    pos = idx if idx <= 15 else idx - 15
    if paksha == "Krishna" and pos == 15:
        return "Amavasya", "Amavasya"
    name = pd.TITHI_NAMES[pos - 1]
    hindi = pd.TITHI_HINDI[pos - 1]
    if paksha == "Shukla" and pos == 15:
        return "Purnima", "Purnima"
    return name, hindi


def _nakshatra_index(moon: float) -> int:
    return int(moon // ref.NAKSHATRA_SPAN) % 27


def _yoga_index(sun: float, moon: float) -> int:
    return int((sun + moon) % 360.0 // _YOGA_ARC) % 27


def _karana_index(elong: float) -> int:
    return int(elong // _KARANA_ARC) % 60


def _karana_name(k: int) -> str:
    if k in pd.FIXED_KARANAS:
        return pd.FIXED_KARANAS[k]
    return pd.MOVABLE_KARANAS[(k - 1) % 7]


def _find_transition(jd_start: float, tz_offset: float, test_fn, max_hours: float = 48.0) -> Optional[datetime]:
    """Binary-search the next UTC Julian day when ``test_fn(jd)`` flips."""
    target = test_fn(jd_start)
    lo, hi = jd_start, jd_start + max_hours / 24.0
    if test_fn(hi) != target:
        for _ in range(40):
            mid = (lo + hi) / 2.0
            if test_fn(mid) != target:
                hi = mid
            else:
                lo = mid
        return _jd_to_local(hi, tz_offset)
    return None


def _hindu_month_purnimanta(sun_lon: float, tithi_idx: int) -> Tuple[str, str]:
    """Approximate Purnimanta month (North India / Rishikesh convention)."""
    sign_idx = int(sun_lon // 30) % 12
    month = pd.SUN_SIGN_TO_MONTH[sign_idx]
    # After Purnima (tithi 15) in Shukla, month advances in Purnimanta.
    if tithi_idx > 15:
        month_idx = pd.HINDU_MONTHS.index(month)
        month = pd.HINDU_MONTHS[(month_idx + 1) % 12]
    hi_idx = pd.HINDU_MONTHS.index(month)
    return month, pd.HINDU_MONTHS_HINDI[hi_idx]


def _samvat(d: date, month_name: str) -> Tuple[int, int]:
    """Vikram & Shaka Samvat (approximate civil year)."""
    # Vikram Samvat: ~57 years ahead; new year around Chaitra (Mar-Apr).
    chaitra_idx = 0
    month_idx = pd.HINDU_MONTHS.index(month_name)
    vs = d.year + 57 if month_idx >= chaitra_idx or d.month >= 3 else d.year + 56
    ss = d.year - 79 if d.month >= 3 else d.year - 80
    return vs, ss


def _segment_window(sunrise: datetime, sunset: datetime, segment: int) -> TimeWindow:
    """One 1/8th daytime segment (segment 1..8)."""
    span = (sunset - sunrise) / 8
    start = sunrise + span * (segment - 1)
    end = sunrise + span * segment
    return TimeWindow(name=f"Segment {segment}", start=start, end=end)


def _choghadiya(sunrise: datetime, sunset: datetime, weekday: int, night_end: datetime) -> Tuple[List, List]:
    day_span = (sunset - sunrise) / 8
    day_start_idx = pd.DAY_CHOGHADIYA_START[weekday]
    day = []
    for i in range(8):
        name = pd.CHOGHADIYA_NAMES[(day_start_idx + i) % 7]
        day.append(TimeWindow(
            name=name,
            start=sunrise + day_span * i,
            end=sunrise + day_span * (i + 1),
            nature=pd.CHOGHADIYA_NATURE[name],
        ))
    night_span = (night_end - sunset) / 8
    night_start_idx = pd.NIGHT_CHOGHADIYA_START[weekday]
    night = []
    for i in range(8):
        name = pd.CHOGHADIYA_NAMES[(night_start_idx + i) % 7]
        night.append(TimeWindow(
            name=name,
            start=sunset + night_span * i,
            end=sunset + night_span * (i + 1),
            nature=pd.CHOGHADIYA_NATURE[name],
        ))
    return day, night


def compute_panchang(
    d: date,
    latitude: float = pd.RISHIKESH["latitude"],
    longitude: float = pd.RISHIKESH["longitude"],
    tz_offset: float = 5.5,
    place: str = pd.RISHIKESH["name"],
    place_hindi: str = pd.RISHIKESH["name_hindi"],
    altitude_m: float = pd.RISHIKESH["altitude_m"],
    at_time: Optional[datetime] = None,
) -> Panchang:
    """Compute full Panchang for ``d`` at ``latitude/longitude``."""
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

    # Search sunrise from midnight local converted to UT.
    midnight_local = datetime(d.year, d.month, d.day, 0, 0, 0)
    jd_mid = _local_to_jd(midnight_local, tz_offset)

    jd_sunrise = _rise_set(jd_mid, swe.SUN, latitude, longitude, altitude_m,
                           swe.CALC_RISE | swe.BIT_DISC_CENTER)
    if jd_sunrise is None:
        jd_sunrise = jd_mid + 0.25
    jd_sunset = _rise_set(jd_sunrise, swe.SUN, latitude, longitude, altitude_m,
                          swe.CALC_SET | swe.BIT_DISC_CENTER)
    if jd_sunset is None:
        jd_sunset = jd_sunrise + 0.45

    sunrise = _jd_to_local(jd_sunrise, tz_offset)
    sunset = _jd_to_local(jd_sunset, tz_offset)

    jd_moonrise = _rise_set(jd_mid, swe.MOON, latitude, longitude, altitude_m,
                            swe.CALC_RISE | swe.BIT_DISC_CENTER)
    jd_moonset = _rise_set(jd_mid, swe.MOON, latitude, longitude, altitude_m,
                           swe.CALC_SET | swe.BIT_DISC_CENTER)
    moonrise = _jd_to_local(jd_moonrise, tz_offset) if jd_moonrise else None
    moonset = _jd_to_local(jd_moonset, tz_offset) if jd_moonset else None

    # Next sunrise for night choghadiya span.
    jd_next = _rise_set(jd_sunset, swe.SUN, latitude, longitude, altitude_m,
                        swe.CALC_RISE | swe.BIT_DISC_CENTER)
    next_sunrise = _jd_to_local(jd_next, tz_offset) if jd_next else sunrise + timedelta(days=1)

    # Reference instant: sunrise (traditional) or user-supplied time.
    ref_jd = jd_sunrise if at_time is None else _local_to_jd(at_time, tz_offset)
    sun_lon, moon_lon = _sun_moon_longitudes(ref_jd)
    elong = _elongation(sun_lon, moon_lon)

    t_idx = _tithi_index(elong)
    t_name, t_hindi = _tithi_name(t_idx)
    paksha = "Shukla Paksha" if t_idx <= 15 else "Krishna Paksha"
    n_idx = _nakshatra_index(moon_lon)
    y_idx = _yoga_index(sun_lon, moon_lon)
    k_idx = _karana_index(elong)

    weekday = d.weekday()
    # Python weekday: Mon=0; Panchang uses Sun=0.
    vaara_idx = (weekday + 1) % 7

    # End times (transition search from reference jd).
    def tithi_at(jd):
        s, m = _sun_moon_longitudes(jd)
        return _tithi_index(_elongation(s, m))

    def nak_at(jd):
        _, m = _sun_moon_longitudes(jd)
        return _nakshatra_index(m)

    def yoga_at(jd):
        s, m = _sun_moon_longitudes(jd)
        return _yoga_index(s, m)

    def kar_at(jd):
        s, m = _sun_moon_longitudes(jd)
        return _karana_index(_elongation(s, m))

    t_end = _find_transition(ref_jd, tz_offset, tithi_at)
    n_end = _find_transition(ref_jd, tz_offset, nak_at)
    y_end = _find_transition(ref_jd, tz_offset, yoga_at)
    k_end = _find_transition(ref_jd, tz_offset, kar_at)

    hindu_month, hindu_month_hi = _hindu_month_purnimanta(sun_lon, t_idx)
    vs, ss = _samvat(d, hindu_month)

    # Inauspicious daytime segments.
    rahu_seg = pd.RAHU_KAAL_SEGMENT[vaara_idx]
    gulika_seg = pd.GULIKA_KAAL_SEGMENT[vaara_idx]
    yama_seg = pd.YAMAGANDA_SEGMENT[vaara_idx]
    rahu = _segment_window(sunrise, sunset, rahu_seg)
    rahu.name = "Rahu Kaal"
    gulika = _segment_window(sunrise, sunset, gulika_seg)
    gulika.name = "Gulika Kaal"
    yama = _segment_window(sunrise, sunset, yama_seg)
    yama.name = "Yamaganda"

    # Abhijit: 24 min centred on local solar noon (midpoint sunrise-sunset).
    noon = sunrise + (sunset - sunrise) / 2
    abhijit = TimeWindow("Abhijit Muhurta", noon - timedelta(minutes=24), noon + timedelta(minutes=24),
                         nature="Auspicious")

    # Brahma Muhurta: 96 min before sunrise, 48 min window.
    brahma = TimeWindow(
        "Brahma Muhurta",
        sunrise - timedelta(minutes=96),
        sunrise - timedelta(minutes=48),
        nature="Highly auspicious",
    )

    day_cho, night_cho = _choghadiya(sunrise, sunset, vaara_idx, next_sunrise)

    ayan = swe.get_ayanamsa_ut(ref_jd)

    return Panchang(
        place=place,
        place_hindi=place_hindi,
        date=d,
        latitude=latitude,
        longitude=longitude,
        tz_offset=tz_offset,
        ayanamsha=ayan,
        sunrise=sunrise,
        sunset=sunset,
        moonrise=moonrise,
        moonset=moonset,
        vaara=LimbInfo(pd.VAARA_SANSKRIT[vaara_idx], pd.VAARA_HINDI[vaara_idx], vaara_idx),
        paksha=paksha,
        tithi=LimbInfo(t_name, t_hindi, t_idx, t_end, paksha),
        nakshatra=LimbInfo(
            ref.NAKSHATRAS[n_idx], ref.NAKSHATRAS[n_idx], n_idx, n_end,
            f"Lord: {ref.NAKSHATRA_LORD[ref.NAKSHATRAS[n_idx]]}",
        ),
        yoga=LimbInfo(pd.YOGAS[y_idx], pd.YOGAS[y_idx], y_idx, y_end),
        karana=LimbInfo(_karana_name(k_idx), _karana_name(k_idx), k_idx, k_end),
        hindu_month=hindu_month,
        hindu_month_hindi=hindu_month_hi,
        vikram_samvat=vs,
        shaka_samvat=ss,
        rahu_kaal=rahu,
        gulika_kaal=gulika,
        yamaganda=yama,
        abhijit_muhurta=abhijit,
        brahma_muhurta=brahma,
        day_choghadiya=day_cho,
        night_choghadiya=night_cho,
        sun_longitude=sun_lon,
        moon_longitude=moon_lon,
    )


def format_time(dt: Optional[datetime]) -> str:
    if dt is None:
        return "\u2014"
    return dt.strftime("%I:%M %p").lstrip("0")


def panchang_to_dict(p: Panchang) -> Dict:
    """Serialisable summary for reports / export."""
    def limb(l: LimbInfo) -> Dict:
        return {
            "name": l.name, "hindi": l.name_hindi, "index": l.index,
            "ends": format_time(l.end_time), "extra": l.extra,
        }

    def win(w: TimeWindow) -> Dict:
        return {
            "name": w.name, "start": format_time(w.start),
            "end": format_time(w.end), "nature": w.nature,
        }

    return {
        "place": p.place,
        "place_hindi": p.place_hindi,
        "date": p.date.isoformat(),
        "sunrise": format_time(p.sunrise),
        "sunset": format_time(p.sunset),
        "moonrise": format_time(p.moonrise),
        "moonset": format_time(p.moonset),
        "vaara": limb(p.vaara),
        "paksha": p.paksha,
        "tithi": limb(p.tithi),
        "nakshatra": limb(p.nakshatra),
        "yoga": limb(p.yoga),
        "karana": limb(p.karana),
        "hindu_month": p.hindu_month,
        "vikram_samvat": p.vikram_samvat,
        "shaka_samvat": p.shaka_samvat,
        "rahu_kaal": win(p.rahu_kaal),
        "gulika_kaal": win(p.gulika_kaal),
        "yamaganda": win(p.yamaganda),
        "abhijit": win(p.abhijit_muhurta),
        "brahma_muhurta": win(p.brahma_muhurta),
        "day_choghadiya": [win(w) for w in p.day_choghadiya],
        "night_choghadiya": [win(w) for w in p.night_choghadiya],
    }
