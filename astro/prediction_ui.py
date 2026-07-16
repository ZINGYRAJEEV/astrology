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
