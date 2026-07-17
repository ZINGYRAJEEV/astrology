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


def _render_life_block(lp: dict, theme: str, heading_level: str = "###") -> None:
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
                f"<div style='margin-top:8px;line-height:1.5'>{plain}</div>"
                f"<div style='margin-top:10px;font-size:13px;color:#9aa3b8;border-left:3px solid "
                f"rgba(245,197,66,0.3);padding-left:10px'>Technical basis: {technical}</div>",
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"{heading_level} {title}")
        st.markdown(f"<span class='{chip}'>{lp['verdict']}</span>", unsafe_allow_html=True)
        st.markdown(plain)
        st.caption(f"Technical basis: {technical}")


def _render_narrative(pred: dict, theme: str, heading: str) -> None:
    """To-the-point plain-talk reading + per-area deep dives (like an astrologer talking)."""
    narrative = pred.get("narrative")
    if not narrative:
        return
    st.markdown(f"{heading} Your reading in plain words")
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
        st.markdown("_Want to go deeper on one area? Pick it below._")
        area = st.selectbox(
            "Ask about a specific area",
            list(deep.keys()),
            key=f"narrative_area_{theme}",
        )
        if theme == "horoscope":
            st.markdown(_wrap(theme, deep[area]), unsafe_allow_html=True)
        else:
            st.markdown(deep[area])
    st.caption(narrative.get("disclaimer", ""))


_YOGA_TONE = {
    "benefic": ("#6fcf97", "chip-ok"),
    "mixed": ("#f2c94c", "chip-mix"),
    "malefic": ("#ef6b6b", "chip-bad"),
}


def _render_yogas(pred: dict, theme: str, heading: str) -> None:
    """Notable classical yogas found in the chart."""
    yogas = pred.get("yogas")
    if not yogas:
        return
    st.markdown(f"{heading} Notable yogas in your chart")
    st.caption("Classical combinations that shape your potentials (they unfold through Dasha & transits).")
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


def _render_divisional(pred: dict, theme: str, heading: str) -> None:
    """Divisional-chart (Varga) highlights for key life areas."""
    divisional = pred.get("divisional")
    if not divisional:
        return
    st.markdown(f"{heading} Divisional charts (Vargas)")
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


def _render_combinations_reading(pred: dict, theme: str, heading: str) -> None:
    """Plain-language mapping of planetary combinations to life outcomes."""
    combos = pred.get("combinations_reading")
    if not combos:
        return
    st.markdown(f"{heading} What your planetary combinations mean")
    st.caption("Your placements, yogas and house-lords translated into plain, "
               "everyday outcomes — grouped by area of life.")
    tone_colour = {"good": "#6fcf97", "caution": "#eb5757", "neutral": "#f2c94c"}
    tone_mark = {"good": "\u2705", "caution": "\u26a0\ufe0f", "neutral": "\u2022"}
    for block in combos:
        st.markdown(f"**{block['area']}**")
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
    """Render user-friendly prediction (Rules 1–10)."""
    heading = "####" if theme == "horoscope" else "###"
    rk = pred.get("rishikesh", {})

    # Rule 8: scope note up front
    st.info(pred.get("scope_note", ""))

    if show_header:
        name = pred["name"] or "Native"
        if theme == "horoscope":
            st.markdown(
                _wrap(
                    theme,
                    f"<div class='subtle' style='letter-spacing:3px;text-transform:uppercase'>"
                    f"Life prediction &middot; {pred['focus_intent']}</div>"
                    f"<div style='font-family:\"Cormorant Garamond\",serif;font-size:22px;"
                    f"color:#ffe9a8;margin-top:6px'>{name}</div>",
                    border="rgba(245,197,66,0.35)",
                ),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"# \U0001f52e {name}")

    # Rule 9: verdict scale once
    with st.expander("How to read verdicts", expanded=False):
        st.markdown(pred.get("verdict_legend", ""))

    # Rule 10: short summary
    st.markdown(f"{heading} At a glance")
    st.markdown(pred.get("summary", pred.get("opening", "")))

    for line in pred.get("birth_intro", []):
        st.markdown(f"- {line}")

    _render_narrative(pred, theme, heading)

    _render_yogas(pred, theme, heading)

    _render_divisional(pred, theme, heading)

    _render_combinations_reading(pred, theme, heading)

    if rk and show_technical_panchang:
        nav = rk["navaratna"]
        st.markdown(f"{heading} Birth quality (Panchang)")
        st.caption(
            f"{nav['verdict']} — {nav['percent']}% "
            f"(scores above 70% are strongly favorable). "
            f"Ishtakal: {rk['ishtakal']['formatted']} after sunrise."
        )

    groups = pred.get("groups", {})
    group_titles = [
        ("Who you are", groups.get("who_you_are", [])),
        ("What's working well", groups.get("working_well", [])),
        ("What needs effort & attention", groups.get("needs_effort", [])),
    ]
    for gtitle, items in group_titles:
        if not items:
            continue
        st.markdown(f"{heading} {gtitle}")
        for lp in items:
            _render_life_block(lp, theme, heading)

    st.markdown(f"{heading} Your focus: {pred['focus_intent']}")
    for fl in pred.get("focus_friendly", pred.get("focus_detail", [])):
        if isinstance(fl, dict):
            st.markdown(fl["plain"])
            if fl.get("technical"):
                st.caption(f"Technical basis: {fl['technical']}")
        else:
            st.markdown(f"- {fl}")

    st.markdown(f"{heading} What's happening now")
    tf = pred.get("timing_friendly", {})
    st.markdown(tf.get("plain", ""))
    if tf.get("technical"):
        st.caption(f"Technical basis: {tf['technical']}")

    if pred.get("cautions"):
        st.markdown(f"{heading} Watch points")
        for c in pred["cautions"]:
            if theme == "horoscope":
                st.markdown(_wrap(theme, c, border="rgba(239,107,107,0.3)"), unsafe_allow_html=True)
            else:
                st.warning(c)

    lk = pred["lucky"]
    st.markdown(f"{heading} Favourable elements")
    st.markdown(
        f"Weekday **{lk['day']}** · Birth star **{lk['nakshatra']}** "
        f"(lord {lk['nakshatra_lord']}) · Gemstone hint: {lk['gemstone_hint']}"
    )

    st.markdown(f"{heading} Remedies")
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
