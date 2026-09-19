"""Shared Streamlit location picker — city, GPS, or manual lat/long."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components

from . import geo


def _ingest_geo_query(key_prefix: str) -> None:
    """Pull browser geolocation from URL query params into session state."""
    try:
        qp = st.query_params
    except Exception:
        return
    if qp.get("geo_key") != key_prefix:
        return
    if "geo_lat" not in qp or "geo_lon" not in qp:
        return
    try:
        lat = float(qp["geo_lat"])
        lon = float(qp["geo_lon"])
    except (TypeError, ValueError):
        return
    near = geo.nearest_city(lat, lon)
    st.session_state[f"{key_prefix}_geo_lat"] = lat
    st.session_state[f"{key_prefix}_geo_lon"] = lon
    st.session_state[f"{key_prefix}_geo_near"] = near.name
    st.session_state[f"{key_prefix}_geo_tz"] = near.timezone
    # Clear params so refresh does not loop.
    try:
        del st.query_params["geo_lat"]
        del st.query_params["geo_lon"]
        del st.query_params["geo_key"]
    except Exception:
        pass


def _geolocation_button(key_prefix: str) -> None:
    """HTML5 geolocation → reloads parent with geo_* query params."""
    components.html(
        f"""
        <div style="font-family:system-ui,sans-serif;margin:0;padding:0;">
          <button id="geoBtn" style="
            background:rgba(245,197,66,0.18);color:#ffe9a8;border:1px solid rgba(245,197,66,0.45);
            border-radius:10px;padding:8px 14px;cursor:pointer;font-size:13px;font-weight:600;">
            Detect my location
          </button>
          <span id="geoMsg" style="color:#9aa3b8;font-size:12px;margin-left:10px;"></span>
        </div>
        <script>
        const btn = document.getElementById('geoBtn');
        const msg = document.getElementById('geoMsg');
        btn.addEventListener('click', () => {{
          msg.textContent = 'Requesting permission…';
          if (!navigator.geolocation) {{
            msg.textContent = 'Geolocation not supported in this browser.';
            return;
          }}
          navigator.geolocation.getCurrentPosition(
            (pos) => {{
              msg.textContent = 'Located — updating…';
              const url = new URL(window.parent.location.href);
              url.searchParams.set('geo_lat', String(pos.coords.latitude));
              url.searchParams.set('geo_lon', String(pos.coords.longitude));
              url.searchParams.set('geo_key', '{key_prefix}');
              window.parent.location.href = url.toString();
            }},
            (err) => {{
              msg.textContent = err && err.message ? err.message : 'Location denied or unavailable.';
            }},
            {{ enableHighAccuracy: true, timeout: 20000, maximumAge: 60000 }}
          );
        }});
        </script>
        """,
        height=46,
    )


def render_location_picker(
    key_prefix: str,
    *,
    place_label: str = "Birth place",
    mode_label: str = "Location",
    default_city: str = "Rishikesh, India",
    at_dt: Optional[datetime] = None,
) -> Tuple[float, float, str, Optional[str], Optional[float]]:
    """Render city / current GPS / manual location controls.

    Returns ``(lat, lon, place_label, tz_name, tz_manual)``.
    Exactly one of ``tz_name`` or ``tz_manual`` is set.
    Birth *clock* time is unchanged — only coordinates and timezone update.
    """
    _ingest_geo_query(key_prefix)
    at_dt = at_dt or datetime.now()

    mode = st.radio(
        mode_label,
        ["Pick a city", "Use current location", "Manual lat/long"],
        horizontal=True,
        key=f"{key_prefix}_place_mode",
    )

    if mode == "Pick a city":
        idx = (
            geo.PLACE_NAMES.index(default_city)
            if default_city in geo.PLACE_NAMES else 0
        )
        city = st.selectbox(place_label, geo.PLACE_NAMES, index=idx, key=f"{key_prefix}_city")
        info = geo.resolve_place(city)
        try:
            off = geo.tz_offset_hours(info.timezone, at_dt)
        except Exception:
            off = geo.tz_offset_hours(info.timezone, datetime.now())
        st.caption(geo.format_place_tz_caption(info.name, info.timezone, off))
        return info.latitude, info.longitude, info.name, info.timezone, None

    if mode == "Use current location":
        st.caption(
            "Allow location when the browser asks. We set coordinates and timezone; "
            "your birth clock time stays as you entered it."
        )
        _geolocation_button(key_prefix)
        lat = st.session_state.get(f"{key_prefix}_geo_lat")
        lon = st.session_state.get(f"{key_prefix}_geo_lon")
        if lat is None or lon is None:
            st.info("Click **Detect my location**, then allow access in the browser.")
            # Safe fallback so the form still works before GPS returns.
            info = geo.resolve_place(
                default_city if default_city in geo.PLACE_NAMES else geo.PLACE_NAMES[0]
            )
            st.caption(f"Waiting for GPS — temporary fallback: {info.name}")
            return info.latitude, info.longitude, info.name, info.timezone, None

        near_name = st.session_state.get(f"{key_prefix}_geo_near") or geo.nearest_city(lat, lon).name
        tz_name = st.session_state.get(f"{key_prefix}_geo_tz") or geo.nearest_city(lat, lon).timezone
        label = f"Current location near {near_name}"
        try:
            off = geo.tz_offset_hours(tz_name, at_dt)
        except Exception:
            off = geo.tz_offset_hours(tz_name, datetime.now())
        st.success(
            f"{label} · {lat:.4f}, {lon:.4f} · "
            f"{geo.format_tz_label(off, timezone_name=tz_name)}"
        )
        if st.button("Clear detected location", key=f"{key_prefix}_geo_clear"):
            for k in ("geo_lat", "geo_lon", "geo_near", "geo_tz"):
                st.session_state.pop(f"{key_prefix}_{k}", None)
            st.rerun()
        return float(lat), float(lon), label, tz_name, None

    # Manual
    lat = st.number_input("Latitude", value=30.0869, format="%.4f", key=f"{key_prefix}_lat")
    lon = st.number_input("Longitude", value=78.2676, format="%.4f", key=f"{key_prefix}_lon")
    tz_manual = st.number_input(
        geo.TZ_INPUT_LABEL,
        value=geo.IST_OFFSET_HOURS,
        step=0.25,
        format="%.2f",
        key=f"{key_prefix}_tz",
        help=geo.TZ_INPUT_HELP,
    )
    label = f"{lat:.3f},{lon:.3f}"
    st.caption(geo.format_tz_label(tz_manual))
    return float(lat), float(lon), label, None, float(tz_manual)
