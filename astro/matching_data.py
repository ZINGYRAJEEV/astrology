"""Ashtakoota Milan reference tables (North-Indian / Rishikesh convention)."""

from __future__ import annotations

from typing import Dict, Tuple

# Varna hierarchy for Varna Koota (groom >= bride in rank = 1 point).
VARNA_RANK: Dict[str, int] = {
    "Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1,
}

# Vashya Koota — groom category vs bride category (max 2 points).
VASHYA_SCORE: Dict[Tuple[str, str], float] = {
    ("Chatushpad", "Chatushpad"): 2.0,
    ("Chatushpad", "Manava"): 1.0,
    ("Chatushpad", "Jalchar"): 1.0,
    ("Chatushpad", "Keet"): 1.0,
    ("Manava", "Chatushpad"): 1.0,
    ("Manava", "Manava"): 2.0,
    ("Manava", "Jalchar"): 1.5,
    ("Manava", "Keet"): 1.0,
    ("Jalchar", "Chatushpad"): 1.0,
    ("Jalchar", "Manava"): 1.5,
    ("Jalchar", "Jalchar"): 2.0,
    ("Jalchar", "Keet"): 1.0,
    ("Keet", "Chatushpad"): 0.0,
    ("Keet", "Manava"): 0.0,
    ("Keet", "Jalchar"): 1.0,
    ("Keet", "Keet"): 2.0,
}

# Gana Koota (max 6 points).
GANA_SCORE: Dict[Tuple[str, str], float] = {
    ("Deva", "Deva"): 6, ("Deva", "Manushya"): 5, ("Deva", "Rakshasa"): 1,
    ("Manushya", "Deva"): 6, ("Manushya", "Manushya"): 6, ("Manushya", "Rakshasa"): 0,
    ("Rakshasa", "Deva"): 0, ("Rakshasa", "Manushya"): 0, ("Rakshasa", "Rakshasa"): 6,
}

# Yoni pairs that score 0 (enemies) — symmetric.
YONI_ENEMIES: set = {
    ("Horse", "Buffalo"), ("Elephant", "Lion"), ("Sheep", "Monkey"),
    ("Serpent", "Mongoose"), ("Dog", "Deer"), ("Cat", "Rat"), ("Cow", "Tiger"),
}

# Friendly yoni pairs (score 3) — symmetric.
YONI_FRIENDS: set = {
    ("Horse", "Elephant"), ("Horse", "Deer"), ("Elephant", "Sheep"),
    ("Sheep", "Elephant"), ("Serpent", "Serpent"), ("Dog", "Dog"),
    ("Cat", "Sheep"), ("Rat", "Rat"), ("Cow", "Deer"), ("Buffalo", "Buffalo"),
    ("Tiger", "Tiger"), ("Deer", "Monkey"), ("Monkey", "Lion"),
    ("Mongoose", "Mongoose"), ("Lion", "Monkey"),
}

# Auspicious Tara positions (1-indexed within the 9-cycle).
AUSPICIOUS_TARA = {2, 4, 6, 8, 9}

# Ashtakoota verdict bands (out of 36).
MATCH_VERDICT = [
    (32, "Excellent", "Highly auspicious union — strong dharmic alignment."),
    (25, "Very Good", "Traditionally favoured — proceed with confidence."),
    (18, "Good", "Meets classical minimum (18+) — suitable with awareness."),
    (12, "Average", "Mixed compatibility — counsel and remedies advised."),
    (0, "Low", "Significant challenges — detailed remedial guidance needed."),
]
