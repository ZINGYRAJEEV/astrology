"""Timing Summary — visual Mahadasha / Antardasha impact map."""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro import persistence
from astro.chart_engine import BirthData, compute_chart
from astro.timing_summary import build_timing_summary, timing_summary_markdown
from astro.timing_viz import render_timing_viz
from astro.chart_explain import build_chart_explain, chart_explain_markdown
from astro.explain_ui import render_chart_explain

st.set_page_config(page_title="Timing Summary", page_icon="\U0001f4c8", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg,#070912,#0c1020); color:#e8ebf2; }
      h1,h2,h3 { color:#f5c542 !important; font-family:'Georgia',serif; }
      .pcard { background:rgba(28,33,54,0.55); border:1px solid rgba(245,197,66,0.14);
               border-radius:16px; padding:16px 20px; margin-bottom:10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# \U0001f4c8 Timing Summary")
st.caption(
    "Graph-first Vimshottari map — Antardasha timeline + impact lines for "
    "Career / Wealth / Family / Health / Spiritual. Green favourable · amber mixed · red challenged."
)

st.markdown("### Whose chart?")
saved = persistence.list_charts()
options = ["Enter birth details"] + [f"{c['name']} — {c['summary']}" for c in saved]
# Prefer a saved chart when available so the map appears with one click.
default_idx = 1 if len(options) > 1 else 0
choice = st.selectbox("Chart", options, index=default_idx, key="ts_choice")

birth = None
if choice == "Enter birth details":
    with st.expander("Birth details", expanded=True):
        name = st.text_input("Name", key="ts_name", placeholder="Your name")
        c1, c2 = st.columns(2)
        with c1:
            b_date = st.date_input(
                "Date of birth", value=date(1990, 1, 1),
                min_value=date(1800, 1, 1), max_value=date(2100, 12, 31), key="ts_bdate",
            )
        with c2:
            b_time = st.time_input("Time of birth", value=time(12, 0), step=60, key="ts_btime")
        b_mode = st.radio(
            "Birth location", ["Pick a city", "Manual lat/long"],
            horizontal=True, key="ts_bplace_mode",
        )
        if b_mode == "Pick a city":
            idx = (
                geo.PLACE_NAMES.index("Rishikesh, India")
                if "Rishikesh, India" in geo.PLACE_NAMES else 0
            )
            bcity = st.selectbox("Birth place", geo.PLACE_NAMES, index=idx, key="ts_bcity")
            binfo = geo.resolve_place(bcity)
            blat, blon, bplace, btz_name, btz_manual = (
                binfo.latitude, binfo.longitude, binfo.name, binfo.timezone, None)
        else:
            blat = st.number_input("Birth latitude", value=30.0869, format="%.4f", key="ts_blat")
            blon = st.number_input("Birth longitude", value=78.2676, format="%.4f", key="ts_blon")
            btz_manual = st.number_input(
                "Birth time zone — IST hours from UTC", value=5.5, step=0.25,
                format="%.2f", key="ts_btz",
            )
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

c1, c2 = st.columns(2)
with c1:
    as_of = st.date_input(
        "As of date", value=date.today(),
        min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), key="ts_asof",
    )
with c2:
    horizon = st.slider("Years ahead", min_value=3, max_value=12, value=6, key="ts_horizon")

run = st.button("Build timing map", type="primary", use_container_width=True)
# Auto-build once a chart is chosen (saved charts or filled birth form).
if run or birth is not None:
    st.session_state["ts_birth"] = birth
    st.session_state["ts_asof"] = as_of
    st.session_state["ts_horizon"] = horizon

if "ts_birth" not in st.session_state or st.session_state["ts_birth"] is None:
    st.info("Pick a saved chart (or enter birth details), then the map builds automatically.")
    st.stop()

chart = compute_chart(st.session_state["ts_birth"])
when = datetime.combine(st.session_state["ts_asof"], time(12, 0))
summary = build_timing_summary(
    chart, when=when, horizon_years=float(st.session_state["ts_horizon"]),
)

cur = summary["current"]
st.markdown(
    f"<div class='pcard'>"
    f"<b style='color:#ffe9a8;font-size:18px'>"
    f"{cur.get('maha') or '—'} / {cur.get('antar') or '—'}</b>"
    f"<div style='margin-top:6px;color:#9aa3b8'>"
    f"Mahadasha theme: {cur.get('maha_theme') or '—'} · "
    f"Antardasha: {cur.get('antar_theme') or '—'} · "
    f"Antar until {cur.get('antar_until') or '—'} · "
    f"{cur.get('sade_sati') or ''}"
    f"</div></div>",
    unsafe_allow_html=True,
)

st.markdown("### Graphs")
render_timing_viz(summary, height=860)

explain = build_chart_explain(
    chart, when=when, horizon_years=float(st.session_state["ts_horizon"]), timing=summary,
)
st.markdown("---")
render_chart_explain(explain, theme="default", show_summary=True)

with st.expander("Natal baseline by life area", expanded=False):
    rows = []
    for area, row in summary.get("natal_baseline", {}).items():
        rows.append({
            "Area": area,
            "Natal verdict": row["verdict"],
            "Lord": row["lord"],
            "Lord dignity": row["lord_dignity"],
            "Lord house": row["lord_house"],
        })
    st.dataframe(rows, hide_index=True, use_container_width=True)

combined_md = timing_summary_markdown(summary) + "\n\n" + chart_explain_markdown(explain)
st.download_button(
    "Download timing + explanation (Markdown)",
    combined_md,
    file_name=f"timing_{(chart.birth.name or 'chart').replace(' ', '_')}.md",
    mime="text/markdown",
    use_container_width=True,
)

st.caption(
    "Scores blend natal house strength with Mahadasha / Antardasha lord dignity and placement. "
    "Phase notes also sample Gochara at mid-phase. Guidance for reflection — not fate. · Lahiri sidereal"
)
