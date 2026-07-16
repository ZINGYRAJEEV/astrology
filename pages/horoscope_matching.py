"""Horoscope Matching — Ashtakoota Gun Milan (Rishikesh Panchang)."""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro.chart_engine import BirthData
from astro.matching import match_from_birth, matching_markdown

st.set_page_config(page_title="Horoscope Matching", page_icon="\U0001f491", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg,#070912,#0c1020); color:#e8ebf2; }
      h1,h2,h3 { color:#f5c542 !important; font-family:'Georgia',serif; }
      .pcard { background:rgba(28,33,54,0.55); border:1px solid rgba(245,197,66,0.14);
               border-radius:16px; padding:16px 20px; margin-bottom:10px; }
      .pred-title { font-size:20px; color:#ffe9a8; font-weight:700; }
      .chip-ok { background:#6fcf97;color:#0b0e1a;padding:2px 10px;border-radius:999px;font-size:12px; }
      .chip-mix { background:#f2c94c;color:#0b0e1a;padding:2px 10px;border-radius:999px;font-size:12px; }
      .chip-bad { background:#ef6b6b;color:#0b0e1a;padding:2px 10px;border-radius:999px;font-size:12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# \U0001f491 Horoscope Matching")
st.caption(
    "Ashtakoota Gun Milan (36 points) \u00b7 Avakhada Chakra \u00b7 "
    "Hrishikesh Panchang birth checks \u00b7 Lahiri sidereal"
)


def _place_inputs(prefix: str, default_city: str = "Rishikesh, India"):
    place_mode = st.radio(
        "Location", ["Pick a city", "Manual lat/long"], horizontal=True,
        key=f"{prefix}_place_mode",
    )
    if place_mode == "Pick a city":
        idx = geo.PLACE_NAMES.index(default_city) if default_city in geo.PLACE_NAMES else 0
        city = st.selectbox("Birth place", geo.PLACE_NAMES, index=idx, key=f"{prefix}_city")
        info = geo.resolve_place(city)
        return info.latitude, info.longitude, info.name, info.timezone, None
    lat = st.number_input("Latitude", value=30.0869, format="%.4f", key=f"{prefix}_lat")
    lon = st.number_input("Longitude", value=78.2676, format="%.4f", key=f"{prefix}_lon")
    tz_manual = st.number_input(
        "UTC offset (hours)", value=5.5, step=0.25, format="%.2f", key=f"{prefix}_tz",
    )
    label = f"{lat:.3f},{lon:.3f}"
    return lat, lon, label, None, tz_manual


def _birth_panel(title: str, prefix: str):
    st.markdown(f"### {title}")
    name = st.text_input("Name", key=f"{prefix}_name", placeholder=title)
    c1, c2 = st.columns(2)
    with c1:
        b_date = st.date_input(
            "Date of birth",
            value=date(1990, 1, 1),
            min_value=date(1800, 1, 1),
            max_value=date.today(),
            key=f"{prefix}_date",
        )
    with c2:
        b_time = st.time_input("Time of birth", value=time(12, 0), step=60, key=f"{prefix}_time")
    lat, lon, place, tz_name, tz_manual = _place_inputs(prefix)
    return name, b_date, b_time, lat, lon, place, tz_name, tz_manual


g_col, b_col = st.columns(2)
with g_col:
    g = _birth_panel("Groom (Var)", "groom")
with b_col:
    b = _birth_panel("Bride (Kanya)", "bride")

if st.button("Match Horoscopes", type="primary", use_container_width=True):
    g_name, g_date, g_time, g_lat, g_lon, g_place, g_tz_name, g_tz_manual = g
    b_name, b_date, b_time, b_lat, b_lon, b_place, b_tz_name, b_tz_manual = b
    g_tz = (
        geo.tz_offset_hours(g_tz_name, datetime.combine(g_date, g_time))
        if g_tz_name else g_tz_manual
    )
    b_tz = (
        geo.tz_offset_hours(b_tz_name, datetime.combine(b_date, b_time))
        if b_tz_name else b_tz_manual
    )
    groom = BirthData(
        name=g_name or "Groom", year=g_date.year, month=g_date.month, day=g_date.day,
        hour=g_time.hour, minute=g_time.minute,
        latitude=g_lat, longitude=g_lon, tz_offset=g_tz, place=g_place,
    )
    bride = BirthData(
        name=b_name or "Bride", year=b_date.year, month=b_date.month, day=b_date.day,
        hour=b_time.hour, minute=b_time.minute,
        latitude=b_lat, longitude=b_lon, tz_offset=b_tz, place=b_place,
    )
    st.session_state["match"] = match_from_birth(groom, bride)

if "match" not in st.session_state:
    st.info("Enter groom and bride birth details, then click **Match Horoscopes**.")
    st.markdown(
        """
        ### Ashtakoota (36 Gun)
        1. **Varna** (1) — mental / professional aptitude  
        2. **Vashya** (2) — mutual attraction  
        3. **Tara** (3) — star strength (Tarabala — Rishikesh priority)  
        4. **Yoni** (4) — primal temperament  
        5. **Graha Maitri** (5) — Moon-lord friendship  
        6. **Gana** (6) — spiritual temperament  
        7. **Bhakoot** (7) — family / prosperity  
        8. **Nadi** (8) — health & offspring (**critical Rishikesh filter**)

        Classical minimum **18/36**; **Nadi Dosha** (same Nadi) requires remedies even if total is high.
        """
    )
    st.stop()

m = st.session_state["match"]
chip = {"Excellent": "chip-ok", "Very Good": "chip-ok", "Good": "chip-mix",
        "Average": "chip-mix", "Low": "chip-bad"}[m["verdict"]]

st.markdown(
    f"""
    <div class="pcard">
      <span class="{chip}">{m['total_points']}/36 — {m['verdict']} ({m['percent']}%)</span>
      <div class="pred-title" style="margin-top:8px">{m['groom_name']} & {m['bride_name']}</div>
      <div style="margin-top:6px;color:#9aa3b8">{m['verdict_detail']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

g_col, b_col = st.columns(2)
for col, person, label in [(g_col, m["groom"], "Groom"), (b_col, m["bride"], "Bride")]:
    av = person["avakhada"]
    mang = "Manglik" if person["manglik"] else "Non-Manglik"
    col.markdown(
        f"""
        <div class="pcard">
          <div class="pred-title">{label}</div>
          <div style="margin-top:6px">
            Lagna <b>{person['lagna']}</b> · Moon <b>{person['moon_sign']}</b><br>
            {person['nakshatra']} (pada {person['pada']}) · {mang}<br>
            Varna {av['varna']} · Gana {av['gana']} · Nadi {av['nadi']} · Yoni {av['yoni']}<br>
            Navaratna birth quality: {person['navaratna']}%
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Ashtakoota breakdown")
for k in m["kootas"]:
    chip_class = "chip-ok" if k["ok"] else "chip-bad" if k["points"] == 0 else "chip-mix"
    st.markdown(
        f"""
        <div class="pcard">
          <span class="{chip_class}">{k['name']} — {k['points']}/{k['max']}</span>
          <div style="margin-top:6px">{k['note']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Birth Panchang at marriage age reference")
pg, pb = m["panchang"]["groom"], m["panchang"]["bride"]
c1, c2 = st.columns(2)
c1.markdown(f"**Groom:** {pg['vaara']}, {pg['tithi']}, Yoga {pg['yoga']}, Karana {pg['karana']}")
c2.markdown(f"**Bride:** {pb['vaara']}, {pb['tithi']}, Yoga {pb['yoga']}, Karana {pb['karana']}")

if m["doshas"]:
    st.markdown("### Doshas & Rishikesh cautions")
    for d in m["doshas"]:
        st.warning(d)

if m["recommendations"]:
    st.markdown("### Recommendations")
    for r in m["recommendations"]:
        st.markdown(f"- {r}")

st.download_button(
    "Download matching report (Markdown)",
    matching_markdown(m),
    file_name=f"matching_{m['groom_name']}_{m['bride_name']}.md".replace(" ", "_"),
    mime="text/markdown",
    use_container_width=True,
)

st.caption(
    "Ashtakoota Milan per North-Indian / Shri Kashi Vishwanath Hrishikesh Panchang Avakhada. "
    "Nadi, Tarabala and birth Panchang limbs follow the same Rishikesh rules as Life Prediction."
)
