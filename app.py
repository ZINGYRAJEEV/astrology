"""Jyotish Darshan - Vedic Horoscope Interpretation.

Streamlit front-end implementing the 12-step interpretation framework from
the briefing across three phases:
  Phase 1 (steps 1-5): birth data -> chart -> ascendant -> style -> intent.
  Phase 2 (steps 6-11): strengths, house-by-house judging, repeating patterns.
  Phase 3 (step 12): synthesis, timing, remedies, downloadable report.
"""

from __future__ import annotations

from datetime import datetime, date, time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from astro import reference as ref
from astro import geo
from astro.chart_engine import BirthData, compute_chart, format_dms
from astro.strength_calc import all_strengths, chart_foundation_score
from astro.aspects import aspects_on_house
from astro.dasha_calc import (
    compute_vimshottari, current_dasha, starting_nakshatra, sade_sati_status,
)
from astro.viewer import chart_svg
from astro.interpret import (
    analyse_all_houses, repeating_patterns, functional_nature,
    recommend_remedies, synthesize, plain_language_reading, INTENT_HOUSES,
)
from astro.ashtakavarga import compute_sav
from astro import wisdom
from astro.report import build_markdown, build_pdf
from astro.prediction import generate_prediction, prediction_markdown
from astro import persistence

st.set_page_config(page_title="Jyotish Darshan", page_icon="\u2728", layout="wide")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

      :root {
        --gold:#f5c542; --gold-soft:#ffe9a8; --ink:#e8ebf2; --muted:#9aa3b8;
        --bg0:#070912; --bg1:#0c1020; --panel:rgba(28,33,54,0.55);
        --border:rgba(245,197,66,0.14); --green:#6fcf97; --red:#ef6b6b; --amber:#f2c94c;
      }

      /* Cosmic gradient backdrop with a soft starfield glow. */
      .stApp, [data-testid="stAppViewContainer"] {
        background:
          radial-gradient(1200px 600px at 15% -10%, rgba(123,97,255,0.18), transparent 60%),
          radial-gradient(1000px 500px at 90% 0%, rgba(245,197,66,0.10), transparent 55%),
          radial-gradient(800px 800px at 80% 110%, rgba(86,160,255,0.10), transparent 60%),
          linear-gradient(180deg, var(--bg0), var(--bg1));
        background-attachment: fixed;
        color: var(--ink);
        font-family: 'Inter', system-ui, sans-serif;
      }
      [data-testid="stHeader"] { background: transparent; }

      /* Sidebar as a frosted glass panel. */
      [data-testid="stSidebar"] {
        background: rgba(10,13,26,0.75);
        backdrop-filter: blur(14px);
        border-right: 1px solid var(--border);
      }
      [data-testid="stSidebar"] * { color: var(--ink) !important; }

      /* Body text contrast. */
      .stApp p, .stApp li, .stApp span, .stApp label,
      .stMarkdown, [data-testid="stMarkdownContainer"] { color: var(--ink); }
      [data-testid="stCaptionContainer"], .stCaption { color: var(--muted) !important; }

      h1, h2, h3, h4 {
        font-family: 'Cormorant Garamond', serif !important;
        color: var(--gold) !important; letter-spacing: .3px; font-weight: 700;
      }

      /* Tabs as a modern segmented control. */
      [data-baseweb="tab-list"] {
        gap: 6px; background: rgba(255,255,255,0.03);
        padding: 6px; border-radius: 14px; border: 1px solid var(--border);
      }
      button[data-baseweb="tab"] {
        background: transparent; border-radius: 10px; padding: 8px 16px;
        color: var(--muted); font-weight: 600; font-family:'Inter';
      }
      button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(245,197,66,0.22), rgba(123,97,255,0.18));
        color: var(--gold-soft) !important;
        box-shadow: inset 0 0 0 1px var(--border);
      }
      [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { background: transparent !important; }

      /* Buttons. */
      .stButton > button, .stDownloadButton > button {
        border-radius: 12px; border: 1px solid var(--border);
        background: rgba(255,255,255,0.04); color: var(--ink);
        font-weight: 600; transition: all .18s ease;
      }
      .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: var(--gold); color: var(--gold-soft);
        transform: translateY(-1px); box-shadow: 0 6px 20px rgba(245,197,66,0.12);
      }
      .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f5c542, #e7a93b);
        color: #1a1407; border: none;
        box-shadow: 0 8px 24px rgba(245,197,66,0.28);
      }

      /* Inputs. */
      [data-baseweb="input"], [data-baseweb="select"] > div, .stDateInput input, .stTimeInput input {
        border-radius: 10px !important;
      }

      /* Expanders + dataframes as glass. */
      [data-testid="stExpander"] {
        border: 1px solid var(--border); border-radius: 14px;
        background: var(--panel); backdrop-filter: blur(8px); overflow: hidden;
      }
      [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

      /* Custom components. */
      .verdict-Supported { color: var(--green); font-weight: 700; }
      .verdict-Challenged { color: var(--red); font-weight: 700; }
      .verdict-Mixed { color: var(--amber); font-weight: 700; }
      .pill { display:inline-block; padding:3px 12px; border-radius:999px;
              font-size:12px; margin:2px; background:rgba(255,255,255,0.06);
              border:1px solid var(--border); color:#cbd2e0; }
      .card {
        background: var(--panel); border: 1px solid var(--border);
        border-radius: 16px; padding: 16px 20px; margin-bottom: 12px;
        color: var(--ink); backdrop-filter: blur(10px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
        transition: transform .18s ease, border-color .18s ease;
      }
      .card:hover { transform: translateY(-2px); border-color: rgba(245,197,66,0.30); }
      .card b { color: #fff; }
      .metric-big {
        font-size: 34px; font-weight: 700; font-family:'Cormorant Garamond',serif;
        background: linear-gradient(135deg, var(--gold), var(--gold-soft));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      }
      .subtle { color: var(--muted); font-size: 13px; letter-spacing:.3px; }

      /* Hero + feature cards (landing). */
      .hero-title {
        font-family:'Cormorant Garamond',serif; font-size: 64px; font-weight:700;
        line-height:1.05; margin:0;
        background: linear-gradient(120deg,#fff 10%, var(--gold) 50%, #b89bff 90%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      }
      .hero-sub { color: var(--muted); font-size:18px; margin-top:10px; max-width:680px; }
      .feature {
        background: var(--panel); border:1px solid var(--border); border-radius:18px;
        padding:22px; height:100%; backdrop-filter: blur(10px);
        transition: transform .2s ease, border-color .2s ease;
      }
      .feature:hover { transform: translateY(-4px); border-color: rgba(245,197,66,0.35); }
      .feature .num { font-family:'Cormorant Garamond',serif; font-size:30px; color:var(--gold); }
      .feature h4 { margin:.2rem 0 .4rem 0; }
      .page-title {
        font-family:'Cormorant Garamond',serif; font-size:40px; font-weight:700;
        background: linear-gradient(120deg,#fff, var(--gold));
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:0;
      }
      hr { border-color: var(--border); }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------
def get_chart():
    return st.session_state.get("chart")


def set_chart(chart):
    st.session_state["chart"] = chart


# ---------------------------------------------------------------------------
# Sidebar - birth data input (Phase 1, steps 1-3) + saved charts
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## \u2728 Jyotish Darshan")
    st.caption("Vedic horoscope interpretation - Lahiri sidereal")

    st.markdown("### Birth Data")
    name = st.text_input("Name", value=st.session_state.get("f_name", ""))

    col_a, col_b = st.columns(2)
    with col_a:
        b_date = st.date_input(
            "Date of birth", value=st.session_state.get("f_date", date(1990, 1, 1)),
            min_value=date(1800, 1, 1), max_value=date(2100, 12, 31),
        )
    with col_b:
        b_time = st.time_input(
            "Time of birth", value=st.session_state.get("f_time", time(12, 0)),
            step=60,
        )
    st.caption("Birth time accuracy is mission-critical for the Ascendant.")

    place_mode = st.radio("Location", ["Pick a city", "Manual lat/long"], horizontal=True)
    if place_mode == "Pick a city":
        city = st.selectbox("City", list(geo.CITIES.keys()))
        lat, lon, tzname = geo.CITIES[city]
        place_label = city
        try:
            tz_off = geo.tz_offset_hours(
                tzname, datetime.combine(b_date, b_time))
        except Exception:
            tz_off = geo.tz_offset_hours(tzname, datetime.now())
        st.caption(f"Lat {lat:.3f}, Lon {lon:.3f}, UTC{tz_off:+.2f} ({tzname})")
    else:
        lat = st.number_input("Latitude", value=28.6139, format="%.4f")
        lon = st.number_input("Longitude", value=77.2090, format="%.4f")
        tz_off = st.number_input("UTC offset (hours)", value=5.5, step=0.25, format="%.2f")
        place_label = f"{lat:.3f},{lon:.3f}"

    if st.button("Calculate Chart", type="primary", use_container_width=True):
        birth = BirthData(
            name=name, year=b_date.year, month=b_date.month, day=b_date.day,
            hour=b_time.hour, minute=b_time.minute,
            latitude=lat, longitude=lon, tz_offset=tz_off, place=place_label,
        )
        set_chart(compute_chart(birth))
        st.session_state.update(f_name=name, f_date=b_date, f_time=b_time)
        st.success("Chart calculated.")

    st.divider()
    st.markdown("### Saved Charts")
    if get_chart() is not None:
        if st.button("\U0001f4be Save current chart", use_container_width=True):
            persistence.save_chart(get_chart().birth)
            st.success("Saved.")
    for item in persistence.list_charts():
        c1, c2 = st.columns([4, 1])
        with c1:
            if st.button(f"{item['name']} - {item['summary']}", key=f"load_{item['id']}",
                         use_container_width=True):
                set_chart(compute_chart(persistence.load_birth(item["id"])))
                st.rerun()
        with c2:
            if st.button("\U0001f5d1", key=f"del_{item['id']}"):
                persistence.delete_chart(item["id"])
                st.rerun()


# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
chart = get_chart()
if chart is None:
    st.markdown(
        """
        <div style="padding:40px 0 8px 0">
          <div style="font-size:14px;letter-spacing:4px;color:#9aa3b8;text-transform:uppercase;">
            Jyotish &middot; The Lore of Light
          </div>
          <div class="hero-title">Jyotish Darshan</div>
          <div class="hero-sub">
            A modern lens on an ancient science. Build a sidereal birth chart and walk
            the classical 12-step interpretation &mdash; positions, strengths, aspects,
            timing and remedies &mdash; in three guided phases.
          </div>
          <div style="margin-top:18px;color:#f5c542;font-size:15px;">
            &#9776; Enter birth details in the sidebar, then press
            <b>Calculate Chart</b> to begin.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        "<div class='feature'><div class='num'>I</div><h4>Construction</h4>"
        "<span class='subtle'>Birth data, Lahiri sidereal positions, the Lagna, "
        "South/North Indian chart styles, and your focus.</span></div>",
        unsafe_allow_html=True)
    c2.markdown(
        "<div class='feature'><div class='num'>II</div><h4>Evaluation</h4>"
        "<span class='subtle'>Planetary dignity & strength, house-by-house judging, "
        "Graha Drishti aspects, and repeating-pattern detection.</span></div>",
        unsafe_allow_html=True)
    c3.markdown(
        "<div class='feature'><div class='num'>III</div><h4>Synthesis</h4>"
        "<span class='subtle'>A written reading, Vimshottari Dasha timing, and "
        "'Do No Harm' remedies with a downloadable report.</span></div>",
        unsafe_allow_html=True)
    st.stop()


# Top-line intent selector (Phase 1, step 5) and chart-style toggle (step 4).
top1, top2, top3 = st.columns([2, 2, 2])
with top1:
    intent = st.selectbox("Your focus (client intent)", list(INTENT_HOUSES.keys()),
                          index=len(INTENT_HOUSES) - 1)
with top2:
    style = st.radio("Chart style", ["South Indian", "North Indian"], horizontal=True)
with top3:
    varga = st.radio("Chart", ["D1 (Rashi)", "D9 (Navamsha)"], horizontal=True)
varga_key = "D9" if varga.startswith("D9") else "D1"

b = chart.birth
moon = chart.planets["Moon"]
st.markdown(
    f"""
    <div class="card" style="margin-top:6px;display:flex;justify-content:space-between;
         align-items:center;flex-wrap:wrap;gap:10px">
      <div>
        <div class="page-title">{b.name or 'Native'}</div>
        <div class="subtle" style="margin-top:4px">
          {b.day:02d}/{b.month:02d}/{b.year} &middot; {b.hour:02d}:{b.minute:02d}
          (UTC{b.tz_offset:+.2f}) &middot; {b.place} &middot;
          Lahiri Ayanamsha {chart.ayanamsha:.3f}&deg;
        </div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <span class="pill">Lagna: <b style="color:#ffe9a8">{chart.lagna_sign}</b></span>
        <span class="pill">Moon: <b style="color:#ffe9a8">{moon.sign}</b></span>
        <span class="pill">Nakshatra: <b style="color:#ffe9a8">{moon.nakshatra}</b></span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_pred, tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "\U0001f52e Predictions", "\U0001f4d6 Your Reading", "Phase 1 - Chart",
    "Phase 2 - Evaluation", "Phase 3 - Synthesis", "Timing & Transits", "\U0001fab7 Witness",
])

# ===========================================================================
# PREDICTIONS - chart + Panchang at birth (name, date, time, place)
# ===========================================================================
with tab_pred:
    pred = generate_prediction(chart, intent)
    pc = pred["panchang_at_birth"]

    st.markdown(
        f"""
        <div class="card" style="border-color:rgba(245,197,66,0.35)">
          <div class="subtle" style="letter-spacing:3px;text-transform:uppercase">
            Personal prediction &middot; {pred['focus_intent']}
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:22px;
               color:#ffe9a8;line-height:1.4;margin-top:6px">{pred['opening'][:280]}...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Birth Panchang (at your birth time)")
    pp1, pp2, pp3, pp4, pp5 = st.columns(5)
    for col, label, val in zip(
        [pp1, pp2, pp3, pp4, pp5],
        ["Vaara", "Tithi", "Nakshatra", "Yoga", "Karana"],
        [pc["vaara"], pc["tithi"],
         f"{pc['nakshatra']} (pada {pc['nakshatra_pada']})", pc["yoga"], pc["karana"]],
    ):
        col.markdown(f"**{label}**  \n{val}")

    st.markdown("#### Life predictions")
    for lp in pred["life_predictions"]:
        chip = {"Supported": "#6fcf97", "Mixed": "#f2c94c", "Challenged": "#ef6b6b"}[lp["verdict"]]
        st.markdown(
            f"""
            <div class="card">
              <span class="pill" style="background:{chip};color:#0b0e1a;border:none">{lp['verdict']}</span>
              <b style="font-size:17px;color:#fff;display:block;margin-top:8px">{lp['area']}</b>
              <div style="margin-top:6px">{lp['prediction']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Year ahead (Dasha timing)")
    t = pred["timing"]
    st.markdown(
        f"<div class='card'>"
        f"Current period: <b>{t['current_maha'] or '—'}</b> Mahadasha"
        + (f" / {t['current_antar']} Antardasha" if t.get('current_antar') else "")
        + f"<br>{t['year_ahead']}<br><span class='subtle'>Sade Sati: {t['sade_sati']}</span></div>",
        unsafe_allow_html=True,
    )

    if pred["cautions"]:
        st.markdown("#### Cautions")
        for c in pred["cautions"]:
            st.markdown(f"<div class='card' style='border-color:rgba(239,107,107,0.3)'>{c}</div>",
                        unsafe_allow_html=True)

    lk = pred["lucky"]
    st.markdown(
        f"<div class='card'><b>Favourable:</b> weekday {lk['day']}, "
        f"star {lk['nakshatra']} (lord {lk['nakshatra_lord']}), "
        f"gemstone hint {lk['gemstone_hint']}</div>",
        unsafe_allow_html=True,
    )

    st.download_button(
        "Download full prediction (Markdown)",
        prediction_markdown(pred),
        file_name=f"prediction_{(pred['name'] or 'chart').replace(' ', '_')}.md",
        mime="text/markdown",
    )
    st.caption("For remedies and technical chart details, see Phase 3 and Evaluation tabs.")

# ===========================================================================
# YOUR READING - plain-language, intent-focused (beginner friendly)
# ===========================================================================
with tab0:
    reading = plain_language_reading(chart, intent)

    st.markdown(
        f"""
        <div class="card" style="border-color:rgba(245,197,66,0.35)">
          <div class="subtle" style="letter-spacing:3px;text-transform:uppercase">
            Reading focus &middot; {reading['title']}
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:26px;
               color:#ffe9a8;line-height:1.3;margin-top:6px">
            {reading.get('headline', '')}
          </div>
          <div style="margin-top:10px;color:#d9ccff;font-size:15px;line-height:1.5">
            {reading.get('headline_extra', '')}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"This page explains, in plain language, what your chart suggests about "
        f"{reading['intro']}. No astrology knowledge needed."
    )

    st.markdown("#### In simple terms")
    st.markdown(f"<div class='card'>{reading['overview']}</div>", unsafe_allow_html=True)

    st.markdown("#### What your chart says about this focus")
    for a in reading["key_areas"]:
        chip = {
            "Supported": ("#6fcf97", "Favourable"),
            "Mixed": ("#f2c94c", "Mixed"),
            "Challenged": ("#ef6b6b", "Needs effort"),
        }[a["verdict"]]
        st.markdown(
            f"""
            <div class="card">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <b style="font-size:17px;color:#fff">{a['title']}</b>
                <span class="pill" style="background:{chip[0]};color:#0b0e1a;border:none">
                  {chip[1]}</span>
              </div>
              <div class="subtle" style="margin:6px 0 8px 0">{a['meaning']}</div>
              <div>{a['explanation']}</div>
              <div style="margin-top:8px;color:#ffe9a8">&#10148; {a['advice']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if reading["timing"]:
        st.markdown("#### What's happening in your life right now")
        st.markdown(f"<div class='card'>{reading['timing']}</div>", unsafe_allow_html=True)

    st.markdown("#### Simple action steps")
    steps_html = "".join(
        f"<li style='margin-bottom:6px'>{s}</li>" for s in reading["actions"]
    )
    st.markdown(
        f"<div class='card'><ul style='margin:0;padding-left:20px'>{steps_html}</ul></div>",
        unsafe_allow_html=True,
    )

    st.caption(
        "Want the technical details behind this? See the Phase 1-3 tabs. "
        "Remedies (gemstones, mantras) are in Phase 3."
    )

# ===========================================================================
# PHASE 1 - Chart construction & identification
# ===========================================================================
with tab1:
    left, right = st.columns([1, 1])
    with left:
        svg = chart_svg(chart, style=style, varga=varga_key, size=460)
        components.html(
            f'<div style="display:flex;justify-content:center">{svg}</div>',
            height=480,
        )
    with right:
        st.markdown("#### Planetary Positions")
        rows = []
        strengths = all_strengths(chart)
        for nm in ref.PLANETS:
            p = chart.planets[nm]
            rows.append({
                "Planet": nm + (" \u211e" if p.retrograde else ""),
                "Sign": p.sign,
                "Deg": format_dms(p.degree_in_sign),
                "House": p.house,
                "Nakshatra": f"{p.nakshatra} ({p.nakshatra_pada})",
                "Dignity": strengths[nm].dignity,
            })
        st.dataframe(rows, hide_index=True, use_container_width=True, height=360)

        asc_lord = ref.SIGN_LORD[chart.lagna_sign]
        st.markdown(
            f"<div class='card'><b>Ascendant (Lagna):</b> {chart.lagna_sign} "
            f"({ref.SIGN_SANSKRIT[chart.lagna_sign]})<br>"
            f"<b>Lagnesh (chart ruler):</b> {asc_lord} \u2014 in house "
            f"{chart.planet_house(asc_lord)}, {strengths[asc_lord].dignity}<br>"
            f"<b>Navamsha Lagna:</b> {chart.navamsha_lagna_sign}</div>",
            unsafe_allow_html=True,
        )

# ===========================================================================
# PHASE 2 - Evaluation of indicators
# ===========================================================================
with tab2:
    strengths = all_strengths(chart)
    foundation = chart_foundation_score(chart)
    nature = functional_nature(chart)

    st.markdown("### Step 6 - Overall Foundation")
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"<div class='card'><div class='metric-big'>{foundation['average_percent']}%</div>"
                f"<div class='subtle'>avg dignity</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='card'><div class='metric-big'>{len(foundation['exalted'])}</div>"
                f"<div class='subtle'>exalted</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='card'><div class='metric-big'>{len(foundation['debilitated'])}</div>"
                f"<div class='subtle'>debilitated</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='card'><div class='metric-big'>{len(foundation['vargottama'])}</div>"
                f"<div class='subtle'>vargottama</div></div>", unsafe_allow_html=True)

    st.markdown("### Step 7 - Individual Planetary Strength")
    prows = []
    for nm in ref.PLANETS:
        s = strengths[nm]
        p = chart.planets[nm]
        prows.append({
            "Planet": nm,
            "Dignity": s.dignity,
            "Strength %": s.percent,
            "Natural (virupas)": s.naisargika or "\u2014",
            "House": p.house,
            "Functional": nature[nm]["nature"] + (" (Yogakaraka)" if nature[nm]["yogakaraka"] else ""),
            "Vargottama": "Yes" if s.vargottama else "",
            "Notes": s.notes,
        })
    st.dataframe(prows, hide_index=True, use_container_width=True)

    # --- Ashtakavarga (Sarvashtakavarga) ---------------------------------
    st.markdown("### Sarvashtakavarga - the Math of Opportunity")
    sav = compute_sav(chart)
    st.caption(
        f"Total {sav['total']} bindus across 12 houses (average "
        f"{sav['average']:.0f}). 30+ = highly auspicious \u00b7 25-30 = stable \u00b7 "
        f"below 25 = challenging."
    )
    sav_rows = []
    for h in range(1, 13):
        ph = sav["per_house"][h]
        sav_rows.append({
            "House": h,
            "Name": ref.HOUSE_NAME[h],
            "Sign": ph["sign"],
            "Bindus": ph["points"],
            "Strength": ph["class"],
        })
    cc1, cc2 = st.columns([3, 2])
    with cc1:
        chart_df = pd.DataFrame(
            {"Bindus": [sav["per_house"][h]["points"] for h in range(1, 13)]},
            index=[f"H{h}" for h in range(1, 13)],
        )
        st.bar_chart(chart_df, height=240, color="#f5c542")
    with cc2:
        st.dataframe(sav_rows, hide_index=True, use_container_width=True, height=240)

    st.markdown("### Steps 8-9 - House-by-House Judging")
    reports = analyse_all_houses(chart)
    for h in range(1, 13):
        r = reports[h]
        emphasised = h in INTENT_HOUSES.get(intent, [])
        title = f"House {h} - {r.name} ({r.sign}) " + ("\u2b50 " if emphasised else "")
        with st.expander(title + f"  \u2014  {r.verdict}", expanded=emphasised):
            st.markdown(f"*{r.signification}*  \n`{r.category}`")
            occ_txt = ", ".join(r.occupants) or "\u2014"
            asp_txt = ", ".join(r.aspecting) or "\u2014"
            st.markdown(
                f"**Lord:** {r.lord} ({r.lord_dignity}, {r.lord_strength}%) in house {r.lord_house}  \n"
                f"**Occupants:** {occ_txt}  \n"
                f"**Aspected by:** {asp_txt}  \n"
                f"**Ashtakavarga:** {r.sav_points} bindus ({r.sav_class})"
            )
            st.markdown(
                f"**Verdict:** <span class='verdict-{r.verdict}'>{r.verdict}</span>",
                unsafe_allow_html=True,
            )
            for sgl in r.signals:
                st.markdown(f"- {sgl}")

    st.markdown("### Step 11 - Repeating Patterns")
    patterns = repeating_patterns(chart)
    if not patterns:
        st.info("No high-confidence repeating patterns detected.")
    for p in patterns:
        icon = "\u2705" if p["direction"] == "favourable" else "\u26a0\ufe0f"
        st.markdown(
            f"<div class='card'>{icon} <b>House {p['house']} - {p['theme']}</b> "
            f"({p['count']} agreeing indicators): {p['detail']}</div>",
            unsafe_allow_html=True,
        )

# ===========================================================================
# PHASE 3 - Synthesis & reporting
# ===========================================================================
with tab3:
    syn = synthesize(chart, intent)
    st.markdown("### Step 12 - Synthesis & Recommendations")
    for para in syn["paragraphs"]:
        st.markdown(f"<div class='card'>{para}</div>", unsafe_allow_html=True)

    st.markdown("### Remedial Measures (Upaye)")
    st.caption("Gated by the 'Do No Harm' rule - only functional benefics are strengthened "
               "with gemstones; functional malefics are pacified with mantra/charity only.")
    remedies = recommend_remedies(chart)
    if not remedies:
        st.success("Functional benefics are reasonably strong; no urgent remedies indicated.")
    for rec in remedies:
        badge = "Strengthen" if rec["strengthen"] else "Pacify only"
        color = "#6fcf97" if rec["strengthen"] else "#f2c94c"
        st.markdown(
            f"<div class='card'><b>{rec['planet']}</b> "
            f"<span class='pill' style='background:{color};color:#0e1117'>{badge}</span><br>"
            f"<span class='subtle'>{rec['rationale']}</span><br>"
            f"\U0001f48e Gemstone: {rec['gemstone']}<br>"
            f"\U0001f549\ufe0f Mantra: {rec['mantra']}<br>"
            f"\U0001f64f Charity: {rec['charity']}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("### Download Report")
    md = build_markdown(chart, intent)
    d1, d2 = st.columns(2)
    with d1:
        st.download_button("\u2b07\ufe0f Markdown report", md,
                           file_name=f"{(b.name or 'chart').replace(' ', '_')}_report.md",
                           mime="text/markdown", use_container_width=True)
    with d2:
        try:
            pdf = build_pdf(chart, intent)
            st.download_button("\u2b07\ufe0f PDF report", pdf,
                               file_name=f"{(b.name or 'chart').replace(' ', '_')}_report.pdf",
                               mime="application/pdf", use_container_width=True)
        except Exception as e:
            st.caption(f"PDF unavailable: {e}")

    with st.expander("Preview full report"):
        st.markdown(md)

# ===========================================================================
# TIMING & TRANSITS - Vimshottari Dasha + Sade Sati
# ===========================================================================
with tab4:
    nak = starting_nakshatra(chart)
    st.markdown("### Vimshottari Dasha")
    st.caption(
        f"Birth Nakshatra: **{nak['nakshatra']}** (lord {nak['lord']}). "
        f"Balance of first Mahadasha at birth: {nak['balance_years']:.2f} years."
    )

    periods = compute_vimshottari(chart)
    maha, antar = current_dasha(periods)
    if maha:
        st.markdown(
            f"<div class='card'><b>Currently running:</b> {maha.lord} Mahadasha"
            + (f" / {antar.lord} Antardasha" if antar else "")
            + f"<br><span class='subtle'>{maha.start:%Y-%m-%d} \u2192 {maha.end:%Y-%m-%d}</span></div>",
            unsafe_allow_html=True,
        )

    drows = []
    for p in periods:
        running = "\u25b6 " if (maha and p.lord == maha.lord and p.start == maha.start) else ""
        drows.append({
            "Mahadasha": running + p.lord,
            "Start": p.start.strftime("%Y-%m-%d"),
            "End": p.end.strftime("%Y-%m-%d"),
            "Years": round(p.years, 1),
        })
    st.dataframe(drows, hide_index=True, use_container_width=True)

    if maha:
        with st.expander(f"Antardashas within {maha.lord} Mahadasha"):
            arows = [{
                "Antardasha": ("\u25b6 " if antar and a.lord == antar.lord else "") + a.lord,
                "Start": a.start.strftime("%Y-%m-%d"),
                "End": a.end.strftime("%Y-%m-%d"),
                "Years": round(a.years, 2),
            } for a in maha.antardashas]
            st.dataframe(arows, hide_index=True, use_container_width=True)

    st.markdown("### Gochara - Sade Sati")
    ss = sade_sati_status(chart)
    if ss["active"]:
        st.warning(
            f"Sade Sati is currently **active** - {ss['phase']}. "
            f"Saturn transits {ss['saturn_sign']}; natal Moon in {ss['moon_sign']}."
        )
    else:
        st.success(
            f"Not currently in Sade Sati. Saturn transits {ss['saturn_sign']}; "
            f"natal Moon in {ss['moon_sign']}."
        )

# ===========================================================================
# WITNESS - Jyotish meets the Ashtavakra Gita (Advaita Vedanta)
# ===========================================================================
with tab5:
    wr = wisdom.witness_reading(chart)
    st.markdown(
        f"""
        <div class="card" style="border-color:rgba(184,155,255,0.4)">
          <div class="subtle" style="letter-spacing:3px;text-transform:uppercase">
            The Witness &middot; Drashta
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:22px;
               color:#d9ccff;line-height:1.4;margin-top:6px">{wr['intro']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Reflections from your chart")
    for refl in wr["reflections"]:
        st.markdown(f"<div class='card'>{refl}</div>", unsafe_allow_html=True)

    st.markdown("#### The Navagrahas as actors in the play")
    st.caption("Each planet's role in the dream (Maya) and the Witness's view of the same.")
    wcols = st.columns(3)
    for i, nm in enumerate(ref.PLANETS):
        w = wr["planets"][nm]
        with wcols[i % 3]:
            st.markdown(
                f"""
                <div class="card" style="min-height:200px">
                  <b style="color:#ffe9a8;font-size:16px">{nm}
                    <span class="subtle">({ref.PLANET_SANSKRIT[nm]})</span></b>
                  <div class="subtle" style="margin:6px 0">{w['metaphysical']}</div>
                  <div><b>Dream:</b> {w['dream']}</div>
                  <div style="margin-top:4px"><b>Witness:</b> {w['witness']}</div>
                  <div style="margin-top:8px;color:#b89bff;font-style:italic">
                    &ldquo;{w['verse']}&rdquo;</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("#### The journey from Aries to Pisces")
    for stage, desc in wr["journey"]:
        st.markdown(
            f"<div class='card'><b style='color:#ffe9a8'>{stage}</b><br>{desc}</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="text-align:center;margin:30px 0 10px 0">
          <div style="font-family:'Cormorant Garamond',serif;font-size:30px;
               background:linear-gradient(120deg,#fff,#b89bff);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent">
            {wr['closing']}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    "<p class='subtle' style='text-align:center;margin-top:24px'>"
    "Jyotish Darshan \u00b7 for insight and self-reflection, not deterministic fate."
    "</p>", unsafe_allow_html=True,
)
