"""Planetary Combinations — a reference for planets in houses and conjunctions,
with significance, merits, demerits, and what appears in your own chart.
"""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro import persistence
from astro import reference as ref
from astro.chart_engine import BirthData, compute_chart
from astro.combinations import (
    CONJUNCTIONS, chart_combinations, conjunction, planet_in_house,
)

st.set_page_config(page_title="Planetary Combinations", page_icon="\U0001fa90", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg,#070912,#0c1020); color:#e8ebf2; }
      h1,h2,h3 { color:#f5c542 !important; font-family:'Georgia',serif; }
      .pcard { background:rgba(28,33,54,0.55); border:1px solid rgba(245,197,66,0.14);
               border-radius:16px; padding:14px 18px; margin-bottom:10px; }
      .merit { color:#6fcf97; } .demerit { color:#eb5757; }
      .tag { display:inline-block; background:rgba(245,197,66,0.16); color:#ffe9a8;
             border-radius:999px; padding:2px 10px; font-size:12px; margin-bottom:6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# \U0001fa90 Planetary Combinations")
st.caption(
    "How each planet behaves in each house, and what the classical two-planet "
    "conjunctions (yogas) mean — with merits, demerits and life effects."
)


def _placement_card(planet: str, house: int, info: dict):
    hs = ref.HOUSE_SIGNIFICATION.get(house, "")
    st.markdown(
        f"<div class='pcard'>"
        f"<span class='tag'>{planet} in House {house} · {ref.HOUSE_NAME.get(house,'')}</span>"
        f"<div class='subtle' style='color:#9aa4bf;font-size:12px;margin-bottom:6px'>{hs}</div>"
        f"<b style='color:#ffe9a8'>Effect:</b> {info['effect']}<br>"
        f"<b class='merit'>Merits:</b> {info['merits']}<br>"
        f"<b class='demerit'>Watch-outs:</b> {info['demerits']}"
        f"</div>",
        unsafe_allow_html=True,
    )


def _conj_card(name: str, planets, significance: str, merits: str, demerits: str,
               where: str = ""):
    body = (
        f"<span class='tag'>{name}{(' · ' + where) if where else ''}</span>"
        f"<div style='margin-bottom:6px'><b style='color:#ffe9a8'>"
        f"{' + '.join(planets)}</b></div>"
        f"<b style='color:#ffe9a8'>Significance:</b> {significance}<br>"
    )
    if merits:
        body += f"<b class='merit'>Merits:</b> {merits}<br>"
    if demerits:
        body += f"<b class='demerit'>Watch-outs:</b> {demerits}"
    st.markdown(f"<div class='pcard'>{body}</div>", unsafe_allow_html=True)


tab_explore, tab_conj, tab_chart = st.tabs(
    ["Planet in a house", "Two-planet conjunctions", "In my chart"]
)

# ---------------------------------------------------------------------------
with tab_explore:
    st.markdown("### Look up a planet in a house")
    c1, c2 = st.columns(2)
    with c1:
        planet = st.selectbox("Planet", ref.PLANETS, key="ex_planet")
    with c2:
        house = st.selectbox("House", list(range(1, 13)),
                             format_func=lambda h: f"House {h} — {ref.HOUSE_NAME.get(h,'')}",
                             key="ex_house")
    info = planet_in_house(planet, house)
    if info:
        _placement_card(planet, house, info)

    with st.expander(f"See {planet} through all 12 houses"):
        for h in range(1, 13):
            pi = planet_in_house(planet, h)
            if pi:
                _placement_card(planet, h, pi)

# ---------------------------------------------------------------------------
with tab_conj:
    st.markdown("### Look up a two-planet conjunction")
    c1, c2 = st.columns(2)
    with c1:
        pa = st.selectbox("First planet", ref.PLANETS, index=0, key="cj_a")
    with c2:
        pb = st.selectbox("Second planet", ref.PLANETS, index=1, key="cj_b")
    if pa == pb:
        st.info("Pick two different planets.")
    else:
        info = conjunction(pa, pb)
        if info:
            _conj_card(info["name"], (pa, pb), info["significance"],
                       info["merits"], info["demerits"])
        else:
            st.warning(
                f"No curated note for {pa} + {pb}. In general, they blend their "
                "significations in the house/sign they share — read each planet's "
                "placement in the first tab."
            )

    st.markdown("### All classical conjunctions")
    st.caption("The famous yogas formed when two planets sit together.")
    for (a, b), info in CONJUNCTIONS.items():
        _conj_card(info["name"], (a, b), info["significance"],
                   info["merits"], info["demerits"])

# ---------------------------------------------------------------------------
with tab_chart:
    st.markdown("### See the combinations in your own chart")
    saved = persistence.list_charts()
    options = ["Enter birth details"] + [f"{c['name']} — {c['summary']}" for c in saved]
    choice = st.selectbox("Chart", options, key="cm_choice")

    birth = None
    if choice == "Enter birth details":
        with st.expander("Birth details", expanded=True):
            name = st.text_input("Name", key="cm_name", placeholder="Your name")
            d1, d2 = st.columns(2)
            with d1:
                b_date = st.date_input("Date of birth", value=date(1990, 1, 1),
                                       min_value=date(1800, 1, 1), max_value=date(2100, 12, 31),
                                       key="cm_bdate")
            with d2:
                b_time = st.time_input("Time of birth", value=time(12, 0), step=60, key="cm_btime")
            b_mode = st.radio("Birth location", ["Pick a city", "Manual lat/long"],
                              horizontal=True, key="cm_bplace_mode")
            if b_mode == "Pick a city":
                idx = geo.PLACE_NAMES.index("Rishikesh, India") if "Rishikesh, India" in geo.PLACE_NAMES else 0
                bcity = st.selectbox("Birth place", geo.PLACE_NAMES, index=idx, key="cm_bcity")
                binfo = geo.resolve_place(bcity)
                blat, blon, bplace, btz_name, btz_manual = (
                    binfo.latitude, binfo.longitude, binfo.name, binfo.timezone, None)
            else:
                blat = st.number_input("Birth latitude", value=30.0869, format="%.4f", key="cm_blat")
                blon = st.number_input("Birth longitude", value=78.2676, format="%.4f", key="cm_blon")
                btz_manual = st.number_input("Birth UTC offset (hours)", value=5.5, step=0.25,
                                             format="%.2f", key="cm_btz")
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

    if st.button("Show my combinations", type="primary", use_container_width=True):
        st.session_state["cm_birth"] = birth

    if "cm_birth" not in st.session_state:
        st.info("Pick a chart, then click **Show my combinations**.")
    else:
        chart = compute_chart(st.session_state["cm_birth"])
        data = chart_combinations(chart)
        native = chart.birth.name or "Native"

        st.markdown(f"#### {native} — planet placements")
        for p in data["placements"]:
            _placement_card(
                p["planet"] + (" (retrograde)" if p["retrograde"] else ""),
                p["house"],
                {"effect": f"In {p['sign']}. {p['effect']}",
                 "merits": p["merits"], "demerits": p["demerits"]},
            )

        st.markdown("#### Conjunctions in your chart")
        if not data["conjunctions"]:
            st.caption("No two planets share a house — no conjunctions in this chart.")
        for c in data["conjunctions"]:
            _conj_card(
                c["name"], c["planets"], c["significance"], c["merits"], c["demerits"],
                where=f"House {c['house']} ({c['house_name']}) · {c['sign']}",
            )

st.caption(
    "Reference guidance · results are modulated by sign, dignity, aspects and Dasha. "
    "For learning and reflection."
)
