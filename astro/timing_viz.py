"""D3.js timing visuals for Mahadasha / Antardasha impact maps.

Embeds via ``streamlit.components.v1.html``. Prefers clarity over text walls:
timeline bars + multi-series impact lines (good / mixed / challenged).
"""

from __future__ import annotations

import json
from typing import Dict, Optional


def _payload(summary: Dict) -> Dict:
    """Slim JSON for the browser (no Python objects)."""
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
    cur = summary.get("current") or {}
    return {
        "areas": summary.get("areas", []),
        "colours": {
            "Career": "#5b8def",
            "Wealth": "#6fcf97",
            "Family": "#f2c94c",
            "Health": "#eb8f6b",
            "Spiritual": "#c9b6ff",
        },
        "current": cur,
        "chapters": chapters,
        "years": years,
        "legend": summary.get("legend", {}),
        "asOf": summary.get("as_of"),
    }


def timing_d3_html(summary: Dict, *, height: int = 720) -> str:
    """Return a full HTML document with interactive D3 timing charts."""
    data = json.dumps(_payload(summary), ensure_ascii=False)
    # Escape </script> in JSON if any planet name weirdness — unlikely but safe.
    data = data.replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
<style>
  :root {{
    --bg: #0b0e1a;
    --panel: #151a2c;
    --ink: #e8ebf2;
    --muted: #9aa3b8;
    --gold: #f5c542;
    --good: #6fcf97;
    --mixed: #f2c94c;
    --bad: #ef6b6b;
    --grid: rgba(255,255,255,0.06);
  }}
  html, body {{
    margin: 0; padding: 0; background: var(--bg); color: var(--ink);
    font-family: "Segoe UI", system-ui, sans-serif; font-size: 13px;
  }}
  .wrap {{ padding: 8px 10px 16px; }}
  .header {{
    display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: baseline;
    margin-bottom: 10px;
  }}
  .header h2 {{
    margin: 0; font-size: 18px; color: var(--gold); font-weight: 700;
    letter-spacing: 0.02em;
  }}
  .chip {{
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--panel); border: 1px solid rgba(245,197,66,0.25);
    border-radius: 999px; padding: 4px 12px; color: var(--muted); font-size: 12px;
  }}
  .chip b {{ color: #ffe9a8; font-weight: 600; }}
  .legend {{
    display: flex; flex-wrap: wrap; gap: 10px 16px; margin: 6px 0 14px;
    color: var(--muted); font-size: 12px;
  }}
  .swatch {{
    display: inline-block; width: 10px; height: 10px; border-radius: 2px;
    margin-right: 5px; vertical-align: middle;
  }}
  .panel {{
    background: var(--panel); border: 1px solid rgba(245,197,66,0.12);
    border-radius: 14px; padding: 12px 14px 8px; margin-bottom: 14px;
  }}
  .panel h3 {{
    margin: 0 0 8px; font-size: 13px; color: #ffe9a8; font-weight: 600;
    letter-spacing: 0.04em; text-transform: uppercase;
  }}
  .hint {{ color: var(--muted); font-size: 11px; margin: -2px 0 10px; }}
  svg {{ display: block; width: 100%; }}
  .axis text {{ fill: var(--muted); font-size: 10px; }}
  .axis line, .axis path {{ stroke: rgba(255,255,255,0.15); }}
  .grid line {{ stroke: var(--grid); }}
  .band-label {{ fill: var(--ink); font-size: 11px; font-weight: 600; }}
  .band-sub {{ fill: var(--muted); font-size: 9px; }}
  .now-line {{ stroke: var(--gold); stroke-width: 1.5; stroke-dasharray: 4 3; }}
  .tip {{
    position: fixed; pointer-events: none; z-index: 20;
    background: #1c2136; border: 1px solid rgba(245,197,66,0.35);
    border-radius: 10px; padding: 10px 12px; max-width: 280px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.45); display: none;
  }}
  .tip .t {{ color: #ffe9a8; font-weight: 700; margin-bottom: 4px; }}
  .tip .d {{ color: var(--muted); font-size: 11px; margin-bottom: 6px; }}
  .tip .row {{ display: flex; justify-content: space-between; gap: 12px; margin: 2px 0; }}
  .tip .good {{ color: var(--good); }}
  .tip .mixed {{ color: var(--mixed); }}
  .tip .bad {{ color: var(--bad); }}
  .year-grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 10px;
  }}
  .year-card {{
    background: rgba(11,14,26,0.55); border-radius: 12px; padding: 10px 12px;
    border-left: 4px solid var(--mixed);
  }}
  .year-card.good {{ border-left-color: var(--good); }}
  .year-card.bad {{ border-left-color: var(--bad); }}
  .year-card .y {{ font-size: 16px; font-weight: 700; color: #fff; }}
  .year-card .tag {{ color: var(--muted); font-size: 11px; margin-bottom: 6px; }}
  .mini {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }}
  .mini span {{
    font-size: 10px; padding: 2px 6px; border-radius: 6px;
    background: rgba(255,255,255,0.06); color: var(--muted);
  }}
  .detail {{
    display: none; margin-top: 8px; padding-top: 8px;
    border-top: 1px solid rgba(255,255,255,0.08); font-size: 11px; color: var(--muted);
  }}
  .detail.show {{ display: block; }}
  .detail b {{ color: var(--ink); }}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h2>Timing map</h2>
    <span class="chip" id="nowChip">Loading…</span>
  </div>
  <div class="legend" id="areaLegend"></div>

  <div class="panel">
    <h3>Antardasha timeline</h3>
    <div class="hint">Each bar is one Mahadasha / Antardasha chapter. Colour = overall tone. Hover for scores.</div>
    <div id="timeline"></div>
  </div>

  <div class="panel">
    <h3>Impact by life area</h3>
    <div class="hint">Lines show favourable (high) vs challenged (low) across each chapter. Gold dashed line = today.</div>
    <div id="impact"></div>
  </div>

  <div class="panel">
    <h3>Year risk &amp; opportunity</h3>
    <div class="hint">Click a year for short watch / lean-into notes.</div>
    <div class="year-grid" id="years"></div>
  </div>
</div>
<div class="tip" id="tip"></div>

<script>
const DATA = {data};

const toneColour = {{ good: "#6fcf97", mixed: "#f2c94c", bad: "#ef6b6b" }};
const toneOf = (s) => (s >= 65 ? "good" : s <= 38 ? "bad" : "mixed");
const avgScore = (scores) => {{
  const vals = Object.values(scores).map(v => (typeof v === "number" ? v : v.score));
  return vals.reduce((a,b)=>a+b,0) / Math.max(vals.length, 1);
}};

const tip = document.getElementById("tip");
function showTip(evt, html) {{
  tip.innerHTML = html;
  tip.style.display = "block";
  const x = Math.min(evt.clientX + 14, window.innerWidth - 300);
  const y = Math.min(evt.clientY + 14, window.innerHeight - 160);
  tip.style.left = x + "px";
  tip.style.top = y + "px";
}}
function hideTip() {{ tip.style.display = "none"; }}

// Header + area legend
(() => {{
  const c = DATA.current || {{}};
  const ss = c.sade_sati_active ? (" · Sade Sati: " + c.sade_sati) : " · not in Sade Sati";
  document.getElementById("nowChip").innerHTML =
    "<b>Now</b> " + (c.maha || "—") + " / " + (c.antar || "—") +
    " · Antar → " + (c.antar_until || "—") + ss;
  const leg = document.getElementById("areaLegend");
  (DATA.areas || []).forEach(a => {{
    const el = document.createElement("span");
    el.innerHTML = '<span class="swatch" style="background:' + (DATA.colours[a]||"#aaa") +
      '"></span>' + a;
    leg.appendChild(el);
  }});
  ["good","mixed","bad"].forEach(t => {{
    const el = document.createElement("span");
    el.innerHTML = '<span class="swatch" style="background:' + toneColour[t] +
      '"></span>' + (t === "good" ? "Favourable" : t === "bad" ? "Challenged" : "Mixed");
    leg.appendChild(el);
  }});
}})();

function drawTimeline() {{
  const host = document.getElementById("timeline");
  host.innerHTML = "";
  const chapters = DATA.chapters || [];
  if (!chapters.length) {{
    host.textContent = "No upcoming periods in range.";
    return;
  }}
  const width = Math.max(host.clientWidth || 640, 320);
  const rowH = 42;
  const margin = {{ top: 18, right: 16, bottom: 28, left: 118 }};
  const height = margin.top + margin.bottom + chapters.length * rowH;
  const svg = d3.select(host).append("svg")
    .attr("viewBox", `0 0 ${{width}} ${{height}}`)
    .attr("height", height);

  const x = d3.scaleTime()
    .domain([d3.min(chapters, d => new Date(d.start)), d3.max(chapters, d => new Date(d.end))])
    .range([margin.left, width - margin.right]);

  const y = d3.scaleBand()
    .domain(chapters.map(d => d.label))
    .range([margin.top, height - margin.bottom])
    .padding(0.28);

  svg.append("g").attr("class", "grid")
    .attr("transform", `translate(0,${{height - margin.bottom}})`)
    .call(d3.axisBottom(x).ticks(6).tickSize(-(height - margin.top - margin.bottom)).tickFormat(""));

  svg.append("g").attr("class", "axis")
    .attr("transform", `translate(0,${{height - margin.bottom}})`)
    .call(d3.axisBottom(x).ticks(6).tickFormat(d3.timeFormat("%b %Y")));

  const g = svg.selectAll(".row").data(chapters).enter().append("g");
  g.append("text").attr("class", "band-label")
    .attr("x", margin.left - 8).attr("y", d => y(d.label) + y.bandwidth() * 0.42)
    .attr("text-anchor", "end").text(d => d.label);
  g.append("text").attr("class", "band-sub")
    .attr("x", margin.left - 8).attr("y", d => y(d.label) + y.bandwidth() * 0.92)
    .attr("text-anchor", "end")
    .text(d => d.startLabel + " → " + d.endLabel);

  g.append("rect")
    .attr("x", d => x(new Date(d.start)))
    .attr("y", d => y(d.label))
    .attr("rx", 6)
    .attr("height", y.bandwidth())
    .attr("width", d => Math.max(4, x(new Date(d.end)) - x(new Date(d.start))))
    .attr("fill", d => toneColour[toneOf(avgScore(d.scores))])
    .attr("opacity", d => d.isCurrent ? 0.95 : 0.72)
    .attr("stroke", d => d.isCurrent ? "#ffe9a8" : "transparent")
    .attr("stroke-width", 1.5)
    .on("mousemove", (evt, d) => {{
      const rows = DATA.areas.map(a => {{
        const s = d.scores[a];
        return `<div class="row"><span>${{a}}</span><span class="${{s.tone}}">${{s.score}} · ${{s.tone}}</span></div>`;
      }}).join("");
      showTip(evt, `<div class="t">${{d.label}}</div><div class="d">${{d.startLabel}} → ${{d.endLabel}}<br>${{d.antarTheme}}</div>${{rows}}`);
    }})
    .on("mouseleave", hideTip);

  const now = DATA.asOf ? new Date(DATA.asOf) : new Date();
  if (now >= x.domain()[0] && now <= x.domain()[1]) {{
    svg.append("line").attr("class", "now-line")
      .attr("x1", x(now)).attr("x2", x(now))
      .attr("y1", margin.top - 4).attr("y2", height - margin.bottom);
  }}
}}

function drawImpact() {{
  const host = document.getElementById("impact");
  host.innerHTML = "";
  const chapters = DATA.chapters || [];
  if (!chapters.length) return;

  // Use phase midpoints for smoother lines, else chapter midpoints.
  const points = [];
  chapters.forEach(c => {{
    if (c.phases && c.phases.length) {{
      c.phases.forEach(p => {{
        const mid = new Date((new Date(p.start).getTime() + new Date(p.end).getTime()) / 2);
        points.push({{ date: mid, label: c.label + " · " + p.name, scores: p.scores, chapter: c }});
      }});
    }} else {{
      const mid = new Date((new Date(c.start).getTime() + new Date(c.end).getTime()) / 2);
      const scores = Object.fromEntries(Object.entries(c.scores).map(([k,v]) => [k, v.score]));
      points.push({{ date: mid, label: c.label, scores, chapter: c }});
    }}
  }});

  const width = Math.max(host.clientWidth || 640, 320);
  const margin = {{ top: 16, right: 18, bottom: 30, left: 36 }};
  const height = 260;
  const svg = d3.select(host).append("svg")
    .attr("viewBox", `0 0 ${{width}} ${{height}}`)
    .attr("height", height);

  const x = d3.scaleTime()
    .domain(d3.extent(points, d => d.date))
    .range([margin.left, width - margin.right]);
  const y = d3.scaleLinear().domain([0, 100]).nice()
    .range([height - margin.bottom, margin.top]);

  // Good / mixed / bad bands
  const bands = [
    {{ y0: 0, y1: 38, c: "rgba(239,107,107,0.08)" }},
    {{ y0: 38, y1: 65, c: "rgba(242,201,76,0.07)" }},
    {{ y0: 65, y1: 100, c: "rgba(111,207,151,0.08)" }},
  ];
  bands.forEach(b => {{
    svg.append("rect")
      .attr("x", margin.left).attr("width", width - margin.left - margin.right)
      .attr("y", y(b.y1)).attr("height", y(b.y0) - y(b.y1))
      .attr("fill", b.c);
  }});

  svg.append("g").attr("class", "grid")
    .attr("transform", `translate(${{margin.left}},0)`)
    .call(d3.axisLeft(y).ticks(5).tickSize(-(width - margin.left - margin.right)).tickFormat(""));

  svg.append("g").attr("class", "axis")
    .attr("transform", `translate(0,${{height - margin.bottom}})`)
    .call(d3.axisBottom(x).ticks(6).tickFormat(d3.timeFormat("%b %Y")));
  svg.append("g").attr("class", "axis")
    .attr("transform", `translate(${{margin.left}},0)`)
    .call(d3.axisLeft(y).ticks(5));

  (DATA.areas || []).forEach(area => {{
    const path = d3.line()
      .x(d => x(d.date))
      .y(d => y(d.scores[area]))
      .curve(d3.curveMonotoneX);
    svg.append("path")
      .datum(points)
      .attr("fill", "none")
      .attr("stroke", DATA.colours[area] || "#aaa")
      .attr("stroke-width", 2.2)
      .attr("opacity", 0.9)
      .attr("d", path);

    svg.selectAll(null).data(points).enter().append("circle")
      .attr("cx", d => x(d.date))
      .attr("cy", d => y(d.scores[area]))
      .attr("r", 3.2)
      .attr("fill", DATA.colours[area] || "#aaa")
      .on("mousemove", (evt, d) => {{
        const s = d.scores[area];
        const t = toneOf(s);
        showTip(evt,
          `<div class="t">${{area}} · ${{s}}</div>` +
          `<div class="d">${{d.label}}</div>` +
          `<div class="${{t}}">${{t === "good" ? "Favourable" : t === "bad" ? "Challenged" : "Mixed"}}</div>` +
          (d.chapter && d.chapter.scores[area] && d.chapter.scores[area].note
            ? `<div class="d" style="margin-top:6px">${{d.chapter.scores[area].note}}</div>` : ""));
      }})
      .on("mouseleave", hideTip);
  }});

  const now = DATA.asOf ? new Date(DATA.asOf) : new Date();
  if (now >= x.domain()[0] && now <= x.domain()[1]) {{
    svg.append("line").attr("class", "now-line")
      .attr("x1", x(now)).attr("x2", x(now))
      .attr("y1", margin.top).attr("y2", height - margin.bottom);
  }}
}}

function drawYears() {{
  const host = document.getElementById("years");
  host.innerHTML = "";
  (DATA.years || []).forEach(y => {{
    const mean = avgScore(y.scores);
    const tone = toneOf(mean);
    const card = document.createElement("div");
    card.className = "year-card " + tone;
    const chips = Object.entries(y.scores).map(([a,s]) =>
      `<span style="color:${{DATA.colours[a]||'#aaa'}}">${{a.slice(0,3)}} ${{s}}</span>`
    ).join("");
    card.innerHTML =
      `<div class="y">${{y.year}}</div><div class="tag">${{y.tag}}</div>` +
      `<div class="mini">${{chips}}</div>` +
      `<div class="detail">` +
      `<div><b>Watch</b><br>${{(y.risks||[]).join("<br>") || "—"}}</div>` +
      `<div style="margin-top:6px"><b>Lean into</b><br>${{(y.opportunities||[]).join("<br>") || "—"}}</div>` +
      `<div style="margin-top:6px;opacity:0.8">${{(y.chapters||[]).join(" · ")}}</div>` +
      `</div>`;
    card.addEventListener("click", () => {{
      card.querySelector(".detail").classList.toggle("show");
    }});
    host.appendChild(card);
  }});
}}

drawTimeline();
drawImpact();
drawYears();
window.addEventListener("resize", () => {{
  drawTimeline();
  drawImpact();
}});
</script>
</body>
</html>
"""


def render_timing_viz(summary: Optional[Dict], *, height: int = 780) -> None:
    """Streamlit helper: embed the D3 timing map."""
    if not summary or not summary.get("chapters"):
        return
    import streamlit.components.v1 as components

    components.html(timing_d3_html(summary, height=height), height=height, scrolling=True)
