"""Yoga detector — classical planetary combinations in a birth chart.

Detects the well-known yogas that shape a reading:
  * Pancha Mahapurusha (Ruchaka, Bhadra, Hamsa, Malavya, Sasha)
  * Gaja Kesari, Budha-Aditya, Chandra-Mangal
  * Sunapha / Anapha / Durudhara / Kemadruma (lunar yogas)
  * Raj Yogas (kendra-trikona lord association) & Dharma-Karmadhipati
  * Dhana Yogas (wealth-house lord association)
  * Vipreet Raja Yogas (Harsha, Sarala, Vimala)
  * Amala Yoga and Neecha Bhanga Raja Yoga
"""

from __future__ import annotations

from typing import Dict, List

from . import reference as ref
from .chart_engine import Chart
from .strength_calc import all_strengths

_KENDRA = {1, 4, 7, 10}
_TRIKONA = {1, 5, 9}
_DUSTHANA = {6, 8, 12}
_WEALTH = {2, 5, 9, 11}
_STRONG_DIGNITY = {"Exalted", "Own Sign", "Moolatrikona"}

# planet -> (yoga name, plain meaning) for Pancha Mahapurusha
_MAHAPURUSHA = {
    "Mars": ("Ruchaka", "courage, leadership and a commanding, athletic presence"),
    "Mercury": ("Bhadra", "sharp intellect, eloquence and business acumen"),
    "Jupiter": ("Hamsa", "wisdom, righteousness and a respected, teacherly nature"),
    "Venus": ("Malavya", "charm, comfort, artistic taste and refined relationships"),
    "Saturn": ("Sasha", "discipline, endurance and authority earned through work"),
}

# sign -> planet exalted there (for Neecha Bhanga)
_EXALT_PLANET = {sign: p for p, (sign, _deg) in ref.EXALTATION.items()}


def _house_from(a_sign_idx: int, b_sign_idx: int) -> int:
    return (a_sign_idx - b_sign_idx) % 12 + 1


def detect_yogas(chart: Chart) -> List[Dict]:
    """Return a list of detected yogas with category, tone and plain meaning."""
    strengths = all_strengths(chart)
    planets = chart.planets
    results: List[Dict] = []

    def lord(h: int) -> str:
        return chart.house_lord(h)

    def phouse(p: str) -> int:
        return planets[p].house

    def dignity(p: str) -> str:
        return strengths[p].dignity

    moon_sign_idx = planets["Moon"].sign_index

    # --- Pancha Mahapurusha Yogas -----------------------------------------
    for planet, (yname, meaning) in _MAHAPURUSHA.items():
        if phouse(planet) in _KENDRA and dignity(planet) in _STRONG_DIGNITY:
            results.append({
                "name": f"{yname} Yoga",
                "category": "Pancha Mahapurusha",
                "tone": "benefic",
                "detail": (
                    f"{planet} is {dignity(planet).lower()} in a kendra (house {phouse(planet)}). "
                    f"Confers {meaning}."
                ),
            })

    # --- Gaja Kesari Yoga --------------------------------------------------
    jup_h_from_moon = _house_from(planets["Jupiter"].sign_index, moon_sign_idx)
    if jup_h_from_moon in _KENDRA:
        results.append({
            "name": "Gaja Kesari Yoga",
            "category": "Lunar",
            "tone": "benefic",
            "detail": (
                f"Jupiter is in a kendra ({jup_h_from_moon}th) from the Moon — "
                "intelligence, good reputation, and lasting respect."
            ),
        })

    # --- Budha-Aditya & Chandra-Mangal ------------------------------------
    if phouse("Sun") == phouse("Mercury"):
        results.append({
            "name": "Budha-Aditya Yoga",
            "category": "Conjunction",
            "tone": "benefic",
            "detail": (
                f"Sun and Mercury are together in house {phouse('Sun')} — "
                "keen intellect, learning and communication skills."
            ),
        })
    if phouse("Moon") == phouse("Mars"):
        results.append({
            "name": "Chandra-Mangal Yoga",
            "category": "Conjunction",
            "tone": "mixed",
            "detail": (
                f"Moon and Mars are together in house {phouse('Moon')} — "
                "drive to earn and accumulate wealth; manage impulsiveness."
            ),
        })

    # --- Lunar yogas: Sunapha / Anapha / Durudhara / Kemadruma ------------
    def occ_excl_luminaries(house: int) -> List[str]:
        return [
            p.name for p in planets.values()
            if p.house == house and p.name not in ("Sun", "Moon", "Rahu", "Ketu")
        ]

    moon_house = phouse("Moon")
    second_from_moon = (moon_house % 12) + 1
    twelfth_from_moon = ((moon_house - 2) % 12) + 1
    sec = occ_excl_luminaries(second_from_moon)
    twe = occ_excl_luminaries(twelfth_from_moon)
    conj_moon = occ_excl_luminaries(moon_house)
    if sec and twe:
        results.append({
            "name": "Durudhara Yoga", "category": "Lunar", "tone": "benefic",
            "detail": ("Planets flank the Moon on both sides (2nd and 12th) — "
                       "all-round support, comforts and helpful people."),
        })
    elif sec:
        results.append({
            "name": "Sunapha Yoga", "category": "Lunar", "tone": "benefic",
            "detail": ("Planet(s) in the 2nd from the Moon — self-earned wealth and status."),
        })
    elif twe:
        results.append({
            "name": "Anapha Yoga", "category": "Lunar", "tone": "benefic",
            "detail": ("Planet(s) in the 12th from the Moon — well-being, health and a genial nature."),
        })
    elif not conj_moon:
        results.append({
            "name": "Kemadruma Yoga", "category": "Lunar", "tone": "malefic",
            "detail": ("The Moon is isolated (no planets in the 2nd, 12th or with it) — "
                       "emotional ups and downs; mitigated if the Moon is otherwise strong."),
        })

    # --- Raj Yogas (kendra-trikona lord association) ----------------------
    seen_pairs = set()
    for kh in _KENDRA:
        for th in _TRIKONA:
            if kh == th:
                continue
            kl, tl = lord(kh), lord(th)
            if kl == tl:
                continue
            pair = frozenset((kl, tl))
            if pair in seen_pairs:
                continue
            if phouse(kl) == phouse(tl):
                seen_pairs.add(pair)
                is_dk = {kh, th} == {9, 10} or (kl == lord(9) and tl == lord(10))
                dk = (f"Dharma-Karmadhipati Yoga ({kl}\u2013{tl})" if is_dk
                      else f"Raj Yoga ({kl}\u2013{tl})")
                results.append({
                    "name": dk,
                    "category": "Raj Yoga",
                    "tone": "benefic",
                    "detail": (
                        f"{kl} (lord of kendra {kh}) and {tl} (lord of trikona {th}) join in "
                        f"house {phouse(kl)} — a combination for power, status and success."
                    ),
                })

    # 9th & 10th lord association (Dharma-Karmadhipati) if not already caught
    l9, l10 = lord(9), lord(10)
    if l9 != l10 and phouse(l9) == phouse(l10) and frozenset((l9, l10)) not in seen_pairs:
        results.append({
            "name": f"Dharma-Karmadhipati Yoga ({l9}\u2013{l10})",
            "category": "Raj Yoga",
            "tone": "benefic",
            "detail": (
                f"The 9th lord {l9} and 10th lord {l10} join in house {phouse(l9)} — "
                "one of the strongest yogas for career and fortune."
            ),
        })

    # --- Dhana Yogas (wealth-house lord association) ----------------------
    wealth_lords = {}
    for h in _WEALTH:
        wealth_lords.setdefault(lord(h), []).append(h)
    seen_dhana = set()
    wl = list(wealth_lords.keys())
    for i in range(len(wl)):
        for j in range(i + 1, len(wl)):
            a, b = wl[i], wl[j]
            if phouse(a) == phouse(b):
                key = frozenset((a, b))
                if key in seen_dhana:
                    continue
                seen_dhana.add(key)
                ha = "/".join(str(x) for x in wealth_lords[a])
                hb = "/".join(str(x) for x in wealth_lords[b])
                results.append({
                    "name": f"Dhana Yoga ({a}\u2013{b})",
                    "category": "Wealth",
                    "tone": "benefic",
                    "detail": (
                        f"Wealth-house lords {a} (house {ha}) and {b} (house {hb}) join in "
                        f"house {phouse(a)} — supports income and accumulation."
                    ),
                })

    # --- Vipreet Raja Yogas ----------------------------------------------
    vipreet = {6: "Harsha", 8: "Sarala", 12: "Vimala"}
    for h, yname in vipreet.items():
        hl = lord(h)
        if phouse(hl) in _DUSTHANA:
            results.append({
                "name": f"{yname} (Vipreet Raja) Yoga",
                "category": "Vipreet Raja",
                "tone": "benefic",
                "detail": (
                    f"The {h}th lord {hl} sits in a dusthana (house {phouse(hl)}) — "
                    "adversity turns into eventual rise and resilience."
                ),
            })

    # --- Amala Yoga -------------------------------------------------------
    tenth_from_lagna = 10
    tenth_from_moon = _house_from_number(moon_house, 10)
    for ref_name, tenth_house in (("Lagna", tenth_from_lagna), ("Moon", tenth_from_moon)):
        occ = [p.name for p in planets.values()
               if p.house == tenth_house and p.name in ref.NATURAL_BENEFICS]
        if occ:
            results.append({
                "name": "Amala Yoga",
                "category": "Reputation",
                "tone": "benefic",
                "detail": (
                    f"Benefic ({', '.join(occ)}) in the 10th from {ref_name} — "
                    "a lasting good reputation and honourable conduct."
                ),
            })
            break

    # --- Neecha Bhanga Raja Yoga -----------------------------------------
    for p in ref.PLANETS:
        if dignity(p) != "Debilitated":
            continue
        sign = planets[p].sign
        dispositor = ref.SIGN_LORD[sign]
        exalt_planet = _EXALT_PLANET.get(sign)
        cancels = []
        if phouse(dispositor) in _KENDRA:
            cancels.append(f"its dispositor {dispositor} is in a kendra")
        if exalt_planet and phouse(exalt_planet) in _KENDRA:
            cancels.append(f"{exalt_planet} (exalted in {sign}) is in a kendra")
        if cancels:
            results.append({
                "name": "Neecha Bhanga Raja Yoga",
                "category": "Cancellation",
                "tone": "benefic",
                "detail": (
                    f"{p} is debilitated in {sign}, but the debility is cancelled because "
                    f"{' and '.join(cancels)} — an initial weakness that turns into strength."
                ),
            })

    return results


def _house_from_number(base_house: int, offset: int) -> int:
    return ((base_house - 1 + (offset - 1)) % 12) + 1


def yogas_markdown(yogas: List[Dict], name: str) -> str:
    lines = [f"# Yogas in the chart — {name}", ""]
    if not yogas:
        lines.append("_No major classical yogas detected._")
        return "\n".join(lines)
    by_cat: Dict[str, List[Dict]] = {}
    for y in yogas:
        by_cat.setdefault(y["category"], []).append(y)
    for cat, items in by_cat.items():
        lines.append(f"## {cat}")
        for y in items:
            lines.append(f"- **{y['name']}** — {y['detail']}")
        lines.append("")
    return "\n".join(lines)
