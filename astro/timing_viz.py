"""Timing visuals for Mahadasha / Antardasha impact maps.

Uses Plotly (already a project dependency) so graphs render reliably on
Streamlit Cloud without external CDN scripts. Optional D3 HTML remains
available for local/embed experiments via ``timing_d3_html``.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional

_AREA_COLOURS = {
    "Career": "#5b8def",
    "Wealth": "#6fcf97",
    "Family": "#f2c94c",
    "Health": "#eb8f6b",
    "Spiritual": "#c9b6ff",
}

_TONE_COLOUR = {"good": "#6fcf97", "mixed": "#f2c94c", "bad": "#ef6b6b"}


def _payload(summary: Dict) -> Dict:
    """Slim JSON for optional D3 HTML embed."""
    chapters = []
    for c in summary.get("chapters", []):
        chapters.append({
            "label": c["label"],
            "maha": c["maha"],
            "antar": c["antar"],
            "start": c["start"],
            "end": c["end"],
            "startLabel": c["start_label"],
            "endLabel": c["end_label"],
            "mahaTheme": c["maha_theme"],
            "antarTheme": c["antar_theme"],
            "isCurrent": c["is_current"],
            "scores": {k: {"score": v["score"], "tone": v["tone"], "note": v["note"]}
                       for k, v in c["scores"].items()},
            "risks": c["risks"],
            "opportunities": c["opportunities"],
            "phases": [
                {
                    "name": p["name"],
                    "start": p["start"],
                    "end": p["end"],
                    "scores": {k: v["score"] for k, v in p["scores"].items()},
                }
                for p in c.get("phases", [])
            ],
        })
    years = []
    for y in summary.get("years", []):
        years.append({
            "year": y["year"],
            "tag": y["tag"],
            "scores": {k: v["score"] for k, v in y["scores"].items()},
            "risks": y["risks"],
            "opportunities": y["opportunities"],
            "chapters": y["chapters"],
        })
    return {
        "areas": summary.get("areas", []),
        "colours": dict(_AREA_COLOURS),
        "current": summary.get("current") or {},
        "chapters": chapters,
        "years": years,
        "legend": summary.get("legend", {}),
        "asOf": summary.get("as_of"),
    }


def _avg_tone(scores: Dict) -> str:
    vals = [v["score"] if isinstance(v, dict) else v for v in scores.values()]
    mean = sum(vals) / max(len(vals), 1)
    if mean >= 65:
        return "good"
    if mean <= 38:
        return "bad"
    return "mixed"


def timeline_figure(summary: Dict):
    """Horizontal Antardasha timeline (good / mixed / challenged colours)."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        return None

    chapters = summary.get("chapters") or []
    if not chapters:
        return None

    fig = go.Figure()
    for ch in reversed(chapters):
        start = datetime.fromisoformat(ch["start"])
        end = datetime.fromisoformat(ch["end"])
        tone = _avg_tone(ch["scores"])
        fig.add_trace(go.Bar(
            base=[start],
            x=[(end - start).total_seconds() * 1000],
            y=[ch["label"]],
            orientation="h",
            marker=dict(
                color=_TONE_COLOUR[tone],
                line=dict(
                    color="#ffe9a8" if ch.get("is_current") else "rgba(0,0,0,0)",
                    width=2 if ch.get("is_current") else 0,
                ),
            ),
            hovertemplate=(
                f"<b>{ch['label']}</b><br>"
                f"{ch['start_label']} → {ch['end_label']}<br>"
                + "<br>".join(
                    f"{a}: {ch['scores'][a]['score']} ({ch['scores'][a]['label']})"
                    for a in summary.get("areas", [])
                )
                + "<extra></extra>"
            ),
            showlegend=False,
        ))

    fig.update_layout(
        title=dict(text="Antardasha timeline", font=dict(color="#f5c542", size=16)),
        barmode="overlay",
        height=max(220, 48 * len(chapters) + 80),
        margin=dict(l=20, r=20, t=50, b=40),
        paper_bgcolor="rgba(11,14,26,0)",
        plot_bgcolor="rgba(21,26,44,0.55)",
        font=dict(color="#e8ebf2"),
        xaxis=dict(
            type="date",
            gridcolor="rgba(255,255,255,0.06)",
            title="",
        ),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", title=""),
        bargap=0.35,
    )
    return fig


def impact_figure(summary: Dict):
    """Multi-line impact chart: high = favourable, low = challenged."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        return None

    chapters = summary.get("chapters") or []
    areas = summary.get("areas") or []
    if not chapters or not areas:
        return None

    # Prefer phase midpoints for smoother curves.
    xs: List[datetime] = []
    series: Dict[str, List[float]] = {a: [] for a in areas}
    labels: List[str] = []
    for ch in chapters:
        phases = ch.get("phases") or []
        if phases:
            for p in phases:
                mid = datetime.fromisoformat(p["start"]) + (
                    datetime.fromisoformat(p["end"]) - datetime.fromisoformat(p["start"])
                ) / 2
                xs.append(mid)
                labels.append(f"{ch['label']} · {p['name']}")
                for a in areas:
                    series[a].append(float(p["scores"][a]["score"] if isinstance(p["scores"][a], dict) else p["scores"][a]))
        else:
            mid = datetime.fromisoformat(ch["start"]) + (
                datetime.fromisoformat(ch["end"]) - datetime.fromisoformat(ch["start"])
            ) / 2
            xs.append(mid)
            labels.append(ch["label"])
            for a in areas:
                series[a].append(float(ch["scores"][a]["score"]))

    fig = go.Figure()
    # Soft good/mixed/bad bands
    if xs:
        x0, x1 = xs[0], xs[-1]
        for y0, y1, colour in (
            (0, 38, "rgba(239,107,107,0.10)"),
            (38, 65, "rgba(242,201,76,0.08)"),
            (65, 100, "rgba(111,207,151,0.10)"),
        ):
            fig.add_shape(
                type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                fillcolor=colour, line=dict(width=0), layer="below",
            )

    for a in areas:
        fig.add_trace(go.Scatter(
            x=xs,
            y=series[a],
            mode="lines+markers",
            name=a,
            line=dict(color=_AREA_COLOURS.get(a, "#aaa"), width=2.4),
            marker=dict(size=7),
            customdata=labels,
            hovertemplate="%{customdata}<br>" + a + ": %{y:.0f}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Impact by life area (high = favourable)", font=dict(color="#f5c542", size=16)),
        height=360,
        margin=dict(l=40, r=20, t=50, b=40),
        paper_bgcolor="rgba(11,14,26,0)",
        plot_bgcolor="rgba(21,26,44,0.55)",
        font=dict(color="#e8ebf2"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(range=[0, 100], title="Score", gridcolor="rgba(255,255,255,0.06)"),
        hovermode="x unified",
    )
    return fig


def render_timing_viz(summary: Optional[Dict], *, height: int = 780) -> None:
    """Streamlit helper: Plotly timeline + impact lines + year cards."""
    if not summary or not summary.get("chapters"):
        return

    import streamlit as st

    st.caption(
        "Green = favourable · amber = mixed · red = challenged. "
        "Hover a bar or line for scores."
    )

    tl = timeline_figure(summary)
    if tl is not None:
        st.plotly_chart(tl, use_container_width=True, config={"displayModeBar": False})
    else:
        st.warning("Plotly is required to draw the timing timeline.")

    imp = impact_figure(summary)
    if imp is not None:
        st.plotly_chart(imp, use_container_width=True, config={"displayModeBar": False})

    years = summary.get("years") or []
    if years:
        st.markdown("#### Year risk & opportunity")
        st.caption("Open a year for short watch / lean-into notes.")
        cols = st.columns(min(3, len(years)))
        for i, y in enumerate(years):
            with cols[i % len(cols)]:
                tone = _avg_tone(y["scores"])
                border = _TONE_COLOUR[tone]
                with st.expander(f"{y['year']} — {y['tag']}", expanded=(i == 0)):
                    st.markdown(
                        f"<div style='border-left:4px solid {border};padding-left:10px'>",
                        unsafe_allow_html=True,
                    )
                    chips = " · ".join(
                        f"**{a}** {s['score']}" for a, s in y["scores"].items()
                    )
                    st.markdown(chips)
                    st.markdown("**Watch**")
                    for r in y.get("risks") or ["—"]:
                        st.markdown(f"- {r}")
                    st.markdown("**Lean into**")
                    for o in y.get("opportunities") or ["—"]:
                        st.markdown(f"- {o}")
                    if y.get("chapters"):
                        st.caption(" · ".join(y["chapters"]))
                    st.markdown("</div>", unsafe_allow_html=True)


def timing_d3_html(summary: Dict, *, height: int = 720) -> str:
    """Optional HTML+D3 document (CDN). Prefer ``render_timing_viz`` for Cloud."""
    data = json.dumps(_payload(summary), ensure_ascii=False).replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
</head><body style="background:#0b0e1a;color:#e8ebf2;font-family:sans-serif;padding:12px">
<p>Interactive D3 embed (requires CDN). App UI uses Plotly instead for reliability.</p>
<pre style="white-space:pre-wrap;font-size:11px;opacity:0.7">{data[:1200]}…</pre>
</body></html>
"""
