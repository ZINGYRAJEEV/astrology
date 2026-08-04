"""Modern dashboard + spiderweb (radar) visuals for prediction reports.

Inspired by the FlowTest automation dashboard pattern: metric strip + chart
first, then the written reading. Scores come from life-area verdicts blended
with house strength / Ashtakavarga where available.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import plotly.graph_objects as go


# Short axis labels that fit a radar chart without crowding.
_AXIS_LABEL = {
    "Personality & nature": "Self",
    "Personality & self": "Self",
    "Wealth & income": "Wealth",
    "Career & status": "Career",
    "Marriage & love": "Love",
    "Health & vitality": "Health",
    "Spiritual path": "Spirit",
}


def life_area_scores(pred: Dict) -> List[Dict]:
    """Return [{label, area, score, verdict}, ...] for spiderweb axes."""
    rows: List[Dict] = []
    for lp in pred.get("life_predictions", []):
        area = lp.get("area", "")
        label = _AXIS_LABEL.get(area) or lp.get("friendly_name") or area.split("&")[0].strip()
        score = lp.get("score")
        if score is None:
            score = {"Supported": 78, "Mixed": 52, "Challenged": 28}.get(
                lp.get("verdict", "Mixed"), 50
            )
        rows.append({
            "label": label,
            "area": area,
            "score": int(score),
            "verdict": lp.get("verdict", "Mixed"),
        })
    return rows


def dashboard_metrics(pred: Dict) -> Dict:
    """Top-line KPIs for the FlowTest-style metric strip."""
    areas = life_area_scores(pred)
    supported = sum(1 for a in areas if a["verdict"] == "Supported")
    challenged = sum(1 for a in areas if a["verdict"] == "Challenged")
    mixed = sum(1 for a in areas if a["verdict"] == "Mixed")
    avg = round(sum(a["score"] for a in areas) / len(areas)) if areas else 50
    nav = pred.get("rishikesh", {}).get("navaratna", {})
    combos = pred.get("combinations_reading") or {}
    from .combinations import outcome_balance
    bal = outcome_balance(combos) if isinstance(combos, dict) and combos.get("areas") else {
        "score": avg, "good": supported, "caution": challenged, "neutral": mixed,
    }
    return {
        "birth_quality": int(nav.get("percent", 0) or 0),
        "birth_verdict": nav.get("verdict", "—"),
        "area_avg": avg,
        "supported": supported,
        "challenged": challenged,
        "mixed": mixed,
        "balance": bal["score"],
        "area_count": len(areas),
    }


def spiderweb_figure(
    pred: Dict,
    *,
    theme: str = "horoscope",
) -> go.Figure:
    """Plotly polar radar chart of life-area strengths."""
    areas = life_area_scores(pred)
    if not areas:
        fig = go.Figure()
        fig.update_layout(title="No life-area scores available", height=360)
        return fig

    labels = [a["label"] for a in areas]
    scores = [a["score"] for a in areas]
    # Close the polygon.
    labels_c = labels + [labels[0]]
    scores_c = scores + [scores[0]]

    dark = theme == "horoscope"
    line = "#f5c542" if dark else "#f83b66"
    fill = "rgba(245,197,66,0.28)" if dark else "rgba(248,59,102,0.22)"
    grid = "rgba(255,255,255,0.12)" if dark else "rgba(36,30,27,0.12)"
    font = "#e8ebf2" if dark else "#241e1b"
    paper = "rgba(0,0,0,0)"

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores_c,
        theta=labels_c,
        fill="toself",
        fillcolor=fill,
        line=dict(color=line, width=2.5),
        marker=dict(size=7, color=line),
        name="Life areas",
        hovertemplate="<b>%{theta}</b><br>Strength: %{r}<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=paper,
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickvals=[25, 50, 75, 100],
                tickfont=dict(size=10, color=font),
                gridcolor=grid, linecolor=grid,
            ),
            angularaxis=dict(
                tickfont=dict(size=13, color=font, family="Inter, DM Sans, sans-serif"),
                gridcolor=grid, linecolor=grid,
            ),
        ),
        showlegend=False,
        paper_bgcolor=paper,
        plot_bgcolor=paper,
        margin=dict(l=40, r=40, t=36, b=36),
        height=420,
        font=dict(color=font, family="Inter, DM Sans, sans-serif"),
        title=dict(
            text="Life-area strength map",
            font=dict(size=16, color=line, family="Cormorant Garamond, Playfair Display, serif"),
            x=0.5, xanchor="center",
        ),
    )
    return fig


def score_table_rows(pred: Dict) -> List[Dict]:
    """Compact table rows under the spiderweb."""
    rows = []
    for a in life_area_scores(pred):
        rows.append({
            "Area": a["area"],
            "Strength": a["score"],
            "Verdict": a["verdict"],
        })
    return rows
