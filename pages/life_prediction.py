"""Life Prediction — Hrishikesh Panchang birth chart + Panchang at birth."""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro.chart_engine import BirthData, compute_chart
from astro.prediction import generate_prediction
from astro.prediction_ui import render_prediction_results
from astro.interpret import INTENT_HOUSES

st.set_page_config(page_title="Life Prediction", page_icon="\U0001f52e", layout="wide")

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

st.markdown("# \U0001f52e Life Prediction")
st.caption("Hrishikesh Panchang tradition \u00b7 birth chart + Panchang at birth")

form_col, _ = st.columns([2, 1])
with form_col:
  with st.container(border=True):
    st.markdown("### Birth Data")
    place_mode = st.radio(
        "Location", ["Pick a city", "Manual lat/long"], horizontal=True,
        key="pred_place_mode",
    )
    if place_mode == "Pick a city":
        city = st.selectbox(
            "Birth place",
            geo.PLACE_NAMES,
            index=geo.PLACE_NAMES.index("Rishikesh, India")
            if "Rishikesh, India" in geo.PLACE_NAMES else 0,
            key="pred_city",
        )
        place_info = geo.resolve_place(city)
        lat, lon, place_label = (
            place_info.latitude, place_info.longitude, place_info.name,
        )
        tz_name = place_info.timezone
        st.caption(f"{place_label} \u00b7 {place_info.timezone}")
    else:
        col_lat, col_lon, col_tz = st.columns(3)
        with col_lat:
            lat = st.number_input("Latitude", value=30.0869, format="%.4f", key="pred_lat")
        with col_lon:
            lon = st.number_input("Longitude", value=78.2676, format="%.4f", key="pred_lon")
        with col_tz:
            tz_off_manual = st.number_input(
                "UTC offset (hours)", value=5.5, step=0.25, format="%.2f",
                key="pred_tz",
            )
        place_label = f"{lat:.3f},{lon:.3f}"
        tz_name = None

    with st.form("prediction_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name", placeholder="Your name")
            b_date = st.date_input(
                "Date of birth",
                value=date(1990, 1, 1),
                min_value=date(1800, 1, 1),
                max_value=date(2100, 12, 31),
            )
            b_time = st.time_input("Time of birth", value=time(12, 0), step=60)
        with c2:
            intent = st.selectbox("Prediction focus", list(INTENT_HOUSES.keys()),
                                  index=len(INTENT_HOUSES) - 1)
        st.caption("Birth time accuracy is mission-critical for the Ascendant.")

        submitted = st.form_submit_button("Generate Prediction", type="primary", use_container_width=True)

if submitted:
    if tz_name:
        tz_off = geo.tz_offset_hours(
            tz_name, datetime.combine(b_date, b_time))
    else:
        tz_off = tz_off_manual
    birth = BirthData(
        name=name, year=b_date.year, month=b_date.month, day=b_date.day,
        hour=b_time.hour, minute=b_time.minute,
        latitude=lat, longitude=lon,
        tz_offset=tz_off, place=place_label,
    )
    chart = compute_chart(birth)
    pred = generate_prediction(chart, intent)
    st.session_state["prediction"] = pred

if "prediction" not in st.session_state:
    st.info("Fill in your birth details above and click **Generate Prediction**.")
    st.markdown(
        """
        ### What you'll receive
        - **Rishikesh Panchang evaluation** — Ishtakal, five limbs, Navaratna scoring
        - **Avakhada Chakra** — Varna, Vashya, Yoni, Gana, Nadi
        - **Birth Panchang** at your exact birth time (Tithi, Nakshatra, Yoga, Karana, Vaara)
        - **Life predictions** for personality, wealth, career, marriage, health and spirituality
        - **Vimshottari Dasha**, Sade Sati & Guru Gochar timing
        - Downloadable Markdown report
        """
    )
    st.stop()

render_prediction_results(st.session_state["prediction"], theme="default")
