"""Rishikesh / Kashi Panchang tradition — rules for life prediction.

Reference framework from the Hrishikesh Panchang school (North India):
  * Five limbs (Pancha-Anga) with elemental governance
  * Avakhada Chakra (Varna, Vashya, Yoni, Gana, Nadi)
  * Phalita Navaratna Samgraha limb weighting
  * Tarabala & Chandrabala priority for natal evaluation
  * Gandanta, Rikta Tithi, Maha Yoga Dosha flags
"""

from __future__ import annotations

from typing import Dict, Set

# ---------------------------------------------------------------------------
# Gandanta Nakshatras — critical early-life transitions (Rishikesh tradition)
# ---------------------------------------------------------------------------
GANDANTA_NAKSHATRAS: Set[str] = {
    "Ashwini", "Ashlesha", "Magha", "Jyeshtha", "Mula", "Revati",
}

# Rikta Tithis — 4th, 9th, 14th in each paksha (avoid new ventures)
RIKTA_TITHI_NUMBERS: Set[int] = {4, 9, 14}

# Maha Yoga Doshas — malefic yogas that can "spoil" an auspicious Nakshatra
MAHA_YOGA_DOSHAS: Set[str] = {
    "Vyatipata", "Vaidhriti", "Vyaghata", "Parigha",
    "Atiganda", "Vishkumbha", "Shoola", "Ganda",
}

# Benefic / malefic weekdays (Vara — fire element / Ayus)
BENEFIC_VAARA: Set[str] = {"Guruvara", "Shukravara"}
MALEFIC_VAARA: Set[str] = {"Shanivara"}

# Fixed Karanas — harder worldly climb (earth element / execution)
FIXED_KARANAS: Set[str] = {"Kimstughna", "Shakuni", "Chatushpada", "Naga"}

# Phalita Navaratna Samgraha — limb point weights
LIMB_WEIGHTS: Dict[str, int] = {
    "tithi": 1,
    "nakshatra": 4,
    "vara": 8,
    "karana": 16,
    "yoga": 32,
    "tarabala": 60,
    "chandrabala": 100,
}

# Tarabala names from Janma Nakshatra (count 1..9 cycling)
TARABALA_NAMES = [
    "Janma", "Sampat", "Vipat", "Kshema", "Pratyak",
    "Sadhana", "Naidhana", "Mitra", "Ati-Mitra",
]
TARABALA_AUSPICIOUS: Set[str] = {"Sampat", "Kshema", "Sadhana", "Mitra", "Ati-Mitra"}

# Chandrabala — Moon transit houses auspicious from natal Moon sign (1-indexed)
CHANDRA_BALA_GOOD_HOUSES: Set[int] = {1, 3, 6, 7, 10, 11}

# Guru Gochar — auspicious Jupiter transit houses from natal Moon
GURU_GOCHAR_GOOD_HOUSES: Set[int] = {2, 5, 7, 9, 11}

# ---------------------------------------------------------------------------
# Avakhada Chakra — Moon sign / Nakshatra tables
# ---------------------------------------------------------------------------
VARNA_BY_SIGN: Dict[str, str] = {
    "Cancer": "Brahmin", "Scorpio": "Brahmin", "Pisces": "Brahmin",
    "Aries": "Kshatriya", "Leo": "Kshatriya", "Sagittarius": "Kshatriya",
    "Taurus": "Vaishya", "Virgo": "Vaishya", "Capricorn": "Vaishya",
    "Gemini": "Shudra", "Libra": "Shudra", "Aquarius": "Shudra",
}

VARNA_MEANING: Dict[str, str] = {
    "Brahmin": "Intellectual / teaching / spiritual sectors",
    "Kshatriya": "Administrative / leadership / protective roles",
    "Vaishya": "Commercial / trade / finance / enterprise",
    "Shudra": "Service / skilled labour / support professions",
}

VASHYA_BY_SIGN: Dict[str, str] = {
    "Aries": "Chatushpad", "Taurus": "Chatushpad", "Gemini": "Manava",
    "Cancer": "Jalchar", "Leo": "Chatushpad", "Virgo": "Manava",
    "Libra": "Manava", "Scorpio": "Keet", "Sagittarius": "Manava",
    "Capricorn": "Chatushpad", "Aquarius": "Manava", "Pisces": "Jalchar",
}

VASHYA_MEANING: Dict[str, str] = {
    "Chatushpad": "Grounded, persistent; magnetism through stability",
    "Manava": "Human-natured; adaptable social intelligence",
    "Jalchar": "Fluid, intuitive; thrives near water or change",
    "Keet": "Intense, penetrating; transformative social presence",
}

GANA_BY_NAKSHATRA: Dict[str, str] = {
    "Ashwini": "Deva", "Bharani": "Manushya", "Krittika": "Rakshasa",
    "Rohini": "Manushya", "Mrigashira": "Deva", "Ardra": "Manushya",
    "Punarvasu": "Deva", "Pushya": "Deva", "Ashlesha": "Rakshasa",
    "Magha": "Rakshasa", "Purva Phalguni": "Manushya", "Uttara Phalguni": "Manushya",
    "Hasta": "Deva", "Chitra": "Rakshasa", "Swati": "Deva",
    "Vishakha": "Rakshasa", "Anuradha": "Deva", "Jyeshtha": "Rakshasa",
    "Mula": "Rakshasa", "Purva Ashadha": "Manushya", "Uttara Ashadha": "Manushya",
    "Shravana": "Deva", "Dhanishta": "Rakshasa", "Shatabhisha": "Rakshasa",
    "Purva Bhadrapada": "Manushya", "Uttara Bhadrapada": "Manushya", "Revati": "Deva",
}

GANA_MEANING: Dict[str, str] = {
    "Deva": "Divine temperament — sattvic, refined, dharmic reactions",
    "Manushya": "Human temperament — pragmatic, balanced worldly-spiritual mix",
    "Rakshasa": "Intense temperament — passionate, assertive, transformative drive",
}

NADI_BY_NAKSHATRA: Dict[str, str] = {
    "Ashwini": "Adi", "Bharani": "Madhya", "Krittika": "Antya",
    "Rohini": "Antya", "Mrigashira": "Madhya", "Ardra": "Adi",
    "Punarvasu": "Adi", "Pushya": "Madhya", "Ashlesha": "Antya",
    "Magha": "Antya", "Purva Phalguni": "Madhya", "Uttara Phalguni": "Adi",
    "Hasta": "Adi", "Chitra": "Madhya", "Swati": "Antya",
    "Vishakha": "Antya", "Anuradha": "Madhya", "Jyeshtha": "Adi",
    "Mula": "Adi", "Purva Ashadha": "Madhya", "Uttara Ashadha": "Antya",
    "Shravana": "Antya", "Dhanishta": "Madhya", "Shatabhisha": "Adi",
    "Purva Bhadrapada": "Adi", "Uttara Bhadrapada": "Madhya", "Revati": "Antya",
}

NADI_MEANING: Dict[str, str] = {
    "Adi": "Vata constitution — quick, mobile, airy vitality",
    "Madhya": "Pitta constitution — focused, driven, fiery metabolism",
    "Antya": "Kapha constitution — steady, nourishing, earthy endurance",
}

# 14 Yoni archetypes mapped to Nakshatra pairs (Kashi / North-Indian convention)
YONI_BY_NAKSHATRA: Dict[str, str] = {
    "Ashwini": "Horse", "Bharani": "Elephant", "Krittika": "Sheep",
    "Rohini": "Serpent", "Mrigashira": "Serpent", "Ardra": "Dog",
    "Punarvasu": "Cat", "Pushya": "Sheep", "Ashlesha": "Cat",
    "Magha": "Rat", "Purva Phalguni": "Rat", "Uttara Phalguni": "Cow",
    "Hasta": "Buffalo", "Chitra": "Tiger", "Swati": "Buffalo",
    "Vishakha": "Tiger", "Anuradha": "Deer", "Jyeshtha": "Deer",
    "Mula": "Dog", "Purva Ashadha": "Monkey", "Uttara Ashadha": "Mongoose",
    "Shravana": "Monkey", "Dhanishta": "Lion", "Shatabhisha": "Horse",
    "Purva Bhadrapada": "Lion", "Uttara Bhadrapada": "Cow", "Revati": "Elephant",
}

YONI_MEANING: Dict[str, str] = {
    "Horse": "Independent, swift primal energy",
    "Elephant": "Noble, patient, enduring temperament",
    "Sheep": "Gentle, artistic, comfort-seeking nature",
    "Serpent": "Magnetic, secretive, deeply intuitive",
    "Dog": "Loyal, vigilant, protective instincts",
    "Cat": "Graceful, self-contained, refined boundaries",
    "Rat": "Resourceful, adaptive, socially alert",
    "Cow": "Nurturing, stable, dharmic domesticity",
    "Buffalo": "Powerful, hardworking, steady force",
    "Tiger": "Fearless, commanding, intense will",
    "Deer": "Sensitive, graceful, peace-loving",
    "Monkey": "Clever, playful, inventive mind",
    "Mongoose": "Sharp, defensive, strategic survivor",
    "Lion": "Regal, authoritative, proud spirit",
}

# Elemental governance of the five limbs (Mahabhutas)
LIMB_ELEMENT: Dict[str, str] = {
    "tithi": "Water — emotional constitution & Lakshmi potential",
    "vara": "Fire — vitality, Ayus & physical endurance",
    "nakshatra": "Air — destiny, talents & Janma Rashi",
    "yoga": "Ether — immunity, spiritual character & health",
    "karana": "Earth — execution, career capability & practicality",
}


def avakhada(moon_sign: str, nakshatra: str, *, detailed: bool = False) -> Dict[str, str]:
    """Avakhada Chakra fields for a native (Moon sign + birth Nakshatra)."""
    varna = VARNA_BY_SIGN[moon_sign]
    vashya = VASHYA_BY_SIGN[moon_sign]
    yoni = YONI_BY_NAKSHATRA[nakshatra]
    gana = GANA_BY_NAKSHATRA[nakshatra]
    nadi = NADI_BY_NAKSHATRA[nakshatra]
    out = {
        "varna": varna,
        "vashya": vashya,
        "yoni": yoni,
        "gana": gana,
        "nadi": nadi,
    }
    if detailed:
        out.update({
            "varna_meaning": VARNA_MEANING[varna],
            "vashya_meaning": VASHYA_MEANING[vashya],
            "yoni_meaning": YONI_MEANING[yoni],
            "gana_meaning": GANA_MEANING[gana],
            "nadi_meaning": NADI_MEANING[nadi],
            "nadi_dosha_note": (
                "Nadi matching is the critical filter in Ashtakoota Milan — "
                "same Nadi between partners is traditionally avoided."
            ),
        })
    return out
