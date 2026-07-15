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

_LIMB_GOOD = {"Auspicious", "Strong", "Sampat", "Kshema", "Sadhana", "Mitra", "Ati-Mitra"}
_LIMB_BAD = {"Challenged", "Weak", "Janma", "Vipat", "Pratyak", "Naidhana"}


def _chip_class(verdict: str, theme: str) -> str:
    if theme == "horoscope":
        return _VERDICT_CHIP["horoscope"].get(verdict, "#f2c94c")
    return _VERDICT_CHIP["default"].get(verdict, "chip-mix")


def _wrap(theme: str, inner: str, *, border: str = "") -> str:
    if theme == "horoscope":
        style = f"border-color:{border};" if border else ""
        return f"<div class='card' style='{style}'>{inner}</div>"
    return f"<div class='pcard'>{inner}</div>"


def render_prediction_results(
    pred: dict,
    *,
    theme: str = "default",
    show_header: bool = True,
    show_download: bool = True,
    download_label: str = "Download prediction report (Markdown)",
    footer_caption: Optional[str] = None,
) -> None:
    """Render full Rishikesh Panchang prediction output."""
    pc = pred["panchang_at_birth"]
    rk = pred.get("rishikesh", {})

    if show_header:
        if theme == "horoscope":
            st.markdown(
                _wrap(
                    theme,
                    f"<div class='subtle' style='letter-spacing:3px;text-transform:uppercase'>"
                    f"Personal prediction &middot; {pred['focus_intent']}</div>"
                    f"<div style='font-family:\"Cormorant Garamond\",serif;font-size:22px;"
                    f"color:#ffe9a8;line-height:1.4;margin-top:6px'>{pred['name'] or 'Native'}</div>"
                    f"<div class='subtle' style='margin-top:4px'>"
                    f"{pred['birth']['date']} {pred['birth']['time']} &middot; {pred['birth']['place']}"
                    f" &middot; Lagna {pred['birth']['lagna']}</div>",
                    border="rgba(245,197,66,0.35)",
                ),
                unsafe_allow_html=True,
            )
        else:
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

    if rk:
        nav = rk["navaratna"]
        chip = _chip_class(nav["verdict"], theme)
        nav_inner = (
            f"<span class='{'pill' if theme == 'horoscope' else chip}' "
            f"style='{'' if theme != 'horoscope' else f'background:{chip};color:#0b0e1a;border:none'}'>"
            f"{nav['verdict']} — {nav['percent']}%</span>"
            f"<div class='{'subtle' if theme == 'horoscope' else 'pred-title'}' "
            f"style='margin-top:8px;font-size:{'13px' if theme == 'horoscope' else '20px'};"
            f"color:{'#9aa3b8' if theme == 'horoscope' else '#ffe9a8'}'>"
            f"Rishikesh Panchang Birth Quality</div>"
            f"<div style='margin-top:6px;color:#9aa3b8'>"
            f"Ishtakal: {rk['ishtakal']['formatted']} after sunrise ({rk['sunrise_at_birth']})<br>"
            f"{rk['tradition']}</div>"
        )
        st.markdown(_wrap(theme, nav_inner), unsafe_allow_html=True)

    heading = "####" if theme == "horoscope" else "###"
    st.markdown(f"{heading} Birth Panchang (at your birth time)")
    p1, p2, p3, p4, p5 = st.columns(5)
    for col, label, val in zip(
        [p1, p2, p3, p4, p5],
        ["Vaara", "Tithi", "Nakshatra", "Yoga", "Karana"],
        [pc["vaara"], pc["tithi"],
         f"{pc['nakshatra']} (p.{pc['nakshatra_pada']})", pc["yoga"], pc["karana"]],
    ):
        col.markdown(f"**{label}**  \n{val}")

    if rk:
        av = rk["avakhada"]
        st.markdown(f"{heading} Avakhada Chakra")
        a1, a2, a3, a4, a5 = st.columns(5)
        for col, label, val in zip(
            [a1, a2, a3, a4, a5],
            ["Varna", "Vashya", "Yoni", "Gana", "Nadi"],
            [av["varna"], av["vashya"], av["yoni"], av["gana"], av["nadi"]],
        ):
            col.markdown(f"**{label}**  \n{val}")

        st.markdown(f"{heading} Five Limbs (Phalita Navaratna weights)")
        for item in rk["navaratna"]["breakdown"]:
            limb = rk["limbs"][item["limb"]]
            q = item["quality"]
            if theme == "horoscope":
                chip_bg = (
                    "#6fcf97" if q in _LIMB_GOOD else
                    "#ef6b6b" if q in _LIMB_BAD else "#f2c94c"
                )
                inner = (
                    f"<span class='pill' style='background:{chip_bg};color:#0b0e1a;border:none'>"
                    f"{item['limb'].title()} (wt {item['weight']}) — {q}</span>"
                    f"<div style='margin-top:6px;font-size:13px;color:#9aa3b8'>{limb['element']}</div>"
                    f"<div style='margin-top:4px'>{limb['note']}</div>"
                )
            else:
                chip_class = (
                    "chip-ok" if q in _LIMB_GOOD else
                    "chip-bad" if q in _LIMB_BAD else "chip-mix"
                )
                inner = (
                    f"<span class='{chip_class}'>{item['limb'].title()} "
                    f"(wt {item['weight']}) — {q}</span>"
                    f"<div style='margin-top:6px;font-size:13px;color:#9aa3b8'>{limb['element']}</div>"
                    f"<div style='margin-top:4px'>{limb['note']}</div>"
                )
            st.markdown(_wrap(theme, inner), unsafe_allow_html=True)
        st.caption(rk["navaratna"]["priority_note"])

    st.markdown(f"{heading} Overview")
    st.markdown(_wrap(theme, pred["opening"]), unsafe_allow_html=True)

    st.markdown(f"{heading} Life predictions")
    for lp in pred["life_predictions"]:
        chip = _chip_class(lp["verdict"], theme)
        if theme == "horoscope":
            inner = (
                f"<span class='pill' style='background:{chip};color:#0b0e1a;border:none'>"
                f"{lp['verdict']}</span>"
                f"<b style='font-size:17px;color:#fff;display:block;margin-top:8px'>{lp['area']}</b>"
                f"<div style='margin-top:6px'>{lp['prediction']}</div>"
            )
        else:
            inner = (
                f"<span class='{chip}'>{lp['verdict']}</span>"
                f"<div class='pred-title' style='margin-top:8px'>{lp['area']}</div>"
                f"<div style='margin-top:6px'>{lp['prediction']}</div>"
            )
        st.markdown(_wrap(theme, inner), unsafe_allow_html=True)

    st.markdown(f"{heading} Your focus area")
    for fl in pred["focus_detail"]:
        st.markdown(f"- {fl}")

    st.markdown(f"{heading} Timing & year ahead")
    t = pred["timing"]
    timing_inner = (
        f"Birth Nakshatra: <b>{t['birth_nakshatra']}</b> "
        f"(Dasha lord: {t['birth_nakshatra_lord']})<br>"
        f"Current: <b>{t['current_maha'] or '—'}</b> Mahadasha"
        + (f" / {t['current_antar']} Antardasha" if t.get("current_antar") else "")
        + f"<br>{t['year_ahead']}<br>"
        f"Sade Sati: {t['sade_sati']}<br>"
        f"Guru Gochar: {t.get('guru_gochar', '—')}"
    )
    st.markdown(_wrap(theme, timing_inner), unsafe_allow_html=True)

    if pred["cautions"]:
        st.markdown(f"{heading} Cautions")
        for c in pred["cautions"]:
            if theme == "horoscope":
                st.markdown(
                    _wrap(theme, c, border="rgba(239,107,107,0.3)"),
                    unsafe_allow_html=True,
                )
            else:
                st.warning(c)

    lk = pred["lucky"]
    st.markdown(f"{heading} Favourable elements")
    lucky_inner = (
        f"Weekday energy: {lk['day']} \u00b7 Birth star: {lk['nakshatra']} "
        f"(lord {lk['nakshatra_lord']}) \u00b7 Gemstone hint: {lk['gemstone_hint']}"
    )
    st.markdown(_wrap(theme, lucky_inner), unsafe_allow_html=True)

    if show_download:
        md = prediction_markdown(pred)
        st.download_button(
            download_label, md,
            file_name=f"prediction_{(pred['name'] or 'chart').replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    default_caption = (
        "Predictions follow the Shri Kashi Vishwanath Hrishikesh Panchang tradition: "
        "Ishtakal, five-limb Navaratna weighting, Avakhada Chakra, Vimshottari Dasha & Gochar. "
        "For guidance and self-reflection, not deterministic fate."
    )
    st.caption(footer_caption or default_caption)
