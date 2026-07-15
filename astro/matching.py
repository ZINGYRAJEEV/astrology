"""Horoscope matching — Ashtakoota Milan with Rishikesh Panchang overlays.

Implements the classical 36-point Ashtakoota (Avakhada-based) system used in
North-Indian / Kashi marriage matching, plus Rishikesh Panchang checks:
  * Nadi Dosha (critical filter)
  * Gandanta & Yoga Dosha flags
  * Birth Panchang limb harmony
  * Manglik (Kuja) Dosha
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from . import matching_data as md
from . import reference as ref
from . import rishikesh_rules as rr
from .chart_engine import BirthData, Chart, compute_chart
from .prediction import birth_panchang, _birth_datetime
from .rishikesh_prediction import analyze_rishikesh_birth


def _nakshatra_index(name: str) -> int:
    return ref.NAKSHATRAS.index(name)


def _tara_points(from_nak: str, to_nak: str) -> float:
    """Tara Koota contribution in one direction (max 1.5)."""
    diff = (_nakshatra_index(to_nak) - _nakshatra_index(from_nak)) % 27
    if diff == 0:
        pos = 9
    else:
        pos = diff % 9 or 9
    return 1.5 if pos in md.AUSPICIOUS_TARA else 0.0


def _varna_koota(groom_ava: dict, bride_ava: dict) -> Tuple[float, str]:
    g_rank = md.VARNA_RANK[groom_ava["varna"]]
    b_rank = md.VARNA_RANK[bride_ava["varna"]]
    pts = 1.0 if g_rank >= b_rank else 0.0
    note = (
        f"Groom {groom_ava['varna']} / Bride {bride_ava['varna']} — "
        + ("compatible mental aptitude." if pts else "varna mismatch (traditional caution).")
    )
    return pts, note


def _vashya_koota(groom_ava: dict, bride_ava: dict) -> Tuple[float, str]:
    pts = md.VASHYA_SCORE[(groom_ava["vashya"], bride_ava["vashya"])]
    note = f"Groom {groom_ava['vashya']} attracts Bride {bride_ava['vashya']} — {pts}/2."
    return pts, note


def _tara_koota(g_nak: str, b_nak: str) -> Tuple[float, str]:
    g_to_b = _tara_points(g_nak, b_nak)
    b_to_g = _tara_points(b_nak, g_nak)
    pts = g_to_b + b_to_g
    note = (
        f"Tarabala groom→bride {g_to_b:.1f}, bride→groom {b_to_g:.1f} "
        f"(Rishikesh priority limb, max 3)."
    )
    return pts, note


def _yoni_koota(g_yoni: str, b_yoni: str) -> Tuple[float, str]:
    if g_yoni == b_yoni:
        pts, label = 4.0, "same yoni — strong primal harmony"
    elif (g_yoni, b_yoni) in md.YONI_ENEMIES or (b_yoni, g_yoni) in md.YONI_ENEMIES:
        pts, label = 0.0, "yoni enemies — temperamental friction"
    elif (g_yoni, b_yoni) in md.YONI_FRIENDS or (b_yoni, g_yoni) in md.YONI_FRIENDS:
        pts, label = 3.0, "friendly yoni — good temperament match"
    else:
        pts, label = 2.0, "neutral yoni — workable with adjustment"
    note = f"{g_yoni} & {b_yoni}: {label}."
    return pts, note


def _graha_maitri(g_sign: str, b_sign: str) -> Tuple[float, str]:
    g_lord, b_lord = ref.SIGN_LORD[g_sign], ref.SIGN_LORD[b_sign]
    if g_lord == b_lord:
        pts = 5.0
    else:
        rel = ref.relationship(g_lord, b_lord)
        pts = {"Friend": 4.0, "Neutral": 3.0, "Enemy": 0.0}[rel]
    note = f"Moon lords {g_lord} & {b_lord} — {pts}/5 (Graha Maitri)."
    return pts, note


def _gana_koota(g_gana: str, b_gana: str) -> Tuple[float, str]:
    pts = md.GANA_SCORE[(g_gana, b_gana)]
    note = f"Groom {g_gana} / Bride {b_gana} — spiritual temperament {pts}/6."
    return pts, note


def _bhakoot(g_sign_idx: int, b_sign_idx: int) -> Tuple[float, str]:
    diff = (b_sign_idx - g_sign_idx) % 12
    dosha = diff in (1, 11, 4, 8, 5, 7)  # 2/12, 5/9, 6/8 pairs
    pts = 0.0 if dosha else 7.0
    labels = {1: "2/12", 11: "12/2", 4: "5/9", 8: "9/5", 5: "6/8", 7: "8/6"}
    if dosha:
        note = f"Bhakoot Dosha ({labels.get(diff, 'inauspicious')}) — family/prosperity caution."
    else:
        note = f"Moon signs {ref.SIGNS[g_sign_idx]} & {ref.SIGNS[b_sign_idx]} — Bhakoot OK (7/7)."
    return pts, note


def _nadi_koota(g_nadi: str, b_nadi: str) -> Tuple[float, str]:
    pts = 0.0 if g_nadi == b_nadi else 8.0
    if pts:
        note = f"Different Nadi ({g_nadi}/{b_nadi}) — 8/8; critical Rishikesh filter passed."
    else:
        note = (
            f"Nadi Dosha — both {g_nadi} Nadi. Same-Nadi match is traditionally "
            "avoided (health/offspring concerns); remedies essential."
        )
    return pts, note


def _manglik(chart: Chart) -> Dict:
    """Kuja Dosha — Mars in 1, 4, 7, 8, 12 from Lagna or Moon."""
    mars = chart.planets["Mars"]
    moon_idx = chart.planets["Moon"].sign_index
    kuja = {1, 4, 7, 8, 12}
    from_lagna = mars.house in kuja
    from_moon = ((mars.sign_index - moon_idx) % 12 + 1) in kuja
    active = from_lagna or from_moon
    return {
        "active": active,
        "from_lagna": from_lagna,
        "from_moon": from_moon,
        "mars_house": mars.house,
        "mars_sign": mars.sign,
    }


def _verdict(total: float) -> Tuple[str, str]:
    for threshold, label, meaning in md.MATCH_VERDICT:
        if total >= threshold:
            return label, meaning
    return "Low", md.MATCH_VERDICT[-1][2]


def _panchang_harmony(g_panch, b_panch) -> List[str]:
    notes = []
    if g_panch.paksha == b_panch.paksha:
        notes.append(f"Both born in {g_panch.paksha} — shared lunar rhythm.")
    if g_panch.yoga.name in rr.MAHA_YOGA_DOSHAS:
        notes.append(f"Groom birth Yoga {g_panch.yoga.name} — Maha Dosha; may affect harmony.")
    if b_panch.yoga.name in rr.MAHA_YOGA_DOSHAS:
        notes.append(f"Bride birth Yoga {b_panch.yoga.name} — Maha Dosha; may affect harmony.")
    g_gand = g_panch.nakshatra.name in rr.GANDANTA_NAKSHATRAS
    b_gand = b_panch.nakshatra.name in rr.GANDANTA_NAKSHATRAS
    if g_gand or b_gand:
        who = "Groom" if g_gand else "Bride"
        if g_gand and b_gand:
            who = "Both"
        notes.append(f"{who} born in Gandanta Nakshatra — Sandhi Shanti traditionally advised.")
    return notes


def match_charts(
    groom_chart: Chart,
    bride_chart: Chart,
    groom_name: str = "Groom",
    bride_name: str = "Bride",
) -> Dict:
    """Full Ashtakoota + Rishikesh Panchang compatibility report."""
    g_moon = groom_chart.planets["Moon"]
    b_moon = bride_chart.planets["Moon"]
    g_ava = rr.avakhada(g_moon.sign, g_moon.nakshatra)
    b_ava = rr.avakhada(b_moon.sign, b_moon.nakshatra)

    kootas = []
    for name, max_pts, pts, note in [
        ("Varna", 1, *_varna_koota(g_ava, b_ava)),
        ("Vashya", 2, *_vashya_koota(g_ava, b_ava)),
        ("Tara", 3, *_tara_koota(g_moon.nakshatra, b_moon.nakshatra)),
        ("Yoni", 4, *_yoni_koota(g_ava["yoni"], b_ava["yoni"])),
        ("Graha Maitri", 5, *_graha_maitri(g_moon.sign, b_moon.sign)),
        ("Gana", 6, *_gana_koota(g_ava["gana"], b_ava["gana"])),
        ("Bhakoot", 7, *_bhakoot(g_moon.sign_index, b_moon.sign_index)),
        ("Nadi", 8, *_nadi_koota(g_ava["nadi"], b_ava["nadi"])),
    ]:
        kootas.append({
            "name": name, "points": pts, "max": max_pts,
            "percent": round(pts / max_pts * 100) if max_pts else 0,
            "note": note,
            "ok": pts >= max_pts * 0.5,
        })

    total = sum(k["points"] for k in kootas)
    label, meaning = _verdict(total)

    g_panch = birth_panchang(groom_chart)
    b_panch = birth_panchang(bride_chart)
    g_rk = analyze_rishikesh_birth(groom_chart, g_panch, _birth_datetime(groom_chart))
    b_rk = analyze_rishikesh_birth(bride_chart, b_panch, _birth_datetime(bride_chart))

    g_mang = _manglik(groom_chart)
    b_mang = _manglik(bride_chart)

    doshas = []
    if kootas[7]["points"] == 0:
        doshas.append("Nadi Dosha (8 points lost) — highest priority in Rishikesh / Ashtakoota.")
    if kootas[6]["points"] == 0:
        doshas.append("Bhakoot Dosha — family harmony and prosperity need care.")
    if g_mang["active"] and b_mang["active"]:
        doshas.append("Both charts Manglik — traditionally cancels Kuja Dosha.")
    elif g_mang["active"]:
        doshas.append(f"Groom Manglik (Mars house {g_mang['mars_house']}) — match with Manglik bride or remedies.")
    elif b_mang["active"]:
        doshas.append(f"Bride Manglik (Mars house {b_mang['mars_house']}) — match with Manglik groom or remedies.")
    doshas.extend(_panchang_harmony(g_panch, b_panch))

    recommendations = []
    if total >= 25:
        recommendations.append("Overall score supports marriage from a classical Jyotish view.")
    elif total >= 18:
        recommendations.append("Score meets 18+ threshold — proceed with priest/astrologer counsel.")
    else:
        recommendations.append("Score below 18 — detailed chart review and remedies recommended.")
    if kootas[7]["points"] == 0:
        recommendations.append("Nadi Dosha: perform Nadi Nivaran puja; many traditions require this before marriage.")
    if g_rk["navaratna"]["percent"] < 50 or b_rk["navaratna"]["percent"] < 50:
        recommendations.append("One or both Navaratna birth scores are low — strengthen weak limbs before marriage.")

    return {
        "groom_name": groom_name,
        "bride_name": bride_name,
        "groom": {
            "lagna": groom_chart.lagna_sign,
            "moon_sign": g_moon.sign,
            "nakshatra": g_moon.nakshatra,
            "pada": g_moon.nakshatra_pada,
            "avakhada": g_ava,
            "navaratna": g_rk["navaratna"]["percent"],
            "manglik": g_mang["active"],
        },
        "bride": {
            "lagna": bride_chart.lagna_sign,
            "moon_sign": b_moon.sign,
            "nakshatra": b_moon.nakshatra,
            "pada": b_moon.nakshatra_pada,
            "avakhada": b_ava,
            "navaratna": b_rk["navaratna"]["percent"],
            "manglik": b_mang["active"],
        },
        "kootas": kootas,
        "total_points": round(total, 1),
        "max_points": 36,
        "percent": round(total / 36 * 100, 1),
        "verdict": label,
        "verdict_detail": meaning,
        "doshas": doshas,
        "recommendations": recommendations,
        "panchang": {
            "groom": {
                "tithi": f"{g_panch.tithi.name} ({g_panch.paksha})",
                "yoga": g_panch.yoga.name,
                "karana": g_panch.karana.name,
                "vaara": g_panch.vaara.name,
            },
            "bride": {
                "tithi": f"{b_panch.tithi.name} ({b_panch.paksha})",
                "yoga": b_panch.yoga.name,
                "karana": b_panch.karana.name,
                "vaara": b_panch.vaara.name,
            },
        },
    }


def match_from_birth(
    groom: BirthData,
    bride: BirthData,
) -> Dict:
    return match_charts(
        compute_chart(groom), compute_chart(bride),
        groom.name or "Groom", bride.name or "Bride",
    )


def matching_markdown(m: Dict) -> str:
    lines = [
        f"# Horoscope Matching — {m['groom_name']} & {m['bride_name']}",
        "",
        f"**Ashtakoota score:** {m['total_points']}/36 ({m['percent']}%) — **{m['verdict']}**",
        f"{m['verdict_detail']}",
        "",
        "## Groom",
        f"- Lagna {m['groom']['lagna']} · Moon {m['groom']['moon_sign']} · "
        f"{m['groom']['nakshatra']} (pada {m['groom']['pada']})",
        f"- Avakhada: {m['groom']['avakhada']['varna']} / {m['groom']['avakhada']['gana']} / "
        f"{m['groom']['avakhada']['nadi']} Nadi · Navaratna {m['groom']['navaratna']}%",
        "",
        "## Bride",
        f"- Lagna {m['bride']['lagna']} · Moon {m['bride']['moon_sign']} · "
        f"{m['bride']['nakshatra']} (pada {m['bride']['pada']})",
        f"- Avakhada: {m['bride']['avakhada']['varna']} / {m['bride']['avakhada']['gana']} / "
        f"{m['bride']['avakhada']['nadi']} Nadi · Navaratna {m['bride']['navaratna']}%",
        "",
        "## Ashtakoota (36 Gun Milan)",
    ]
    for k in m["kootas"]:
        lines.append(f"- **{k['name']}**: {k['points']}/{k['max']} — {k['note']}")
    lines += ["", "## Birth Panchang"]
    gp, bp = m["panchang"]["groom"], m["panchang"]["bride"]
    lines.append(f"- Groom: {gp['vaara']}, {gp['tithi']}, Yoga {gp['yoga']}, Karana {gp['karana']}")
    lines.append(f"- Bride: {bp['vaara']}, {bp['tithi']}, Yoga {bp['yoga']}, Karana {bp['karana']}")
    if m["doshas"]:
        lines += ["", "## Doshas & Rishikesh cautions"]
        for d in m["doshas"]:
            lines.append(f"- {d}")
    if m["recommendations"]:
        lines += ["", "## Recommendations"]
        for r in m["recommendations"]:
            lines.append(f"- {r}")
    lines += [
        "",
        "_Ashtakoota Milan per North-Indian / Hrishikesh Panchang Avakhada. "
        "For guidance; consult a qualified Jyotishi for final muhurta._",
    ]
    return "\n".join(lines)
