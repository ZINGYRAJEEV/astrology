"""Streamlit render helpers for Copilot-style chart explanations."""

from __future__ import annotations

from typing import Optional

import streamlit as st


def _tone_colour(tone: str) -> str:
    return {"good": "#6fcf97", "bad": "#ef6b6b", "mixed": "#f2c94c"}.get(tone, "#f2c94c")


def render_chart_explain(
    ex: dict,
    *,
    theme: str = "default",
    show_summary: bool = True,
    show_timing: bool = True,
) -> None:
    """Render structured birth summary + timing why/phases."""
    if not ex:
        return

    if show_summary:
        st.markdown(f"### {ex.get('title', 'Birth Chart Summary')}")
        st.caption(
            "Clean, structured summary — the parts that matter. "
            "Scan verdicts first; open a chapter for phase detail and “why”."
        )

        o = ex.get("overall") or {}
        st.markdown(
            f"**Overall quality:** {o.get('score', '—')}% ({o.get('verdict', '—')}) — "
            f"“{o.get('quote', '')}”. {o.get('balance', '')}"
        )

        idn = ex.get("identity") or {}
        with st.expander("Core identity", expanded=True):
            st.markdown(f"- **Ascendant:** {idn.get('ascendant', '—')}")
            st.markdown(f"- **Moon:** {idn.get('moon', '—')}")
            st.markdown(f"- **Chart ruler:** {idn.get('chart_ruler', '—')}")
            st.caption(idn.get("quote", ""))

        cur = ex.get("current_chapter") or {}
        with st.expander("Current life chapter", expanded=True):
            st.markdown(
                f"**Mahadasha:** {cur.get('maha') or '—'} · "
                f"**Antardasha:** {cur.get('antar') or '—'} "
                f"(until {cur.get('antar_until') or '—'})"
            )
            for t in cur.get("themes") or []:
                if t:
                    st.markdown(f"- {t}")
            st.caption(cur.get("quote", ""))
            if cur.get("sade_sati_active"):
                st.warning(f"Sade Sati: {cur.get('sade_sati')}")
            else:
                st.markdown(f"You are **not in Sade Sati** ({cur.get('sade_sati', '—')}).")

        with st.expander("Life areas — quick verdicts", expanded=True):
            for a in ex.get("life_areas") or []:
                colour = _tone_colour(a.get("tone", "mixed"))
                st.markdown(
                    f"<div style='margin:8px 0 4px;font-weight:700'>"
                    f"<span style='color:{colour}'>{a.get('name')} — {a.get('verdict')}</span></div>",
                    unsafe_allow_html=True,
                )
                for b in a.get("bullets") or []:
                    st.markdown(f"- {b}")

        snap = ex.get("planet_snapshot") or {}
        with st.expander("Planet-by-planet behaviour snapshot", expanded=False):
            if snap.get("strong"):
                st.markdown("**Strongest placements**")
                for s in snap["strong"]:
                    st.markdown(f"- {s}")
            if snap.get("challenged"):
                st.markdown("**Challenged placements**")
                for s in snap["challenged"]:
                    st.markdown(f"- {s}")

        with st.expander("Transits (Gochara) — current pressures", expanded=False):
            for g in ex.get("gochara") or []:
                st.markdown(f"- {g}")

        wve = ex.get("working_vs_effort") or {}
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Working well**")
            for x in wve.get("working") or []:
                st.markdown(f"- {x}")
        with c2:
            st.markdown("**Needs effort**")
            for x in wve.get("effort") or []:
                st.markdown(f"- {x}")

        fav = ex.get("favourable") or {}
        st.markdown(
            f"**Favourable:** Weekday **{fav.get('weekday', '—')}** · "
            f"Birth star **{fav.get('birth_star', '—')}** · "
            f"Gemstone hint: {fav.get('gemstone_hint', '—')}"
        )
        st.caption(ex.get("remedies_note", ""))

    # Timing chapters with why + phases
    chapters = ex.get("timing_chapters") or []
    if show_timing and chapters:
        st.markdown("### Timing-focused breakdown (with explanation)")
        st.caption(
            "Each chapter: what happens → why (Mahadasha / Antardasha / transits) → "
            "three phases for Career, Wealth, Family, Health, Spiritual."
        )
        for ch in chapters:
            title = f"{ch['label']} · {ch['dates']}"
            if ch.get("is_current"):
                title = "▶ " + title + " (current)"
            with st.expander(title, expanded=bool(ch.get("is_current"))):
                st.markdown(ch.get("intro", ""))
                why = ch.get("why") or {}
                st.markdown(f"**{why.get('maha', {}).get('title', 'Mahadasha')}**")
                st.markdown(why.get("maha", {}).get("placement", ""))
                brings = why.get("maha", {}).get("brings") or []
                if brings:
                    st.markdown("Brings: " + " · ".join(brings[:4]))
                st.caption(why.get("maha", {}).get("quote", ""))

                st.markdown(f"**{why.get('antar', {}).get('title', 'Antardasha')}**")
                st.markdown(why.get("antar", {}).get("placement", ""))
                acts = why.get("antar", {}).get("activates") or []
                if acts:
                    st.markdown("Activates: " + " · ".join(acts[:4]))
                st.caption(why.get("antar", {}).get("quote", ""))
                st.info(why.get("fluctuation", ""))

                for ph in ch.get("phases") or []:
                    st.markdown(f"#### {ph['name']} — *{ph.get('theme', '')}*")
                    st.caption(ph.get("dates", ""))
                    for w in ph.get("why") or []:
                        st.markdown(f"- **Why:** {w}")
                    if ph.get("gochara"):
                        st.markdown("Transit cues: " + "; ".join(ph["gochara"]))
                    for area, bullets in (ph.get("areas") or {}).items():
                        st.markdown(f"**{area}**")
                        for b in bullets[:3]:
                            st.markdown(f"- {b}")

                st.markdown("**Key takeaways**")
                for area, text in (ch.get("takeaways") or {}).items():
                    st.markdown(f"- **{area}:** {text}")
                if ch.get("next_teaser"):
                    st.success(ch["next_teaser"])

    years = ex.get("year_maps") or []
    if show_timing and years:
        with st.expander("Year risk & opportunity map", expanded=False):
            for y in years:
                st.markdown(f"**{y.get('headline', y.get('year'))}**")
                st.caption(y.get("summary", ""))
                if y.get("chapters"):
                    st.markdown("Chapters: " + " · ".join(y["chapters"]))
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("Risks")
                    for r in y.get("risks") or []:
                        st.markdown(f"- {r}")
                with c2:
                    st.markdown("Opportunities")
                    for o in y.get("opportunities") or []:
                        st.markdown(f"- {o}")
