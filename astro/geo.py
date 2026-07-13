"""Lightweight, offline geo & timezone helpers.

To avoid a network dependency for something this core, we ship a small
built-in city table (lat, lon, IANA timezone). Users can always override
with manual latitude/longitude/UTC-offset entry in the UI.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

import pytz

# name -> (latitude, longitude, IANA timezone)
CITIES: Dict[str, tuple] = {
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
    "Rishikesh, India": (30.0869, 78.2676, "Asia/Kolkata"),
    "Haridwar, India": (29.9457, 78.1642, "Asia/Kolkata"),
    "Kathmandu, Nepal": (27.7172, 85.3240, "Asia/Kathmandu"),
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


def tz_offset_hours(tz_name: str, dt: datetime) -> float:
    """UTC offset (hours, east-positive) for ``tz_name`` on date ``dt``.

    Uses pytz so historical/DST rules are honoured for the birth date.
    """
    tz = pytz.timezone(tz_name)
    localized = tz.localize(dt, is_dst=None) if dt else tz.localize(datetime.now())
    return localized.utcoffset().total_seconds() / 3600.0


def lookup(city: str) -> Optional[tuple]:
    return CITIES.get(city)
