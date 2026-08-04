"""Modern dashboard + spiderweb (radar) visuals for prediction reports.

Inspired by the FlowTest automation dashboard pattern: metric strip + chart
first, then the written reading. Scores come from life-area verdicts blended
with house strength / Ashtakavarga where available.

Plotly is preferred when installed; an SVG spiderweb is used as a fallback so
Streamlit Cloud never crashes if the package is still installing / unavailable.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

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


def chart_life_area_scores(chart) -> List[Dict]:
    """Life-area scores directly from a chart (for matching / dual spiderwebs)."""
    from . import prediction_data as pd
    from . import reference as ref
    from .friendly_report import format_house_section, format_personality_section
    from .interpret import analyse_all_houses
    from .strength_calc import all_strengths

    houses = analyse_all_houses(chart)
    strengths = all_strengths(chart)
    lagna_lord = ref.SIGN_LORD[chart.lagna_sign]
    ll = strengths[lagna_lord]
    moon = chart.planets["Moon"]
    # Lightweight personality score without full Rishikesh block.
    personality = format_personality_section(
        nak={"nature": "", "prediction": ""},
        av={"varna": "—", "varna_meaning": "—", "gana": "—", "yoni": "—", "nadi": "—"},
        nav_percent=55.0,
        vaara_text="", tithi_text="", yoga_text="", karana_text="",
        lagna=chart.lagna_sign, lagna_lord=lagna_lord,
        ll_dignity=ll.dignity, ll_score=ll.score, nav_verdict="Mixed",
    )
    # Override area name to match LIFE_AREAS personality key used elsewhere.
    personality["area"] = "Personality & nature"
    rows = [personality]
    for area_name, house_num, _ in pd.LIFE_AREAS[1:]:
        rows.append(format_house_section(area_name, house_num, houses[house_num]))
    # Reuse the same packing as life_area_scores.
    return life_area_scores({"life_predictions": rows})


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


def plotly_available() -> bool:
    try:
        import plotly.graph_objects  # noqa: F401
        return True
    except ImportError:
        return False


def spiderweb_figure(
    pred: Optional[Dict] = None,
    *,
    scores: Optional[List[Dict]] = None,
    theme: str = "horoscope",
    title: str = "Life-area strength map",
    line_color: Optional[str] = None,
    fill_color: Optional[str] = None,
) -> Optional[Any]:
    """Plotly polar radar chart, or None if plotly is not installed."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        return None

    areas = scores if scores is not None else life_area_scores(pred or {})
    if not areas:
        fig = go.Figure()
        fig.update_layout(title="No life-area scores available", height=360)
        return fig

    labels = [a["label"] for a in areas]
    vals = [a["score"] for a in areas]
    labels_c = labels + [labels[0]]
    scores_c = vals + [vals[0]]

    dark = theme == "horoscope"
    line = line_color or ("#f5c542" if dark else "#f83b66")
    fill = fill_color or ("rgba(245,197,66,0.28)" if dark else "rgba(248,59,102,0.22)")
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
            text=title,
            font=dict(size=16, color=line, family="Cormorant Garamond, Playfair Display, serif"),
            x=0.5, xanchor="center",
        ),
    )
    return fig


def spiderweb_overlay_figure(
    groom_scores: List[Dict],
    bride_scores: List[Dict],
    *,
    groom_name: str = "Groom",
    bride_name: str = "Bride",
    theme: str = "default",
) -> Optional[Any]:
    """Overlay bride + groom on one radar for quick comparison."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        return None
    if not groom_scores or not bride_scores:
        return None
    labels = [a["label"] for a in groom_scores]
    g_vals = [a["score"] for a in groom_scores] + [groom_scores[0]["score"]]
    b_vals = [a["score"] for a in bride_scores] + [bride_scores[0]["score"]]
    labels_c = labels + [labels[0]]
    dark = theme == "horoscope"
    grid = "rgba(255,255,255,0.12)" if dark else "rgba(36,30,27,0.12)"
    font = "#e8ebf2" if dark else "#241e1b"
    paper = "rgba(0,0,0,0)"
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=g_vals, theta=labels_c, fill="toself",
        fillcolor="rgba(86,160,255,0.22)", line=dict(color="#56a0ff", width=2.5),
        name=groom_name, hovertemplate="<b>%{theta}</b><br>" + groom_name + ": %{r}<extra></extra>",
    ))
    fig.add_trace(go.Scatterpolar(
        r=b_vals, theta=labels_c, fill="toself",
        fillcolor="rgba(245,197,66,0.22)", line=dict(color="#f5c542", width=2.5),
        name=bride_name, hovertemplate="<b>%{theta}</b><br>" + bride_name + ": %{r}<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=paper,
            radialaxis=dict(visible=True, range=[0, 100], tickvals=[25, 50, 75, 100],
                            tickfont=dict(size=10, color=font), gridcolor=grid, linecolor=grid),
            angularaxis=dict(tickfont=dict(size=13, color=font), gridcolor=grid, linecolor=grid),
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center"),
        paper_bgcolor=paper, plot_bgcolor=paper,
        margin=dict(l=40, r=40, t=56, b=36), height=440,
        font=dict(color=font),
        title=dict(text="Bride & Groom life-area comparison",
                   font=dict(size=16, color="#f5c542"), x=0.5, xanchor="center"),
    )
    return fig


def spiderweb_svg(
    pred: Optional[Dict] = None,
    *,
    scores: Optional[List[Dict]] = None,
    theme: str = "horoscope",
    size: int = 420,
    title: str = "Life-area strength map",
    line_color: Optional[str] = None,
) -> str:
    """Pure-SVG spiderweb that works without plotly (Streamlit Cloud safe)."""
    areas = scores if scores is not None else life_area_scores(pred or {})
    dark = theme == "horoscope"
    line = line_color or ("#f5c542" if dark else "#e11d48")
    fill = "rgba(245,197,66,0.30)" if dark else "rgba(225,29,72,0.22)"
    if line_color == "#56a0ff":
        fill = "rgba(86,160,255,0.28)"
    grid = "rgba(255,255,255,0.18)" if dark else "rgba(36,30,27,0.18)"
    font = "#e8ebf2" if dark else "#241e1b"
    cx = cy = size / 2
    radius = size * 0.34
    n = max(len(areas), 3)

    def point(i: int, score: float) -> tuple[float, float]:
        angle = -math.pi / 2 + (2 * math.pi * i / n)
        r = radius * (score / 100.0)
        return cx + r * math.cos(angle), cy + r * math.sin(angle)

    rings = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        pts = [point(i, frac * 100) for i in range(n)]
        d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
        rings.append(f'<path d="{d}" fill="none" stroke="{grid}" stroke-width="1"/>')

    spokes = []
    labels_svg = []
    for i, a in enumerate(areas or [{"label": "—", "score": 0}] * 3):
        x, y = point(i, 100)
        spokes.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}" '
            f'stroke="{grid}" stroke-width="1"/>'
        )
        lx, ly = point(i, 118)
        labels_svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{font}" font-size="13" '
            f'font-family="Inter,sans-serif" text-anchor="middle" '
            f'dominant-baseline="middle">{a["label"]}</text>'
        )

    poly = ""
    if areas:
        pts = [point(i, a["score"]) for i, a in enumerate(areas)]
        d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
        dots = "".join(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{line}"/>' for x, y in pts
        )
        poly = (
            f'<path d="{d}" fill="{fill}" stroke="{line}" stroke-width="2.5"/>'
            f"{dots}"
        )

    title_svg = (
        f'<text x="{cx:.1f}" y="28" fill="{line}" font-size="16" '
        f'font-family="Georgia,serif" text-anchor="middle" font-weight="700">'
        f"{title}</text>"
    )
    return (
        f'<svg viewBox="0 0 {size} {size}" width="100%" '
        f'style="max-width:{size}px;display:block;margin:0 auto">'
        f"{title_svg}{''.join(rings)}{''.join(spokes)}{poly}{''.join(labels_svg)}"
        f"</svg>"
    )


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
