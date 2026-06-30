"""Static reference data for Vedic astrology (Jyotish).

This module is the single source of truth for the "rules" of the system:
the nine planets (Navagrahas), twelve signs (Rashis), twelve houses
(Bhavas), planetary friendships, dignities (exaltation/debilitation/own),
house classifications, special aspects (Graha Drishti) and the Vimshottari
Dasha periods. Keeping it as plain data keeps the calculation and
interpretation layers testable and easy to audit.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Planets (Navagrahas)
# ---------------------------------------------------------------------------
# Order follows the classical weekday/graha order. Rahu/Ketu are the lunar
# nodes (shadow planets) and are always exactly 180 degrees apart.
PLANETS = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter",
    "Venus", "Saturn", "Rahu", "Ketu",
]

PLANET_SANSKRIT = {
    "Sun": "Surya",
    "Moon": "Chandra",
    "Mars": "Mangala",
    "Mercury": "Budha",
    "Jupiter": "Guru",
    "Venus": "Shukra",
    "Saturn": "Shani",
    "Rahu": "Rahu",
    "Ketu": "Ketu",
}

PLANET_GLYPH = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke",
}

# Natural benefics / malefics (general classification used as a fallback when a
# functional classification for the ascendant is not decisive).
NATURAL_BENEFICS = {"Jupiter", "Venus", "Moon", "Mercury"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# ---------------------------------------------------------------------------
# Signs (Rashis)
# ---------------------------------------------------------------------------
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_SANSKRIT = {
    "Aries": "Mesha", "Taurus": "Vrishabha", "Gemini": "Mithuna",
    "Cancer": "Karka", "Leo": "Simha", "Virgo": "Kanya",
    "Libra": "Tula", "Scorpio": "Vrishchika", "Sagittarius": "Dhanu",
    "Capricorn": "Makara", "Aquarius": "Kumbha", "Pisces": "Meena",
}

# Ruler (lord) of each sign.
SIGN_LORD = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

SIGN_ELEMENT = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}

# ---------------------------------------------------------------------------
# Houses (Bhavas)
# ---------------------------------------------------------------------------
HOUSE_NAME = {
    1: "Lagna", 2: "Dhana", 3: "Sahaja", 4: "Sukha", 5: "Putra", 6: "Ripu",
    7: "Kalatra", 8: "Randhra", 9: "Dharma", 10: "Karma", 11: "Labha", 12: "Vyaya",
}

HOUSE_SIGNIFICATION = {
    1: "Self, physical body, appearance, vitality, personality.",
    2: "Wealth, speech, family of origin, food habits.",
    3: "Courage, siblings, communication, short journeys.",
    4: "Mother, home, vehicles, emotional foundation.",
    5: "Creativity, children, intelligence, past-life merit.",
    6: "Health challenges, enemies, debts, daily work.",
    7: "Marriage, partnerships, business relationships.",
    8: "Transformation, longevity, hidden matters, inheritance.",
    9: "Higher learning, father, luck, spiritual purpose.",
    10: "Career, reputation, public life, authority.",
    11: "Gains, social networks, aspirations, income.",
    12: "Losses, spiritual liberation (Moksha), isolation.",
}

# Short theme keyword for "repeating pattern" detection.
HOUSE_THEME = {
    1: "self & vitality", 2: "wealth & speech", 3: "courage & siblings",
    4: "home & mother", 5: "children & creativity", 6: "health & enemies",
    7: "marriage & partnership", 8: "transformation & longevity",
    9: "fortune & dharma", 10: "career & status", 11: "gains & income",
    12: "loss & liberation",
}

# House categories.
KENDRA = {1, 4, 7, 10}          # angular - pillars of stability
TRIKONA = {1, 5, 9}             # trines - auspicious
DUSTHANA = {6, 8, 12}           # challenging - transformation
UPACHAYA = {3, 6, 10, 11}       # houses of growth over time

def house_category(house: int) -> str:
    cats = []
    if house in KENDRA:
        cats.append("Kendra")
    if house in TRIKONA:
        cats.append("Trikona")
    if house in DUSTHANA:
        cats.append("Dusthana")
    if house in UPACHAYA:
        cats.append("Upachaya")
    return ", ".join(cats) if cats else "Neutral"

# ---------------------------------------------------------------------------
# Planetary friendships (natural relationships)
# ---------------------------------------------------------------------------
# friend / enemy / neutral relationships from the briefing table.
FRIENDS = {
    "Sun":     {"Moon", "Mars", "Jupiter"},
    "Moon":    {"Sun", "Mercury"},
    "Mars":    {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus":   {"Mercury", "Saturn", "Rahu"},
    "Saturn":  {"Mercury", "Venus", "Rahu"},
    "Rahu":    {"Venus", "Saturn"},
    "Ketu":    {"Sun", "Mars"},
}

ENEMIES = {
    "Sun":     {"Venus", "Saturn", "Rahu"},
    "Moon":    set(),
    "Mars":    {"Mercury"},
    "Mercury": {"Moon", "Ketu"},
    "Jupiter": {"Mercury", "Venus", "Rahu"},
    "Venus":   {"Sun", "Moon"},
    "Saturn":  {"Sun", "Moon", "Mars"},
    "Rahu":    {"Sun", "Moon", "Mars"},
    "Ketu":    {"Venus", "Saturn"},
}

NEUTRALS = {
    "Sun":     {"Mercury", "Ketu"},
    "Moon":    {"Mars", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"},
    "Mars":    {"Venus", "Saturn", "Rahu", "Ketu"},
    "Mercury": {"Mars", "Jupiter", "Saturn", "Rahu"},
    "Jupiter": {"Saturn", "Ketu"},
    "Venus":   {"Mars", "Jupiter", "Ketu"},
    "Saturn":  {"Jupiter", "Ketu"},
    "Rahu":    {"Mercury", "Jupiter", "Ketu"},
    "Ketu":    {"Mercury", "Jupiter", "Moon", "Rahu"},
}

def relationship(planet: str, other: str) -> str:
    """Return 'Friend', 'Enemy' or 'Neutral' of ``other`` w.r.t ``planet``."""
    if other in FRIENDS.get(planet, set()):
        return "Friend"
    if other in ENEMIES.get(planet, set()):
        return "Enemy"
    return "Neutral"

# ---------------------------------------------------------------------------
# Dignities: exaltation, debilitation, moolatrikona and own signs
# ---------------------------------------------------------------------------
# Exaltation sign + exact degree of deep exaltation.
EXALTATION = {
    "Sun": ("Aries", 10), "Moon": ("Taurus", 3), "Mars": ("Capricorn", 28),
    "Mercury": ("Virgo", 15), "Jupiter": ("Cancer", 5), "Venus": ("Pisces", 27),
    "Saturn": ("Libra", 20),
    # Nodes have no universally agreed exaltation; a common scheme used here:
    "Rahu": ("Taurus", 20), "Ketu": ("Scorpio", 20),
}

# Debilitation is exactly opposite the exaltation sign.
DEBILITATION = {
    "Sun": ("Libra", 10), "Moon": ("Scorpio", 3), "Mars": ("Cancer", 28),
    "Mercury": ("Pisces", 15), "Jupiter": ("Capricorn", 5), "Venus": ("Virgo", 27),
    "Saturn": ("Aries", 20),
    "Rahu": ("Scorpio", 20), "Ketu": ("Taurus", 20),
}

# Own signs (rulership). Sun and Moon own one sign each; the rest own two.
OWN_SIGNS = {
    "Sun": {"Leo"},
    "Moon": {"Cancer"},
    "Mars": {"Aries", "Scorpio"},
    "Mercury": {"Gemini", "Virgo"},
    "Jupiter": {"Sagittarius", "Pisces"},
    "Venus": {"Taurus", "Libra"},
    "Saturn": {"Capricorn", "Aquarius"},
    "Rahu": set(),
    "Ketu": set(),
}

# ---------------------------------------------------------------------------
# Special aspects (Graha Drishti)
# ---------------------------------------------------------------------------
# Every planet aspects the 7th house/sign from itself. These planets cast
# additional "special" full aspects. (Offsets counted inclusively, 1 = same.)
SPECIAL_ASPECTS = {
    "Mars": [4, 7, 8],
    "Jupiter": [5, 7, 9],
    "Saturn": [3, 7, 10],
    # Rahu/Ketu are sometimes given Jupiter-like aspects; included as optional.
    "Rahu": [5, 7, 9],
    "Ketu": [5, 7, 9],
}
DEFAULT_ASPECTS = [7]

# ---------------------------------------------------------------------------
# Nakshatras (lunar mansions) + Vimshottari Dasha
# ---------------------------------------------------------------------------
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
]

# Each nakshatra spans 13 deg 20 min (= 800 arc-minutes).
NAKSHATRA_SPAN = 360.0 / 27.0  # 13.333... degrees

# Lord of each nakshatra in the Vimshottari sequence (repeats every 9).
VIMSHOTTARI_ORDER = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury",
]

# Mahadasha length in years for each planet. Total = 120 years.
VIMSHOTTARI_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}

# The 27 nakshatras map cyclically to the 9 dasha lords.
NAKSHATRA_LORD = {
    name: VIMSHOTTARI_ORDER[i % 9] for i, name in enumerate(NAKSHATRAS)
}

# ---------------------------------------------------------------------------
# Remedial measures (Upaye) per planet
# ---------------------------------------------------------------------------
REMEDIES = {
    "Sun": {
        "gemstone": "Ruby (Manik)",
        "mantra": "Om Hraam Hreem Hraum Sah Suryaya Namah",
        "charity": "Offer wheat/jaggery; respect father and elders.",
    },
    "Moon": {
        "gemstone": "Pearl (Moti)",
        "mantra": "Om Shraam Shreem Shraum Sah Chandraya Namah",
        "charity": "Donate milk/rice; serve your mother.",
    },
    "Mars": {
        "gemstone": "Red Coral (Moonga)",
        "mantra": "Om Kraam Kreem Kraum Sah Bhaumaya Namah",
        "charity": "Donate red lentils; support siblings.",
    },
    "Mercury": {
        "gemstone": "Emerald (Panna)",
        "mantra": "Om Braam Breem Braum Sah Budhaya Namah",
        "charity": "Donate green moong; feed green fodder to cows.",
    },
    "Jupiter": {
        "gemstone": "Yellow Sapphire (Pukhraj)",
        "mantra": "Om Graam Greem Graum Sah Gurave Namah",
        "charity": "Donate turmeric/yellow items; honour teachers.",
    },
    "Venus": {
        "gemstone": "Diamond / White Sapphire",
        "mantra": "Om Draam Dreem Draum Sah Shukraya Namah",
        "charity": "Donate white clothes/sugar; respect women.",
    },
    "Saturn": {
        "gemstone": "Blue Sapphire (Neelam)",
        "mantra": "Om Praam Preem Praum Sah Shanaye Namah",
        "charity": "Feed crows/labourers; donate black sesame/iron.",
    },
    "Rahu": {
        "gemstone": "Hessonite (Gomed)",
        "mantra": "Om Bhraam Bhreem Bhraum Sah Rahave Namah",
        "charity": "Donate mustard oil; feed the needy.",
    },
    "Ketu": {
        "gemstone": "Cat's Eye (Lehsunia)",
        "mantra": "Om Sraam Sreem Sraum Sah Ketave Namah",
        "charity": "Feed dogs; donate multi-coloured blankets.",
    },
}
