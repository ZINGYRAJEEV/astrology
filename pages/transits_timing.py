"""Transits & Timing — live Gochar (transits) + Dasha depth (Maha/Antar/Pratyantar)."""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro import persistence
from astro.chart_engine import BirthData, compute_chart
from astro.gochar import gochar_report
from astro.dasha_calc import (
    compute_vimshottari, current_dasha_full, upcoming_changes,
)
from astro.narrative import DASHA_THEME

st.set_page_config(page_title="Transits & Timing", page_icon="\U0001fa90", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg,#070912,#0c1020); color:#e8ebf2; }
      h1,h2,h3 { color:#f5c542 !important; font-family:'Georgia',serif; }
      .pcard { background:rgba(28,33,54,0.55); border:1px solid rgba(245,197,66,0.14);
               border-radius:16px; padding:16px 20px; margin-bottom:10px; }
      .good { border-left:4px solid #6fcf97; }
      .bad { border-left:4px solid #ef6b6b; }
      .neutral { border-left:4px solid #f2c94c; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# \U0001fa90 Transits & Timing")
st.caption(
    "Live Gochar (planetary transits) vs your birth chart \u00b7 "
    "Vimshottari Dasha to the Pratyantardasha (third) level \u00b7 Lahiri sidereal"
)


# ---------------------------------------------------------------------------
# Chart selection
# ---------------------------------------------------------------------------
st.markdown("### Whose chart?")
saved = persistence.list_charts()
options = ["Enter birth details"] + [f"{c['name']} — {c['summary']}" for c in saved]
choice = st.selectbox("Chart", options, key="tt_choice")

birth = None
if choice == "Enter birth details":
    with st.expander("Birth details", expanded=True):
        name = st.text_input("Name", key="tt_name", placeholder="Your name")
        c1, c2 = st.columns(2)
        with c1:
            b_date = st.date_input("Date of birth", value=date(1990, 1, 1),
                                   min_value=date(1800, 1, 1), max_value=date(2100, 12, 31),
                                   key="tt_bdate")
        with c2:
            b_time = st.time_input("Time of birth", value=time(12, 0), step=60, key="tt_btime")
        b_mode = st.radio("Birth location", ["Pick a city", "Manual lat/long"],
                          horizontal=True, key="tt_bplace_mode")
        if b_mode == "Pick a city":
            idx = geo.PLACE_NAMES.index("Rishikesh, India") if "Rishikesh, India" in geo.PLACE_NAMES else 0
            bcity = st.selectbox("Birth place", geo.PLACE_NAMES, index=idx, key="tt_bcity")
            binfo = geo.resolve_place(bcity)
            blat, blon, bplace, btz_name, btz_manual = (
                binfo.latitude, binfo.longitude, binfo.name, binfo.timezone, None)
        else:
            blat = st.number_input("Birth latitude", value=30.0869, format="%.4f", key="tt_blat")
            blon = st.number_input("Birth longitude", value=78.2676, format="%.4f", key="tt_blon")
            btz_manual = st.number_input("Birth UTC offset (hours)", value=5.5, step=0.25,
                                         format="%.2f", key="tt_btz")
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

as_of = st.date_input("As of date", value=date.today(),
                      min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), key="tt_asof")

if st.button("Show transits & timing", type="primary", use_container_width=True):
    st.session_state["tt_chart_birth"] = birth
    st.session_state["tt_asof_val"] = as_of

if "tt_chart_birth" not in st.session_state:
    st.info("Pick a chart and a date, then click **Show transits & timing**.")
    st.stop()

chart = compute_chart(st.session_state["tt_chart_birth"])
when = datetime.combine(st.session_state["tt_asof_val"], time(12, 0))

# ---------------------------------------------------------------------------
# Gochar
# ---------------------------------------------------------------------------
report = gochar_report(chart, when)
st.markdown(f"## \U0001f30c Transits on {when.strftime('%d %b %Y')}")
st.caption(f"Judged from your Janma Rashi (Moon in {report['moon_sign']}) and Lagna ({report['lagna']}).")

_TONE = {"favourable": "good", "challenging": "bad", "neutral": "neutral"}
for h in report["highlights"]:
    st.markdown(
        f"<div class='pcard {_TONE.get(h['tone'], 'neutral')}'>"
        f"<b style='color:#ffe9a8'>{h['title']}</b>"
        f"<div style='margin-top:4px'>{h['detail']}</div></div>",
        unsafe_allow_html=True,
    )

st.markdown("### All transiting planets")
table = []
for r in report["rows"]:
    table.append({
        "Planet": r["planet"] + (" \u211e" if r["retrograde"] else ""),
        "Sign": r["sign"],
        "Dignity": r["dignity"] or "—",
        "From Moon": f"{r['house_from_moon']}th",
        "From Lagna": f"{r['house_from_lagna']}th",
        "Gochar": "Favourable" if r["favourable"] else "Neutral/testing",
    })
st.dataframe(table, hide_index=True, use_container_width=True)

# ---------------------------------------------------------------------------
# Dasha depth
# ---------------------------------------------------------------------------
st.markdown("## \u23f3 Dasha timing (to Pratyantardasha)")
periods = compute_vimshottari(chart, pratyantardashas=True)
maha, antar, prat = current_dasha_full(periods, when)


def _theme(lord):
    return DASHA_THEME.get(lord, "karmic growth")


if maha:
    st.markdown(
        f"<div class='pcard'>"
        f"<b style='color:#ffe9a8;font-size:18px'>Mahadasha: {maha.lord}</b> "
        f"<span style='color:#9aa3b8'>({maha.start:%b %Y} → {maha.end:%b %Y})</span>"
        f"<div style='margin-top:4px'>Broad life theme: {_theme(maha.lord)}.</div></div>",
        unsafe_allow_html=True,
    )
if antar:
    st.markdown(
        f"<div class='pcard'>"
        f"<b style='color:#ffe9a8;font-size:17px'>Antardasha: {antar.lord}</b> "
        f"<span style='color:#9aa3b8'>({antar.start:%d %b %Y} → {antar.end:%d %b %Y})</span>"
        f"<div style='margin-top:4px'>Sub-theme: {_theme(antar.lord)}.</div></div>",
        unsafe_allow_html=True,
    )
if prat:
    st.markdown(
        f"<div class='pcard'>"
        f"<b style='color:#ffe9a8;font-size:16px'>Pratyantardasha: {prat.lord}</b> "
        f"<span style='color:#9aa3b8'>({prat.start:%d %b %Y} → {prat.end:%d %b %Y})</span>"
        f"<div style='margin-top:4px'>Immediate flavour right now: {_theme(prat.lord)}.</div></div>",
        unsafe_allow_html=True,
    )

st.markdown("### Upcoming period changes")
changes = upcoming_changes(periods, when, count=8)
if not changes:
    st.caption("No further changes in the computed timeline.")
for e in changes:
    st.markdown(f"- **{e['start']:%d %b %Y}** — {e['level']} begins: {e['label']} "
                f"(new flavour: {_theme(e['label'].split(' / ')[-1])})")

st.caption(
    "Gochar uses the classical benefic-house scheme from the natal Moon. "
    "Rishikesh tradition · for guidance and reflection."
)
