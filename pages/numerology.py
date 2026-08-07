"""Numerology — core chart synthesis for everyday users."""

from __future__ import annotations

from datetime import date

import streamlit as st

from astro.numerology import (
    NumerologyInput, build_chart, chart_markdown, compare_systems, meaning_for,
)

st.set_page_config(page_title="Numerology", page_icon="🔢", layout="wide")

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

      :root {
        --ink:#e8ebf2; --muted:#9aa3b8; --gold:#f5c542; --gold-soft:#ffe9a8;
        --panel:rgba(28,33,54,0.55); --border:rgba(245,197,66,0.16);
        --ok:#6fcf97; --warn:#f2c94c; --bad:#ef6b6b;
      }
      .stApp, [data-testid="stAppViewContainer"] {
        background:
          radial-gradient(900px 480px at 10% -8%, rgba(86,160,255,0.14), transparent 55%),
          radial-gradient(800px 420px at 92% 0%, rgba(245,197,66,0.10), transparent 50%),
          linear-gradient(180deg,#070912,#0c1020);
        color: var(--ink);
        font-family: 'DM Sans', system-ui, sans-serif;
      }
      [data-testid="stHeader"] { background: transparent; }
      h1,h2,h3 { font-family:'Cormorant Garamond',serif !important; color:var(--gold) !important; }
      .hero {
        font-family:'Cormorant Garamond',serif; font-size:48px; font-weight:700;
        line-height:1.05; margin:0;
        background: linear-gradient(120deg,#fff 8%, var(--gold) 55%, #9ec5ff 95%);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
      }
      .hero-sub { color:var(--muted); font-size:16px; max-width:640px; margin-top:8px; }
      .num-card {
        background: var(--panel); border:1px solid var(--border); border-radius:18px;
        padding:18px 18px 16px; height:100%; backdrop-filter:blur(8px);
      }
      .num-big {
        font-family:'Cormorant Garamond',serif; font-size:44px; font-weight:700;
        color:var(--gold-soft); line-height:1; margin:6px 0 4px;
      }
      .num-label { font-size:13px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
      .num-sub { color:#cbd2e0; font-size:14px; margin-top:4px; }
      .pill {
        display:inline-block; padding:3px 10px; border-radius:999px; font-size:12px;
        border:1px solid var(--border); color:#cbd2e0; margin-right:6px;
      }
      .pill-ok { background:rgba(111,207,151,0.18); color:var(--ok); border-color:rgba(111,207,151,0.35); }
      .pill-warn { background:rgba(242,201,76,0.16); color:var(--warn); border-color:rgba(242,201,76,0.35); }
      .section-card {
        background: var(--panel); border:1px solid var(--border); border-radius:16px;
        padding:16px 18px; margin-bottom:10px;
      }
      .muted { color:var(--muted); font-size:13px; }
      .stButton > button[kind="primary"] {
        background: linear-gradient(135deg,#f5c542,#e7a93b); color:#1a1407;
        border:none; font-weight:600; border-radius:12px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="padding:8px 0 4px">
      <div class="hero">Numerology</div>
      <div class="hero-sub">
        Your name and birth date, translated into clear core numbers —
        Life Path, Destiny, Heart’s Desire, Personality, and more.
        Choose Pythagorean or Chaldean, then read the story in plain words.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Inputs ----
with st.container(border=True):
    st.markdown("### Your details")
    c1, c2 = st.columns([1.4, 1])
    with c1:
        birth_name = st.text_input(
            "Full birth name",
            placeholder="e.g. Amit Kumar Sharma",
            help="As on birth certificate. Jr./Sr./II/III are ignored automatically.",
        )
        current_name = st.text_input(
            "Current name (optional)",
            placeholder="Married or preferred name, if different",
            help="Shows how a name change shifts Destiny / Heart / Personality.",
        )
    with c2:
        dob = st.date_input(
            "Date of birth",
            value=date(1990, 1, 1),
            min_value=date(1800, 1, 1),
            max_value=date(2100, 12, 31),
        )
        system = st.radio(
            "System",
            ["Pythagorean (Western)", "Chaldean (Vedic)", "Compare both"],
            horizontal=False,
            help="Pythagorean maps personality traits; Chaldean emphasises sound/planetary luck.",
        )

    st.caption(
        "Tip: enter the full birth name (first + middle + last). "
        "Generational tags like Jr. or III are never counted."
    )
    go = st.button("Calculate my numbers", type="primary", use_container_width=True)

if go:
    if not birth_name.strip():
        st.error("Please enter your full birth name.")
        st.stop()
    mode = (
        "compare" if system.startswith("Compare")
        else "chaldean" if system.startswith("Chaldean") else "pythagorean"
    )
    data = NumerologyInput(
        birth_name=birth_name,
        birth_date=dob,
        current_name=current_name,
        system="chaldean" if mode == "chaldean" else "pythagorean",
    )
    if mode == "compare":
        st.session_state["num_chart"] = {"mode": "compare", **compare_systems(data)}
    else:
        st.session_state["num_chart"] = {"mode": "single", "chart": build_chart(data)}

if "num_chart" not in st.session_state:
    st.markdown("#### What you’ll get")
    a, b, c = st.columns(3)
    a.markdown(
        "<div class='section-card'><b style='color:#ffe9a8'>Core portrait</b>"
        "<div class='muted' style='margin-top:6px'>Life Path, Destiny, Heart’s Desire, "
        "Personality, and Attainment — each with a plain-language meaning.</div></div>",
        unsafe_allow_html=True,
    )
    b.markdown(
        "<div class='section-card'><b style='color:#ffe9a8'>Inner alignment</b>"
        "<div class='muted' style='margin-top:6px'>Whether your private drive and public "
        "mask agree — or where the tension lives.</div></div>",
        unsafe_allow_html=True,
    )
    c.markdown(
        "<div class='section-card'><b style='color:#ffe9a8'>Two systems</b>"
        "<div class='muted' style='margin-top:6px'>Pythagorean for personality depth, "
        "Chaldean for vibrational / luck lens — or compare both.</div></div>",
        unsafe_allow_html=True,
    )
    with st.expander("Quick guide: Pythagorean vs Chaldean"):
        st.markdown(
            """
| | Pythagorean (Western) | Chaldean (Vedic) |
|---|---|---|
| Basis | Alphabetical sequence | Sound / Law of Vibrations |
| Letters | 1–9 | 1–8 (9 is sacred) |
| Focus | Personality traits | Planetary influence & luck |
| Best for | “Who am I?” depth | Name luck & career tone |
            """
        )
    st.stop()


def _render_core_cards(chart: dict) -> None:
    st.markdown(
        f"<div class='pill'>{chart['system_label']}</div>"
        f"<div class='pill'>{chart['birth_name']}</div>"
        f"<div class='pill'>{chart['birth_date']}</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(5)
    for col, item in zip(cols, chart["core"]):
        with col:
            st.markdown(
                f"""
                <div class="num-card">
                  <div class="num-label">{item['label']}</div>
                  <div class="num-big">{item['number']['display']}</div>
                  <div class="num-sub"><b>{item['meaning']['title']}</b></div>
                  <div class="muted">{item['subtitle']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_meanings(chart: dict, key_prefix: str = "num") -> None:
    st.markdown("### What your numbers mean")
    for item in chart["core"]:
        m = item["meaning"]
        # Unique labels avoid duplicate element IDs when comparing both systems.
        with st.expander(
            f"{item['label']} · {item['number']['display']} — {m['title']} ({key_prefix})",
            expanded=(item["key"] == "life_path"),
        ):
            st.markdown(m["plain"])
            c1, c2 = st.columns(2)
            c1.markdown(f"**Eastern lens**  \n{m['eastern']}")
            c2.markdown(f"**Western lens**  \n{m['western']}")
            if item["key"] == "life_path":
                lp = chart["life_path"]
                st.caption(
                    f"Calculation: preferred **{lp['preferred_method']}** method · "
                    f"Grouping → {lp['grouping']['display']} · "
                    f"Alternate (all digits) → {lp['alternate']['display']}"
                    + (" · Master Number revealed by alternate method"
                       if lp["master_revealed_by_alternate"] else "")
                )
            if item["key"] in ("destiny", "heart", "personality"):
                segs = item["number"].get("segments", [])
                if segs:
                    bits = ", ".join(f"{s['segment']}={s['reduced']}" for s in segs)
                    st.caption(f"Name segments reduced: {bits}")


def _render_alignment(chart: dict) -> None:
    al = chart["alignment"]
    cls = "pill-ok" if al["tone"] == "aligned" else "pill-warn"
    label = "Aligned" if al["tone"] == "aligned" else "Inner tension to notice"
    st.markdown("### Heart vs Personality")
    st.markdown(
        f"<div class='section-card'><span class='pill {cls}'>{label}</span>"
        f"<div style='margin-top:10px;line-height:1.55'>{al['text']}</div></div>",
        unsafe_allow_html=True,
    )


def _render_planes(chart: dict) -> None:
    st.markdown("### Planes of Expression")
    st.caption(
        "How you process life — mental, physical, emotional, intuitive. "
        "Useful when comparing partners: same Life Path can still clash here."
    )
    cols = st.columns(4)
    for col, (plane, info) in zip(cols, chart["planes"].items()):
        with col:
            st.markdown(
                f"""
                <div class="num-card">
                  <div class="num-label">{plane}</div>
                  <div class="num-big" style="font-size:34px">{info['display']}</div>
                  <div class="muted">{info['letters']} letters in this plane</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_current(chart: dict) -> None:
    cur = chart.get("current_name")
    if not cur:
        return
    st.markdown("### Current name shift")
    st.markdown(
        f"<div class='section-card'>{cur['note']}<br><br>"
        f"<b style='color:#ffe9a8'>{cur['name']}</b> → "
        f"Destiny <b>{cur['destiny']['display']}</b> · "
        f"Heart <b>{cur['heart']['display']}</b> · "
        f"Personality <b>{cur['personality']['display']}</b></div>",
        unsafe_allow_html=True,
    )


def _render_master_legend(key_prefix: str = "num") -> None:
    with st.expander(f"Master Numbers 11 · 22 · 33 — how to read them ({key_prefix})"):
        for n in (11, 22, 33):
            m = meaning_for(n)
            st.markdown(f"**{m['title']}** — {m['plain']}")


def _render_chart(chart: dict, *, key_prefix: str = "num", show_download: bool = True) -> None:
    _render_core_cards(chart)
    st.write("")
    _render_alignment(chart)
    _render_meanings(chart, key_prefix=key_prefix)
    _render_planes(chart)
    _render_current(chart)
    _render_master_legend(key_prefix=key_prefix)
    if show_download:
        safe = chart["birth_name"].replace(" ", "_") or "chart"
        st.download_button(
            f"Download {key_prefix} chart (Markdown)",
            chart_markdown(chart),
            file_name=f"numerology_{safe}_{key_prefix}.md",
            mime="text/markdown",
            use_container_width=True,
            key=f"num_download_{key_prefix}",
        )


payload = st.session_state["num_chart"]
if payload["mode"] == "compare":
    st.markdown("### Side-by-side systems")
    st.caption(
        "Same name and birth date under both lenses. Life Path is date-based, "
        "so it stays the same; name numbers often shift."
    )
    t1, t2 = st.tabs(["Pythagorean (Western)", "Chaldean (Vedic)"])
    with t1:
        _render_chart(payload["pythagorean"], key_prefix="pythagorean")
    with t2:
        _render_chart(payload["chaldean"], key_prefix="chaldean")
else:
    _render_chart(payload["chart"], key_prefix=payload["chart"]["system"])

st.caption(
    "Professional practice notes applied: segment-then-sum name protocol, "
    "Master Numbers 11/22/33 preserved, alternate Life Path check for hidden 33, "
    "generational suffixes excluded. For guidance, not deterministic fate."
)
