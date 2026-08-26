"""Lightweight, offline geo & timezone helpers.

Place names map to latitude, longitude and IANA timezone internally. The UI
offers a city picker or manual latitude/longitude/IST-offset entry
(India Standard Time = 5.5 hours east of UTC by default).
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, NamedTuple, Optional

import pytz

# Place name -> (latitude, longitude, IANA timezone)
CITIES: Dict[str, tuple] = {
    "Rishikesh, India": (30.0869, 78.2676, "Asia/Kolkata"),
    "Haridwar, India": (29.9457, 78.1642, "Asia/Kolkata"),
    "Dehradun, India": (30.3165, 78.0322, "Asia/Kolkata"),
    "New Delhi, India": (28.6139, 77.2090, "Asia/Kolkata"),
    "Mumbai, India": (19.0760, 72.8777, "Asia/Kolkata"),
    "Kolkata, India": (22.5726, 88.3639, "Asia/Kolkata"),
    "Chennai, India": (13.0827, 80.2707, "Asia/Kolkata"),
    "Bengaluru, India": (12.9716, 77.5946, "Asia/Kolkata"),
    "Hyderabad, India": (17.3850, 78.4867, "Asia/Kolkata"),
    "Pune, India": (18.5204, 73.8567, "Asia/Kolkata"),
    "Ahmedabad, India": (23.0225, 72.5714, "Asia/Kolkata"),
    "Jaipur, India": (26.9124, 75.7873, "Asia/Kolkata"),
    "Varanasi, India": (25.3176, 82.9739, "Asia/Kolkata"),
    "Lucknow, India": (26.8467, 80.9462, "Asia/Kolkata"),
    "Patna, India": (25.5941, 85.1376, "Asia/Kolkata"),
    "Giridih, Jharkhand, India": (24.1847, 86.3022, "Asia/Kolkata"),
    "Ramgarh, Jharkhand, India": (23.6333, 85.5667, "Asia/Kolkata"),
    "Jamshedpur, India": (22.8056, 86.2031, "Asia/Kolkata"),
    "Chandigarh, India": (30.7333, 76.7794, "Asia/Kolkata"),
    "Amritsar, India": (31.6340, 74.8723, "Asia/Kolkata"),
    "Srinagar, India": (34.0837, 74.7973, "Asia/Kolkata"),
    "Guwahati, India": (26.1445, 91.7362, "Asia/Kolkata"),
    "Bhopal, India": (23.2599, 77.4126, "Asia/Kolkata"),
    "Indore, India": (22.7196, 75.8577, "Asia/Kolkata"),
    "Nagpur, India": (21.1458, 79.0882, "Asia/Kolkata"),
    "Kathmandu, Nepal": (27.7172, 85.3240, "Asia/Kathmandu"),
    "Almere, Netherlands": (52.3714, 5.2212, "Europe/Amsterdam"),
    "London, UK": (51.5074, -0.1278, "Europe/London"),
    "New York, USA": (40.7128, -74.0060, "America/New_York"),
    "Los Angeles, USA": (34.0522, -118.2437, "America/Los_Angeles"),
    "Chicago, USA": (41.8781, -87.6298, "America/Chicago"),
    "Toronto, Canada": (43.6532, -79.3832, "America/Toronto"),
    "Dubai, UAE": (25.2048, 55.2708, "Asia/Dubai"),
    "Singapore": (1.3521, 103.8198, "Asia/Singapore"),
    "Sydney, Australia": (-33.8688, 151.2093, "Australia/Sydney"),
    "Tokyo, Japan": (35.6762, 139.6503, "Asia/Tokyo"),
}

# Sorted list for dropdowns (Rishikesh first as default panchang city).
PLACE_NAMES = list(CITIES.keys())


class PlaceInfo(NamedTuple):
    name: str
    latitude: float
    longitude: float
    timezone: str


def resolve_place(place_name: str) -> PlaceInfo:
    """Look up coordinates and timezone for a place name."""
    if place_name not in CITIES:
        raise KeyError(f"Unknown place: {place_name}")
    lat, lon, tz = CITIES[place_name]
    return PlaceInfo(name=place_name, latitude=lat, longitude=lon, timezone=tz)


def tz_offset_hours(tz_name: str, dt: datetime) -> float:
    """UTC offset (hours, east-positive) for ``tz_name`` on date ``dt``."""
    tz = pytz.timezone(tz_name)
    localized = tz.localize(dt, is_dst=None) if dt else tz.localize(datetime.now())
    return localized.utcoffset().total_seconds() / 3600.0


# India Standard Time — default for this app's audience.
IST_OFFSET_HOURS = 5.5
IST_LABEL = "IST (India Standard Time)"
# Streamlit label for the manual offset field (still stores hours east of UTC).
TZ_INPUT_LABEL = "Time zone — IST hours from UTC"
TZ_INPUT_HELP = (
    "India Standard Time (IST) is **5.5**. "
    "Change only if the birth/place is outside India."
)
BIRTH_TZ_INPUT_LABEL = "Birth time zone — IST hours from UTC"


def format_tz_label(offset_hours: float, *, timezone_name: str = "") -> str:
    """Friendly timezone label: IST for India, else UTC±h."""
    if abs(offset_hours - IST_OFFSET_HOURS) < 0.01 or timezone_name == "Asia/Kolkata":
        return "IST (UTC+5:30)"
    return f"UTC{offset_hours:+.2f}"


def format_place_tz_caption(place_label: str, timezone_name: str, offset_hours: float) -> str:
    """Caption under city picker: 'Rishikesh · IST (UTC+5:30)'."""
    return f"{place_label} · {format_tz_label(offset_hours, timezone_name=timezone_name)}"


def lookup(city: str) -> Optional[tuple]:
    return CITIES.get(city)
