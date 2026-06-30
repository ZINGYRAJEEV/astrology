"""The Witness layer - Jyotish meets the Ashtavakra Gita (Advaita Vedanta).

This module adds a non-dual, contemplative reframe to the chart. Where the
rest of the engine maps Vyavaharika Satya (transactional reality - the
"dream"), this layer points to the Drashta (the Witness) for whom the chart
is merely a map of Maya to be transcended.

It is pure reference data + a small synthesis helper; no calculation.
"""

from __future__ import annotations

from typing import Dict

from . import reference as ref

INTRO = (
    "Vedic astrology maps the dance of the planets (Maya) - your transactional "
    "reality. The Ashtavakra Gita reminds us that you are not the actor but the "
    "Drashta, the Witness on whose screen the whole chart appears. Use this map "
    "to play your role with grace, then go beyond it."
)

CLOSING = "You are the stillness behind the stars."

# Per-planet: metaphysical meaning, the astrological role (the dream), the
# Witness perspective (the reality), and a core verse.
PLANET_WITNESS: Dict[str, Dict[str, str]] = {
    "Sun": {
        "metaphysical": "Soul of the universe; the Atman, the innermost essence.",
        "dream": "Inner light, vitality, dharma and authority - the most glorious role.",
        "witness": "The pure Witness watching the light shine; you watch even the Sun.",
        "verse": "I am the pure witness - complete and free.",
    },
    "Moon": {
        "metaphysical": "Reflective consciousness (Manas); holds the vasanas (latent impressions).",
        "dream": "Mind, emotions, moods and cravings - the filter of experience.",
        "witness": "The silent observer of thoughts; the mind is a passing object.",
        "verse": "As one thinks, so one becomes.",
    },
    "Mars": {
        "metaphysical": "The generative life-spark; Rajasic energy and will.",
        "dream": "Drive, courage, surgical aggression and ambition.",
        "witness": "Action belongs to nature alone - the 'I' should not claim doership.",
        "verse": "Action belongs to nature alone.",
    },
    "Mercury": {
        "metaphysical": "The faculty of intellect (Buddhi) and discrimination (Viveka).",
        "dream": "Logic, analysis, speech and justification - and its endless loops.",
        "witness": "See thought as a transient object, not the Subject; stop planning the uncontrollable.",
        "verse": "The wise one does not plan or grieve.",
    },
    "Jupiter": {
        "metaphysical": "The Guru principle; grace and the expansion of consciousness.",
        "dream": "Wisdom, growth, fortune, children and faith.",
        "witness": "Grace that points beyond itself, toward Jnana (knowledge).",
        "verse": "Knowledge dawns; the seeker dissolves into the known.",
    },
    "Venus": {
        "metaphysical": "Cosmic attraction; the refinement of Maya into Bhakti (devotion).",
        "dream": "Love, beauty, comfort, art and union.",
        "witness": "Devotion that transcends the self - love as a doorway to Ananda.",
        "verse": "Through love that transcends the self, one reaches the feet of the Supreme.",
    },
    "Saturn": {
        "metaphysical": "Enforcer of time and karma; the purifying 'ring-pass-not'.",
        "dream": "Discipline, delay, loss and the long lessons of duty.",
        "witness": "A purifying fire; harshness is only the friction of the ego resisting dissolution.",
        "verse": "When there is no 'I', there is freedom.",
    },
    "Rahu": {
        "metaphysical": "Vikshepa Shakti - the projecting power of Maya.",
        "dream": "Insatiable desire and obsession; the temporary made to feel urgent.",
        "witness": "A dream-state; awareness is the solvent in which obsession melts.",
        "verse": "This world is like a dream - it vanishes upon waking.",
    },
    "Ketu": {
        "metaphysical": "Moksha-karaka; the drive toward liberation (Vairagya).",
        "dream": "Detachment, loss, mysticism and the end of material desire.",
        "witness": "The space cleared for Truth; awakening unfolds through letting go.",
        "verse": "Awakening unfolds through letting go.",
    },
}

# Per-house Vedantic / contemplative context.
HOUSE_SPIRITUAL: Dict[int, str] = {
    1: "The Chariot (vehicle) and the 'doer'. Body-identification (Dehatma Buddhi) is to be transcended; you are the screen, not the actor.",
    2: "Artha - resources and speech; the family ties you are born into.",
    3: "Kriyamana Karma - present action and self-effort that can re-shape destiny.",
    4: "The Hiranyagarbha (primeval seed); the Antahkarana, your inner emotional ground of peace.",
    5: "The store of Sanchita Karma carried in the causal body; intelligence and past-life merit.",
    6: "Karma Yoga - selfless service (Seva); struggle that ripens latent spiritual power.",
    7: "The 'Other' - the polar opposite of the self; the marketplace of relationship.",
    8: "Death of the ego (Atma-vichara); the Chakras and Kundalini; the immortal Self beneath crisis.",
    9: "Bhagya & Dharma - grace and accumulated merit; the higher teacher.",
    10: "The externalised fruit of action; righteous duty made visible to the world.",
    11: "Fulfilment of desires (Kama) within dharma; gains and hopes.",
    12: "Vyaya - expenditure and dissolution; Moksha, the merging of the individual back into the Absolute.",
}

# Sign reframes for the soul's journey (Aries -> Pisces).
SIGN_WISDOM: Dict[str, str] = {
    "Aries": "Aja, the unborn - the Jiva's first identification with the body (Avidya); the journey begins.",
    "Pisces": "Dissolution of Ahamkara - surrender and Bhakti into Brahman. (Venus exalted here; Mercury debilitated - analysis must stop for surrender to bloom.)",
}

JOURNEY = [
    ("Identification (Aries)", "The 'unborn' Witness begins to watch the 'born' ego identify with the body."),
    ("Struggle (mid-cycle)", "The soul wanders, caught between Mercury's scrutiny and Rahu's obsessions, refined by Saturn's delays."),
    ("Surrender (Pisces)", "The end of the road: ego dissolves, devotion blooms, and the self returns to the infinite."),
]


def witness_reading(chart) -> Dict:
    """Build a contemplative reading anchored to this chart's key points."""
    from .dasha_calc import compute_vimshottari, current_dasha

    lagna_lord = ref.SIGN_LORD[chart.lagna_sign]
    moon = chart.planets["Moon"]

    periods = compute_vimshottari(chart)
    maha, _ = current_dasha(periods)

    reflections = []
    # Lagna as the screen.
    reflections.append(
        f"Your Ascendant is {chart.lagna_sign} - the 'role' you play and the vehicle "
        f"of action. {HOUSE_SPIRITUAL[1]} Watch the actor; rest as the screen."
    )
    # Moon as the mind.
    reflections.append(
        f"Your Moon sits in {moon.sign} ({moon.nakshatra}) - the texture of your mind "
        f"and vasanas. {PLANET_WITNESS['Moon']['witness']} \u201c{PLANET_WITNESS['Moon']['verse']}\u201d"
    )
    # Current dasha as the present teacher.
    if maha:
        w = PLANET_WITNESS[maha.lord]
        reflections.append(
            f"You are in a {maha.lord} period - in the dream it brings "
            f"{w['dream'].lower()} As the Witness: {w['witness']} \u201c{w['verse']}\u201d"
        )

    return {
        "intro": INTRO,
        "closing": CLOSING,
        "reflections": reflections,
        "planets": PLANET_WITNESS,
        "journey": JOURNEY,
        "lagna_lord": lagna_lord,
    }
