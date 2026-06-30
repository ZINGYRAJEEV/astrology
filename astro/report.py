"""Auto-generated report (Step 7 of the build plan).

Produces a structured, prose report from the synthesised findings. Two
outputs are supported: a Markdown string (for on-screen display / download)
and a PDF (via reportlab) organised by the briefing's phase structure.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Dict

from . import reference as ref
from .chart_engine import Chart, format_dms
from .strength_calc import all_strengths
from .interpret import (
    synthesize, analyse_all_houses, recommend_remedies, plain_language_reading,
)
from .ashtakavarga import compute_sav
from . import wisdom


def build_markdown(chart: Chart, intent: str = "General reading") -> str:
    syn = synthesize(chart, intent)
    strengths = all_strengths(chart)
    houses = analyse_all_houses(chart)
    remedies = recommend_remedies(chart)
    b = chart.birth

    lines = []
    lines.append(f"# Vedic Horoscope Report - {b.name or 'Native'}")
    lines.append("")
    lines.append(
        f"**Birth:** {b.day:02d}/{b.month:02d}/{b.year} at {b.hour:02d}:{b.minute:02d} "
        f"({'+' if b.tz_offset>=0 else ''}{b.tz_offset} UTC) - {b.place}"
    )
    lines.append(
        f"**Ascendant:** {chart.lagna_sign} ({ref.SIGN_SANSKRIT[chart.lagna_sign]}) "
        f"| **Ayanamsha (Lahiri):** {chart.ayanamsha:.4f}\u00b0"
    )
    lines.append(f"_Generated {datetime.now():%Y-%m-%d %H:%M}_")
    lines.append("")

    # Beginner-friendly reading first.
    reading = plain_language_reading(chart, intent)
    lines.append(f"## Your Reading - {reading['title']} (in plain language)")
    lines.append(f"**{reading['headline']}**")
    lines.append("")
    if reading.get("headline_extra"):
        lines.append(f"_{reading['headline_extra']}_")
        lines.append("")
    lines.append(reading["overview"])
    lines.append("")
    for a in reading["key_areas"]:
        lines.append(f"- **{a['title']} ({a['label']})** - {a['explanation']} {a['advice']}")
    lines.append("")
    if reading["timing"]:
        lines.append("**Right now:** " + reading["timing"])
        lines.append("")
    lines.append("**Action steps:**")
    for s in reading["actions"]:
        lines.append(f"- {s}")
    lines.append("")

    lines.append("## Phase 3 - Synthesis")
    for para in syn["paragraphs"]:
        lines.append(para)
        lines.append("")

    lines.append("## Planetary Positions")
    lines.append("| Planet | Sign | Degree | House | Nakshatra | Dignity | Strength |")
    lines.append("|---|---|---|---|---|---|---|")
    for name in ref.PLANETS:
        p = chart.planets[name]
        s = strengths[name]
        retro = " (R)" if p.retrograde else ""
        lines.append(
            f"| {name}{retro} | {p.sign} | {format_dms(p.degree_in_sign)} | {p.house} "
            f"| {p.nakshatra} | {s.dignity} | {s.percent}% |"
        )
    lines.append("")

    sav = compute_sav(chart)
    lines.append("## Sarvashtakavarga (Math of Opportunity)")
    lines.append(f"_Total {sav['total']} bindus, average {sav['average']:.0f} per house. "
                 "30+ auspicious, 25-30 stable, below 25 challenging._")
    lines.append("")
    lines.append("| House | Sign | Bindus | Strength |")
    lines.append("|---|---|---|---|")
    for h in range(1, 13):
        ph = sav["per_house"][h]
        lines.append(f"| {h} ({ref.HOUSE_NAME[h]}) | {ph['sign']} | {ph['points']} | {ph['class']} |")
    lines.append("")

    lines.append("## House-by-House Analysis")
    for h in range(1, 13):
        r = houses[h]
        lines.append(f"### House {h} - {r.name} ({r.sign}) - {r.verdict}")
        lines.append(f"*{r.signification}* ({r.category})")
        lines.append(f"- Lord **{r.lord}** ({r.lord_dignity}) in house {r.lord_house}")
        if r.occupants:
            lines.append(f"- Occupants: {', '.join(r.occupants)}")
        if r.aspecting:
            lines.append(f"- Aspected by: {', '.join(r.aspecting)}")
        lines.append(f"- Ashtakavarga: {r.sav_points} bindus ({r.sav_class})")
        lines.append("")

    lines.append("## Remedial Measures (Upaye)")
    lines.append("_Gated by the 'Do No Harm' rule - only functional benefics are strengthened._")
    lines.append("")
    if not remedies:
        lines.append("No urgent remedies indicated; functional benefics are reasonably strong.")
    for rec in remedies:
        lines.append(f"### {rec['planet']}")
        lines.append(f"- {rec['rationale']}")
        lines.append(f"- Gemstone: {rec['gemstone']}")
        lines.append(f"- Mantra: {rec['mantra']}")
        lines.append(f"- Charity: {rec['charity']}")
        lines.append("")

    wr = wisdom.witness_reading(chart)
    lines.append("## The Witness (Ashtavakra Gita)")
    lines.append(f"_{wr['intro']}_")
    lines.append("")
    for refl in wr["reflections"]:
        lines.append(f"- {refl}")
    lines.append("")
    lines.append(f"> {wr['closing']}")
    lines.append("")

    lines.append("---")
    lines.append(
        "_This report is generated for educational and self-reflection purposes, "
        "in the spirit of Jyotish as a tool for insight, not deterministic fate._"
    )
    return "\n".join(lines)


def build_pdf(chart: Chart, intent: str = "General reading") -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    )

    syn = synthesize(chart, intent)
    strengths = all_strengths(chart)
    houses = analyse_all_houses(chart)
    remedies = recommend_remedies(chart)
    b = chart.birth

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=colors.HexColor("#5b3a8a"))
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=colors.HexColor("#5b3a8a"))
    body = styles["BodyText"]
    flow = []

    flow.append(Paragraph(f"Vedic Horoscope Report - {b.name or 'Native'}", h1))
    flow.append(Paragraph(
        f"Birth: {b.day:02d}/{b.month:02d}/{b.year} at {b.hour:02d}:{b.minute:02d} "
        f"(UTC{'+' if b.tz_offset>=0 else ''}{b.tz_offset}) &mdash; {b.place}", body))
    flow.append(Paragraph(
        f"Ascendant: {chart.lagna_sign} ({ref.SIGN_SANSKRIT[chart.lagna_sign]}) | "
        f"Lahiri Ayanamsha: {chart.ayanamsha:.4f}&deg;", body))
    flow.append(Spacer(1, 8))

    flow.append(Paragraph("Synthesis", h2))
    for para in syn["paragraphs"]:
        flow.append(Paragraph(para, body))
        flow.append(Spacer(1, 4))

    flow.append(Spacer(1, 6))
    flow.append(Paragraph("Planetary Positions", h2))
    data = [["Planet", "Sign", "Degree", "Hse", "Nakshatra", "Dignity", "Str%"]]
    for name in ref.PLANETS:
        p = chart.planets[name]
        s = strengths[name]
        retro = " (R)" if p.retrograde else ""
        data.append([name + retro, p.sign, format_dms(p.degree_in_sign), str(p.house),
                     p.nakshatra, s.dignity, f"{s.percent}"])
    tbl = Table(data, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5b3a8a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2eef8")]),
    ]))
    flow.append(tbl)
    flow.append(Spacer(1, 10))

    # Sarvashtakavarga table.
    sav = compute_sav(chart)
    flow.append(Paragraph("Sarvashtakavarga (Math of Opportunity)", h2))
    sdata = [["House", "Sign", "Bindus", "Strength"]]
    for h in range(1, 13):
        ph = sav["per_house"][h]
        sdata.append([f"{h} {ref.HOUSE_NAME[h]}", ph["sign"], str(ph["points"]), ph["class"]])
    stbl = Table(sdata, repeatRows=1)
    stbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5b3a8a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2eef8")]),
    ]))
    flow.append(stbl)
    flow.append(Spacer(1, 10))

    flow.append(Paragraph("House-by-House Analysis", h2))
    for h in range(1, 13):
        r = houses[h]
        flow.append(Paragraph(
            f"<b>House {h} - {r.name} ({r.sign}) - {r.verdict}</b>", body))
        flow.append(Paragraph(
            f"<i>{r.signification}</i> Lord {r.lord} ({r.lord_dignity}) in house {r.lord_house}."
            + (f" Occupants: {', '.join(r.occupants)}." if r.occupants else "")
            + (f" Aspected by: {', '.join(r.aspecting)}." if r.aspecting else "")
            + f" Ashtakavarga: {r.sav_points} bindus ({r.sav_class}).", body))
        flow.append(Spacer(1, 3))

    flow.append(Spacer(1, 6))
    flow.append(Paragraph("Remedial Measures (Do No Harm)", h2))
    if not remedies:
        flow.append(Paragraph("No urgent remedies indicated.", body))
    for rec in remedies:
        flow.append(Paragraph(
            f"<b>{rec['planet']}</b>: {rec['rationale']} "
            f"Gemstone: {rec['gemstone']}. Mantra: {rec['mantra']}. Charity: {rec['charity']}.",
            body))
        flow.append(Spacer(1, 3))

    # Witness (Ashtavakra) reflection.
    wr = wisdom.witness_reading(chart)
    flow.append(Spacer(1, 8))
    flow.append(Paragraph("The Witness (Ashtavakra Gita)", h2))
    flow.append(Paragraph(f"<i>{wr['intro']}</i>", body))
    flow.append(Spacer(1, 4))
    for refl in wr["reflections"]:
        flow.append(Paragraph(refl, body))
        flow.append(Spacer(1, 3))
    flow.append(Spacer(1, 4))
    flow.append(Paragraph(f"<b>{wr['closing']}</b>", h2))

    doc.build(flow)
    return buf.getvalue()
