"""Planetary combinations reference — Bhava Phala (planet-in-house) and the
classical two-planet conjunctions (yogas), with significance, merits and
demerits, plus a detector for what actually occurs in a given chart.

This is a teaching/reference layer built on classical Parashari and Tajika
significations. Real-life results are modulated by sign, dignity, aspects and
Dasha — so treat the general notes as tendencies, not verdicts.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from . import reference as ref
from .chart_engine import Chart
from .strength_calc import all_strengths
from .aspects import aspects_on_planet

# Short theme for each of the 27 nakshatras (its flavour).
NAKSHATRA_TRAIT: Dict[str, str] = {
    "Ashwini": "healing, speed and fresh starts",
    "Bharani": "endurance, creativity and transformation",
    "Krittika": "sharpness, purification and leadership",
    "Rohini": "growth, beauty and material comfort",
    "Mrigashira": "curiosity, searching and gentleness",
    "Ardra": "storms, breakthroughs and intensity",
    "Punarvasu": "renewal, optimism and homecoming",
    "Pushya": "nourishment, care and stability",
    "Ashlesha": "intuition, cunning and mysticism",
    "Magha": "authority, ancestry and tradition",
    "Purva Phalguni": "pleasure, creativity and ease",
    "Uttara Phalguni": "service, integrity and partnership",
    "Hasta": "skill, dexterity and cleverness",
    "Chitra": "craft, brilliance and design",
    "Swati": "independence, adaptability and trade",
    "Vishakha": "ambition, focus and achievement",
    "Anuradha": "friendship, devotion and discipline",
    "Jyeshtha": "seniority, protection and courage",
    "Mula": "roots, investigation and upheaval",
    "Purva Ashadha": "invincibility, pride and persuasion",
    "Uttara Ashadha": "victory, ethics and endurance",
    "Shravana": "listening, learning and connection",
    "Dhanishta": "rhythm, wealth and ambition",
    "Shatabhisha": "healing, secrecy and innovation",
    "Purva Bhadrapada": "idealism, intensity and transformation",
    "Uttara Bhadrapada": "depth, wisdom and endurance",
    "Revati": "compassion, completion and nourishment",
}

PLANET_KEYWORD = {
    "Sun": "authority & vitality", "Moon": "emotions & the mind",
    "Mars": "drive & courage", "Mercury": "intellect & communication",
    "Jupiter": "wisdom & fortune", "Venus": "love & artistry",
    "Saturn": "discipline & endurance", "Rahu": "ambition & the unconventional",
    "Ketu": "detachment & spirituality",
}

_KENDRA_TRIKONA = {1, 4, 5, 7, 9, 10}
_UPACHAYA = {11}
_DUSTHANA = {6, 8, 12}


def _ordinal(n: int) -> str:
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(n, f"{n}th")

# ---------------------------------------------------------------------------
# Planet-in-house (Bhava Phala) — significance / merits / demerits
# ---------------------------------------------------------------------------
# Each entry: {"effect": ..., "merits": ..., "demerits": ...}
PLANET_IN_HOUSE: Dict[str, Dict[int, Dict[str, str]]] = {
    "Sun": {
        1: {"effect": "A strong, authoritative personality with leadership and vitality.",
            "merits": "Confidence, health, ambition, recognition, willpower.",
            "demerits": "Pride, ego clashes, domineering nature, eye/hair issues."},
        2: {"effect": "Wealth and status through authority; forceful, commanding speech.",
            "merits": "Income via position, family pride, self-made resources.",
            "demerits": "Harsh speech, strained family, eye or dental trouble."},
        3: {"effect": "Courage and initiative; influential (or competitive) siblings.",
            "merits": "Bravery, drive, authoritative communication, self-effort.",
            "demerits": "Dominating siblings, restlessness, ego in expression."},
        4: {"effect": "Gains of property/status but a restless home and strained mother tie.",
            "merits": "Property, vehicles, education, public standing.",
            "demerits": "Domestic tension, mother's health, inner discontent."},
        5: {"effect": "Bright intellect and authority in creativity; some strain with children.",
            "merits": "Leadership in learning, speculation gains, sharp intellect.",
            "demerits": "Ego with children, few progeny, pride in knowledge."},
        6: {"effect": "Defeats enemies and excels in service and competition.",
            "merits": "Wins disputes, disciplined work, good recovery from illness.",
            "demerits": "Conflicts with authority, stomach/heat ailments."},
        7: {"effect": "Dominant in partnerships; ego expressed through marriage/business.",
            "merits": "Influential spouse and partners, business authority.",
            "demerits": "Marital friction, delayed or dominated marriage."},
        8: {"effect": "Interest in the occult and research; concerns over longevity/inheritance.",
            "merits": "Research ability, resilience, sudden authority.",
            "demerits": "Health scares, father-related issues, ups and downs."},
        9: {"effect": "Fortunate and dharmic, respected, good relations with father.",
            "merits": "Luck, higher status, spirituality, father's blessings.",
            "demerits": "Dogmatism, pride in one's beliefs."},
        10: {"effect": "Outstanding for career, fame and authority; government success.",
             "merits": "High position, reputation, leadership, achievement.",
             "demerits": "Workaholism, ego at work, pressure of expectations."},
        11: {"effect": "Strong gains, a powerful network and fulfilled ambitions.",
             "merits": "Income via authority, influential friends, achievement of goals.",
             "demerits": "Ego in groups, friction with elder sibling."},
        12: {"effect": "Expenses tied to authority; foreign/spiritual pursuits, low visibility.",
             "merits": "Spiritual growth, foreign links, charity.",
             "demerits": "Hidden enemies, weak eyesight, isolation, father distance."},
    },
    "Moon": {
        1: {"effect": "Emotional, sensitive and charming with strong public appeal.",
            "merits": "Empathy, adaptability, likeability, imagination.",
            "demerits": "Mood swings, dependence, indecision."},
        2: {"effect": "Fluctuating wealth, sweet speech and a family-centred life.",
            "merits": "Savings instinct, pleasant speech, family support.",
            "demerits": "Variable income, emotional eating."},
        3: {"effect": "Emotionally courageous, creative communication, supportive siblings.",
            "merits": "Boldness, expressiveness, good bond with sisters.",
            "demerits": "Restlessness, emotional impulsiveness."},
        4: {"effect": "Excellent — a happy home, mother's love, property and contentment.",
            "merits": "Emotional security, property, vehicles, education.",
            "demerits": "Over-attachment, homesickness, clinginess."},
        5: {"effect": "Creative and romantic with loving children and a good memory.",
            "merits": "Intelligence, progeny, artistry, devotion.",
            "demerits": "Emotional in love; moods affect studies."},
        6: {"effect": "Emotional stress and health sensitivity; caring toward others.",
            "merits": "Compassion in service, quick recovery.",
            "demerits": "Anxiety, digestive/chest issues, worry."},
        7: {"effect": "Attractive and caring; emotionally needs partnership.",
            "merits": "Loving marriage, public popularity, business flair.",
            "demerits": "Emotional dependence on spouse, fluctuating relations."},
        8: {"effect": "Emotional turbulence and fascination with mysteries; health varies.",
            "merits": "Intuition, research ability, capacity to transform.",
            "demerits": "Anxiety, chronic worry, instability."},
        9: {"effect": "Fortunate and devotional; loves travel and learning.",
            "merits": "Luck, faith, good bond with parents.",
            "demerits": "Restlessness, a wandering mind."},
        10: {"effect": "A public-facing career with popularity and caring leadership.",
             "merits": "Fame, people-oriented work, success.",
             "demerits": "Emotional ups and downs in career, frequent change."},
        11: {"effect": "Good gains, a wide social circle and fulfilled desires.",
             "merits": "Income, many friends, popularity.",
             "demerits": "Fickle friendships, over-desiring."},
        12: {"effect": "Spiritual and imaginative; foreign residence, emotional withdrawal.",
             "merits": "Meditation, charity, foreign gains, imagination.",
             "demerits": "Loneliness, sleep/mental unrest, expenses."},
    },
    "Mars": {
        1: {"effect": "Energetic, bold and athletic, with a forceful presence (Manglik).",
            "merits": "Courage, leadership, stamina, drive.",
            "demerits": "Anger, accidents, impulsiveness, marital strain (Manglik)."},
        2: {"effect": "Wealth via land/energy but harsh speech and family friction.",
            "merits": "Assertive earning, property, drive.",
            "demerits": "Rude speech, family disputes, dental issues."},
        3: {"effect": "Very courageous and competitive with strong initiative.",
            "merits": "Bravery, enterprise, aptitude for sports.",
            "demerits": "Rashness, quarrels with siblings."},
        4: {"effect": "Property and land gains but tension at home (Manglik).",
            "merits": "Real estate, vehicles, energetic drive.",
            "demerits": "Domestic conflict, mother's health, anger at home."},
        5: {"effect": "Sharp, strategic intellect and competitiveness; strain with children.",
            "merits": "Strategic mind, speculation, courage.",
            "demerits": "Temper, risk to progeny, ego with children."},
        6: {"effect": "Excellent — crushes enemies; ideal for competition, defence, surgery.",
            "merits": "Wins disputes, courage, strong recovery.",
            "demerits": "Injuries, inflammation, frequent conflicts."},
        7: {"effect": "Manglik — dominant, aggressive energy in marriage and business.",
            "merits": "Energetic partner, business drive.",
            "demerits": "Marital discord, quarrels, delays."},
        8: {"effect": "Risk of accidents/surgery and longevity concerns; occult drive.",
            "merits": "Research, resilience, occasional sudden gains.",
            "demerits": "Injuries, chronic issues, inheritance disputes."},
        9: {"effect": "Energetic in dharma but clashes over father/beliefs.",
            "merits": "Bold fortune, leadership, love of travel.",
            "demerits": "Argumentativeness, dogmatism, friction with father."},
        10: {"effect": "Great for career — engineering, defence, leadership and action.",
             "merits": "Professional success, authority, decisive drive.",
             "demerits": "Workplace conflict, overwork, burnout."},
        11: {"effect": "Strong gains through effort and bold ambition.",
             "merits": "Income via enterprise, courageous allies.",
             "demerits": "Aggressive ambition, disputes in groups."},
        12: {"effect": "Hidden anger and expenses; foreign or covert action, secret enemies.",
             "merits": "Covert strength, foreign/defence gains.",
             "demerits": "Injuries, losses, sleep issues, isolation."},
    },
    "Mercury": {
        1: {"effect": "Intelligent, witty, communicative and youthful.",
            "merits": "Intellect, speech, business acumen, adaptability.",
            "demerits": "Nervousness, overthinking, skin sensitivity."},
        2: {"effect": "Wealth through communication and trade; clever speech.",
            "merits": "Earning via skill, eloquence, numeracy.",
            "demerits": "Calculative or nervous speech."},
        3: {"effect": "Excellent communicator and writer with a courageous intellect.",
            "merits": "Writing, media, skills, good with siblings.",
            "demerits": "Restlessness, tendency to gossip."},
        4: {"effect": "Educated with a happy home; property gained through intellect.",
            "merits": "Education, vehicles, mother bond, comfort.",
            "demerits": "Overthinking at home, nervousness."},
        5: {"effect": "Brilliant intellect, good with children, skill in speculation.",
            "merits": "Learning, creativity, mantra, progeny.",
            "demerits": "Over-analysis, nervous energy."},
        6: {"effect": "Sharp in analysis and service; wins by wit but nervous health.",
            "merits": "Problem-solving, service, debating skill.",
            "demerits": "Anxiety, nerves, skin/intestinal issues."},
        7: {"effect": "Business partnerships and a youthful, clever spouse.",
            "merits": "Business success, communication in marriage.",
            "demerits": "Calculative relations, immaturity."},
        8: {"effect": "Investigative, research-oriented mind drawn to the occult.",
            "merits": "Research, hidden knowledge, analytical depth.",
            "demerits": "Anxiety, secretiveness, nervous disorders."},
        9: {"effect": "Learned and philosophical; a natural teacher or writer.",
            "merits": "Higher learning, publishing, luck via intellect.",
            "demerits": "Over-rationalising matters of faith."},
        10: {"effect": "Career in communication, business, trade or writing.",
             "merits": "Professional success via skill, versatility.",
             "demerits": "Restlessness, frequent job changes."},
        11: {"effect": "Gains via trade and communication; intellectual friends.",
             "merits": "Income through skill, strong networking.",
             "demerits": "Calculative friendships."},
        12: {"effect": "Imaginative with foreign trade links but a scattered mind.",
             "merits": "Research, foreign gains, spirituality.",
             "demerits": "Nervousness, indecision, losses via miscommunication."},
    },
    "Jupiter": {
        1: {"effect": "Wise, optimistic and respected, with good health and fortune.",
            "merits": "Wisdom, morality, luck, growth, good nature.",
            "demerits": "Over-optimism, weight gain, complacency."},
        2: {"effect": "Wealthy and generous with good family values and speech.",
            "merits": "Wealth, savings, family harmony, eloquence.",
            "demerits": "Overindulgence, weight gain."},
        3: {"effect": "Ethical in effort (Jupiter is mild here); supportive siblings.",
            "merits": "Principled communication, good siblings.",
            "demerits": "Over-caution, reduced initiative."},
        4: {"effect": "Excellent — a happy home, property, education and mother's blessings.",
            "merits": "Comfort, land, learning, contentment.",
            "demerits": "Complacency, overindulgence."},
        5: {"effect": "Superb — intelligence, virtuous children, wisdom and mantra.",
            "merits": "Progeny, learning, teaching, good fortune.",
            "demerits": "Preachiness, over-idealism with children."},
        6: {"effect": "Wins over enemies ethically (Jupiter mild in a dusthana).",
            "merits": "Victory via wisdom, service, sound health advice.",
            "demerits": "Debts if weak, liver issues."},
        7: {"effect": "Excellent — a virtuous spouse and a harmonious marriage.",
            "merits": "Happy marriage, wise partner, ethical business.",
            "demerits": "Over-idealising the spouse."},
        8: {"effect": "Drawn to philosophy and the occult; matters of longevity/legacy.",
            "merits": "Research into dharma, resilience, inheritance/insurance.",
            "demerits": "Obstacles to gains, liver concerns."},
        9: {"effect": "Best placement — highly fortunate, dharmic, guru-like, respected.",
            "merits": "Great luck, wisdom, spirituality, father's grace.",
            "demerits": "Dogmatism, over-preaching."},
        10: {"effect": "An ethical career in teaching, law or advisory roles; fame.",
             "merits": "Reputation, leadership, righteous success.",
             "demerits": "Complacency if over-confident."},
        11: {"effect": "Excellent gains, wise mentors and fulfilled hopes.",
             "merits": "Strong income, good network, elder sibling support.",
             "demerits": "Over-optimistic expansion."},
        12: {"effect": "Spiritual, charitable and moksha-oriented with foreign luck.",
             "merits": "Liberation, wisdom, charity, foreign gains.",
             "demerits": "Over-spending on causes, detachment from worldly duty."},
    },
    "Venus": {
        1: {"effect": "Charming, attractive and artistic, seeking comfort and harmony.",
            "merits": "Beauty, charm, relationships, refinement.",
            "demerits": "Vanity, indulgence, laziness."},
        2: {"effect": "Wealth via arts/luxury with sweet speech and family harmony.",
            "merits": "Wealth, pleasant speech, family comfort.",
            "demerits": "Overspending on luxury, indulgence."},
        3: {"effect": "Artistic communication and pleasant siblings; mild courage.",
            "merits": "Arts, media, diplomacy.",
            "demerits": "Comfort preferred over effort."},
        4: {"effect": "Excellent — a luxurious home, vehicles, mother's love and comfort.",
            "merits": "Property, conveyances, happiness, art at home.",
            "demerits": "Over-attachment to comfort."},
        5: {"effect": "Romantic and creative with artistic children and love affairs.",
            "merits": "Creativity, romance, progeny, the arts.",
            "demerits": "Over-indulgence in romance, distraction."},
        6: {"effect": "Relationship/health strain via indulgence; charm used in service.",
            "merits": "Charm in service, skill at reconciliation.",
            "demerits": "Relationship trouble, kidney/diabetic risk, debts via luxury."},
        7: {"effect": "Excellent — an attractive, loving spouse and a harmonious marriage.",
            "merits": "Happy marriage, good partnerships, luxury.",
            "demerits": "Over-dependence on partner, indulgence."},
        8: {"effect": "Hidden relationships and sudden gains via spouse; sensual nature.",
            "merits": "Inheritance via partner, transformation through love.",
            "demerits": "Secret affairs, reproductive/urinary issues."},
        9: {"effect": "Fortunate and refined; loves travel, beauty and higher arts.",
            "merits": "Luck, refinement, higher arts, fortunate spouse.",
            "demerits": "Indulgence in pleasures over duty."},
        10: {"effect": "Career in arts, luxury, beauty, entertainment or diplomacy.",
             "merits": "Fame via art, a pleasant profession, success.",
             "demerits": "Comfort-seeking, image over substance."},
        11: {"effect": "Gains via arts/luxury with charming friends and fulfilled desires.",
             "merits": "Income, rich social life, romance fulfilled.",
             "demerits": "Overspending, indulgent company."},
        12: {"effect": "Pleasures, foreign romance and luxury spending; leanings to moksha.",
             "merits": "Comfort, foreign links, artistic solitude, spiritual love.",
             "demerits": "Hidden affairs, overspending, indulgence."},
    },
    "Saturn": {
        1: {"effect": "Serious and disciplined, with early responsibility and delayed success.",
            "merits": "Discipline, endurance, maturity, longevity.",
            "demerits": "Pessimism, delays, joint/health issues, cold manner."},
        2: {"effect": "Slow-built, frugal wealth with measured speech and family duty.",
            "merits": "Savings via discipline, wealth later in life.",
            "demerits": "Early financial struggle, slow speech, family burdens."},
        3: {"effect": "Excellent — disciplined, persistent effort that pays over time.",
            "merits": "Perseverance, durable skills, resilience.",
            "demerits": "Pessimism, early strain with siblings."},
        4: {"effect": "Hardships at home and with mother; property comes later.",
            "merits": "Property after struggle, a disciplined foundation.",
            "demerits": "Unhappy home, mother's health, emotional coldness."},
        5: {"effect": "Delays or issues with children; a disciplined, deep intellect.",
            "merits": "Deep thinking, methodical learning, responsible children later.",
            "demerits": "Progeny delays, pessimism in creativity."},
        6: {"effect": "Excellent — defeats enemies by patience; great for service and endurance.",
            "merits": "Wins over rivals via patience, disciplined work, health mgmt.",
            "demerits": "Chronic ailments, heavy workload."},
        7: {"effect": "A delayed but stable marriage, often to a mature/older partner.",
            "merits": "Loyal, lasting marriage, disciplined partnership, business.",
            "demerits": "Marital delays, coldness, emotional distance."},
        8: {"effect": "Grants longevity and interest in the occult; slow inheritance.",
            "merits": "Long life, research, resilience, endurance.",
            "demerits": "Chronic illness, delays, obstacles."},
        9: {"effect": "Traditional and disciplined in dharma; some hardship via father.",
            "merits": "Deep philosophy, disciplined faith, fortune later.",
            "demerits": "Delays in luck, father issues, rigidity."},
        10: {"effect": "Excellent for career via hard work — authority earned slowly.",
             "merits": "High position after effort, discipline, lasting career.",
             "demerits": "Slow rise, burdens, obstacles from superiors."},
        11: {"effect": "Excellent — steady, large gains over time and a disciplined network.",
             "merits": "Reliable income, elder sibling support, goals met later.",
             "demerits": "Delayed gains, few but solid friends."},
        12: {"effect": "Spiritual discipline, foreign residence, expenses and solitude.",
             "merits": "Moksha via discipline, foreign settlement, detachment.",
             "demerits": "Losses, loneliness, sleep issues, hidden enemies."},
    },
    "Rahu": {
        1: {"effect": "Ambitious, unconventional and magnetic, with a restless identity.",
            "merits": "Worldly ambition, innovation, foreign appeal.",
            "demerits": "Confusion, illusion, anxiety, a deceptive self-image."},
        2: {"effect": "Unusual or foreign wealth; blunt, sometimes manipulative speech.",
            "merits": "Sudden wealth, foreign earning.",
            "demerits": "Dishonest speech, family discord, food issues."},
        3: {"effect": "Bold, ambitious and courageous, with media/tech aptitude.",
            "merits": "Daring, communication, foreign connections.",
            "demerits": "Recklessness, manipulation."},
        4: {"effect": "Home unrest and foreign property; an unconventional mother bond.",
            "merits": "Foreign property, unconventional gains.",
            "demerits": "Domestic discontent, mother's health, restlessness."},
        5: {"effect": "Unconventional intellect and speculation; issues with children.",
            "merits": "Innovative mind, sudden gains, mantra power.",
            "demerits": "Progeny issues, gambling, scattered focus."},
        6: {"effect": "Excellent — defeats enemies; great for competition and foreign service.",
            "merits": "Crushes rivals, foreign jobs, litigation wins.",
            "demerits": "Mysterious ailments, risk of addictions."},
        7: {"effect": "An unusual or foreign spouse and intense partnerships; illusions in love.",
            "merits": "Foreign/unconventional marriage, business abroad.",
            "demerits": "Deception in relations, discord."},
        8: {"effect": "Occult interest, sudden events and research; longevity fluctuates.",
            "merits": "Research, occult mastery, sudden gains, inheritance.",
            "demerits": "Accidents, obscure ailments, scandals."},
        9: {"effect": "Unconventional beliefs and foreign dharma/travel; distance from father.",
            "merits": "Foreign luck, innovative philosophy, travel.",
            "demerits": "Unorthodox faith, friction with father."},
        10: {"effect": "Large worldly ambition — foreign/tech/political career and fame.",
             "merits": "High rise, foreign career, innovation, power.",
             "demerits": "Unethical shortcuts, risk of sudden falls."},
        11: {"effect": "Excellent — large, sudden gains and a powerful/foreign network.",
             "merits": "Big income, influential/foreign friends, desires fulfilled.",
             "demerits": "Insatiable desire, dubious company."},
        12: {"effect": "Foreign residence, occult/spiritual pursuits and heavy expenses.",
             "merits": "Foreign settlement, moksha via unconventional paths, research.",
             "demerits": "Losses, hidden enemies, phobias, isolation."},
    },
    "Ketu": {
        1: {"effect": "A detached, spiritual identity with intuitive/healing gifts.",
            "merits": "Spirituality, intuition, detachment, wisdom.",
            "demerits": "Identity confusion, low confidence, obscure health issues."},
        2: {"effect": "Detachment from wealth and family; spiritually inclined speech.",
            "merits": "Non-materialism, mantra, spiritual values.",
            "demerits": "Financial instability, curt speech, food issues."},
        3: {"effect": "Detached courage and intuitive communication; spiritual siblings.",
            "merits": "Intuition, occult skill, fearlessness.",
            "demerits": "Low drive, distance from siblings."},
        4: {"effect": "Detachment from home/property; a spiritual bond with mother.",
            "merits": "Inner peace, spiritual home, moksha leanings.",
            "demerits": "Domestic discontent, property loss, mother's health."},
        5: {"effect": "A spiritual intellect with mantra siddhi; some issues with children.",
            "merits": "Mantra/occult mastery, sharp intuition.",
            "demerits": "Difficulty with progeny, scattered studies."},
        6: {"effect": "Excellent — defeats enemies effortlessly; healing and service gifts.",
            "merits": "Crushes rivals, medical/healing talent, wins disputes.",
            "demerits": "Mysterious ailments, isolation at work."},
        7: {"effect": "A detached marriage and spiritual partner; risk of dissatisfaction.",
            "merits": "Spiritual partnership, non-possessive love.",
            "demerits": "Marital detachment, discord, delays."},
        8: {"effect": "Strong occult and research ability with sudden transformations.",
            "merits": "Occult mastery, deep research, moksha.",
            "demerits": "Accidents, chronic mysteries, sudden loss."},
        9: {"effect": "Spiritual dharma and past-life merit; detachment from dogma.",
            "merits": "Intuition, moksha, spiritual fortune.",
            "demerits": "Unorthodox faith, father distance, wandering."},
        10: {"effect": "A detached career, often spiritual/healing; sudden shifts.",
             "merits": "Intuitive work, healing/tech niche, freedom from status.",
             "demerits": "Career instability, low ambition."},
        11: {"effect": "Gains that come and then detach; a spiritual network.",
             "merits": "Effortless niche gains, spiritual friends.",
             "demerits": "Unstable income, few friends, dissatisfaction."},
        12: {"effect": "Best for moksha — liberation and foreign/spiritual seclusion.",
             "merits": "Enlightenment, deep meditation, foreign spiritual life.",
             "demerits": "Losses, isolation, escapism, sleep/eye issues."},
    },
}

# ---------------------------------------------------------------------------
# Two-planet conjunctions (yogas) — keyed by a sorted planet pair.
# ---------------------------------------------------------------------------
CONJUNCTIONS: Dict[Tuple[str, str], Dict[str, str]] = {
    ("Moon", "Sun"): {"name": "Amavasya (New-Moon) combination",
        "significance": "The luminaries together — strong will but inner-outer tension.",
        "merits": "Self-reliance, strong willpower, single-minded focus.",
        "demerits": "Ego-vs-emotion conflict, mother/father tension, mood swings."},
    ("Mercury", "Sun"): {"name": "Budha-Aditya Yoga",
        "significance": "Intellect allied with authority — a classic yoga of intelligence.",
        "merits": "Sharp intellect, eloquence, success in administration/analysis.",
        "demerits": "Ego in intellect; if Mercury is combust, nervousness/overthinking."},
    ("Sun", "Venus"): {"name": "Sun-Venus",
        "significance": "Authority with artistry and charm (Venus often combust here).",
        "merits": "Creativity with status, refinement, diplomacy.",
        "demerits": "Relationship strain, weakened romance if Venus is combust."},
    ("Mars", "Sun"): {"name": "Sun-Mars (Agni)",
        "significance": "Two fiery planets — bold, commanding, action-driven.",
        "merits": "Courage, leadership, decisiveness, energy.",
        "demerits": "Anger, aggression, blood pressure, conflicts."},
    ("Jupiter", "Sun"): {"name": "Sun-Jupiter",
        "significance": "Authority guided by wisdom — righteous and respected.",
        "merits": "Ethical leadership, fortune, honour, guru-like nature.",
        "demerits": "Pride, dogmatism, over-confidence."},
    ("Saturn", "Sun"): {"name": "Sun-Saturn",
        "significance": "Ego vs discipline; classic father-authority tension.",
        "merits": "Disciplined leadership, endurance, responsibility.",
        "demerits": "Father conflict, frustration, delays, self-doubt."},
    ("Rahu", "Sun"): {"name": "Sun-Rahu (Grahan Yoga)",
        "significance": "Authority clouded by ambition and illusion (eclipse effect).",
        "merits": "Worldly rise, innovation, unconventional power.",
        "demerits": "Ego confusion, reputation risk, father issues."},
    ("Ketu", "Sun"): {"name": "Sun-Ketu (Grahan Yoga)",
        "significance": "Identity meets spiritual detachment (eclipse effect).",
        "merits": "Spiritual insight, research, detachment.",
        "demerits": "Low confidence, father detachment, self-doubt."},
    ("Mars", "Moon"): {"name": "Chandra-Mangal Yoga",
        "significance": "Emotion fused with drive — a noted wealth combination.",
        "merits": "Earning power, ambition, real-estate/enterprise flair.",
        "demerits": "Emotional aggression, impulsiveness."},
    ("Mercury", "Moon"): {"name": "Moon-Mercury",
        "significance": "A quick, communicative and business-minded temperament.",
        "merits": "Wit, adaptability, aptitude for trade.",
        "demerits": "Overthinking, nervousness."},
    ("Jupiter", "Moon"): {"name": "Gaja Kesari (when in kendra)",
        "significance": "Wisdom with emotional warmth — prosperity and respect.",
        "merits": "Fortune, wisdom, popularity, morality.",
        "demerits": "Over-optimism, complacency."},
    ("Moon", "Venus"): {"name": "Moon-Venus",
        "significance": "Emotion refined by beauty — charming and artistic.",
        "merits": "Beauty, artistry, warm relationships, luxury.",
        "demerits": "Over-indulgence, emotionality in love."},
    ("Moon", "Saturn"): {"name": "Vish/Punarphoo Yoga",
        "significance": "Emotional heaviness and delay — maturity born of difficulty.",
        "merits": "Emotional discipline, maturity, endurance.",
        "demerits": "Melancholy, pessimism, mother-related issues."},
    ("Moon", "Rahu"): {"name": "Moon-Rahu (Grahan/Chandal)",
        "significance": "Imagination amplified but destabilised by illusion.",
        "merits": "Creativity, intuition, foreign appeal.",
        "demerits": "Anxiety, phobias, emotional instability."},
    ("Ketu", "Moon"): {"name": "Moon-Ketu",
        "significance": "Intuitive and detached, with a moody, spiritual mind.",
        "merits": "Intuition, spirituality, imagination.",
        "demerits": "Emotional detachment, anxiety, moodiness."},
    ("Mars", "Mercury"): {"name": "Mars-Mercury",
        "significance": "Quick, sharp and technical — but a cutting tongue.",
        "merits": "Engineering/surgery/debate skill, fast thinking.",
        "demerits": "Harsh speech, argumentativeness."},
    ("Jupiter", "Mars"): {"name": "Guru-Mangal Yoga",
        "significance": "Energy guided by wisdom — the dharmic warrior.",
        "merits": "Courageous ethics, teaching plus action, prosperity.",
        "demerits": "Over-zealousness, dogmatic aggression."},
    ("Mars", "Venus"): {"name": "Mars-Venus",
        "significance": "Passion and creative energy — strong drives.",
        "merits": "Creativity, passion, dynamism, artistry.",
        "demerits": "Relationship volatility, impulsive desires."},
    ("Mars", "Saturn"): {"name": "Mars-Saturn",
        "significance": "Drive meets restriction — relentless but frustrated energy.",
        "merits": "Tireless work, mastery of labour/engineering, endurance.",
        "demerits": "Accidents, harshness, chronic frustration, injuries."},
    ("Mars", "Rahu"): {"name": "Angarak Yoga",
        "significance": "Explosive, daring and impulsive energy.",
        "merits": "Fearless enterprise, mechanical/technical daring.",
        "demerits": "Aggression, accidents, impulsive risk-taking."},
    ("Ketu", "Mars"): {"name": "Mars-Ketu",
        "significance": "Sharp, surgical energy — a spiritual warrior with a temper.",
        "merits": "Precision, occult/healing courage.",
        "demerits": "Accidents, sudden anger."},
    ("Jupiter", "Mercury"): {"name": "Mercury-Jupiter",
        "significance": "Intellect wedded to wisdom — counsel, teaching and writing.",
        "merits": "Scholarship, eloquence, ethics.",
        "demerits": "Over-analysis, indecision."},
    ("Mercury", "Venus"): {"name": "Mercury-Venus",
        "significance": "Artistic intellect and charming communication.",
        "merits": "Arts, diplomacy, business, refinement.",
        "demerits": "Over-talkative or calculative charm."},
    ("Mercury", "Saturn"): {"name": "Mercury-Saturn",
        "significance": "A methodical, precise and disciplined mind.",
        "merits": "Research, planning, mathematics, patience.",
        "demerits": "Pessimism, slow or anxious thinking."},
    ("Mercury", "Rahu"): {"name": "Mercury-Rahu",
        "significance": "Clever and unconventional — tech and foreign trade.",
        "merits": "Innovation, foreign business, technical skill.",
        "demerits": "Deception, scattered nerves."},
    ("Ketu", "Mercury"): {"name": "Mercury-Ketu",
        "significance": "Intuitive intellect — coding, mantra and the occult.",
        "merits": "Research, mantra, sharp intuition.",
        "demerits": "Nervousness, communication gaps."},
    ("Jupiter", "Venus"): {"name": "Guru-Shukra",
        "significance": "Wisdom and refinement — teachers of art and ethics.",
        "merits": "Refinement, wealth, ethics, artistry.",
        "demerits": "Over-indulgence, indecision between duty and pleasure."},
    ("Jupiter", "Saturn"): {"name": "Jupiter-Saturn",
        "significance": "Expansion meets discipline — slow, mature, steady growth.",
        "merits": "Patient wisdom, institutional success, longevity.",
        "demerits": "Tension between growth and restriction, delays."},
    ("Jupiter", "Rahu"): {"name": "Guru-Chandal Yoga",
        "significance": "An unconventional guru — big vision, questionable orthodoxy.",
        "merits": "Foreign wisdom, innovation, grand vision.",
        "demerits": "Unethical shortcuts, false gurus, dogma."},
    ("Jupiter", "Ketu"): {"name": "Jupiter-Ketu",
        "significance": "Detached wisdom — spiritual and moksha-oriented.",
        "merits": "Spiritual depth, non-attachment, intuition.",
        "demerits": "Withdrawal from worldly duty, indecision."},
    ("Saturn", "Venus"): {"name": "Venus-Saturn",
        "significance": "Love and art under discipline — mature, lasting bonds.",
        "merits": "Loyal love, structured artistry, durable marriage.",
        "demerits": "Coldness in love, delays, reticence."},
    ("Rahu", "Venus"): {"name": "Venus-Rahu",
        "significance": "Intense desires — unconventional/foreign love and glamour.",
        "merits": "Artistic fame, foreign romance, luxury.",
        "demerits": "Excess, scandals, addictions."},
    ("Ketu", "Venus"): {"name": "Venus-Ketu",
        "significance": "Detached love and spiritual art; romance feels unfulfilling.",
        "merits": "Spiritual love, artistic intuition.",
        "demerits": "Relationship detachment, dissatisfaction."},
    ("Rahu", "Saturn"): {"name": "Saturn-Rahu",
        "significance": "Cold ambition — foreign/industrial power with anxiety.",
        "merits": "Relentless worldly rise, mass/technical work.",
        "demerits": "Anxiety, isolation, ruthless drive."},
    ("Ketu", "Saturn"): {"name": "Saturn-Ketu",
        "significance": "Deep detachment and discipline — renunciation and solitude.",
        "merits": "Renunciation, deep research, moksha.",
        "demerits": "Depression, isolation, chronic issues."},
}


# ---------------------------------------------------------------------------
# Three-planet combinations (curated stelliums) — keyed by a sorted triple.
# ---------------------------------------------------------------------------
THREE_PLANET: Dict[Tuple[str, str, str], Dict[str, str]] = {
    ("Mercury", "Sun", "Venus"): {"name": "Sun-Mercury-Venus",
        "significance": "Authority, intellect and artistry together — refined, expressive, capable.",
        "merits": "Intelligence, communication, artistic and diplomatic skill, status.",
        "demerits": "Combustion can weaken Mercury/Venus; ego or indulgence in expression."},
    ("Mercury", "Moon", "Venus"): {"name": "Moon-Mercury-Venus",
        "significance": "A charming, artistic and communicative temperament with emotional refinement.",
        "merits": "Charisma, creativity, eloquence, warm relationships.",
        "demerits": "Over-sensitivity, indulgence, scattered focus."},
    ("Jupiter", "Mars", "Sun"): {"name": "Sun-Mars-Jupiter",
        "significance": "Fiery leadership guided by wisdom — a dharmic commander.",
        "merits": "Courage, righteous authority, drive, prosperity.",
        "demerits": "Pride, aggression, dogmatism, burnout."},
    ("Jupiter", "Mercury", "Venus"): {"name": "Mercury-Venus-Jupiter",
        "significance": "Learning, art and wisdom combined — ideal for teaching and the arts.",
        "merits": "Scholarship, refinement, ethics, wealth, eloquence.",
        "demerits": "Indecision, over-indulgence, idealism."},
    ("Mars", "Rahu", "Saturn"): {"name": "Mars-Saturn-Rahu",
        "significance": "Intense, karmically heavy energy — relentless but harsh.",
        "merits": "Endurance, fearless work, capacity in crises and heavy industry.",
        "demerits": "Accidents, anxiety, conflict, ruthless or destructive drive."},
    ("Mercury", "Moon", "Sun"): {"name": "Sun-Moon-Mercury",
        "significance": "Will, emotion and intellect fused (near new moon) — self-directed.",
        "merits": "Focus, communication, self-reliance.",
        "demerits": "Inner ego-emotion tension, restlessness, combustion effects."},
}


def _triple_key(a: str, b: str, c: str) -> Tuple[str, str, str]:
    return tuple(sorted((a, b, c)))  # type: ignore[return-value]


def three_planet(a: str, b: str, c: str) -> Optional[Dict[str, str]]:
    return THREE_PLANET.get(_triple_key(a, b, c))


def _pair_key(a: str, b: str) -> Tuple[str, str]:
    return tuple(sorted((a, b)))  # type: ignore[return-value]


def planet_in_house(planet: str, house: int) -> Optional[Dict[str, str]]:
    return PLANET_IN_HOUSE.get(planet, {}).get(house)


def conjunction(a: str, b: str) -> Optional[Dict[str, str]]:
    return CONJUNCTIONS.get(_pair_key(a, b))


def _dignity_modifier(dignity: str) -> Tuple[str, str]:
    """(state, note) describing how dignity re-colours a placement."""
    if dignity in ("Exalted", "Own Sign", "Moolatrikona"):
        return ("strengthened", "This placement is strong (dignified), so its merits "
                "express fully and the watch-outs stay mild.")
    if dignity in ("Debilitated", "Enemy's Sign"):
        return ("weakened", "This placement is under strain (undignified), so the "
                "watch-outs need care and the merits come with extra effort.")
    return ("moderate", "This placement is moderate in strength, giving steady, "
            "ordinary results.")


def _house_quality(to_house: int, dignity: str) -> str:
    if to_house in _DUSTHANA:
        base = "challenging"
    elif to_house in _KENDRA_TRIKONA or to_house in _UPACHAYA:
        base = "favourable"
    else:
        base = "mixed"
    if dignity in ("Exalted", "Own Sign", "Moolatrikona") and base != "favourable":
        base += " (helped by strong dignity)"
    elif dignity in ("Debilitated", "Enemy's Sign") and base == "favourable":
        base += " (dented by weak dignity)"
    return base


def house_lord_placements(chart: Chart) -> List[Dict]:
    """Lord of each house and the house it occupies (Bhavesh-in-Bhava)."""
    strengths = all_strengths(chart)
    out: List[Dict] = []
    for h in range(1, 13):
        sign = chart.house_signs[h]
        lord = ref.SIGN_LORD[sign]
        to_house = chart.planet_house(lord)
        from_matters = ref.HOUSE_THEME.get(h, "")
        to_matters = ref.HOUSE_THEME.get(to_house, "")
        dignity = strengths[lord].dignity
        quality = _house_quality(to_house, dignity)
        effect = (f"The lord of the {_ordinal(h)} house ({lord}, {dignity.lower()}) is "
                  f"placed in the {_ordinal(to_house)} house.")
        meaning = (f"Your {from_matters} are channelled toward {to_matters} — "
                   f"a {quality} direction for this area of life.")
        out.append({
            "from_house": h,
            "to_house": to_house,
            "lord": lord,
            "sign": sign,
            "dignity": dignity,
            "quality": quality,
            "from_matters": from_matters,
            "to_matters": to_matters,
            "effect": effect,
            "meaning": meaning,
        })
    return out


def house_lord_generic(from_house: int, to_house: int) -> Dict:
    """Chart-free meaning of 'lord of house X placed in house Y'."""
    from_matters = ref.HOUSE_THEME.get(from_house, "")
    to_matters = ref.HOUSE_THEME.get(to_house, "")
    quality = _house_quality(to_house, "Neutral's Sign")
    return {
        "from_house": from_house,
        "to_house": to_house,
        "from_matters": from_matters,
        "to_matters": to_matters,
        "quality": quality,
        "effect": (f"The lord of the {_ordinal(from_house)} house placed in the "
                   f"{_ordinal(to_house)} house."),
        "meaning": (f"The matters of {from_matters} are directed toward {to_matters} — "
                    f"a {quality} placement. When the {_ordinal(from_house)} lord is strong "
                    "and well-aspected, this expresses at its best."),
    }


def _stellium_description(names: List[str], house: int, sign: str) -> Dict:
    curated = None
    if len(names) == 3:
        curated = three_planet(*names)
    theme = ref.HOUSE_THEME.get(house, "")
    blended = ", ".join(PLANET_KEYWORD.get(n, n) for n in names)
    if curated:
        return {
            "name": curated["name"],
            "significance": curated["significance"],
            "merits": curated["merits"],
            "demerits": curated["demerits"],
            "curated": True,
        }
    return {
        "name": f"{'-'.join(names)} stellium",
        "significance": (f"A stellium of {len(names)} planets in the {_ordinal(house)} "
                         f"house puts intense focus on {theme}. Blended energies: {blended}."),
        "merits": "Concentrated strength and talent in this area of life.",
        "demerits": "Over-emphasis here can unbalance other areas; mixed planets can clash.",
        "curated": False,
    }


def _aspect_note(aspects: List[Dict]) -> str:
    if not aspects:
        return "No planetary aspects fall here — the placement acts on its own."
    benefics = [a["planet"] for a in aspects if a["is_benefic"]]
    malefics = [a["planet"] for a in aspects if not a["is_benefic"]]
    parts = []
    if benefics:
        parts.append(f"benefic support from {', '.join(benefics)} (protects and softens)")
    if malefics:
        parts.append(f"malefic pressure from {', '.join(malefics)} (adds challenge or urgency)")
    return "Receives " + "; ".join(parts) + "."


def _nakshatra_note(planet: str, nakshatra: str, pada: int) -> str:
    trait = NAKSHATRA_TRAIT.get(nakshatra, "its own themes")
    lord = ref.NAKSHATRA_LORD.get(nakshatra, "")
    return (f"In {nakshatra} (pada {pada}), ruled by {lord} — colouring {planet} with "
            f"{trait}.")


def chart_combinations(chart: Chart) -> Dict:
    """Actual placements, conjunctions, stelliums and house-lords in a chart."""
    strengths = all_strengths(chart)
    placements: List[Dict] = []
    for name in ref.PLANETS:
        p = chart.planets[name]
        info = planet_in_house(name, p.house) or {}
        dignity = strengths[name].dignity
        state, dignity_note = _dignity_modifier(dignity)
        aspects = aspects_on_planet(chart, name)
        placements.append({
            "planet": name,
            "house": p.house,
            "house_name": ref.HOUSE_NAME.get(p.house, ""),
            "sign": p.sign,
            "retrograde": p.retrograde,
            "dignity": dignity,
            "dignity_state": state,
            "dignity_note": dignity_note,
            "nakshatra": p.nakshatra,
            "nakshatra_pada": p.nakshatra_pada,
            "nakshatra_note": _nakshatra_note(name, p.nakshatra, p.nakshatra_pada),
            "aspects": [{"planet": a["planet"], "is_benefic": a["is_benefic"]} for a in aspects],
            "aspect_note": _aspect_note(aspects),
            "effect": info.get("effect", ""),
            "merits": info.get("merits", ""),
            "demerits": info.get("demerits", ""),
        })

    # Group planets by house for conjunctions and stelliums.
    by_house: Dict[int, List[str]] = {}
    for name in ref.PLANETS:
        by_house.setdefault(chart.planets[name].house, []).append(name)

    conjunctions: List[Dict] = []
    stelliums: List[Dict] = []
    for house, names in sorted(by_house.items()):
        if len(names) < 2:
            continue
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                info = conjunction(a, b)
                conjunctions.append({
                    "planets": (a, b),
                    "house": house,
                    "house_name": ref.HOUSE_NAME.get(house, ""),
                    "sign": chart.planets[a].sign,
                    "name": (info or {}).get("name", f"{a}-{b} conjunction"),
                    "significance": (info or {}).get(
                        "significance", f"{a} and {b} blend their significations here."),
                    "merits": (info or {}).get("merits", ""),
                    "demerits": (info or {}).get("demerits", ""),
                    "curated": info is not None,
                })
        if len(names) >= 3:
            desc = _stellium_description(names, house, chart.planets[names[0]].sign)
            desc.update({
                "planets": tuple(names),
                "house": house,
                "house_name": ref.HOUSE_NAME.get(house, ""),
                "sign": chart.planets[names[0]].sign,
            })
            stelliums.append(desc)

    return {
        "placements": placements,
        "conjunctions": conjunctions,
        "stelliums": stelliums,
        "house_lords": house_lord_placements(chart),
    }


def combinations_markdown(chart: Chart, native: str) -> str:
    """Full planetary-combinations report for a chart, as Markdown."""
    data = chart_combinations(chart)
    lines = [
        f"# Planetary Combinations Report — {native}",
        "",
        f"Ascendant: {chart.lagna_sign} · Moon: {chart.planets['Moon'].sign}",
        "",
        "## Planet placements",
    ]
    for p in data["placements"]:
        retro = " (retrograde)" if p["retrograde"] else ""
        lines += [
            f"### {p['planet']}{retro} — House {p['house']} ({p['house_name']}), "
            f"{p['sign']} · {p['dignity']}",
            f"- **Effect:** {p['effect']}",
            f"- **Merits:** {p['merits']}",
            f"- **Watch-outs:** {p['demerits']}",
            f"- **Dignity:** {p['dignity_note']}",
            f"- **Nakshatra:** {p['nakshatra_note']}",
            f"- **Aspects:** {p['aspect_note']}",
            "",
        ]

    lines.append("## House-lord placements")
    for d in data["house_lords"]:
        lines.append(f"- **{_ordinal(d['from_house'])} lord {d['lord']} in "
                     f"{_ordinal(d['to_house'])}** ({d['quality']}) — {d['meaning']}")
    lines.append("")

    if data["conjunctions"]:
        lines.append("## Conjunctions")
        for c in data["conjunctions"]:
            lines.append(f"- **{c['name']}** — House {c['house']} ({c['house_name']}), "
                         f"{c['sign']}. {c['significance']}"
                         + (f" _Merits:_ {c['merits']}" if c["merits"] else "")
                         + (f" _Watch-outs:_ {c['demerits']}" if c["demerits"] else ""))
        lines.append("")

    if data["stelliums"]:
        lines.append("## Stelliums (3+ planets together)")
        for s in data["stelliums"]:
            lines.append(f"- **{s['name']}** — House {s['house']} ({s['house_name']}), "
                         f"{s['sign']}. {s['significance']}")
        lines.append("")

    lines.append("> Reference guidance · results are modulated by sign, dignity, "
                 "aspects and Dasha. For learning and reflection.")
    return "\n".join(lines)
