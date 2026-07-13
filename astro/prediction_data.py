"""Prediction reference data — Panchang limbs at birth.

Short interpretive texts for Tithi, Nakshatra, Yoga, Karana and Vaara used
by the prediction engine. These are traditional Jyotish themes expressed in
plain language for end-user predictions.
"""

from __future__ import annotations

# Nakshatra: personality, strength, caution (27).
NAKSHATRA_PREDICTION = {
    "Ashwini": {
        "nature": "Swift, healing, pioneering",
        "prediction": "You move fast and recover quickly. New beginnings favour you; impatience is the main pitfall.",
        "career": "Medicine, healing arts, sports, entrepreneurship, emergency services.",
        "relationship": "Warm but needs space; attraction is instant, commitment needs conscious pacing.",
    },
    "Bharani": {
        "nature": "Intense, transformative, creative",
        "prediction": "You carry deep creative and transformative power. Life asks you to balance desire with discipline.",
        "career": "Arts, media, law, research, fields involving transformation or crisis management.",
        "relationship": "Passionate and loyal; jealousy or control themes may appear if trust is weak.",
    },
    "Krittika": {
        "nature": "Sharp, purifying, courageous",
        "prediction": "A cutting clarity defines you — you speak truth and cut through confusion. Guard against harshness.",
        "career": "Military, surgery, cooking, editing, leadership, audit and quality control.",
        "relationship": "Direct and protective; soften tone for harmony at home.",
    },
    "Rohini": {
        "nature": "Magnetic, artistic, nurturing",
        "prediction": "Charm and creativity are your gifts. Material comfort and beauty matter; avoid over-indulgence.",
        "career": "Fashion, agriculture, hospitality, finance, arts, luxury goods.",
        "relationship": "Romantic and affectionate; stability comes when emotions are grounded.",
    },
    "Mrigashira": {
        "nature": "Curious, searching, gentle",
        "prediction": "You are a lifelong seeker — restless mind that finds answers through exploration.",
        "career": "Writing, travel, research, sales, communication, exploration.",
        "relationship": "Needs mental stimulation; boredom is the enemy of lasting bonds.",
    },
    "Ardra": {
        "nature": "Stormy, intellectual, renewing",
        "prediction": "Emotional storms clear the way for renewal. Intellect is strong; channel intensity constructively.",
        "career": "Technology, science, psychology, disaster relief, innovation.",
        "relationship": "Deep bonds possible after weathering storms; honesty is essential.",
    },
    "Punarvasu": {
        "nature": "Optimistic, returning, wise",
        "prediction": "Second chances favour you. Optimism and wisdom grow with age; home and learning are central.",
        "career": "Teaching, counselling, publishing, architecture, philosophy.",
        "relationship": "Forgiving nature; relationships improve when you return to core values.",
    },
    "Pushya": {
        "nature": "Nourishing, spiritual, prosperous",
        "prediction": "One of the most auspicious birth stars — nourishment, faith and steady prosperity are themes.",
        "career": "Counselling, food, spirituality, government service, philanthropy.",
        "relationship": "Devoted and caring; attracts partners who value stability.",
    },
    "Ashlesha": {
        "nature": "Penetrating, mystical, intense",
        "prediction": "Deep intuition and psychological insight. Guard against manipulation — in self or others.",
        "career": "Occult sciences, psychology, politics, research, pharmaceuticals.",
        "relationship": "Magnetic but complex; transparency builds trust.",
    },
    "Magha": {
        "nature": "Regal, ancestral, authoritative",
        "prediction": "Strong sense of lineage and authority. Leadership comes naturally; humility opens doors.",
        "career": "Government, history, management, heritage, performing arts.",
        "relationship": "Expects respect; thrives with a partner who honours tradition.",
    },
    "Purva Phalguni": {
        "nature": "Creative, relaxed, generous",
        "prediction": "Creativity and relaxation are your themes — you create best when at ease.",
        "career": "Entertainment, marriage counselling, luxury, event management.",
        "relationship": "Romantic and generous; watch laziness in long-term duties.",
    },
    "Uttara Phalguni": {
        "nature": "Helpful, contractual, balanced",
        "prediction": "Partnerships and contracts shape your destiny. Reliability is your superpower.",
        "career": "HR, law, social work, administration, partnership business.",
        "relationship": "Marriage and formal commitments are strongly highlighted.",
    },
    "Hasta": {
        "nature": "Skilled, witty, crafty",
        "prediction": "Hands and mind work together — dexterity and wit open many paths.",
        "career": "Crafts, astrology, comedy, surgery, software, handicrafts.",
        "relationship": "Charming communicator; needs honesty to avoid games.",
    },
    "Chitra": {
        "nature": "Brilliant, aesthetic, builder",
        "prediction": "You build beautiful structures — literal or metaphorical. Pride in work is justified.",
        "career": "Architecture, design, engineering, fashion, advertising.",
        "relationship": "Attracted to beauty and intelligence; vanity can be a blind spot.",
    },
    "Swati": {
        "nature": "Independent, diplomatic, flexible",
        "prediction": "Independence and adaptability define you. Business and trade favour your flexible nature.",
        "career": "Business, diplomacy, aviation, trade, independent consulting.",
        "relationship": "Needs freedom within commitment; suffocation ends bonds quickly.",
    },
    "Vishakha": {
        "nature": "Goal-oriented, dual-natured, determined",
        "prediction": "Single-pointed ambition after initial wandering. Festivals and goals mark your path.",
        "career": "Politics, goals-driven sales, sports, competitive fields.",
        "relationship": "All-or-nothing energy; choose partners who share your ambitions.",
    },
    "Anuradha": {
        "nature": "Devoted, friendly, traveller",
        "prediction": "Friendship and devotion carry you far. Foreign connections and groups favour you.",
        "career": "Organisation work, travel, occult, team leadership abroad.",
        "relationship": "Deep loyalty; friendships often become lifelong bonds.",
    },
    "Jyeshtha": {
        "nature": "Senior, protective, occult",
        "prediction": "Natural elder energy — protection and responsibility come early in life.",
        "career": "Management, occult, military, senior advisory roles.",
        "relationship": "Protective; may attract younger or dependent partners.",
    },
    "Mula": {
        "nature": "Root-seeking, investigative, uprooting",
        "prediction": "You dig to the root of everything. Destruction of the false precedes rebuilding.",
        "career": "Research, investigation, spirituality, mining, root-cause analysis.",
        "relationship": "Transformative bonds; old patterns must be uprooted for happiness.",
    },
    "Purva Ashadha": {
        "nature": "Invincible, philosophical, watery",
        "prediction": "Conviction and philosophy guide you. 'Cannot lose' attitude — ensure it stays humble.",
        "career": "Law, philosophy, water-related fields, advocacy.",
        "relationship": "Idealistic in love; reality checks help long-term harmony.",
    },
    "Uttara Ashadha": {
        "nature": "Victorious, enduring, lawful",
        "prediction": "Victory through patience and dharma. Long-term success is your pattern.",
        "career": "Government, law, long-term projects, judiciary.",
        "relationship": "Late but lasting commitments; values duty alongside love.",
    },
    "Shravana": {
        "nature": "Listening, learning, connecting",
        "prediction": "You learn by listening and connect people and ideas. Education is lifelong.",
        "career": "Media, teaching, counselling, translation, audio/tech.",
        "relationship": "Communication is the foundation; silence breeds misunderstanding.",
    },
    "Dhanishta": {
        "nature": "Wealthy, rhythmic, group-oriented",
        "prediction": "Rhythm, wealth and fame are possible. Music and groups amplify your gifts.",
        "career": "Music, finance, real estate, event management, drums/rhythm arts.",
        "relationship": "Social and fun-loving; needs a partner who shares celebrations.",
    },
    "Shatabhisha": {
        "nature": "Healing, secretive, scientific",
        "prediction": "Healing and science merge in you. Solitude recharges; secrets must be handled ethically.",
        "career": "Medicine, astrology, astronomy, research, alternative healing.",
        "relationship": "Private nature; trust is built slowly but deeply.",
    },
    "Purva Bhadrapada": {
        "nature": "Intense, fiery, transformative",
        "prediction": "Fire and transformation — spiritual intensity runs through your life script.",
        "career": "Occult, funeral services, metallurgy, radical reform.",
        "relationship": "Intense bonds; spiritual compatibility matters more than surface charm.",
    },
    "Uttara Bhadrapada": {
        "nature": "Wise, stable, deep",
        "prediction": "Depth and wisdom mature over time. Serpent energy — kundalini and depth psychology.",
        "career": "Counselling, charity, marine fields, meditation teaching.",
        "relationship": "Stable and deep; attracts partners seeking inner peace.",
    },
    "Revati": {
        "nature": "Compassionate, nourishing, completing",
        "prediction": "Compassion and safe passage — you guide others through endings and new starts.",
        "career": "Travel, imports, animal care, hospice, spiritual guidance.",
        "relationship": "Gentle and nurturing; may sacrifice self — learn healthy boundaries.",
    },
}

# Tithi themes (1-15; Krishna uses same names with darker tone).
TITHI_PREDICTION = {
    1: "New beginnings and fresh initiative. Good for starts; finish what you begin.",
    2: "Cooperation and partnership energy. Relationships and shared resources matter.",
    3: "Courage and communication. Siblings, short journeys and self-effort are highlighted.",
    4: "Home, mother and emotional roots. Property and inner peace are life themes.",
    5: "Creativity, children and intelligence. Past merit (Purva Punya) supports you.",
    6: "Service, health and overcoming obstacles. Enemies become teachers.",
    7: "Partnership and marriage are central life themes. The 'other' mirrors the self.",
    8: "Transformation, research and hidden matters. Sudden changes bring growth.",
    9: "Fortune, father and dharma. Higher learning and grace protect you.",
    10: "Career, status and public life. Actions become visible to the world.",
    11: "Gains, income and social networks. Hopes materialise with sustained effort.",
    12: "Spirituality, foreign lands and letting go. Liberation themes grow with age.",
    13: "Intensity before completion. Clear old karma; avoid starting major new ventures.",
    14: "Penultimate energy — refine and prepare. Detachment from outcomes helps.",
    15: "Completion and culmination. Full moon brings clarity; new moon brings introspection.",
}

YOGA_PREDICTION = {
    "Vishkumbha": "Initial obstacles melt with patience — slow starts, strong finishes.",
    "Preeti": "Love and affection flow easily; relationships are a life blessing.",
    "Ayushman": "Longevity and vitality are supported; health improves with routine.",
    "Saubhagya": "Good fortune and luck follow sincere effort.",
    "Shobhana": "Beauty, charm and refinement attract opportunities.",
    "Atiganda": "Excess and obstacles — moderation is the key lesson.",
    "Sukarma": "Righteous action brings rewards; karma yoga suits you.",
    "Dhriti": "Determination and steadiness win over time.",
    "Shoola": "Sharp challenges in early life forge resilience.",
    "Ganda": "Confusion clears when you simplify and seek guidance.",
    "Vriddhi": "Growth and expansion are natural themes.",
    "Dhruva": "Stability and permanence — what you build lasts.",
    "Vyaghata": "Sudden blocks teach flexibility and faith.",
    "Harshana": "Joy and optimism lift you and others.",
    "Vajra": "Diamond-like strength; intensity must be channelled wisely.",
    "Siddhi": "Accomplishment and mastery are within reach.",
    "Vyatipata": "Reversals bring unexpected blessings when ego is set aside.",
    "Variyan": "Comfort and luxury are possible; avoid complacency.",
    "Parigha": "Obstacles at gates — persistence opens doors.",
    "Shiva": "Spiritual grace and auspiciousness protect the path.",
    "Siddha": "Perfection and skill develop through dedicated practice.",
    "Sadhya": "Achievable goals — what you aim for with dharma, you attain.",
    "Shubha": "Auspiciousness marks your undertakings.",
    "Shukla": "Purity and clarity of purpose guide decisions.",
    "Brahma": "Creative and divine energy supports new ventures.",
    "Indra": "Leadership and authority come with responsibility.",
    "Vaidhriti": "Instability requires anchoring in spiritual practice.",
}

VAARA_PREDICTION = {
    "Ravivara": "Solar energy — leadership, vitality and father themes are strong.",
    "Somavara": "Lunar energy — mind, mother and emotions shape your temperament.",
    "Mangalavara": "Martian energy — courage, energy and occasional impulsiveness.",
    "Budhavara": "Mercurial energy — intellect, business sense and adaptability.",
    "Guruvara": "Jupiterian energy — wisdom, optimism and good counsel.",
    "Shukravara": "Venusian energy — love of beauty, comfort and harmony.",
    "Shanivara": "Saturnine energy — discipline, patience and karmic lessons.",
}

KARANA_PREDICTION = {
    "Kimstughna": "Unique karmic signature — spiritual purpose is distinctive.",
    "Bava": "Auspicious for beginnings and creative work.",
    "Balava": "Strength in power and authority; leadership suits you.",
    "Kaulava": "Family and lineage themes; ancestral blessings matter.",
    "Taitila": "Wealth through trade and skilled negotiation.",
    "Gara": "Hard work and agriculture/building bring steady results.",
    "Vanija": "Commerce and business acumen are highlighted.",
    "Vishti": "Bhadravajra — caution in new ventures; introspection helps.",
    "Shakuni": "Intuition and unconventional paths; watch illusions.",
    "Chatushpada": "Stability through four-legged support — property and animals.",
    "Naga": "Mystical depth; kundalini and hidden knowledge.",
}

# Life-area prediction templates keyed by verdict.
VERDICT_PREDICTION = {
    "Supported": "Strongly favourable — this area tends to support you naturally.",
    "Mixed": "Mixed influences — your choices and timing decide the outcome.",
    "Challenged": "Requires conscious effort — patience and remedies help most here.",
}

LIFE_AREAS = [
    ("Personality & self", 1, "Who you are at core"),
    ("Wealth & income", 2, "Money, speech and family resources"),
    ("Career & status", 10, "Work, reputation and public life"),
    ("Marriage & love", 7, "Partnership and relationships"),
    ("Health & vitality", 6, "Health, service and daily discipline"),
    ("Spiritual path", 9, "Dharma, grace and higher purpose"),
]
