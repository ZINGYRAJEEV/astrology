"""Shared Streamlit UI for life-prediction results (Horoscope + Life Prediction pages)."""

from __future__ import annotations

from typing import Optional

import streamlit as st

from .prediction import prediction_markdown

_VERDICT_CHIP = {
    "default": {
        "Supported": "chip-ok", "Mixed": "chip-mix", "Challenged": "chip-bad",
        "Auspicious": "chip-ok", "Strong": "chip-ok",
    },
    "horoscope": {
        "Supported": "#6fcf97", "Mixed": "#f2c94c", "Challenged": "#ef6b6b",
        "Auspicious": "#6fcf97",
    },
}


def _chip_class(verdict: str, theme: str) -> str:
    if theme == "horoscope":
        return _VERDICT_CHIP["horoscope"].get(verdict, "#f2c94c")
    return _VERDICT_CHIP["default"].get(verdict, "chip-mix")


def _wrap(theme: str, inner: str, *, border: str = "", muted: bool = False) -> str:
    if theme == "horoscope":
        style = f"border-color:{border};" if border else ""
        if muted:
            style += "font-size:13px;color:#9aa3b8;margin-top:8px;"
        return f"<div class='card' style='{style}'>{inner}</div>"
    cls = "pcard"
    style = "font-size:13px;color:#9aa3b8;margin-top:8px;" if muted else ""
    return f"<div class='{cls}' style='{style}'>{inner}</div>"


def _step_heading(n: int, title: str, theme: str) -> None:
    """Numbered section heading so the report reads top-to-bottom."""
    if theme == "horoscope":
        st.markdown(
            f"<div style='margin:22px 0 10px 0;display:flex;align-items:center;gap:12px'>"
            f"<span style='display:inline-flex;align-items:center;justify-content:center;"
            f"width:28px;height:28px;border-radius:999px;background:rgba(245,197,66,0.22);"
            f"border:1px solid rgba(245,197,66,0.45);color:#ffe9a8;font-weight:700;"
            f"font-size:13px'>{n}</span>"
            f"<span style='font-family:Cormorant Garamond,serif;font-size:26px;"
            f"color:#f5c542;font-weight:700'>{title}</span></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"### {n}. {title}")


def _render_life_block(lp: dict, theme: str) -> None:
    chip = _chip_class(lp["verdict"], theme)
    title = lp.get("title", lp["area"])
    plain = lp.get("plain", lp.get("prediction", ""))
    technical = lp.get("technical", lp.get("technical_basis", ""))
    if theme == "horoscope":
        st.markdown(
            _wrap(
                theme,
                f"<span class='pill' style='background:{chip};color:#0b0e1a;border:none'>"
                f"{lp['verdict']}</span>"
                f"<b style='font-size:17px;color:#fff;display:block;margin-top:8px'>{title}</b>"
                f"<div style='margin-top:8px;line-height:1.5'>{plain}</div>",
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"**{title}** · <span class='{chip}'>{lp['verdict']}</span>",
                    unsafe_allow_html=True)
        st.markdown(plain)
    if technical:
        with st.expander("Technical basis", expanded=False):
            st.caption(technical)


def _render_narrative(pred: dict, theme: str) -> None:
    narrative = pred.get("narrative")
    if not narrative:
        return
    for sub_heading, text in narrative["overview"]:
        if theme == "horoscope":
            st.markdown(
                _wrap(
                    theme,
                    f"<b style='font-size:16px;color:#ffe9a8'>{sub_heading}</b>"
                    f"<div style='margin-top:8px;line-height:1.6'>{text}</div>",
                ),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"**{sub_heading}**")
            st.markdown(text)

    deep = narrative.get("deep_dives", {})
    if deep:
        with st.expander("Go deeper on one life area", expanded=False):
            area = st.selectbox(
                "Choose an area",
                list(deep.keys()),
                key=f"narrative_area_{theme}",
            )
            if theme == "horoscope":
                st.markdown(_wrap(theme, deep[area]), unsafe_allow_html=True)
            else:
                st.markdown(deep[area])
    if narrative.get("disclaimer"):
        st.caption(narrative["disclaimer"])


_YOGA_TONE = {
    "benefic": ("#6fcf97", "chip-ok"),
    "mixed": ("#f2c94c", "chip-mix"),
    "malefic": ("#ef6b6b", "chip-bad"),
}


def _render_yogas(pred: dict, theme: str) -> None:
    yogas = pred.get("yogas")
    if not yogas:
        return
    st.caption("Classical combinations that shape potentials (they unfold through Dasha & transits).")
    for y in yogas:
        colour, cls = _YOGA_TONE.get(y["tone"], ("#f2c94c", "chip-mix"))
        if theme == "horoscope":
            st.markdown(
                _wrap(
                    theme,
                    f"<span class='pill' style='background:{colour};color:#0b0e1a;border:none'>"
                    f"{y['category']}</span>"
                    f"<b style='font-size:16px;color:#fff;display:block;margin-top:6px'>{y['name']}</b>"
                    f"<div style='margin-top:6px;line-height:1.5'>{y['detail']}</div>",
                    border=f"rgba({'111,207,151' if y['tone']=='benefic' else '239,107,107' if y['tone']=='malefic' else '242,201,76'},0.3)",
                ),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"<span class='{cls}'>{y['category']}</span> **{y['name']}**",
                        unsafe_allow_html=True)
            st.markdown(y["detail"])


def _render_divisional(pred: dict, theme: str) -> None:
    divisional = pred.get("divisional")
    if not divisional:
        return
    st.caption("Finer charts that zoom into specific life areas — D-9 marriage, "
               "D-10 career, D-7 children.")
    for d in divisional:
        vg = (f" &middot; Vargottama: {', '.join(d['vargottama'])}"
              if d["vargottama"] else "")
        if theme == "horoscope":
            st.markdown(
                _wrap(
                    theme,
                    f"<b style='font-size:16px;color:#ffe9a8;display:block'>{d['name']}</b>"
                    f"<div class='subtle' style='margin-top:2px'>{d['theme']}</div>"
                    f"<div style='margin-top:6px;line-height:1.5'>Ascendant "
                    f"<b>{d['lagna_sign']}</b>{vg}.<br>{d['note']}</div>",
                    border="rgba(245,197,66,0.25)",
                ),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"**{d['name']}** — {d['theme']}")
            st.markdown(f"Ascendant {d['lagna_sign']}{vg}. {d['note']}")


def _render_combinations_reading(pred: dict, theme: str) -> None:
    combos = pred.get("combinations_reading")
    if not combos:
        return
    nutshell = combos.get("nutshell", "") if isinstance(combos, dict) else ""
    areas = combos.get("areas", []) if isinstance(combos, dict) else combos

    if isinstance(combos, dict):
        from .combinations import outcome_balance
        bal = outcome_balance(combos)
        st.progress(bal["score"] / 100.0)
        st.caption(f"Positivity balance: {bal['score']}% \u00b7 "
                   f"\u2705 {bal['good']} strengths \u00b7 \u26a0\ufe0f {bal['caution']} cautions "
                   f"\u00b7 \u2022 {bal['neutral']} to note")

    if nutshell:
        st.markdown(
            _wrap(theme, f"<b style='color:#ffe9a8'>In a nutshell</b><br>{nutshell}",
                  border="rgba(245,197,66,0.4)") if theme == "horoscope"
            else f"> {nutshell}",
            unsafe_allow_html=(theme == "horoscope"),
        )

    tone_colour = {"good": "#6fcf97", "caution": "#eb5757", "neutral": "#f2c94c"}
    tone_mark = {"good": "\u2705", "caution": "\u26a0\ufe0f", "neutral": "\u2022"}
    for block in areas:
        with st.expander(block["area"], expanded=False):
            for ln in block["lines"]:
                colour = tone_colour.get(ln["tone"], "#f2c94c")
                mark = tone_mark.get(ln["tone"], "\u2022")
                if theme == "horoscope":
                    st.markdown(
                        _wrap(theme,
                              f"<span style='color:{colour}'>{mark}</span> {ln['text']}",
                              border="rgba(245,197,66,0.18)"),
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(f"<div style='margin:2px 0'><span style='color:{colour}'>"
                                f"{mark}</span> {ln['text']}</div>", unsafe_allow_html=True)
                reason = ln.get("reason")
                if reason:
                    st.caption(f"Why: {reason}")


def _render_dashboard(pred: dict, theme: str) -> None:
    """FlowTest-style metric strip + spiderweb before the written reading."""
    from .report_viz import dashboard_metrics, score_table_rows, spiderweb_figure

    metrics = dashboard_metrics(pred)
    name = pred.get("name") or "Native"

    if theme == "horoscope":
        st.markdown(
            _wrap(
                theme,
                f"<div class='subtle' style='letter-spacing:3px;text-transform:uppercase'>"
                f"Life prediction dashboard &middot; {pred['focus_intent']}</div>"
                f"<div style='font-family:\"Cormorant Garamond\",serif;font-size:26px;"
                f"color:#ffe9a8;margin-top:6px'>{name}</div>"
                f"<div class='subtle' style='margin-top:8px'>Scan the spiderweb for your "
                f"strongest and weakest life areas, then read the numbered story below.</div>",
                border="rgba(245,197,66,0.4)",
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"# \U0001f52e {name}")
        st.caption("Scan the spiderweb for strongest / weakest areas, then read the story below.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Birth quality", f"{metrics['birth_quality']}%", metrics["birth_verdict"])
    m2.metric("Area strength", f"{metrics['area_avg']}/100", "average across life areas")
    m3.metric("Supported areas", metrics["supported"], f"{metrics['challenged']} need effort")
    m4.metric("Positivity balance", f"{metrics['balance']}%",
              f"{metrics['mixed']} mixed")

    chart_col, table_col = st.columns([1.35, 1])
    with chart_col:
        fig = spiderweb_figure(pred, theme=theme)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with table_col:
        st.markdown("**Strength by area**")
        st.caption("Higher = themes tend to flow more easily.")
        st.dataframe(
            score_table_rows(pred),
            hide_index=True,
            use_container_width=True,
            height=360,
        )


def render_prediction_results(
    pred: dict,
    *,
    theme: str = "default",
    show_header: bool = True,
    show_download: bool = True,
    show_technical_panchang: bool = False,
    download_label: str = "Download prediction report (Markdown)",
    footer_caption: Optional[str] = None,
) -> None:
    """Render a guided, top-to-bottom prediction report for a layman reader."""
    rk = pred.get("rishikesh", {})

    # ---- Visual dashboard (spiderweb + KPIs) ----
    if show_header:
        _render_dashboard(pred, theme)

    # ---- Reading roadmap ----
    st.markdown(
        _wrap(
            theme,
            "<b style='color:#ffe9a8'>How to read this report</b>"
            "<div style='margin-top:8px;line-height:1.6'>"
            "1. Scan the spiderweb &amp; metrics &middot; "
            "2. Read the plain-language story &middot; "
            "3. Open life-area cards by verdict &middot; "
            "4. Check timing &amp; watch points &middot; "
            "5. Open deeper chart signals only if you want the why."
            "</div>"
            f"<div style='margin-top:10px;font-size:13px;color:#9aa3b8'>"
            f"{pred.get('scope_note', '')}</div>",
            border="rgba(245,197,66,0.35)",
        ) if theme == "horoscope" else (
            f"**How to read this report**\n\n"
            f"1. Spiderweb & metrics → 2. Plain story → 3. Life areas → "
            f"4. Timing → 5. Deeper signals (optional)\n\n"
            f"{pred.get('scope_note', '')}"
        ),
        unsafe_allow_html=(theme == "horoscope"),
    )

    with st.expander("How to read verdicts (Supported / Mixed / Challenged)", expanded=False):
        st.markdown(pred.get("verdict_legend", ""))

    # ---- 1. At a glance ----
    _step_heading(1, "At a glance", theme)
    st.markdown(pred.get("summary", pred.get("opening", "")))
    birth_intro = pred.get("birth_intro", [])
    if birth_intro:
        st.markdown("**Birth snapshot**")
        for line in birth_intro:
            st.markdown(f"- {line}")

    # ---- 2. Plain-language story ----
    if pred.get("narrative"):
        _step_heading(2, "Your story in plain words", theme)
        _render_narrative(pred, theme)

    # ---- 3. Life areas by group ----
    groups = pred.get("groups", {})
    group_titles = [
        ("Who you are", groups.get("who_you_are", [])),
        ("What's working well", groups.get("working_well", [])),
        ("What needs effort & attention", groups.get("needs_effort", [])),
    ]
    if any(items for _, items in group_titles):
        _step_heading(3, "Life areas", theme)
        st.caption("Each card is one area of life. Open “Technical basis” only if you want the chart reason.")
        for gtitle, items in group_titles:
            if not items:
                continue
            with st.expander(gtitle, expanded=(gtitle == "Who you are")):
                for lp in items:
                    _render_life_block(lp, theme)

    # ---- 4. Focus + timing + cautions ----
    _step_heading(4, "Right now — focus, timing & watch points", theme)
    st.markdown(f"**Your focus:** {pred['focus_intent']}")
    for fl in pred.get("focus_friendly", pred.get("focus_detail", [])):
        if isinstance(fl, dict):
            st.markdown(f"- {fl['plain']}")
            if fl.get("technical"):
                st.caption(f"  Technical: {fl['technical']}")
        else:
            st.markdown(f"- {fl}")

    tf = pred.get("timing_friendly", {})
    st.markdown("**What's happening now**")
    st.markdown(tf.get("plain", ""))
    if tf.get("technical"):
        with st.expander("Timing technical basis", expanded=False):
            st.caption(tf["technical"])

    if pred.get("cautions"):
        st.markdown("**Watch points**")
        for c in pred["cautions"]:
            if theme == "horoscope":
                st.markdown(_wrap(theme, c, border="rgba(239,107,107,0.3)"),
                            unsafe_allow_html=True)
            else:
                st.warning(c)

    # ---- 5. Deeper signals (collapsed) ----
    _step_heading(5, "Deeper chart signals (optional)", theme)
    st.caption("Open these only if you want the underlying yogas, vargas, and combination details.")

    with st.expander("Notable yogas", expanded=False):
        if pred.get("yogas"):
            _render_yogas(pred, theme)
        else:
            st.caption("No notable yogas flagged for this chart.")

    with st.expander("Divisional charts (Vargas)", expanded=False):
        if pred.get("divisional"):
            _render_divisional(pred, theme)
        else:
            st.caption("No divisional highlights available.")

    with st.expander("What your planetary combinations mean", expanded=False):
        if pred.get("combinations_reading"):
            _render_combinations_reading(pred, theme)
        else:
            st.caption("No combination reading available.")

    if rk and show_technical_panchang:
        with st.expander("Birth quality (Panchang)", expanded=False):
            nav = rk["navaratna"]
            st.caption(
                f"{nav['verdict']} — {nav['percent']}% "
                f"(scores above 70% are strongly favorable). "
                f"Ishtakal: {rk['ishtakal']['formatted']} after sunrise."
            )

    # ---- 6. Favourable + remedies + download ----
    _step_heading(6, "Favourable elements & next steps", theme)
    lk = pred["lucky"]
    st.markdown(
        f"Weekday **{lk['day']}** · Birth star **{lk['nakshatra']}** "
        f"(lord {lk['nakshatra_lord']}) · Gemstone hint: {lk['gemstone_hint']}"
    )
    st.markdown("**Remedies**")
    st.caption(pred.get("remedies_note", ""))

    if show_download:
        st.download_button(
            download_label,
            prediction_markdown(pred),
            file_name=f"prediction_{(pred['name'] or 'chart').replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.caption(footer_caption or (
        "Hrishikesh Panchang tradition · plain language first, technical details optional."
    ))
