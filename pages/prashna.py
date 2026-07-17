"""Prashna (horary) — answer a question from the moment it is asked."""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro.prashna import QUESTION_TYPES, answer_prashna

st.set_page_config(page_title="Prashna (Horary)", page_icon="\U0001f52e", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg,#070912,#0c1020); color:#e8ebf2; }
      h1,h2,h3 { color:#f5c542 !important; font-family:'Georgia',serif; }
      .pcard { background:rgba(28,33,54,0.55); border:1px solid rgba(245,197,66,0.14);
               border-radius:16px; padding:14px 18px; margin-bottom:10px; }
      .verdict { font-size:1.5rem; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# \U0001f52e Prashna — Horary Astrology")
st.caption(
    "Ask a question and get an answer from the chart of this very moment — "
    "no birth details needed · Lahiri sidereal"
)

st.markdown("### Your question")
qtype = st.selectbox(
    "What is it about?", list(QUESTION_TYPES.keys()),
    format_func=lambda k: QUESTION_TYPES[k]["label"],
)
question_text = st.text_input("Type your question (optional, for your own record)",
                              placeholder="e.g., Will I get the new job?")

st.markdown("### When & where the question is asked")
use_now = st.checkbox("Use the current moment", value=True)
c1, c2 = st.columns(2)
with c1:
    q_date = st.date_input("Date", value=date.today(), disabled=use_now,
                           min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))
with c2:
    q_time = st.time_input("Time", value=datetime.now().time().replace(second=0, microsecond=0),
                           step=60, disabled=use_now)

mode = st.radio("Location", ["Pick a city", "Manual lat/long"], horizontal=True)
if mode == "Pick a city":
    idx = geo.PLACE_NAMES.index("Rishikesh, India") if "Rishikesh, India" in geo.PLACE_NAMES else 0
    city = st.selectbox("Place", geo.PLACE_NAMES, index=idx)
    info = geo.resolve_place(city)
    lat, lon, place, tz_name, tz_manual = (
        info.latitude, info.longitude, info.name, info.timezone, None)
else:
    lat = st.number_input("Latitude", value=30.0869, format="%.4f")
    lon = st.number_input("Longitude", value=78.2676, format="%.4f")
    tz_manual = st.number_input("UTC offset (hours)", value=5.5, step=0.25, format="%.2f")
    place, tz_name = f"{lat:.3f},{lon:.3f}", None

if st.button("Cast the chart & answer", type="primary", use_container_width=True):
    when = datetime.now() if use_now else datetime.combine(q_date, q_time)
    if tz_name:
        tz = geo.tz_offset_hours(tz_name, when)
    else:
        tz = tz_manual
    res = answer_prashna(qtype, when, lat, lon, tz, place)

    color = {"Favourable": "#6fcf97", "Mixed": "#f2c94c", "Unfavourable": "#eb5757"}[res["verdict"]]
    if question_text:
        st.markdown(f"> **Q:** {question_text}")
    st.markdown(
        f"<div class='pcard'>"
        f"<span class='verdict' style='color:{color}'>{res['verdict']}</span> "
        f"&nbsp; <span style='color:#9aa4bf'>({res['score']}% favourable)</span><br>"
        f"<span style='color:#9aa4bf'>{res['question_type']} · asked {res['asked_at']} · {res['place']}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.progress(min(1.0, res["score"] / 100.0))

    st.markdown(
        f"<div class='pcard'>"
        f"<b style='color:#ffe9a8'>Query Ascendant:</b> {res['lagna']} &nbsp;·&nbsp; "
        f"<b style='color:#ffe9a8'>Moon:</b> {res['moon_sign']} ({res['moon_nakshatra']})"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Why")
    for r in res["reasons"]:
        st.markdown(f"- {r}")

    if res.get("yogas"):
        st.markdown("### Tajika yogas (how the significators connect)")
        tone = {"Ithasala": "#6fcf97", "Kamboola": "#6fcf97",
                "Nakta": "#f2c94c", "Yamaya": "#f2c94c",
                "Ishrafa": "#eb5757", "Manau": "#eb5757"}
        for y in res["yogas"]:
            c = tone.get(y["type"], "#9aa4bf")
            st.markdown(
                f"<div class='pcard'><b style='color:{c}'>{y['type']}</b> "
                f"({' & '.join(y['planets'])}) — {y['reason']}</div>",
                unsafe_allow_html=True,
            )

    st.markdown(f"**Timing:** {res['timing']}")

    st.caption(
        "Horary judgement is indicative and depends on a sincere question asked once. "
        "For reflection and guidance."
    )
