"""Chart layout logic (Step 2 of the build plan).

Maps the engine output into the data each traditional chart style needs.
The South Indian style uses *fixed sign* cells; the North Indian style uses
*fixed house* cells with rotating signs. This module only produces the
logical placement; ``viewer.py`` turns it into SVG.
"""

from __future__ import annotations

from typing import Dict, List

from . import reference as ref
from .chart_engine import Chart

# South Indian: signs occupy fixed cells in a 4x4 grid (only the border
# cells are used). Mapping = (row, col) -> sign index (0 = Aries).
SOUTH_INDIAN_CELLS = {
    (0, 0): 11, (0, 1): 0, (0, 2): 1, (0, 3): 2,
    (1, 0): 10, (1, 3): 3,
    (2, 0): 9, (2, 3): 4,
    (3, 0): 8, (3, 1): 7, (3, 2): 6, (3, 3): 5,
}


def house_contents(chart: Chart, varga: str = "D1") -> Dict[int, Dict]:
    """Per-house dict of sign + planets for the requested divisional chart.

    ``varga`` is "D1" (Rashi) or "D9" (Navamsha).
    """
    contents: Dict[int, Dict] = {}
    if varga == "D9":
        lagna_idx = chart.navamsha_lagna_index
    else:
        lagna_idx = chart.lagna_sign_index

    for h in range(1, 13):
        sign_idx = (lagna_idx + h - 1) % 12
        contents[h] = {
            "house": h,
            "sign": ref.SIGNS[sign_idx],
            "sign_index": sign_idx,
            "name": ref.HOUSE_NAME[h],
            "lord": ref.SIGN_LORD[ref.SIGNS[sign_idx]],
            "planets": [],
        }

    for p in chart.planets.values():
        house = p.navamsha_house if varga == "D9" else p.house
        contents[house]["planets"].append(p)
    return contents


def sign_to_planets(chart: Chart, varga: str = "D1") -> Dict[int, List]:
    """Sign index -> list of planets in that sign (for South Indian layout)."""
    mapping: Dict[int, List] = {i: [] for i in range(12)}
    for p in chart.planets.values():
        idx = p.navamsha_sign_index if varga == "D9" else p.sign_index
        mapping[idx].append(p)
    return mapping
