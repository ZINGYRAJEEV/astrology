"""ऋषिकेश पंचांग — daily Hindu almanac (separate feature).

Calculates Tithi, Nakshatra, Yoga, Karana, Vaara, sunrise/sunset,
inauspicious periods (Rahu Kaal, Gulika, Yamaganda), Brahma & Abhijit
Muhurta, and Choghadiya. Defaults to Rishikesh; any city supported.
"""

from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import streamlit as st

from astro import geo
from astro.panchang import compute_panchang, format_time
from astro.chart_engine import format_dms
from astro import reference as ref

st.set_page_config(page_title="Daily Panchang", page_icon="\U0001f4c5", layout="wide")

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;600&display=swap');
      .stApp { background: linear-gradient(180deg,#070912,#0c1020); color:#e8ebf2; font-family:Inter,sans-serif; }
      h1,h2,h3 { font-family:'Cormorant Garamond',serif !important; color:#f5c542 !important; }
      .pcard { background:rgba(28,33,54,0.55); border:1px solid rgba(245,197,66,0.14);
               border-radius:16px; padding:16px 20px; margin-bottom:10px; backdrop-filter:blur(8px); }
      .plimb { font-size:22px; font-weight:700; color:#ffe9a8; font-family:'Cormorant Garamond',serif; }
      .psub { color:#9aa3b8; font-size:13px; }
      .phero { font-family:'Cormorant Garamond',serif; font-size:48px; font-weight:700;
               background:linear-gradient(120deg,#fff,#f5c542); -webkit-background-clip:text;
               -webkit-text-fill-color:transparent; }
      .inausp { border-color:rgba(239,107,107,0.35) !important; }
      .ausp { border-color:rgba(111,207,151,0.35) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar inputs
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## \U0001f4c5 Daily Panchang")
    st.caption("Tithi, Nakshatra, Yoga, Muhurta & Choghadiya \u00b7 Lahiri sidereal")

    p_date = st.date_input("Date", value=date.today())
    use_now = st.checkbox("Show Panchang at current time (not sunrise)", value=False)

    st.markdown("### Location")
    place_mode = st.radio(
        "Location", ["Pick a city", "Manual lat/long"], horizontal=True,
    )
    if place_mode == "Pick a city":
        place_name = st.selectbox("Place", geo.PLACE_NAMES, index=0)
        place_info = geo.resolve_place(place_name)
        lat, lon, place_label = (
            place_info.latitude, place_info.longitude, place_info.name,
        )
        tz_off = geo.tz_offset_hours(
            place_info.timezone, datetime.combine(p_date, datetime.now().time()))
        st.caption(
            f"{place_label} \u00b7 {place_info.timezone} (UTC{tz_off:+.2f})"
        )
    else:
        lat = st.number_input("Latitude", value=30.0869, format="%.4f")
        lon = st.number_input("Longitude", value=78.2676, format="%.4f")
        tz_off = st.number_input(
            "UTC offset (hours)", value=5.5, step=0.25, format="%.2f",
        )
        place_label = f"{lat:.3f},{lon:.3f}"
        place_name = place_label

    place_hi = place_name.split(",")[0]
    alt = 400 if "Rishikesh" in place_name else 200

    at_time = datetime.now() if use_now else None
    if st.button("Calculate Panchang", type="primary", use_container_width=True):
        st.session_state["panchang"] = compute_panchang(
            p_date, lat, lon, tz_off,
            place_label, place_hi, alt, at_time=at_time,
        )

if "panchang" not in st.session_state:
    st.session_state["panchang"] = compute_panchang(
        p_date, lat, lon, tz_off,
        place_label, place_hi, alt,
        at_time=datetime.now() if use_now else None,
    )

p = st.session_state["panchang"]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="pcard">
      <div class="psub">ऋषिकेश पंचांग · {p.place_hindi}</div>
      <div class="phero">{p.date.strftime('%A, %d %B %Y')}</div>
      <div class="psub" style="margin-top:6px">
        Vikram Samvat {p.vikram_samvat} · Shaka Samvat {p.shaka_samvat} ·
        {p.hindu_month} ({p.hindu_month_hindi}) · Lahiri Ayanamsha {p.ayanamsha:.4f}°
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

ref_note = "at sunrise" if not use_now else "at current time"
st.caption(f"Panchang values computed {ref_note} for {p.place}.")

# ---------------------------------------------------------------------------
# Five limbs + sun/moon times
# ---------------------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
limbs = [
    ("Vaara", p.vaara, p.vaara.end_time is None),
    ("Tithi", p.tithi, True),
    ("Nakshatra", p.nakshatra, True),
    ("Yoga", p.yoga, True),
    ("Karana", p.karana, True),
]
for col, (label, limb, show_end) in zip([c1, c2, c3, c4, c5], limbs):
    with col:
        end_txt = f"until {format_time(limb.end_time)}" if show_end and limb.end_time else ""
        st.markdown(
            f"""
            <div class="pcard">
              <div class="psub">{label}</div>
              <div class="plimb">{limb.name}</div>
              <div class="psub">{p.paksha if label == 'Tithi' else limb.extra}</div>
              <div class="psub">{end_txt}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("### Sun & Moon")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Sunrise", format_time(p.sunrise))
m2.metric("Sunset", format_time(p.sunset))
m3.metric("Moonrise", format_time(p.moonrise))
m4.metric("Moonset", format_time(p.moonset))

st.markdown(
    f"<div class='pcard'><span class='psub'>Sidereal positions · </span>"
    f"Sun {ref.SIGNS[int(p.sun_longitude // 30)]} {format_dms(p.sun_longitude % 30)} · "
    f"Moon {ref.SIGNS[int(p.moon_longitude // 30)]} {format_dms(p.moon_longitude % 30)}</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Muhurtas & inauspicious periods
# ---------------------------------------------------------------------------
st.markdown("### Muhurta & Inauspicious Periods")
a1, a2 = st.columns(2)
with a1:
    st.markdown("#### Auspicious")
    for w in (p.brahma_muhurta, p.abhijit_muhurta):
        st.markdown(
            f"<div class='pcard ausp'><b>{w.name}</b><br>"
            f"{format_time(w.start)} \u2013 {format_time(w.end)}<br>"
            f"<span class='psub'>{w.nature}</span></div>",
            unsafe_allow_html=True,
        )
with a2:
    st.markdown("#### Inauspicious (avoid new work)")
    for w in (p.rahu_kaal, p.gulika_kaal, p.yamaganda):
        st.markdown(
            f"<div class='pcard inausp'><b>{w.name}</b><br>"
            f"{format_time(w.start)} \u2013 {format_time(w.end)}</div>",
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Choghadiya
# ---------------------------------------------------------------------------
st.markdown("### Choghadiya")
tab_day, tab_night = st.tabs(["Day (sunrise \u2192 sunset)", "Night (sunset \u2192 sunrise)"])

def _cho_table(windows):
    return pd.DataFrame([{
        "Name": w.name,
        "Start": format_time(w.start),
        "End": format_time(w.end),
        "Nature": w.nature,
    } for w in windows])

with tab_day:
    st.dataframe(_cho_table(p.day_choghadiya), hide_index=True, use_container_width=True)
with tab_night:
    st.dataframe(_cho_table(p.night_choghadiya), hide_index=True, use_container_width=True)

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
st.markdown("### Download")
summary_lines = [
    f"# Panchang — {p.place} ({p.date.isoformat()})",
    f"Vikram Samvat {p.vikram_samvat} | {p.hindu_month} | {p.vaara.name}",
    "",
    f"- **Tithi:** {p.tithi.name} ({p.paksha}) until {format_time(p.tithi.end_time)}",
    f"- **Nakshatra:** {p.nakshatra.name} until {format_time(p.nakshatra.end_time)}",
    f"- **Yoga:** {p.yoga.name} until {format_time(p.yoga.end_time)}",
    f"- **Karana:** {p.karana.name} until {format_time(p.karana.end_time)}",
    f"- **Sunrise:** {format_time(p.sunrise)} | **Sunset:** {format_time(p.sunset)}",
    f"- **Rahu Kaal:** {format_time(p.rahu_kaal.start)} – {format_time(p.rahu_kaal.end)}",
    f"- **Abhijit Muhurta:** {format_time(p.abhijit_muhurta.start)} – {format_time(p.abhijit_muhurta.end)}",
]
md_export = "\n".join(summary_lines)
st.download_button("Download Panchang (Markdown)", md_export,
                   file_name=f"panchang_{p.date.isoformat()}.md", mime="text/markdown")

st.caption(
    "Panchang follows Lahiri Ayanamsha and sunrise-based North-Indian convention "
    "(Rishikesh / Uttarakhand style). For exact temple almanac, cross-check locally."
)
