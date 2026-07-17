"""Muhurta Finder — auspicious electional timing (Rishikesh / Kashi tradition)."""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro import reference as ref
from astro.muhurta import ACTIVITIES, find_muhurta, muhurta_markdown

st.set_page_config(page_title="Muhurta Finder", page_icon="\U0001f550", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg,#070912,#0c1020); color:#e8ebf2; }
      h1,h2,h3 { color:#f5c542 !important; font-family:'Georgia',serif; }
      .pcard { background:rgba(28,33,54,0.55); border:1px solid rgba(245,197,66,0.14);
               border-radius:16px; padding:16px 20px; margin-bottom:10px; }
      .chip-ok { background:#6fcf97;color:#0b0e1a;padding:2px 10px;border-radius:999px;font-size:12px; }
      .chip-mix { background:#f2c94c;color:#0b0e1a;padding:2px 10px;border-radius:999px;font-size:12px; }
      .chip-bad { background:#ef6b6b;color:#0b0e1a;padding:2px 10px;border-radius:999px;font-size:12px; }
      .win { display:inline-block; background:rgba(111,207,151,0.12);
             border:1px solid rgba(111,207,151,0.35); border-radius:999px;
             padding:3px 12px; margin:3px 4px 0 0; font-size:13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# \U0001f550 Muhurta Finder")
st.caption(
    "Auspicious timing (Rishikesh / Kashi tradition) \u00b7 Phalita Navaratna scoring "
    "\u00b7 Rahu Kaal / Vishti / Rikta vetoes \u00b7 Lahiri sidereal"
)

_CHIP = {"Auspicious": "chip-ok", "Workable": "chip-mix", "Avoid": "chip-bad"}


def _location():
    mode = st.radio("Location", ["Pick a city", "Manual lat/long"], horizontal=True,
                    key="mh_place_mode")
    if mode == "Pick a city":
        idx = geo.PLACE_NAMES.index("Rishikesh, India") if "Rishikesh, India" in geo.PLACE_NAMES else 0
        city = st.selectbox("Place", geo.PLACE_NAMES, index=idx, key="mh_city")
        info = geo.resolve_place(city)
        return info.latitude, info.longitude, info.name, info.timezone, None
    lat = st.number_input("Latitude", value=30.0869, format="%.4f", key="mh_lat")
    lon = st.number_input("Longitude", value=78.2676, format="%.4f", key="mh_lon")
    tz_manual = st.number_input("UTC offset (hours)", value=5.5, step=0.25, format="%.2f",
                                key="mh_tz")
    return lat, lon, f"{lat:.3f},{lon:.3f}", None, tz_manual


with st.form("muhurta_form"):
    c1, c2 = st.columns(2)
    with c1:
        act_key = st.selectbox(
            "Activity", list(ACTIVITIES.keys()),
            format_func=lambda k: ACTIVITIES[k].label,
        )
        start = st.date_input("Search from", value=date.today(),
                              min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))
        num_days = st.slider("Number of days to scan", 1, 60, 14)
    with c2:
        lat, lon, place, tz_name, tz_manual = _location()

    st.markdown("#### Personalise (optional)")
    st.caption("Add your birth star & Moon sign to include Tarabala (60) and Chandrabala (100) "
               "— the highest-weighted factors for personal timing.")
    personalise = st.checkbox("Personalise for me")
    pc1, pc2 = st.columns(2)
    with pc1:
        janma_nak = st.selectbox("Your Janma Nakshatra (birth star)",
                                 ["—"] + ref.NAKSHATRAS, disabled=not personalise)
    with pc2:
        moon_sign = st.selectbox("Your Moon sign (Janma Rashi)",
                                 ["—"] + ref.SIGNS, disabled=not personalise)

    submitted = st.form_submit_button("Find Muhurta", type="primary", use_container_width=True)

if submitted:
    if tz_name:
        tz_off = geo.tz_offset_hours(tz_name, datetime.combine(start, time(12, 0)))
    else:
        tz_off = tz_manual
    jn = janma_nak if (personalise and janma_nak != "\u2014") else None
    ms = moon_sign if (personalise and moon_sign != "\u2014") else None
    st.session_state["muhurta"] = find_muhurta(
        act_key, start, num_days, lat, lon, tz_off, place,
        janma_nakshatra=jn, natal_moon_sign=ms,
    )

result = st.session_state.get("muhurta")
if not result:
    st.info("Choose an activity, date range and location, then click **Find Muhurta**.")
    st.markdown(
        """
        ### What this does
        - Scores each day using the **Phalita Navaratna** limb weights
          (Tithi 1 · Nakshatra 4 · Vara 8 · Karana 16 · Yoga 32)
        - Adds **Tarabala (60)** and **Chandrabala (100)** when you personalise
        - Recommends concrete **time windows** (auspicious Choghadiya + Abhijit Muhurta)
        - Vetoes **Rahu Kaal / Yamaganda / Gulika Kaal**, **Rikta Tithis**,
          **Vishti (Bhadra) Karana**, **Amavasya** and **Maha Yoga Doshas**
        """
    )
    st.stop()

st.markdown(f"### {result['activity']}")
st.caption(result["activity_note"])
mode_note = ("Personalised — Tarabala & Chandrabala included."
             if result["personalised"]
             else "General scan — tick *Personalise for me* to weight by your birth star.")
st.caption(mode_note)

st.markdown("## \u2b50 Top recommended dates")
if not result["top"]:
    st.warning("No clearly auspicious dates in this range. Try widening the date range.")
for r in result["top"]:
    bw = r.best_window
    when = f"{bw['name']} · {bw['start']}–{bw['end']}" if bw else "see windows below"
    st.markdown(
        f"<div class='pcard'>"
        f"<span class='{_CHIP[r.verdict]}'>{r.verdict} · {r.score:.0f}%</span> "
        f"<b style='color:#ffe9a8;font-size:17px'>&nbsp;{r.d.strftime('%A, %d %b %Y')}</b>"
        f"<div style='margin-top:6px'>Best window: <b>{when}</b></div>"
        f"<div style='margin-top:4px;color:#9aa3b8'>{r.nakshatra} nakshatra · "
        f"{r.tithi} · Yoga {r.yoga} · Karana {r.karana}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("## Day-by-day")
for r in result["days"]:
    header = f"{r.d.strftime('%a %d %b')} · {r.score:.0f}% ({r.verdict}) · {r.nakshatra}"
    with st.expander(header, expanded=False):
        st.markdown(
            f"**Tithi:** {r.tithi}  \n**Nakshatra:** {r.nakshatra}  \n"
            f"**Yoga:** {r.yoga}  \n**Karana:** {r.karana}"
        )
        if r.windows:
            st.markdown("**Auspicious windows**")
            chips = "".join(
                f"<span class='win'>{w['name']}: {w['start']}–{w['end']}</span>"
                for w in r.windows
            )
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.markdown("_No clear auspicious window today._")
        with st.container():
            st.markdown("**Panchang notes**")
            for p in r.positives:
                st.markdown(f"- {p}")
        if r.warnings:
            for w in r.warnings:
                st.warning(w)

st.download_button(
    "Download muhurta report (Markdown)",
    muhurta_markdown(result),
    file_name=f"muhurta_{result['activity'].split(' ')[0].lower()}_{result['start']}.md",
    mime="text/markdown",
    use_container_width=True,
)

st.caption(
    "Rishikesh Panchang tradition · for guidance and reflection. "
    "For life-critical events, confirm with a qualified astrologer."
)
