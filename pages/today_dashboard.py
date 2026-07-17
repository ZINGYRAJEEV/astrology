"""Today for You — personalised daily dashboard for a saved/entered chart."""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro import persistence
from astro.chart_engine import BirthData, compute_chart
from astro.daily_dashboard import build_dashboard

st.set_page_config(page_title="Today for You", page_icon="\U0001f31e", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg,#070912,#0c1020); color:#e8ebf2; }
      h1,h2,h3 { color:#f5c542 !important; font-family:'Georgia',serif; }
      .pcard { background:rgba(28,33,54,0.55); border:1px solid rgba(245,197,66,0.14);
               border-radius:16px; padding:16px 20px; margin-bottom:10px; }
      .metric-big { font-size:38px; font-weight:700; color:#ffe9a8; }
      .chip-ok { background:#6fcf97;color:#0b0e1a;padding:3px 12px;border-radius:999px;font-size:13px; }
      .chip-mix { background:#f2c94c;color:#0b0e1a;padding:3px 12px;border-radius:999px;font-size:13px; }
      .chip-bad { background:#ef6b6b;color:#0b0e1a;padding:3px 12px;border-radius:999px;font-size:13px; }
      .win { display:inline-block; background:rgba(111,207,151,0.12);
             border:1px solid rgba(111,207,151,0.35); border-radius:999px;
             padding:3px 12px; margin:3px 4px 0 0; font-size:13px; }
      .bad { display:inline-block; background:rgba(239,107,107,0.12);
             border:1px solid rgba(239,107,107,0.35); border-radius:999px;
             padding:3px 12px; margin:3px 4px 0 0; font-size:13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# \U0001f31e Today for You")
st.caption(
    "Personalised daily guidance \u00b7 your Panchang, Tarabala & Chandrabala, "
    "auspicious windows, Dasha & transits \u00b7 Rishikesh tradition"
)

_CHIP = {"Auspicious": "chip-ok", "Workable": "chip-mix", "Avoid": "chip-bad"}


def _location(default_place: str = "Rishikesh, India"):
    mode = st.radio("Today's location", ["Pick a city", "Manual lat/long"],
                    horizontal=True, key="td_place_mode")
    if mode == "Pick a city":
        idx = geo.PLACE_NAMES.index(default_place) if default_place in geo.PLACE_NAMES else 0
        city = st.selectbox("Where are you today?", geo.PLACE_NAMES, index=idx, key="td_city")
        info = geo.resolve_place(city)
        return info.latitude, info.longitude, info.name, info.timezone, None
    lat = st.number_input("Latitude", value=30.0869, format="%.4f", key="td_lat")
    lon = st.number_input("Longitude", value=78.2676, format="%.4f", key="td_lon")
    tz_manual = st.number_input("UTC offset (hours)", value=5.5, step=0.25, format="%.2f",
                                key="td_tz")
    return lat, lon, f"{lat:.3f},{lon:.3f}", None, tz_manual


# ---------------------------------------------------------------------------
# Whose day? — saved chart or manual birth entry
# ---------------------------------------------------------------------------
st.markdown("### Whose day?")
saved = persistence.list_charts()
options = ["Enter birth details"] + [f"{c['name']} — {c['summary']}" for c in saved]
choice = st.selectbox("Chart", options, key="td_choice")

birth = None
if choice == "Enter birth details":
    with st.expander("Birth details", expanded=True):
        name = st.text_input("Name", key="td_name", placeholder="Your name")
        c1, c2 = st.columns(2)
        with c1:
            b_date = st.date_input("Date of birth", value=date(1990, 1, 1),
                                   min_value=date(1800, 1, 1), max_value=date(2100, 12, 31),
                                   key="td_bdate")
        with c2:
            b_time = st.time_input("Time of birth", value=time(12, 0), step=60, key="td_btime")
        st.caption("Birth place")
        b_mode = st.radio("Birth location", ["Pick a city", "Manual lat/long"],
                          horizontal=True, key="td_bplace_mode")
        if b_mode == "Pick a city":
            idx = geo.PLACE_NAMES.index("Rishikesh, India") if "Rishikesh, India" in geo.PLACE_NAMES else 0
            bcity = st.selectbox("Birth place", geo.PLACE_NAMES, index=idx, key="td_bcity")
            binfo = geo.resolve_place(bcity)
            blat, blon, bplace, btz_name, btz_manual = (
                binfo.latitude, binfo.longitude, binfo.name, binfo.timezone, None)
        else:
            blat = st.number_input("Birth latitude", value=30.0869, format="%.4f", key="td_blat")
            blon = st.number_input("Birth longitude", value=78.2676, format="%.4f", key="td_blon")
            btz_manual = st.number_input("Birth UTC offset (hours)", value=5.5, step=0.25,
                                         format="%.2f", key="td_btz")
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

# ---------------------------------------------------------------------------
# Day & location
# ---------------------------------------------------------------------------
d1, d2 = st.columns([1, 2])
with d1:
    target = st.date_input("Day to check", value=date.today(),
                           min_value=date(1900, 1, 1), max_value=date(2100, 12, 31),
                           key="td_target")
with d2:
    default_place = birth.place if (birth and birth.place in geo.PLACE_NAMES) else "Rishikesh, India"
    lat, lon, place, tz_name, tz_manual = _location(default_place)

if st.button("Show my day", type="primary", use_container_width=True):
    if tz_name:
        tz_off = geo.tz_offset_hours(tz_name, datetime.combine(target, time(12, 0)))
    else:
        tz_off = tz_manual
    chart = compute_chart(birth)
    st.session_state["dashboard"] = build_dashboard(chart, target, lat, lon, tz_off, place)

db = st.session_state.get("dashboard")
if not db:
    st.info("Pick a chart, a day and your location, then click **Show my day**.")
    st.stop()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    f"<div class='pcard'>"
    f"<span class='{_CHIP[db['verdict']]}'>{db['verdict']} · {db['score']:.0f}%</span> "
    f"<b style='color:#ffe9a8;font-size:20px'>&nbsp;{db['name']}</b>"
    f"<div style='margin-top:8px;font-size:16px'>{db['headline']}</div>"
    f"<div style='margin-top:6px;color:#9aa3b8'>{db['date'].strftime('%A, %d %b %Y')} · "
    f"{db['weekday']} · {db['place']}</div>"
    f"</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Windows
# ---------------------------------------------------------------------------
wc1, wc2 = st.columns(2)
with wc1:
    st.markdown("#### \u2705 Good windows today")
    if db["good_windows"]:
        chips = "".join(
            f"<span class='win'>{w['name']}: {w['start']}–{w['end']}</span>"
            for w in db["good_windows"]
        )
        st.markdown(chips, unsafe_allow_html=True)
    else:
        st.markdown("_No clearly auspicious window today._")
    ab = db["panchang"]["abhijit"]
    st.caption(f"Abhijit Muhurta: {ab['start']}–{ab['end']} · "
               f"Brahma Muhurta: {db['panchang']['brahma_muhurta']['start']}–"
               f"{db['panchang']['brahma_muhurta']['end']}")
with wc2:
    st.markdown("#### \u26d4 Avoid these windows")
    chips = "".join(
        f"<span class='bad'>{w['name']}: {w['start']}–{w['end']}</span>"
        for w in db["avoid_windows"]
    )
    st.markdown(chips, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Panchang + personal notes
# ---------------------------------------------------------------------------
p = db["panchang"]
st.markdown("#### Today's Panchang")
st.markdown(
    f"Tithi **{p['tithi']}** · Nakshatra **{p['nakshatra']}** · Yoga **{p['yoga']}** · "
    f"Karana **{p['karana']}**  \nSunrise {p['sunrise']} · Sunset {p['sunset']}"
)

st.markdown("#### Why this score")
for note in db["positives"]:
    st.markdown(f"- {note}")
if db["warnings"]:
    for w in db["warnings"]:
        st.warning(w)

# ---------------------------------------------------------------------------
# Timing (Dasha + transits)
# ---------------------------------------------------------------------------
st.markdown("#### Where you are (timing)")
st.markdown(db["dasha"]["line"])
st.markdown(f"- {db['sade_sati']['note']}")
st.markdown(f"- {db['guru_gochar']}")

st.caption(
    f"Personalised for Janma Nakshatra {db['janma_nakshatra']} · Moon sign {db['moon_sign']}. "
    "Rishikesh tradition · for reflection and guidance."
)
