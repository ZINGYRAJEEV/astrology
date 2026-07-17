"""Festival & Vrat calendar — derived from the tithi / month engine.

Reliable recurring observances (Ekadashi, Pradosh, Chaturthi, Purnima,
Amavasya, Sankranti) are computed directly from each day's Panchang. Major
festivals are matched by (Purnimanta month + paksha + tithi) rules following
the North-Indian / Rishikesh convention.

Note: festival dates depend on the Purnimanta month boundary (approximate in
this engine); recurring vrats are exact to the tithi. Always confirm exact
festival timings with a local Panchang.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from typing import Dict, List, Optional

from .panchang import compute_panchang
from . import panchang_data as pd
from . import reference as ref

# Major festivals: (name, Purnimanta month, paksha, tithi-in-paksha, note).
# paksha is "Shukla"/"Krishna"; use tithi_name for Purnima/Amavasya.
FESTIVAL_RULES: List[Dict] = [
    {"name": "Makar Sankranti", "sankranti": "Capricorn",
     "note": "Sun enters Capricorn — harvest festival, holy bathing."},
    {"name": "Vasant Panchami", "month": "Magha", "paksha": "Shukla", "tithi": 5,
     "note": "Saraswati Puja; onset of spring."},
    {"name": "Maha Shivaratri", "month": "Phalguna", "paksha": "Krishna", "tithi": 14,
     "note": "Great night of Shiva; fasting and vigil."},
    {"name": "Holika Dahan", "month": "Phalguna", "tithi_name": "Purnima",
     "note": "Bonfire on Phalguna Purnima."},
    {"name": "Holi (Dhulandi)", "month": "Chaitra", "paksha": "Krishna", "tithi": 1,
     "note": "Festival of colours."},
    {"name": "Gudi Padwa / Ugadi", "month": "Chaitra", "paksha": "Shukla", "tithi": 1,
     "note": "Lunar new year (many regions)."},
    {"name": "Ram Navami", "month": "Chaitra", "paksha": "Shukla", "tithi": 9,
     "note": "Birth of Lord Rama."},
    {"name": "Hanuman Jayanti", "month": "Chaitra", "tithi_name": "Purnima",
     "note": "Birth of Hanuman."},
    {"name": "Akshaya Tritiya", "month": "Vaishakha", "paksha": "Shukla", "tithi": 3,
     "note": "Highly auspicious for new beginnings & purchases."},
    {"name": "Guru Purnima", "month": "Ashadha", "tithi_name": "Purnima",
     "note": "Honouring the guru."},
    {"name": "Raksha Bandhan", "month": "Shravana", "tithi_name": "Purnima",
     "note": "Bond between siblings."},
    {"name": "Krishna Janmashtami", "month": "Bhadrapada", "paksha": "Krishna", "tithi": 8,
     "note": "Birth of Lord Krishna."},
    {"name": "Ganesh Chaturthi", "month": "Bhadrapada", "paksha": "Shukla", "tithi": 4,
     "note": "Birth of Ganesha."},
    {"name": "Navratri begins", "month": "Ashwin", "paksha": "Shukla", "tithi": 1,
     "note": "Nine nights of the Goddess."},
    {"name": "Durga Ashtami", "month": "Ashwin", "paksha": "Shukla", "tithi": 8,
     "note": "Maha Ashtami of Navratri."},
    {"name": "Vijayadashami (Dussehra)", "month": "Ashwin", "paksha": "Shukla", "tithi": 10,
     "note": "Victory of good over evil."},
    {"name": "Sharad Purnima", "month": "Ashwin", "tithi_name": "Purnima",
     "note": "Kojagari Purnima."},
    {"name": "Karva Chauth", "month": "Kartik", "paksha": "Krishna", "tithi": 4,
     "note": "Fast for spouse's long life."},
    {"name": "Dhanteras", "month": "Kartik", "paksha": "Krishna", "tithi": 13,
     "note": "Start of Diwali; buying metals."},
    {"name": "Diwali (Lakshmi Puja)", "month": "Kartik", "tithi_name": "Amavasya",
     "note": "Festival of lights."},
    {"name": "Govardhan Puja", "month": "Kartik", "paksha": "Shukla", "tithi": 1,
     "note": "Annakut."},
    {"name": "Bhai Dooj", "month": "Kartik", "paksha": "Shukla", "tithi": 2,
     "note": "Sisters honour brothers."},
    {"name": "Chhath Puja", "month": "Kartik", "paksha": "Shukla", "tithi": 6,
     "note": "Worship of the Sun god."},
    {"name": "Dev Uthani Ekadashi", "month": "Kartik", "paksha": "Shukla", "tithi": 11,
     "note": "Vishnu awakens; marriage season begins."},
]

_PAKSHA_SHORT = {"Shukla Paksha": "Shukla", "Krishna Paksha": "Krishna"}


def _tithi_num(idx: int) -> int:
    return idx if idx <= 15 else idx - 15


def _recurring(panch) -> List[Dict]:
    """Month-agnostic vrats from the day's tithi."""
    out: List[Dict] = []
    num = _tithi_num(panch.tithi.index)
    paksha = _PAKSHA_SHORT.get(panch.paksha, "")
    name = panch.tithi.name
    if num == 11:
        out.append({"name": f"Ekadashi ({paksha})", "type": "vrat",
                    "note": "Vishnu fast; abstain from grains."})
    if num == 13:
        out.append({"name": f"Pradosh Vrat ({paksha})", "type": "vrat",
                    "note": "Evening Shiva worship."})
    if num == 4:
        if paksha == "Krishna":
            out.append({"name": "Sankashti Chaturthi", "type": "vrat",
                        "note": "Ganesha fast until moonrise."})
        else:
            out.append({"name": "Vinayaka Chaturthi", "type": "vrat",
                        "note": "Ganesha worship."})
    if name == "Purnima":
        out.append({"name": "Purnima (full moon)", "type": "vrat",
                    "note": "Full-moon fast & worship."})
    if name == "Amavasya":
        out.append({"name": "Amavasya (new moon)", "type": "vrat",
                    "note": "Ancestral offerings (Tarpan)."})
    return out


def _match_festivals(panch, month_name: str) -> List[Dict]:
    out: List[Dict] = []
    num = _tithi_num(panch.tithi.index)
    paksha = _PAKSHA_SHORT.get(panch.paksha, "")
    for rule in FESTIVAL_RULES:
        if "sankranti" in rule:
            continue
        if rule.get("month") != month_name:
            continue
        if "tithi_name" in rule:
            if panch.tithi.name == rule["tithi_name"]:
                out.append({"name": rule["name"], "type": "festival", "note": rule["note"]})
        elif rule.get("paksha") == paksha and rule.get("tithi") == num:
            out.append({"name": rule["name"], "type": "festival", "note": rule["note"]})
    return out


def compute_festivals(
    year: int,
    month: int,
    latitude: float = pd.RISHIKESH["latitude"],
    longitude: float = pd.RISHIKESH["longitude"],
    tz_offset: float = 5.5,
    place: str = pd.RISHIKESH["name"],
) -> List[Dict]:
    """All festivals & vrats in the given civil ``month`` of ``year``."""
    days_in_month = monthrange(year, month)[1]
    events: List[Dict] = []
    prev_sun_sign: Optional[int] = None

    # Seed previous day's sun sign for Sankranti detection.
    try:
        prev_day = date(year, month, 1) - timedelta(days=1)
        pp = compute_panchang(prev_day, latitude=latitude, longitude=longitude,
                              tz_offset=tz_offset, place=place, place_hindi="", altitude_m=0.0)
        prev_sun_sign = int(pp.sun_longitude // 30) % 12
    except Exception:
        prev_sun_sign = None

    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        panch = compute_panchang(d, latitude=latitude, longitude=longitude,
                                 tz_offset=tz_offset, place=place, place_hindi="",
                                 altitude_m=0.0)
        sun_sign = int(panch.sun_longitude // 30) % 12
        day_events: List[Dict] = []

        # Sankranti — sun ingress into a new sign vs previous day.
        if prev_sun_sign is not None and sun_sign != prev_sun_sign:
            sign = ref.SIGNS[sun_sign]
            special = "Makar Sankranti" if sign == "Capricorn" else f"{sign} Sankranti"
            note = ("Sun enters Capricorn — harvest festival."
                    if sign == "Capricorn" else f"Sun enters {sign}.")
            day_events.append({"name": special, "type": "sankranti", "note": note})
        prev_sun_sign = sun_sign

        day_events += _match_festivals(panch, panch.hindu_month)
        day_events += _recurring(panch)

        for e in day_events:
            events.append({
                "date": d,
                "name": e["name"],
                "type": e["type"],
                "note": e["note"],
                "tithi": f"{panch.tithi.name} ({panch.paksha})",
                "nakshatra": panch.nakshatra.name,
                "hindu_month": panch.hindu_month,
            })
    return events


def festivals_markdown(events: List[Dict], year: int, month: int) -> str:
    import calendar
    lines = [f"# Festivals & Vrats — {calendar.month_name[month]} {year}", ""]
    if not events:
        lines.append("_No observances detected in this month._")
    cur = None
    for e in events:
        if e["date"] != cur:
            cur = e["date"]
            lines.append(f"\n### {e['date'].strftime('%a %d %b %Y')}")
        tag = {"festival": "Festival", "vrat": "Vrat", "sankranti": "Sankranti"}[e["type"]]
        lines.append(f"- **{e['name']}** ({tag}) — {e['note']}")
    lines.append("\n> Recurring vrats are exact to the tithi; festival dates are "
                 "approximate to the Purnimanta month — confirm with a local Panchang.")
    return "\n".join(lines)
