"""Core numerology chart synthesis — Pythagorean & Chaldean.

Implements Heart's Desire, Personality, Destiny, Life Path (grouping +
alternate Master-33 check), Attainment, Planes of Expression, and Master
Number handling (11 / 22 / 33) per the practitioner guide.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Letter charts
# ---------------------------------------------------------------------------
PYTHAGOREAN = {
    **{c: i for i, c in enumerate("ABCDEFGHI", 1)},
    **{c: i for i, c in enumerate("JKLMNOPQR", 1)},
    **{c: i for i, c in enumerate("STUVWXYZ", 1)},
}

# Chaldean: numbers 1–8 only (9 is sacred / excluded from letter assignment).
CHALDEAN = {
    "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1,
    "B": 2, "K": 2, "R": 2,
    "C": 3, "G": 3, "L": 3, "S": 3,
    "D": 4, "M": 4, "T": 4,
    "E": 5, "H": 5, "N": 5, "X": 5,
    "U": 6, "V": 6, "W": 6,
    "O": 7, "Z": 7,
    "F": 8, "P": 8,
}

VOWELS = set("AEIOU")

# Planes of Expression (letter groups — Pythagorean tradition).
PLANES = {
    "Mental": set("AHJNP"),
    "Physical": set("DEMW"),
    "Emotional": set("BORSTX"),
    "Intuitive": set("CFGIKLQUVYZ"),
}

# Generational suffixes never included in calculations.
_SUFFIX_RE = re.compile(
    r"\b(JR\.?|SR\.?|II|III|IV|V|VI|VII|VIII|IX|X|2ND|3RD|4TH)\b",
    re.IGNORECASE,
)

MASTER_NUMBERS = {11, 22, 33}

# ---------------------------------------------------------------------------
# Interpretations (1–9 + Masters) — plain language for end users
# ---------------------------------------------------------------------------
NUMBER_MEANING: Dict[int, Dict[str, str]] = {
    1: {
        "title": "The Pioneer",
        "eastern": "Water · independence and honour; watch isolation.",
        "western": "Initiator and warrior energy — beginnings, leadership, self-drive.",
        "plain": "You lead, start, and stand on your own. Best when you act; strain shows as loneliness or ego.",
    },
    2: {
        "title": "The Diplomat",
        "eastern": "Earth · symmetry and ease; partnership energy.",
        "western": "Sensitive, cooperative, peacemaking — the dual / relational root.",
        "plain": "You thrive in partnership and harmony. Strength is empathy; watch people-pleasing.",
    },
    3: {
        "title": "The Creator",
        "eastern": "Wood · growth, birth, abundance.",
        "western": "Artistic, social, optimistic — creative expression.",
        "plain": "You express, create, and connect. Joy and communication are gifts; scatter is the pitfall.",
    },
    4: {
        "title": "The Architect",
        "eastern": "Wood · structure and rebirth (challenging sound in some East Asian systems).",
        "western": "Solid foundations, practical systems, discipline.",
        "plain": "You build what lasts. Reliability is your edge; rigidity can box you in.",
    },
    5: {
        "title": "The Voyager",
        "eastern": "Earth · balance and movement; freedom tone.",
        "western": "Adventure, change, curiosity, the open road.",
        "plain": "You need freedom and variety. Adaptability is power; restlessness can scatter focus.",
    },
    6: {
        "title": "The Nurturer",
        "eastern": "Metal · wealth / profitable, auspicious care.",
        "western": "Home, responsibility, harmony, service to loved ones.",
        "plain": "You care, protect, and create beauty. Watch over-giving and the martyr pattern.",
    },
    7: {
        "title": "The Seeker",
        "eastern": "Metal · togetherness and inner truth.",
        "western": "Analysis, introspection, spiritual inquiry.",
        "plain": "You dig for truth. Depth and wisdom are gifts; isolation or overthinking are risks.",
    },
    8: {
        "title": "The Powerhouse",
        "eastern": "Earth · prosperity and material mastery.",
        "western": "Efficiency, authority, respect, worldly balance.",
        "plain": "You aim for results and recognition. Ambition builds; obsession or control can harden you.",
    },
    9: {
        "title": "The Humanitarian",
        "eastern": "Fire · longevity, motivation, completion.",
        "western": "Compassion, idealism, worldly sophistication.",
        "plain": "You serve the larger picture. Idealism inspires; burnout or bitterness can follow if you give without boundaries.",
    },
    11: {
        "title": "Master 11 — The Visionary",
        "eastern": "Heightened 2 energy — intuition as messenger.",
        "western": "Illuminated, inspirational; can feel shy or misunderstood.",
        "plain": "High-intensity intuition and inspiration. Ambition is 11; grounded instinct is 2 (diplomacy).",
    },
    22: {
        "title": "Master 22 — The Master Builder",
        "eastern": "Heightened 4 energy — global structure.",
        "western": "Logical vision made real at scale; can become demanding.",
        "plain": "You can build big systems from practical roots. Ambition is 22; instinct is 4 (the architect).",
    },
    33: {
        "title": "Master 33 — The Master Teacher",
        "eastern": "Heightened 6 energy — healing and service.",
        "western": "Universal altruism and healing presence; watch martyrdom.",
        "plain": "You teach and heal through care. Ambition is 33; instinct is 6 (the nurturer).",
    },
}


def meaning_for(n: int) -> Dict[str, str]:
    if n in NUMBER_MEANING:
        return NUMBER_MEANING[n]
    base = _force_single(n)
    return NUMBER_MEANING.get(base, {
        "title": f"Number {n}",
        "eastern": "",
        "western": "",
        "plain": f"Core vibration {n}.",
    })


# ---------------------------------------------------------------------------
# Reduction helpers
# ---------------------------------------------------------------------------
def _force_single(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def reduce_number(n: int, *, keep_masters: bool = True) -> Tuple[int, Optional[int]]:
    """Reduce to single digit, optionally preserving 11 / 22 / 33.

    Returns (display_number, base_number_or_None).
    For masters: (22, 4). For ordinary: (7, None).
    """
    if n <= 0:
        return 0, None
    while n > 9:
        if keep_masters and n in MASTER_NUMBERS:
            return n, _force_single(n)
        n = sum(int(d) for d in str(n))
    return n, None


def format_number(n: int, base: Optional[int] = None) -> str:
    if base:
        return f"{n}/{base}"
    return str(n)


# ---------------------------------------------------------------------------
# Name cleaning
# ---------------------------------------------------------------------------
def clean_name(name: str) -> str:
    """Strip generational suffixes and normalize whitespace."""
    name = _SUFFIX_RE.sub("", name or "")
    name = re.sub(r"[^A-Za-z\s\-']", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def name_segments(name: str) -> List[str]:
    cleaned = clean_name(name)
    if not cleaned:
        return []
    # Split on spaces; keep hyphenated parts as one segment for letter walk.
    return [p for p in cleaned.split(" ") if p]


def _is_vowel(letter: str, word: str, index: int) -> bool:
    """Y is a vowel only when it supplies a vowel sound (not leading consonant)."""
    ch = letter.upper()
    if ch in VOWELS:
        return True
    if ch != "Y":
        return False
    # Leading Y → consonant (Young). Otherwise treat as vowel (Candy, Mary).
    return index > 0


def _chart_for(system: str) -> Dict[str, int]:
    return CHALDEAN if system.lower().startswith("chal") else PYTHAGOREAN


def letter_value(letter: str, system: str = "pythagorean") -> int:
    return _chart_for(system).get(letter.upper(), 0)


# ---------------------------------------------------------------------------
# Name number calculations
# ---------------------------------------------------------------------------
def _sum_letters(text: str, system: str, *, vowels_only: bool = False,
                 consonants_only: bool = False) -> int:
    total = 0
    # Walk each alphabetic char; for Y rule use word context per segment.
    word = re.sub(r"[^A-Za-z]", "", text)
    letters = list(word.upper())
    for i, ch in enumerate(letters):
        is_v = _is_vowel(ch, word, i)
        if vowels_only and not is_v:
            continue
        if consonants_only and is_v:
            continue
        total += letter_value(ch, system)
    return total


def _segment_reduce(total: int, *, keep_masters: bool) -> int:
    n, _ = reduce_number(total, keep_masters=keep_masters)
    return n


def name_number(
    full_name: str,
    system: str = "pythagorean",
    *,
    vowels_only: bool = False,
    consonants_only: bool = False,
    keep_masters: bool = True,
) -> Dict:
    """Destiny / Heart's Desire / Personality via segment-then-sum protocol."""
    segs = name_segments(full_name)
    segment_details = []
    reduced_parts: List[int] = []
    for seg in segs:
        raw = _sum_letters(seg, system, vowels_only=vowels_only,
                           consonants_only=consonants_only)
        red = _segment_reduce(raw, keep_masters=keep_masters)
        segment_details.append({"segment": seg, "raw": raw, "reduced": red})
        reduced_parts.append(red)
    combined = sum(reduced_parts) if reduced_parts else 0
    final, base = reduce_number(combined, keep_masters=keep_masters)
    return {
        "value": final,
        "base": base,
        "display": format_number(final, base),
        "segments": segment_details,
        "combined_before_final": combined,
    }


def destiny_number(full_name: str, system: str = "pythagorean") -> Dict:
    return name_number(full_name, system)


def hearts_desire(full_name: str, system: str = "pythagorean") -> Dict:
    return name_number(full_name, system, vowels_only=True)


def personality_number(full_name: str, system: str = "pythagorean") -> Dict:
    return name_number(full_name, system, consonants_only=True)


# ---------------------------------------------------------------------------
# Birth-date numbers
# ---------------------------------------------------------------------------
def life_path_grouping(dob: date) -> Dict:
    """Standard: reduce month, day, year separately, then sum."""
    m, _ = reduce_number(dob.month, keep_masters=True)
    d, _ = reduce_number(dob.day, keep_masters=True)
    y_sum = sum(int(x) for x in str(dob.year))
    y, y_base = reduce_number(y_sum, keep_masters=True)
    total = m + d + y
    final, base = reduce_number(total, keep_masters=True)
    return {
        "method": "grouping",
        "parts": {"month": m, "day": d, "year": y, "year_raw_sum": y_sum},
        "value": final,
        "base": base,
        "display": format_number(final, base),
        "total_before_final": total,
    }


def life_path_alternate(dob: date) -> Dict:
    """Alternate: sum all digits at once — reveals hidden 33 profiles."""
    digits = [int(x) for x in f"{dob.month:02d}{dob.day:02d}{dob.year}"]
    total = sum(digits)
    final, base = reduce_number(total, keep_masters=True)
    return {
        "method": "alternate",
        "digits_sum": total,
        "value": final,
        "base": base,
        "display": format_number(final, base),
        "total_before_final": total,
    }


def life_path_number(dob: date) -> Dict:
    """Prefer alternate when it surfaces a Master Number the grouping hides."""
    grouped = life_path_grouping(dob)
    alternate = life_path_alternate(dob)
    preferred = alternate if (
        alternate["value"] in MASTER_NUMBERS
        and grouped["value"] not in MASTER_NUMBERS
    ) else grouped
    return {
        "value": preferred["value"],
        "base": preferred["base"],
        "display": preferred["display"],
        "preferred_method": preferred["method"],
        "grouping": grouped,
        "alternate": alternate,
        "master_revealed_by_alternate": (
            alternate["value"] in MASTER_NUMBERS
            and grouped["value"] != alternate["value"]
        ),
    }


def attainment_number(destiny: Dict, life_path: Dict) -> Dict:
    total = destiny["value"] + life_path["value"]
    # If destiny/life path are masters, use the display values as-is (already reduced form).
    final, base = reduce_number(total, keep_masters=True)
    return {
        "value": final,
        "base": base,
        "display": format_number(final, base),
        "from": f"{destiny['display']} + {life_path['display']} = {total}",
    }


# ---------------------------------------------------------------------------
# Planes of Expression
# ---------------------------------------------------------------------------
def planes_of_expression(full_name: str, system: str = "pythagorean") -> Dict[str, Dict]:
    cleaned = clean_name(full_name).upper()
    letters = [c for c in cleaned if c.isalpha()]
    counts = {plane: 0 for plane in PLANES}
    values = {plane: 0 for plane in PLANES}
    for ch in letters:
        for plane, group in PLANES.items():
            if ch in group:
                counts[plane] += 1
                values[plane] += letter_value(ch, system)
                break
    result = {}
    for plane in PLANES:
        n, base = reduce_number(values[plane], keep_masters=True) if values[plane] else (0, None)
        result[plane] = {
            "letters": counts[plane],
            "raw": values[plane],
            "value": n,
            "base": base,
            "display": format_number(n, base) if values[plane] else "—",
        }
    return result


# ---------------------------------------------------------------------------
# Conflict / harmony note between Heart's Desire and Personality
# ---------------------------------------------------------------------------
def inner_alignment_note(heart: Dict, personality: Dict) -> Dict:
    h = heart["base"] or heart["value"]
    p = personality["base"] or personality["value"]
    if h == p:
        tone = "aligned"
        text = (
            f"Heart’s Desire {heart['display']} and Personality {personality['display']} "
            f"match — your outer style and inner drive pull in the same direction."
        )
    else:
        tone = "tension"
        hm = meaning_for(heart["value"])["title"]
        pm = meaning_for(personality["value"])["title"]
        text = (
            f"Inner drive ({heart['display']} — {hm}) and outer mask "
            f"({personality['display']} — {pm}) differ. That gap can feel like "
            f"living behind a persona — useful to notice, not a flaw."
        )
    return {"tone": tone, "text": text}


# ---------------------------------------------------------------------------
# Full chart
# ---------------------------------------------------------------------------
@dataclass
class NumerologyInput:
    birth_name: str
    birth_date: date
    current_name: str = ""
    system: str = "pythagorean"  # or "chaldean"


def build_chart(data: NumerologyInput) -> Dict:
    """Full core-chart synthesis for one system."""
    system = data.system
    birth = clean_name(data.birth_name)
    current = clean_name(data.current_name) if data.current_name.strip() else ""

    destiny = destiny_number(birth, system)
    heart = hearts_desire(birth, system)
    personality = personality_number(birth, system)
    life = life_path_number(data.birth_date)
    attain = attainment_number(destiny, life)
    planes = planes_of_expression(birth, system)
    alignment = inner_alignment_note(heart, personality)

    current_block = None
    if current and current.upper() != birth.upper():
        current_block = {
            "name": current,
            "destiny": destiny_number(current, system),
            "heart": hearts_desire(current, system),
            "personality": personality_number(current, system),
            "note": (
                "Birth name is the root karmic imprint. Current name shows how you "
                "have rebranded or evolved — useful for luck, career, and relationships."
            ),
        }

    core = [
        {"key": "life_path", "label": "Life Path", "subtitle": "Your journey & tools",
         "number": life, "role": "The path"},
        {"key": "destiny", "label": "Destiny / Expression", "subtitle": "What you came to build",
         "number": destiny, "role": "The what"},
        {"key": "heart", "label": "Heart’s Desire", "subtitle": "Your secret why",
         "number": heart, "role": "The why"},
        {"key": "personality", "label": "Personality", "subtitle": "The mask others see",
         "number": personality, "role": "The how"},
        {"key": "attainment", "label": "Attainment", "subtitle": "Soul’s design this life",
         "number": attain, "role": "The aim"},
    ]

    enriched = []
    for item in core:
        n = item["number"]["value"]
        m = meaning_for(n)
        enriched.append({**item, "meaning": m})

    return {
        "system": system,
        "system_label": "Chaldean (Vedic)" if system.startswith("chal") else "Pythagorean (Western)",
        "birth_name": birth,
        "birth_date": data.birth_date.isoformat(),
        "core": enriched,
        "life_path": life,
        "destiny": destiny,
        "heart": heart,
        "personality": personality,
        "attainment": attain,
        "planes": planes,
        "alignment": alignment,
        "current_name": current_block,
        "letter_chart": _chart_for(system),
    }


def compare_systems(data: NumerologyInput) -> Dict:
    """Side-by-side Pythagorean vs Chaldean for the same inputs."""
    py = build_chart(NumerologyInput(
        data.birth_name, data.birth_date, data.current_name, "pythagorean"))
    ch = build_chart(NumerologyInput(
        data.birth_name, data.birth_date, data.current_name, "chaldean"))
    return {"pythagorean": py, "chaldean": ch}


def chart_markdown(chart: Dict) -> str:
    lines = [
        f"# Numerology Chart — {chart['birth_name']}",
        "",
        f"**System:** {chart['system_label']}  ",
        f"**Birth date:** {chart['birth_date']}",
        "",
        "## Core numbers",
    ]
    for item in chart["core"]:
        m = item["meaning"]
        lines += [
            f"### {item['label']}: {item['number']['display']} — {m['title']}",
            m["plain"],
            f"- Eastern lens: {m['eastern']}",
            f"- Western lens: {m['western']}",
            "",
        ]
    lines += [
        "## Inner alignment",
        chart["alignment"]["text"],
        "",
        "## Planes of Expression",
    ]
    for plane, info in chart["planes"].items():
        lines.append(f"- **{plane}**: {info['display']} ({info['letters']} letters)")
    if chart.get("current_name"):
        cur = chart["current_name"]
        lines += [
            "",
            "## Current name",
            cur["note"],
            f"- Destiny {cur['destiny']['display']} · Heart {cur['heart']['display']} · "
            f"Personality {cur['personality']['display']}",
        ]
    lines += [
        "",
        "_For reflection and guidance — not deterministic fate. "
        "Jr./Sr. and generational suffixes are excluded by professional standard._",
    ]
    return "\n".join(lines)
