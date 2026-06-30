"""Interactive chart viewer (Step 8 of the build plan).

Renders the chart as an SVG (South Indian grid or North Indian diamond)
with planet glyphs, retrograde markers and hover tooltips. The SVG string
is embedded in Streamlit via ``components.html``.
"""

from __future__ import annotations

from typing import Dict, List

from . import reference as ref
from .chart_engine import Chart, PlanetPosition, format_dms
from .chart_layout import SOUTH_INDIAN_CELLS, sign_to_planets, house_contents

_BG = "#0b0e1a"
_LINE = "#4a4f63"
_TEXT = "#e8ebf2"
_ACCENT = "#f5c542"
_SIGN_TXT = "#8b93a7"
_BENEFIC = "#6fcf97"
_MALEFIC = "#ef6b6b"


def _planet_label(p: PlanetPosition) -> str:
    g = ref.PLANET_GLYPH[p.name]
    return g + ("\u207a" if p.retrograde else "")  # superscript + = retro marker


def _planet_color(name: str) -> str:
    return _BENEFIC if name in ref.NATURAL_BENEFICS else _MALEFIC


def _tooltip(p: PlanetPosition) -> str:
    retro = " (Retrograde)" if p.retrograde else ""
    return (
        f"{p.name} ({ref.PLANET_SANSKRIT[p.name]}){retro}\n"
        f"{p.sign} {format_dms(p.degree_in_sign)}\n"
        f"House {p.house} - {ref.HOUSE_NAME[p.house]}\n"
        f"Nakshatra: {p.nakshatra} (pada {p.nakshatra_pada})\n"
        f"Navamsha: {p.navamsha_sign}"
    )


def _planets_text(planets: List[PlanetPosition], cx: float, cy: float) -> str:
    """Lay out up to a handful of planet glyphs around a cell centre."""
    out = []
    n = len(planets)
    if n == 0:
        return ""
    per_row = 3
    line_h = 16
    rows = (n + per_row - 1) // per_row
    start_y = cy - (rows - 1) * line_h / 2 + 4
    for i, p in enumerate(planets):
        row = i // per_row
        col = i % per_row
        in_row = min(per_row, n - row * per_row)
        x = cx + (col - (in_row - 1) / 2) * 26
        y = start_y + row * line_h
        out.append(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{_planet_color(p.name)}" '
            f'font-size="13" font-weight="600" text-anchor="middle">'
            f'<title>{_tooltip(p)}</title>{_planet_label(p)}</text>'
        )
    return "".join(out)


# ---------------------------------------------------------------------------
# South Indian (fixed signs, 4x4 grid)
# ---------------------------------------------------------------------------
def south_indian_svg(chart: Chart, varga: str = "D1", size: int = 460) -> str:
    cell = size / 4
    lagna_idx = chart.navamsha_lagna_index if varga == "D9" else chart.lagna_sign_index
    planets_by_sign = sign_to_planets(chart, varga)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">',
        f'<defs><radialGradient id="bgGrad" cx="50%" cy="20%" r="90%">'
        f'<stop offset="0%" stop-color="#141a2e"/>'
        f'<stop offset="100%" stop-color="{_BG}"/></radialGradient></defs>',
        f'<rect width="{size}" height="{size}" rx="18" fill="url(#bgGrad)" '
        f'stroke="rgba(245,197,66,0.18)" stroke-width="1"/>',
    ]

    for (row, col), sign_idx in SOUTH_INDIAN_CELLS.items():
        x = col * cell
        y = row * cell
        is_lagna = sign_idx == lagna_idx
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
            f'fill="none" stroke="{_LINE}" stroke-width="1.2"/>'
        )
        # sign abbreviation in the corner
        parts.append(
            f'<text x="{x+5}" y="{y+15}" fill="{_SIGN_TXT}" font-size="10">'
            f'{ref.SIGN_SANSKRIT[ref.SIGNS[sign_idx]][:3]}</text>'
        )
        if is_lagna:
            parts.append(
                f'<text x="{x+cell-5}" y="{y+15}" fill="{_ACCENT}" font-size="11" '
                f'font-weight="700" text-anchor="end">Asc</text>'
            )
            parts.append(
                f'<line x1="{x}" y1="{y}" x2="{x+18}" y2="{y+18}" '
                f'stroke="{_ACCENT}" stroke-width="2"/>'
            )
        parts.append(_planets_text(planets_by_sign[sign_idx], x + cell / 2, y + cell / 2 + 4))

    parts.append(
        f'<text x="{size/2}" y="{size/2-6}" fill="{_SIGN_TXT}" font-size="12" '
        f'text-anchor="middle">South Indian</text>'
    )
    parts.append(
        f'<text x="{size/2}" y="{size/2+12}" fill="{_ACCENT}" font-size="13" '
        f'font-weight="700" text-anchor="middle">{"Navamsha D-9" if varga=="D9" else "Rashi D-1"}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# North Indian (fixed houses, diamond)
# ---------------------------------------------------------------------------
def _centroid(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def north_indian_svg(chart: Chart, varga: str = "D1", size: int = 460) -> str:
    S = size
    # key points
    TL, TR, BR, BL = (0, 0), (S, 0), (S, S), (0, S)
    T, R, B, L = (S/2, 0), (S, S/2), (S/2, S), (0, S/2)
    C = (S/2, S/2)
    QTL, QTR, QBR, QBL = (S/4, S/4), (3*S/4, S/4), (3*S/4, 3*S/4), (S/4, 3*S/4)

    house_polys = {
        1: [T, QTR, C, QTL],
        2: [TL, T, QTL],
        3: [TL, QTL, L],
        4: [L, QTL, C, QBL],
        5: [L, QBL, BL],
        6: [BL, QBL, B],
        7: [B, QBL, C, QBR],
        8: [B, QBR, BR],
        9: [BR, QBR, R],
        10: [R, QBR, C, QTR],
        11: [R, QTR, TR],
        12: [TR, QTR, T],
    }

    contents = house_contents(chart, varga)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" '
        f'viewBox="0 0 {S} {S}">',
        f'<defs><radialGradient id="bgGradN" cx="50%" cy="20%" r="90%">'
        f'<stop offset="0%" stop-color="#141a2e"/>'
        f'<stop offset="100%" stop-color="{_BG}"/></radialGradient></defs>',
        f'<rect width="{S}" height="{S}" rx="18" fill="url(#bgGradN)"/>',
        # outer square
        f'<rect x="0" y="0" width="{S}" height="{S}" rx="18" fill="none" stroke="{_LINE}" stroke-width="1.2"/>',
        # diagonals
        f'<line x1="0" y1="0" x2="{S}" y2="{S}" stroke="{_LINE}" stroke-width="1.2"/>',
        f'<line x1="{S}" y1="0" x2="0" y2="{S}" stroke="{_LINE}" stroke-width="1.2"/>',
        # inner diamond
        f'<polygon points="{S/2},0 {S},{S/2} {S/2},{S} 0,{S/2}" fill="none" '
        f'stroke="{_LINE}" stroke-width="1.2"/>',
    ]

    for h, poly in house_polys.items():
        cx, cy = _centroid(poly)
        info = contents[h]
        # sign number (Rashi number 1-12) shown faint
        parts.append(
            f'<text x="{cx:.1f}" y="{cy-18:.1f}" fill="{_SIGN_TXT}" font-size="10" '
            f'text-anchor="middle">{info["sign_index"]+1} {ref.SIGN_SANSKRIT[info["sign"]][:3]}</text>'
        )
        if h == 1:
            parts.append(
                f'<text x="{cx:.1f}" y="{cy-30:.1f}" fill="{_ACCENT}" font-size="10" '
                f'font-weight="700" text-anchor="middle">Asc</text>'
            )
        parts.append(_planets_text(info["planets"], cx, cy + 2))

    parts.append(
        f'<text x="6" y="{S-8}" fill="{_SIGN_TXT}" font-size="11">North Indian - '
        f'{"Navamsha D-9" if varga=="D9" else "Rashi D-1"}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def chart_svg(chart: Chart, style: str = "South Indian", varga: str = "D1", size: int = 460) -> str:
    if style == "North Indian":
        return north_indian_svg(chart, varga, size)
    return south_indian_svg(chart, varga, size)
