# Jyotish Darshan — Vedic Horoscope Interpretation

A free, offline Vedic astrology (Jyotish) application that builds a birth
chart and walks through the classical **12-step interpretation framework**
across three phases: construction, evaluation and synthesis. It implements
sidereal calculation (Lahiri Ayanamsha), planetary strengths, Graha Drishti
(aspects), the Navamsha (D-9) divisional chart, the Vimshottari Dasha timing
system, Sade Sati detection, and "Do No Harm" remedial measures.

Built with Python + Streamlit + Swiss Ephemeris (`pyswisseph`) — no paid
APIs, no network dependency for the core calculations.

## Features

| Build step | Module | What it does |
|---|---|---|
| 1. Chart engine | `astro/chart_engine.py` | Sidereal planetary longitudes, Lagna, signs & whole-sign houses |
| 2. Chart layout | `astro/chart_layout.py` | South / North Indian placement logic |
| 3. Strength rules | `astro/strength_calc.py`, `astro/reference.py` | Dignity scoring (exalted/own/friend/enemy/debilitated) |
| 4. Navamsha (D-9) | `astro/chart_engine.py` | D-9 placements + Vargottama detection |
| 5. Dasha engine | `astro/dasha_calc.py` | Vimshottari Mahadasha/Antardasha + Sade Sati |
| 6. 12-step wizard | `app.py` | Three-phase Streamlit UI |
| 7. Report | `astro/report.py` | Markdown + PDF auto-generated report |
| 8. Viewer | `astro/viewer.py` | SVG chart wheel/grid with hover tooltips |
| 9. Persistence | `astro/persistence.py` | SQLite save / load / compare charts |

Interpretation logic (functional benefic/malefic, house-by-house judging,
repeating-pattern detection, remedies) lives in `astro/interpret.py`.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Then enter birth **date, time and place** in the sidebar and click
**Calculate Chart**. Birth-time accuracy is mission-critical for the
Ascendant.

## Test

```bash
python tests/test_engine.py
```

## How the interpretation works

- **Phase 1 — Construction:** gather birth data, compute sidereal positions,
  determine the Ascendant, render the chart (South/North Indian, D-1/D-9),
  and pick your focus (health, career, marriage, etc.).
- **Phase 2 — Evaluation:** overall foundation score, each planet's dignity
  and functional nature, a house-by-house verdict from ruler + occupants +
  aspects, and a "repeating patterns" panel that raises confidence when
  several independent indicators agree.
- **Phase 3 — Synthesis:** a written reading tailored to your focus, the
  current Vimshottari Dasha, and remedial measures gated by the "Do No Harm"
  rule, plus a downloadable Markdown/PDF report.

## Notes & disclaimer

- Uses the built-in Moshier ephemeris model (arc-second accuracy, no data
  files needed).
- The Swiss Ephemeris binding is [`pysweph`](https://pypi.org/project/pysweph/),
  the maintained fork of `pyswisseph` (same `import swisseph` API) which ships
  wheels for current Python versions. The code also runs on the original
  `pyswisseph` if you prefer.
- Rahu is the **Mean Node**; Ketu is exactly opposite.
- This tool is for education and self-reflection, in the spirit of Jyotish
  as a lamp for insight — not deterministic fate.
