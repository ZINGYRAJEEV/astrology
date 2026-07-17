"""Festivals & Vrats — monthly Hindu festival and observance calendar."""

from __future__ import annotations

import calendar
from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro.festivals import compute_festivals, festivals_markdown

st.set_page_config(page_title="Festivals & Vrats", page_icon="\U0001fa94", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg,#070912,#0c1020); color:#e8ebf2; }
      h1,h2,h3 { color:#f5c542 !important; font-family:'Georgia',serif; }
      .pcard { background:rgba(28,33,54,0.55); border:1px solid rgba(245,197,66,0.14);
               border-radius:16px; padding:14px 18px; margin-bottom:10px; }
      .tag-festival { background:#f5c542;color:#0b0e1a;padding:2px 10px;border-radius:999px;font-size:12px; }
      .tag-vrat { background:#8fbcff;color:#0b0e1a;padding:2px 10px;border-radius:999px;font-size:12px; }
      .tag-sankranti { background:#ffa86b;color:#0b0e1a;padding:2px 10px;border-radius:999px;font-size:12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# \U0001fa94 Festivals & Vrats")
st.caption(
    "Monthly festival, vrat & Sankranti calendar \u00b7 derived from the tithi engine "
    "\u00b7 North-Indian / Rishikesh convention"
)

_TAG = {"festival": "tag-festival", "vrat": "tag-vrat", "sankranti": "tag-sankranti"}
_TAG_LABEL = {"festival": "Festival", "vrat": "Vrat", "sankranti": "Sankranti"}

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    year = st.number_input("Year", min_value=1900, max_value=2100, value=date.today().year)
with c2:
    month = st.selectbox("Month", list(range(1, 13)),
                         index=date.today().month - 1,
                         format_func=lambda m: calendar.month_name[m])
with c3:
    mode = st.radio("Location", ["Pick a city", "Manual lat/long"], horizontal=True,
                    key="fc_place_mode")
    if mode == "Pick a city":
        idx = geo.PLACE_NAMES.index("Rishikesh, India") if "Rishikesh, India" in geo.PLACE_NAMES else 0
        city = st.selectbox("Place", geo.PLACE_NAMES, index=idx, key="fc_city")
        info = geo.resolve_place(city)
        lat, lon, place, tz_name, tz_manual = (info.latitude, info.longitude, info.name,
                                               info.timezone, None)
    else:
        lat = st.number_input("Latitude", value=30.0869, format="%.4f", key="fc_lat")
        lon = st.number_input("Longitude", value=78.2676, format="%.4f", key="fc_lon")
        tz_manual = st.number_input("UTC offset (hours)", value=5.5, step=0.25, format="%.2f",
                                    key="fc_tz")
        place, tz_name = f"{lat:.3f},{lon:.3f}", None

if st.button("Show calendar", type="primary", use_container_width=True):
    if tz_name:
        tz_off = geo.tz_offset_hours(tz_name, datetime(int(year), int(month), 15, 12, 0))
    else:
        tz_off = tz_manual
    with st.spinner("Computing the month's Panchang…"):
        st.session_state["festivals"] = {
            "events": compute_festivals(int(year), int(month), lat, lon, tz_off, place),
            "year": int(year), "month": int(month), "place": place,
        }

data = st.session_state.get("festivals")
if not data:
    st.info("Pick a month, year and location, then click **Show calendar**.")
    st.markdown(
        """
        ### What you'll see
        - **Festivals** — Diwali, Holi, Navratri, Janmashtami, Ganesh Chaturthi, and more
        - **Vrats** — Ekadashi, Pradosh, Sankashti/Vinayaka Chaturthi, Purnima, Amavasya
        - **Sankranti** — the Sun's monthly ingress into a new sign (incl. Makar Sankranti)
        """
    )
    st.stop()

events = data["events"]
st.markdown(f"## {calendar.month_name[data['month']]} {data['year']} · {data['place']}")

# Quick filter.
show = st.multiselect("Show", ["festival", "vrat", "sankranti"],
                      default=["festival", "vrat", "sankranti"],
                      format_func=lambda t: _TAG_LABEL[t])
filtered = [e for e in events if e["type"] in show]

if not filtered:
    st.info("No observances match the current filter for this month.")
else:
    cur = None
    for e in filtered:
        if e["date"] != cur:
            cur = e["date"]
            st.markdown(f"#### {e['date'].strftime('%A, %d %b')}")
        st.markdown(
            f"<div class='pcard'>"
            f"<span class='{_TAG[e['type']]}'>{_TAG_LABEL[e['type']]}</span> "
            f"<b style='color:#ffe9a8;font-size:16px'>&nbsp;{e['name']}</b>"
            f"<div style='margin-top:4px'>{e['note']}</div>"
            f"<div style='margin-top:4px;color:#9aa3b8;font-size:13px'>"
            f"{e['tithi']} · {e['nakshatra']} · {e['hindu_month']} maas</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.download_button(
        "Download calendar (Markdown)",
        festivals_markdown(filtered, data["year"], data["month"]),
        file_name=f"festivals_{data['year']}_{data['month']:02d}.md",
        mime="text/markdown",
        use_container_width=True,
    )

st.caption(
    "Recurring vrats are exact to the tithi; festival dates follow the Purnimanta "
    "month boundary (approximate) — confirm exact timings with a local Panchang."
)
