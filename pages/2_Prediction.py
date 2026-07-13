"""Astrology Prediction — birth chart + Panchang at birth.

Enter name, date, time and place to receive personalised life predictions
combining Janam Kundli (Lahiri sidereal) with the Panchang at your exact
birth moment.
"""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro.chart_engine import BirthData, compute_chart
from astro.prediction import generate_prediction, prediction_markdown
from astro.interpret import INTENT_HOUSES

st.set_page_config(page_title="Astrology Prediction", page_icon="\U0001f52e", layout="wide")

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

st.markdown("# \U0001f52e Astrology Prediction")
st.caption("Janam Kundli + Panchang at birth \u00b7 Lahiri sidereal \u00b7 plain-language predictions")

with st.form("prediction_form"):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full name", placeholder="Your name")
        b_date = st.date_input("Date of birth", value=date(1990, 1, 1))
        b_time = st.time_input("Time of birth", value=time(12, 0), step=60)
    with c2:
        intent = st.selectbox("Prediction focus", list(INTENT_HOUSES.keys()),
                              index=len(INTENT_HOUSES) - 1)
        city = st.selectbox("Birth place", list(geo.CITIES.keys()),
                            index=list(geo.CITIES.keys()).index("Rishikesh, India")
                            if "Rishikesh, India" in geo.CITIES else 0)
        lat, lon, tzname = geo.CITIES[city]
        st.caption(f"{city} \u00b7 lat {lat:.3f}, lon {lon:.3f}")

    submitted = st.form_submit_button("Generate Prediction", type="primary", use_container_width=True)

if submitted:
    tz_off = geo.tz_offset_hours(tzname, datetime.combine(b_date, b_time))
    birth = BirthData(
        name=name, year=b_date.year, month=b_date.month, day=b_date.day,
        hour=b_time.hour, minute=b_time.minute,
        latitude=lat, longitude=lon, tz_offset=tz_off, place=city,
    )
    chart = compute_chart(birth)
    pred = generate_prediction(chart, intent)
    st.session_state["prediction"] = pred

if "prediction" not in st.session_state:
    st.info("Fill in your birth details above and click **Generate Prediction**.")
    st.markdown(
        """
        ### What you'll receive
        - **Birth Panchang** at your exact birth time (Tithi, Nakshatra, Yoga, Karana, Vaara)
        - **Life predictions** for personality, wealth, career, marriage, health and spirituality
        - **Current Dasha timing** and year-ahead themes
        - **Lucky elements** and cautions from your chart
        - Downloadable Markdown report
        """
    )
    st.stop()

pred = st.session_state["prediction"]
pc = pred["panchang_at_birth"]

st.markdown(
    f"""
    <div class="pcard">
      <div class="pred-title">{pred['name']}</div>
      <div style="color:#9aa3b8;margin-top:4px">
        Born {pred['birth']['date']} at {pred['birth']['time']} \u00b7 {pred['birth']['place']}<br>
        Lagna: {pred['birth']['lagna']} \u00b7 Focus: {pred['focus_intent']}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Birth Panchang (at your birth time)")
p1, p2, p3, p4, p5 = st.columns(5)
for col, label, val in zip(
    [p1, p2, p3, p4, p5],
    ["Vaara", "Tithi", "Nakshatra", "Yoga", "Karana"],
    [pc["vaara"], pc["tithi"],
     f"{pc['nakshatra']} (p.{pc['nakshatra_pada']})", pc["yoga"], pc["karana"]],
):
    col.markdown(f"**{label}**  \n{val}")

st.markdown("### Overview")
st.markdown(f"<div class='pcard'>{pred['opening']}</div>", unsafe_allow_html=True)

st.markdown("### Life predictions")
for lp in pred["life_predictions"]:
    chip_class = {"Supported": "chip-ok", "Mixed": "chip-mix", "Challenged": "chip-bad"}[lp["verdict"]]
    st.markdown(
        f"""
        <div class="pcard">
          <span class="{chip_class}">{lp['verdict']}</span>
          <div class="pred-title" style="margin-top:8px">{lp['area']}</div>
          <div style="margin-top:6px">{lp['prediction']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Your focus area")
for fl in pred["focus_detail"]:
    st.markdown(f"- {fl}")

st.markdown("### Timing & year ahead")
t = pred["timing"]
st.markdown(
    f"<div class='pcard'>"
    f"Birth Nakshatra: <b>{t['birth_nakshatra']}</b> (Dasha lord: {t['birth_nakshatra_lord']})<br>"
    f"Current: <b>{t['current_maha'] or '—'}</b> Mahadasha"
    + (f" / {t['current_antar']} Antardasha" if t.get("current_antar") else "")
    + f"<br>{t['year_ahead']}<br>"
    f"Sade Sati: {t['sade_sati']}"
    f"</div>",
    unsafe_allow_html=True,
)

if pred["cautions"]:
    st.markdown("### Cautions")
    for c in pred["cautions"]:
        st.warning(c)

lk = pred["lucky"]
st.markdown("### Favourable elements")
st.markdown(
    f"<div class='pcard'>"
    f"Weekday energy: {lk['day']} \u00b7 Birth star: {lk['nakshatra']} "
    f"(lord {lk['nakshatra_lord']}) \u00b7 "
    f"Gemstone hint: {lk['gemstone_hint']}"
    f"</div>",
    unsafe_allow_html=True,
)

md = prediction_markdown(pred)
st.download_button("Download prediction report (Markdown)", md,
                   file_name=f"prediction_{pred['name'].replace(' ','_')}.md",
                   mime="text/markdown", use_container_width=True)

st.caption(
    "Predictions merge sidereal chart analysis with Panchang at birth. "
    "Use alongside the main Horoscope app for full chart details and remedies."
)
