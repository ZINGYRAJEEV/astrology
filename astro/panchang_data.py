"""Panchang reference data (Sanskrit / Hindi names).

Tables for the five limbs (Pancha-Anga): Tithi, Nakshatra, Yoga, Karana,
Vaara, plus Choghadiya, Hindu months, and inauspicious-period rules used by
North-Indian almanacs such as the Rishikesh Panchang style.
"""

from __future__ import annotations

# Vaara (weekday) - index 0 = Sunday
VAARA_SANSKRIT = [
    "Ravivara", "Somavara", "Mangalavara", "Budhavara",
    "Guruvara", "Shukravara", "Shanivara",
]
VAARA_HINDI = [
    "Ravivar", "Somvar", "Mangalvar", "Budhvar",
    "Guruvar", "Shukravar", "Shanivar",
]

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
]
TITHI_HINDI = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
]
# Krishna paksha 15th is Amavasya instead of Purnima
KRISHNA_TITHI_15 = "Amavasya"

YOGAS = [
    "Vishkumbha", "Preeti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti",
]

# Movable karanas (repeat); fixed karanas at cycle boundaries.
MOVABLE_KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
]
FIXED_KARANAS = {0: "Kimstughna", 57: "Shakuni", 58: "Chatushpada", 59: "Naga"}

# Purnimanta Hindu lunar months (North India / Uttarakhand convention).
HINDU_MONTHS = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
    "Ashwin", "Kartik", "Margashirsha", "Pausha", "Magha", "Phalguna",
]
HINDU_MONTHS_HINDI = [
    "Chaitra", "Vaishakh", "Jyeshtha", "Ashadh", "Sawan", "Bhadon",
    "Ashwin", "Kartik", "Margshirsh", "Paush", "Magh", "Phalgun",
]

# Sun's sidereal sign index -> Purnimanta month name (when moon is in bright half).
SUN_SIGN_TO_MONTH = {
    0: "Phalguna", 1: "Chaitra", 2: "Vaishakha", 3: "Jyeshtha",
    4: "Ashadha", 5: "Shravana", 6: "Bhadrapada", 7: "Ashwin",
    8: "Kartik", 9: "Margashirsha", 10: "Pausha", 11: "Magha",
}

# Choghadiya sequence (7 names cycling).
CHOGHADIYA_NAMES = ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"]
CHOGHADIYA_NATURE = {
    "Udveg": "Inauspicious", "Char": "Good for travel", "Labh": "Auspicious",
    "Amrit": "Highly auspicious", "Kaal": "Inauspicious", "Shubh": "Auspicious",
    "Rog": "Inauspicious",
}
# Weekday index (Sun=0) -> index into CHOGHADIYA_NAMES for first day segment.
DAY_CHOGHADIYA_START = [0, 3, 6, 2, 5, 1, 4]   # Udveg, Amrit, Rog, ...
NIGHT_CHOGHADIYA_START = [6, 5, 4, 3, 2, 1, 0]  # night order reversed pattern

# Rahu Kaal: which 1/8th of the day (1-8) is inauspicious (Sun=0 weekday).
RAHU_KAAL_SEGMENT = {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 4, 6: 3}
GULIKA_KAAL_SEGMENT = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}
YAMAGANDA_SEGMENT = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 7, 6: 6}

# Rishikesh default (ऋषिकेश पंचांग)
RISHIKESH = {
    "name": "Rishikesh, Uttarakhand",
    "name_hindi": "ऋषिकेश",
    "latitude": 30.0869,
    "longitude": 78.2676,
    "timezone": "Asia/Kolkata",
    "altitude_m": 400,
}
