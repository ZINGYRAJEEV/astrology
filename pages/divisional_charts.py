"""Divisional Charts (Vargas) — D3, D7, D9, D10, D12, D30 with readings."""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro import persistence
from astro.chart_engine import BirthData, compute_chart
from astro.vargas import VARGAS, build_varga_chart, varga_markdown

st.set_page_config(page_title="Divisional Charts", page_icon="\U0001f9e9", layout="wide")

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

st.markdown("# \U0001f9e9 Divisional Charts (Vargas)")
st.caption(
    "Finer charts for specific life areas — Navamsha (marriage), Dasamsa (career), "
    "Saptamsa (children) & more \u00b7 Parashari · Lahiri sidereal"
)


st.markdown("### Whose chart?")
saved = persistence.list_charts()
options = ["Enter birth details"] + [f"{c['name']} — {c['summary']}" for c in saved]
choice = st.selectbox("Chart", options, key="dv_choice")

birth = None
if choice == "Enter birth details":
    with st.expander("Birth details", expanded=True):
        name = st.text_input("Name", key="dv_name", placeholder="Your name")
        c1, c2 = st.columns(2)
        with c1:
            b_date = st.date_input("Date of birth", value=date(1990, 1, 1),
                                   min_value=date(1800, 1, 1), max_value=date(2100, 12, 31),
                                   key="dv_bdate")
        with c2:
            b_time = st.time_input("Time of birth", value=time(12, 0), step=60, key="dv_btime")
        st.caption("Birth time accuracy matters most for divisional charts.")
        b_mode = st.radio("Birth location", ["Pick a city", "Manual lat/long"],
                          horizontal=True, key="dv_bplace_mode")
        if b_mode == "Pick a city":
            idx = geo.PLACE_NAMES.index("Rishikesh, India") if "Rishikesh, India" in geo.PLACE_NAMES else 0
            bcity = st.selectbox("Birth place", geo.PLACE_NAMES, index=idx, key="dv_bcity")
            binfo = geo.resolve_place(bcity)
            blat, blon, bplace, btz_name, btz_manual = (
                binfo.latitude, binfo.longitude, binfo.name, binfo.timezone, None)
        else:
            blat = st.number_input("Birth latitude", value=30.0869, format="%.4f", key="dv_blat")
            blon = st.number_input("Birth longitude", value=78.2676, format="%.4f", key="dv_blon")
            btz_manual = st.number_input("Birth UTC offset (hours)", value=5.5, step=0.25,
                                         format="%.2f", key="dv_btz")
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

varga = st.selectbox(
    "Divisional chart", list(VARGAS.keys()),
    format_func=lambda v: f"{VARGAS[v]['name']} — {VARGAS[v]['signifies']}",
    index=list(VARGAS.keys()).index(9),
)

if st.button("Build divisional chart", type="primary", use_container_width=True):
    st.session_state["dv_birth"] = birth

if "dv_birth" not in st.session_state:
    st.info("Pick a chart and a divisional chart, then click **Build divisional chart**.")
    st.stop()

chart = compute_chart(st.session_state["dv_birth"])
vc = build_varga_chart(chart, varga)
native = chart.birth.name or "Native"

st.markdown(f"## {vc['name']} — {native}")
st.caption(vc["signifies"])
st.markdown(
    f"<div class='pcard'><b style='color:#ffe9a8'>Divisional Ascendant:</b> "
    f"{vc['lagna_sign']} (lord {vc['lagna_lord']})"
    + (f" · <b style='color:#6fcf97'>Vargottama:</b> {', '.join(vc['vargottama'])}"
       if vc["vargottama"] else "")
    + "</div>",
    unsafe_allow_html=True,
)

rows = []
for p in vc["planets"]:
    rows.append({
        "Planet": p["planet"] + (" \u211e" if p["retrograde"] else ""),
        "Sign": p["sign"],
        "House": p["house"],
        "Dignity": p["dignity"] or "—",
        "Vargottama": "Yes" if p["vargottama"] else "",
        "D-1 sign": p["d1_sign"],
    })
st.dataframe(rows, hide_index=True, use_container_width=True)

st.caption(
    "Vargottama planets (same sign in D-1 and this chart) are notably strengthened. "
    "Read each divisional chart for its own life area — the Navamsha (D-9) is the most "
    "important after the birth chart."
)

st.download_button(
    "Download this chart (Markdown)",
    varga_markdown(vc, native),
    file_name=f"{vc['name'].split(' ')[0].lower()}_{native.replace(' ', '_')}.md",
    mime="text/markdown",
    use_container_width=True,
)
