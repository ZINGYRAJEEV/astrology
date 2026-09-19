"""Tests for nearest-city / GPS place helpers."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro import geo


def test_nearest_city_delhi():
    # Near India Gate
    p = geo.nearest_city(28.6129, 77.2295)
    assert p.name == "New Delhi, India"
    assert p.timezone == "Asia/Kolkata"


def test_nearest_city_amsterdam_area():
    p = geo.nearest_city(52.37, 5.22)
    assert "Almere" in p.name or "Amsterdam" in p.timezone or p.timezone == "Europe/Amsterdam"


def test_place_from_coordinates_keeps_gps():
    info = geo.place_from_coordinates(28.61, 77.21)
    assert abs(info.latitude - 28.61) < 1e-6
    assert abs(info.longitude - 77.21) < 1e-6
    assert info.timezone == "Asia/Kolkata"
    assert "Near" in info.name or "Delhi" in info.name


if __name__ == "__main__":
    test_nearest_city_delhi()
    test_nearest_city_amsterdam_area()
    test_place_from_coordinates_keeps_gps()
    print("geo location tests OK")
