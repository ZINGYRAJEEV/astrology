"""AI & Tech Themes — Lahiri Prashna for collective / career / risk questions."""

from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from astro import geo
from astro.mundane_ai import AI_PRESETS, analyze_ai_themes
from astro.notify import notify_scan_complete

st.set_page_config(page_title="AI & Tech Themes", page_icon="\U0001f916", layout="wide")

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

st.markdown("# \U0001f916 AI & Tech Themes")
st.caption(
    "Ask about AI’s collective path, a product launch, or risk/regulation — "
    "judged with Lahiri sidereal Prashna, focusing Mercury · Rahu · Saturn "
    "(intellect, disruption, structure). Symbolic themes only."
)

preset_labels = {p["key"]: p["title"] for p in AI_PRESETS}
preset_q = {p["key"]: p["question"] for p in AI_PRESETS}
qkey = st.selectbox(
    "Theme",
    list(preset_labels.keys()),
    format_func=lambda k: preset_labels[k],
)
question_text = st.text_area(
    "Your question",
    value=preset_q[qkey],
    height=80,
)

st.markdown("### When & where the question is asked")
use_now = st.checkbox("Use the current moment", value=True, key="ai_use_now")
c1, c2 = st.columns(2)
with c1:
    q_date = st.date_input(
        "Date", value=date.today(), disabled=use_now,
        min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), key="ai_qdate",
    )
with c2:
    q_time = st.time_input(
        "Time",
        value=datetime.now().time().replace(second=0, microsecond=0),
        step=60, disabled=use_now, key="ai_qtime",
    )

mode = st.radio("Location", ["Pick a city", "Manual lat/long"], horizontal=True, key="ai_loc")
if mode == "Pick a city":
    idx = geo.PLACE_NAMES.index("Rishikesh, India") if "Rishikesh, India" in geo.PLACE_NAMES else 0
    city = st.selectbox("Place", geo.PLACE_NAMES, index=idx, key="ai_city")
    info = geo.resolve_place(city)
    lat, lon, place, tz_name, tz_manual = (
        info.latitude, info.longitude, info.name, info.timezone, None)
else:
    lat = st.number_input("Latitude", value=30.0869, format="%.4f", key="ai_lat")
    lon = st.number_input("Longitude", value=78.2676, format="%.4f", key="ai_lon")
    tz_manual = st.number_input(
        "Time zone — IST hours from UTC", value=5.5, step=0.25, format="%.2f", key="ai_tz",
    )
    place, tz_name = f"{lat:.3f},{lon:.3f}", None

if st.button("Cast Lahiri chart & read themes", type="primary", use_container_width=True):
    when = datetime.now() if use_now else datetime.combine(q_date, q_time)
    if isinstance(q_time, time) and not use_now:
        when = datetime.combine(q_date, q_time)
    tz = geo.tz_offset_hours(tz_name, when) if tz_name else tz_manual
    res = analyze_ai_themes(qkey, when, lat, lon, tz, place, question_text=question_text)
    st.session_state["ai_themes_result"] = res
    snippet = (
        f"{res['verdict']} ({res['score']}%) — {res['question_type']}\n"
        + "\n".join(res.get("horizon", [])[:2])
    )
    ok, _ = notify_scan_complete(
        "prediction",
        "AI & Tech Themes",
        snippet,
        "Open AI & Tech Themes in Jyotish Darshan for the full reading.",
        once_key=f"ai:{qkey}:{when.isoformat(timespec='minutes')}",
    )
    if ok:
        st.toast("Telegram alert sent", icon="📱")

if "ai_themes_result" not in st.session_state:
    st.info(
        "Pick a theme, confirm place/time, then cast. "
        "You can also use the same AI options under **Prashna (Horary)**."
    )
    st.stop()

res = st.session_state["ai_themes_result"]
color = {"Favourable": "#6fcf97", "Mixed": "#f2c94c", "Unfavourable": "#eb5757"}[res["verdict"]]

if res.get("question_text"):
    st.markdown(f"> **Q:** {res['question_text']}")

st.markdown(
    f"<div class='pcard'>"
    f"<span class='verdict' style='color:{color}'>{res['verdict']}</span> "
    f"&nbsp; <span style='color:#9aa4bf'>({res['score']}% favourable)</span><br>"
    f"<span style='color:#9aa4bf'>{res['question_type']} · {res['asked_at']} · {res['place']}</span>"
    f"<div style='margin-top:8px'>{res['summary']}</div>"
    f"</div>",
    unsafe_allow_html=True,
)
st.progress(min(1.0, res["score"] / 100.0))

st.markdown("### Mercury · Rahu · Saturn (AI significators)")
for s in res.get("significators", []):
    st.markdown(
        f"<div class='pcard'><b style='color:#ffe9a8'>{s['planet']}</b> — {s['role']}<br>"
        f"{s['line']}</div>",
        unsafe_allow_html=True,
    )

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Leaning supportive**")
    for line in res.get("working") or ["—"]:
        st.markdown(f"- {line}")
with c2:
    st.markdown("**Needs care**")
    for line in res.get("watch") or ["—"]:
        st.markdown(f"- {line}")

st.markdown("### Why (chart logic)")
for r in res.get("reasons", []):
    st.markdown(f"- {r}")

if res.get("yogas"):
    with st.expander("Tajika yogas", expanded=False):
        for y in res["yogas"]:
            st.markdown(f"- **{y['type']}** ({' & '.join(y['planets'])}) — {y['reason']}")

st.markdown("### Horizon cues")
for h in res.get("horizon", []):
    st.markdown(f"- {h}")

st.caption(res.get("disclaimer", ""))
st.caption(f"Method: {res.get('method', 'Lahiri')}")
