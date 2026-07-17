"""Sahams — Tajika sensitive points for a chart."""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro import persistence
from astro.chart_engine import BirthData, compute_chart
from astro.sahams import compute_sahams, is_day_birth, sahams_markdown

st.set_page_config(page_title="Sahams", page_icon="\U0001f3af", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg,#070912,#0c1020); color:#e8ebf2; }
      h1,h2,h3 { color:#f5c542 !important; font-family:'Georgia',serif; }
      .pcard { background:rgba(28,33,54,0.55); border:1px solid rgba(245,197,66,0.14);
               border-radius:16px; padding:14px 18px; margin-bottom:10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# \U0001f3af Sahams — Tajika Sensitive Points")
st.caption(
    "Vedic analogues of Arabic Parts — Punya (fortune), Vivaha (marriage), "
    "Karma (career) & more · Lahiri sidereal"
)


st.markdown("### Whose chart?")
saved = persistence.list_charts()
options = ["Enter birth details"] + [f"{c['name']} — {c['summary']}" for c in saved]
choice = st.selectbox("Chart", options, key="sh_choice")

birth = None
if choice == "Enter birth details":
    with st.expander("Birth details", expanded=True):
        name = st.text_input("Name", key="sh_name", placeholder="Your name")
        c1, c2 = st.columns(2)
        with c1:
            b_date = st.date_input("Date of birth", value=date(1990, 1, 1),
                                   min_value=date(1800, 1, 1), max_value=date(2100, 12, 31),
                                   key="sh_bdate")
        with c2:
            b_time = st.time_input("Time of birth", value=time(12, 0), step=60, key="sh_btime")
        b_mode = st.radio("Birth location", ["Pick a city", "Manual lat/long"],
                          horizontal=True, key="sh_bplace_mode")
        if b_mode == "Pick a city":
            idx = geo.PLACE_NAMES.index("Rishikesh, India") if "Rishikesh, India" in geo.PLACE_NAMES else 0
            bcity = st.selectbox("Birth place", geo.PLACE_NAMES, index=idx, key="sh_bcity")
            binfo = geo.resolve_place(bcity)
            blat, blon, bplace, btz_name, btz_manual = (
                binfo.latitude, binfo.longitude, binfo.name, binfo.timezone, None)
        else:
            blat = st.number_input("Birth latitude", value=30.0869, format="%.4f", key="sh_blat")
            blon = st.number_input("Birth longitude", value=78.2676, format="%.4f", key="sh_blon")
            btz_manual = st.number_input("Birth UTC offset (hours)", value=5.5, step=0.25,
                                         format="%.2f", key="sh_btz")
            bplace, btz_name = f"{blat:.3f},{blon:.3f}", None
        if btz_name:
            btz = geo.tz_offset_hours(btz_name, datetime.combine(b_date, b_time))
        else:
            btz = btz_manual
        birth = BirthData(
            name=name, year=b_date.year, month=b_date.month, day=b_date.day,
            hour=b_time.hour, minute=b_time.minute, latitude=blat, longitude=blon,
            tz_offset=btz, place=bplace,
        )
else:
    sel = saved[options.index(choice) - 1]
    birth = persistence.load_birth(sel["id"])

if st.button("Compute Sahams", type="primary", use_container_width=True):
    st.session_state["sh_birth"] = birth

if "sh_birth" not in st.session_state:
    st.info("Pick a chart, then click **Compute Sahams**.")
    st.stop()

chart = compute_chart(st.session_state["sh_birth"])
sahams = compute_sahams(chart)
day = is_day_birth(chart)
native = chart.birth.name or "Native"

st.markdown(f"## {native} — Sahams")
st.caption(f"{'Day' if day else 'Night'} birth · each Saham is judged by its house and its lord.")

rows = []
for s in sahams:
    rows.append({
        "Saham": s["label"],
        "Sign": f"{s['sign']} {s['degree']}°",
        "House": s["house"],
        "Lord": s["lord"],
        "Signifies": s["signifies"],
    })
st.dataframe(rows, hide_index=True, use_container_width=True)

st.download_button(
    "Download Sahams (Markdown)",
    sahams_markdown(sahams, native, day),
    file_name=f"sahams_{native.replace(' ', '_')}.md",
    mime="text/markdown",
    use_container_width=True,
)

st.caption(
    "Day-formula with night reversal; operand traditions vary between texts. "
    "For reflection and guidance."
)
