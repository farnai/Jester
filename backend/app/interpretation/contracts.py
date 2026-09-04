"""
Contract Registry defining structured Interpretation Contracts for Jester V1.
Decouples deterministic astrological signals from human semantic meaning.
Encompasses ~112 semantic interpretation contracts across:
1. Self / Me (43 contracts: Sun, Moon, Rising, Elements, Modalities)
2. Relationships / Synastry (45 contracts: Attraction, Harmony, Growth, Communication, Stability, Notice, Macro)
3. Friendship / Platonic (12 contracts: Chemistry, Banter, Loyalty, Refuge, etc.)
4. Daily Energy (12 contracts: Confidence, Focus, Clarity, Vitality, etc.)
"""
from backend.app.interpretation.models import (
    InterpretationConstraints,
    InterpretationContract,
    InterpretationMeaning,
    InterpretationOutput,
    InterpretationSignal,
    InterpretationVoice,
)

# Base default constraints preventing astrology jargon and future-telling
DEFAULT_CONSTRAINTS = InterpretationConstraints(
    must_not=[
        "predict the future",
        "claim certainty about another person's feelings",
        "use astrology jargon",
        "sound generic or horoscope-like",
        "humiliate or degrade user",
    ]
)

INTERPRETATION_CONTRACTS: dict[str, InterpretationContract] = {
    # =============================================================
    # 1. SELF / ME — CORE IDENTITY (12 SUN SIGNS)
    # =============================================================
    "self.identity.sun_aries.v1": InterpretationContract(
        interpretation_id="self.identity.sun_aries.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_aries", strength=0.90),
        meaning=InterpretationMeaning(
            type="direct_catalyst",
            intensity="high",
            human_meaning=["instinctive momentum", "unfiltered directness", "impatience with hesitation"],
        ),
    ),
    "self.identity.sun_taurus.v1": InterpretationContract(
        interpretation_id="self.identity.sun_taurus.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_taurus", strength=0.90),
        meaning=InterpretationMeaning(
            type="grounded_anchor",
            intensity="high",
            human_meaning=["unshakable stamina", "sensory discernment", "deliberate measured pace"],
        ),
    ),
    "self.identity.sun_gemini.v1": InterpretationContract(
        interpretation_id="self.identity.sun_gemini.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_gemini", strength=0.90),
        meaning=InterpretationMeaning(
            type="agile_synthesizer",
            intensity="high",
            human_meaning=["rapid intellectual curiosity", "multifaceted perspective", "conversational playfulness"],
        ),
    ),
    "self.identity.sun_cancer.v1": InterpretationContract(
        interpretation_id="self.identity.sun_cancer.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_cancer", strength=0.90),
        meaning=InterpretationMeaning(
            type="protective_radar",
            intensity="high",
            human_meaning=["intuitive emotional vigilance", "fierce loyalty to inner circle", "instinctive empathy"],
        ),
    ),
    "self.identity.sun_leo.v1": InterpretationContract(
        interpretation_id="self.identity.sun_leo.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_leo", strength=0.90),
        meaning=InterpretationMeaning(
            type="radiant_presence",
            intensity="high",
            human_meaning=["generous warmth", "expressive authenticity", "unapologetic creative confidence"],
        ),
    ),
    "self.identity.sun_virgo.v1": InterpretationContract(
        interpretation_id="self.identity.sun_virgo.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_virgo", strength=0.90),
        meaning=InterpretationMeaning(
            type="discerning_architect",
            intensity="high",
            human_meaning=["systematic precision", "quiet operational competence", "instinctive habit of refinement"],
        ),
    ),
    "self.identity.sun_libra.v1": InterpretationContract(
        interpretation_id="self.identity.sun_libra.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_libra", strength=0.90),
        meaning=InterpretationMeaning(
            type="social_diplomat",
            intensity="high",
            human_meaning=["aesthetic sensitivity", "instinctive mediation", "relational balance and charm"],
        ),
    ),
    "self.identity.sun_scorpio.v1": InterpretationContract(
        interpretation_id="self.identity.sun_scorpio.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_scorpio", strength=0.90),
        meaning=InterpretationMeaning(
            type="penetrating_observer",
            intensity="high",
            human_meaning=["psychological radar", "uncompromising authenticity", "guarded regenerative power"],
        ),
    ),
    "self.identity.sun_sagittarius.v1": InterpretationContract(
        interpretation_id="self.identity.sun_sagittarius.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_sagittarius", strength=0.90),
        meaning=InterpretationMeaning(
            type="philosophical_explorer",
            intensity="high",
            human_meaning=["unbounded curiosity", "candid frankness", "hunger for intellectual horizon expansion"],
        ),
    ),
    "self.identity.sun_capricorn.v1": InterpretationContract(
        interpretation_id="self.identity.sun_capricorn.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_capricorn", strength=0.90),
        meaning=InterpretationMeaning(
            type="strategic_builder",
            intensity="high",
            human_meaning=["long-range discipline", "quiet ambition", "unflinching accountability"],
        ),
    ),
    "self.identity.sun_aquarius.v1": InterpretationContract(
        interpretation_id="self.identity.sun_aquarius.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_aquarius", strength=0.90),
        meaning=InterpretationMeaning(
            type="autonomous_visionary",
            intensity="high",
            human_meaning=["intellectual sovereignty", "unconventional logic", "refusal of unexamined norms"],
        ),
    ),
    "self.identity.sun_pisces.v1": InterpretationContract(
        interpretation_id="self.identity.sun_pisces.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="sun_sign_pisces", strength=0.90),
        meaning=InterpretationMeaning(
            type="fluid_dreamer",
            intensity="high",
            human_meaning=["permeable empathy", "imaginative depth", "comfort with ambiguity and subtle nuance"],
        ),
    ),

    # =============================================================
    # 2. SELF / ME — EMOTIONAL PROCESSING (12 MOON SIGNS)
    # =============================================================
    "self.emotional.moon_aries.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_aries.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_aries", strength=0.85),
        meaning=InterpretationMeaning(
            type="instant_discharge",
            intensity="high",
            human_meaning=["immediate emotional honesty", "rapid recovery", "zero emotional lingering"],
        ),
    ),
    "self.emotional.moon_taurus.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_taurus.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_taurus", strength=0.85),
        meaning=InterpretationMeaning(
            type="steady_grounding",
            intensity="high",
            human_meaning=["sensory reset", "emotional composure", "reluctance to be rushed or provoked"],
        ),
    ),
    "self.emotional.moon_gemini.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_gemini.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_gemini", strength=0.85),
        meaning=InterpretationMeaning(
            type="verbal_processing",
            intensity="high",
            human_meaning=["talking through feeling", "analyzing emotional patterns", "lightening heavy atmospheres"],
        ),
    ),
    "self.emotional.moon_cancer.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_cancer.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_cancer", strength=0.85),
        meaning=InterpretationMeaning(
            type="sanctuary_seeking",
            intensity="high",
            human_meaning=["deep tidal memory", "protective sensitivity", "retreating to trusted private spaces"],
        ),
    ),
    "self.emotional.moon_leo.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_leo.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_leo", strength=0.85),
        meaning=InterpretationMeaning(
            type="expressive_heart",
            intensity="high",
            human_meaning=["generous emotional pride", "needs heartfelt recognition", "dramatic warmth"],
        ),
    ),
    "self.emotional.moon_virgo.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_virgo.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_virgo", strength=0.85),
        meaning=InterpretationMeaning(
            type="pragmatic_repair",
            intensity="high",
            human_meaning=["coping through constructive action", "internal self-critique", "practical care"],
        ),
    ),
    "self.emotional.moon_libra.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_libra.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_libra", strength=0.85),
        meaning=InterpretationMeaning(
            type="relational_calm",
            intensity="high",
            human_meaning=["peace-seeking equilibrium", "avoidance of unnecessary discord", "perspective-taking"],
        ),
    ),
    "self.emotional.moon_scorpio.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_scorpio.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_scorpio", strength=0.85),
        meaning=InterpretationMeaning(
            type="private_intensity",
            intensity="high",
            human_meaning=["all-or-nothing emotional depth", "protective boundaries", "transformative regeneration"],
        ),
    ),
    "self.emotional.moon_sagittarius.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_sagittarius.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_sagittarius", strength=0.85),
        meaning=InterpretationMeaning(
            type="philosophical_reset",
            intensity="high",
            human_meaning=["humorous reframing", "needs breathing room to process", "optimistic perspective"],
        ),
    ),
    "self.emotional.moon_capricorn.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_capricorn.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_capricorn", strength=0.85),
        meaning=InterpretationMeaning(
            type="stoic_containment",
            intensity="high",
            human_meaning=["self-sufficient emotional discipline", "delayed vulnerability", "quiet resilience"],
        ),
    ),
    "self.emotional.moon_aquarius.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_aquarius.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_aquarius", strength=0.85),
        meaning=InterpretationMeaning(
            type="detached_clarity",
            intensity="high",
            human_meaning=["stepping back to observe feelings objectively", "cool autonomy", "unconventional comfort"],
        ),
    ),
    "self.emotional.moon_pisces.v1": InterpretationContract(
        interpretation_id="self.emotional.moon_pisces.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="moon_sign_pisces", strength=0.85),
        meaning=InterpretationMeaning(
            type="spongelike_empathy",
            intensity="high",
            human_meaning=["absorbing environmental moods", "intuitive sensitivity", "creative decompression"],
        ),
    ),

    # =============================================================
    # 3. SELF / ME — PERSONA & FIRST IMPRESSION (12 ASCENDANTS)
    # =============================================================
    "self.persona.rising_aries.v1": InterpretationContract(
        interpretation_id="self.persona.rising_aries.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_aries", strength=0.80),
        meaning=InterpretationMeaning(
            type="direct_stride",
            intensity="high",
            human_meaning=["dynamic physical entry", "cutting past social fluff", "commanding initial presence"],
        ),
    ),
    "self.persona.rising_taurus.v1": InterpretationContract(
        interpretation_id="self.persona.rising_taurus.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_taurus", strength=0.80),
        meaning=InterpretationMeaning(
            type="calm_gravity",
            intensity="high",
            human_meaning=["grounded composure", "effortless visual poise", "unrushed conversational entry"],
        ),
    ),
    "self.persona.rising_gemini.v1": InterpretationContract(
        interpretation_id="self.persona.rising_gemini.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_gemini", strength=0.80),
        meaning=InterpretationMeaning(
            type="playful_spark",
            intensity="high",
            human_meaning=["alert observational curiosity", "expressive humor", "approachable disarming wit"],
        ),
    ),
    "self.persona.rising_cancer.v1": InterpretationContract(
        interpretation_id="self.persona.rising_cancer.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_cancer", strength=0.80),
        meaning=InterpretationMeaning(
            type="protective_warmth",
            intensity="high",
            human_meaning=["gentle approachable demeanor", "subtle observation buffer", "reassuring presence"],
        ),
    ),
    "self.persona.rising_leo.v1": InterpretationContract(
        interpretation_id="self.persona.rising_leo.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_leo", strength=0.80),
        meaning=InterpretationMeaning(
            type="magnetic_stage",
            intensity="high",
            human_meaning=["natural focal point", "warm radiant posture", "charismatic entrance"],
        ),
    ),
    "self.persona.rising_virgo.v1": InterpretationContract(
        interpretation_id="self.persona.rising_virgo.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_virgo", strength=0.80),
        meaning=InterpretationMeaning(
            type="crisp_understatement",
            intensity="high",
            human_meaning=["attentive modesty", "sharp observational eye", "effortless tidy polish"],
        ),
    ),
    "self.persona.rising_libra.v1": InterpretationContract(
        interpretation_id="self.persona.rising_libra.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_libra", strength=0.80),
        meaning=InterpretationMeaning(
            type="graceful_charm",
            intensity="high",
            human_meaning=["instinctive social diplomacy", "disarming smile", "harmonious aesthetic presentation"],
        ),
    ),
    "self.persona.rising_scorpio.v1": InterpretationContract(
        interpretation_id="self.persona.rising_scorpio.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_scorpio", strength=0.80),
        meaning=InterpretationMeaning(
            type="intense_enigma",
            intensity="high",
            human_meaning=["penetrating gaze", "compelling quiet mystery", "perceived strength before speaking"],
        ),
    ),
    "self.persona.rising_sagittarius.v1": InterpretationContract(
        interpretation_id="self.persona.rising_sagittarius.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_sagittarius", strength=0.80),
        meaning=InterpretationMeaning(
            type="breezy_candor",
            intensity="high",
            human_meaning=["open-hearted enthusiasm", "informal approachable banter", "unpretentious posture"],
        ),
    ),
    "self.persona.rising_capricorn.v1": InterpretationContract(
        interpretation_id="self.persona.rising_capricorn.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_capricorn", strength=0.80),
        meaning=InterpretationMeaning(
            type="measured_authority",
            intensity="high",
            human_meaning=["calm competence", "professional composure", "earned gravity and reserve"],
        ),
    ),
    "self.persona.rising_aquarius.v1": InterpretationContract(
        interpretation_id="self.persona.rising_aquarius.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_aquarius", strength=0.80),
        meaning=InterpretationMeaning(
            type="distinctive_original",
            intensity="high",
            human_meaning=["unconventional aura", "observant friendly distance", "independent style"],
        ),
    ),
    "self.persona.rising_pisces.v1": InterpretationContract(
        interpretation_id="self.persona.rising_pisces.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="ascendant_sign_pisces", strength=0.80),
        meaning=InterpretationMeaning(
            type="dreamlike_fluidity",
            intensity="high",
            human_meaning=["soft receptive demeanor", "chameleon adaptability", "gentle empathetic aura"],
        ),
    ),

    # =============================================================
    # 4. SELF / ME — ELEMENT DOMINANCE (4 CONTRACTS)
    # =============================================================
    "self.element.fire_dominant.v1": InterpretationContract(
        interpretation_id="self.element.fire_dominant.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="element_dominant_fire", strength=0.85),
        meaning=InterpretationMeaning(
            type="kinetic_instinct",
            intensity="high",
            human_meaning=["bias toward immediate action", "contagious enthusiasm", "impatience with passive waiting"],
        ),
    ),
    "self.element.earth_dominant.v1": InterpretationContract(
        interpretation_id="self.element.earth_dominant.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="element_dominant_earth", strength=0.85),
        meaning=InterpretationMeaning(
            type="tactile_pragmatism",
            intensity="high",
            human_meaning=["focus on tangible results", "operational stamina", "low tolerance for empty rhetoric"],
        ),
    ),
    "self.element.air_dominant.v1": InterpretationContract(
        interpretation_id="self.element.air_dominant.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="element_dominant_air", strength=0.85),
        meaning=InterpretationMeaning(
            type="conceptual_agility",
            intensity="high",
            human_meaning=["hunger for fresh frameworks", "social connectivity", "preference for objective dialogue"],
        ),
    ),
    "self.element.water_dominant.v1": InterpretationContract(
        interpretation_id="self.element.water_dominant.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="element_dominant_water", strength=0.85),
        meaning=InterpretationMeaning(
            type="intuitive_resonance",
            intensity="high",
            human_meaning=["deep subtext sensing", "emotional intelligence", "unspoken psychological awareness"],
        ),
    ),

    # =============================================================
    # 5. SELF / ME — MODALITY DOMINANCE (3 CONTRACTS)
    # =============================================================
    "self.modality.cardinal_dominant.v1": InterpretationContract(
        interpretation_id="self.modality.cardinal_dominant.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="modality_dominant_cardinal", strength=0.85),
        meaning=InterpretationMeaning(
            type="pioneering_instigation",
            intensity="high",
            human_meaning=["starting movements", "comfortable seizing initiative", "restlessness when stagnant"],
        ),
    ),
    "self.modality.fixed_dominant.v1": InterpretationContract(
        interpretation_id="self.modality.fixed_dominant.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="modality_dominant_fixed", strength=0.85),
        meaning=InterpretationMeaning(
            type="sustained_tenacity",
            intensity="high",
            human_meaning=["unwavering persistence", "deep loyalty to chosen paths", "resistance to arbitrary change"],
        ),
    ),
    "self.modality.mutable_dominant.v1": InterpretationContract(
        interpretation_id="self.modality.mutable_dominant.v1",
        context="self",
        signal=InterpretationSignal(category="self", type="modality_dominant_mutable", strength=0.85),
        meaning=InterpretationMeaning(
            type="fluid_versatility",
            intensity="high",
            human_meaning=["rapid adaptation to shifting conditions", "multitasking comfort", "mental flexibility"],
        ),
    ),

    # =============================================================
    # 6. RELATIONSHIP / SYNASTRY (45 CONTRACTS)
    # =============================================================
    # Core Attraction Dynamics
    "relationship.attraction.strong_chemistry.v1": InterpretationContract(
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="venus_mars_aspect", strength=0.91),
        meaning=InterpretationMeaning(
            type="strong_chemistry",
            intensity="high",
            human_meaning=["strong interpersonal pull", "easy attraction", "high interpersonal magnetism"],
        ),
    ),
    "relationship.attraction.strong_chemistry.v2": InterpretationContract(
        interpretation_id="relationship.attraction.strong_chemistry.v2",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="venus_mars_aspect", strength=0.91),
        meaning=InterpretationMeaning(
            type="strong_chemistry",
            intensity="high",
            human_meaning=["strong interpersonal pull", "easy attraction", "high interpersonal magnetism"],
        ),
    ),
    "relationship.attraction.magnetic_chemistry.v1": InterpretationContract(
        interpretation_id="relationship.attraction.magnetic_chemistry.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="venus_mars_aspect", strength=0.85),
        meaning=InterpretationMeaning(
            type="magnetic_chemistry",
            intensity="high",
            human_meaning=["spontaneous physical or romantic chemistry", "high kinetic attraction", "dynamic spark"],
        ),
    ),
    "relationship.attraction.warm_affection.v1": InterpretationContract(
        interpretation_id="relationship.attraction.warm_affection.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="sun_venus_harmony", strength=0.80),
        meaning=InterpretationMeaning(
            type="warm_affection",
            intensity="high",
            human_meaning=["warm interpersonal charm", "shared aesthetic taste", "instinctive social gentleness"],
        ),
    ),
    "relationship.attraction.energized_collaboration.v1": InterpretationContract(
        interpretation_id="relationship.attraction.energized_collaboration.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="sun_mars_trine", strength=0.80),
        meaning=InterpretationMeaning(
            type="energized_collaboration",
            intensity="high",
            human_meaning=["shared physical and creative momentum", "instinctive teamwork", "catalytic enthusiasm"],
        ),
    ),
    "relationship.attraction.dynamic_drive.v1": InterpretationContract(
        interpretation_id="relationship.attraction.dynamic_drive.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="sun_mars_conjunction", strength=0.80),
        meaning=InterpretationMeaning(
            type="dynamic_drive",
            intensity="high",
            human_meaning=["bold collective motivation", "impatience with delay", "unflinching mutual energy"],
        ),
    ),
    "relationship.attraction.intense_magnetism.v1": InterpretationContract(
        interpretation_id="relationship.attraction.intense_magnetism.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="venus_pluto_aspect", strength=0.85),
        meaning=InterpretationMeaning(
            type="intense_magnetism",
            intensity="high",
            human_meaning=["deep psychological fascination", "intuitive draw beyond the surface", "transformative pull"],
        ),
    ),
    "relationship.attraction.mars_friction.v1": InterpretationContract(
        interpretation_id="relationship.attraction.mars_friction.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="mars_mars_friction", strength=0.75),
        meaning=InterpretationMeaning(
            type="competitive_friction",
            intensity="high",
            human_meaning=["fiery competitive edge", "provocative attraction", "mutual testing of boundaries"],
        ),
    ),
    "relationship.attraction.electric_fascination.v1": InterpretationContract(
        interpretation_id="relationship.attraction.electric_fascination.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="venus_uranus_aspect", strength=0.80),
        meaning=InterpretationMeaning(
            type="electric_fascination",
            intensity="high",
            human_meaning=["unpredictable attraction", "exciting novelty", "refusal to fit conventional molds"],
        ),
    ),
    "relationship.attraction.instinctive_heat.v1": InterpretationContract(
        interpretation_id="relationship.attraction.instinctive_heat.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="moon_mars_attraction", strength=0.80),
        meaning=InterpretationMeaning(
            type="instinctive_heat",
            intensity="high",
            human_meaning=["gut-level emotional arousal", "spontaneous passion", "heightened responsive spark"],
        ),
    ),
    "relationship.attraction.aesthetic_harmony.v1": InterpretationContract(
        interpretation_id="relationship.attraction.aesthetic_harmony.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="venus_venus_harmony", strength=0.75),
        meaning=InterpretationMeaning(
            type="aesthetic_resonance",
            intensity="medium",
            human_meaning=["shared romantic cadence", "effortless social rhythm", "mutual appreciation for beauty"],
        ),
    ),
    "relationship.attraction.magnetic_presence.v1": InterpretationContract(
        interpretation_id="relationship.attraction.magnetic_presence.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="venus_ascendant_harmony", strength=0.80),
        meaning=InterpretationMeaning(
            type="visual_allure",
            intensity="high",
            human_meaning=["instant outward attraction", "disarming physical appeal", "effortless mutual flattery"],
        ),
    ),
    "relationship.attraction.bold_momentum.v1": InterpretationContract(
        interpretation_id="relationship.attraction.bold_momentum.v1",
        context="relationship",
        signal=InterpretationSignal(category="attraction", type="mars_ascendant_aspect", strength=0.80),
        meaning=InterpretationMeaning(
            type="kinetic_spark",
            intensity="high",
            human_meaning=["outward physical chemistry", "spontaneous action together", "bold direct engagement"],
        ),
    ),

    # Emotional & Harmony Dynamics
    "relationship.harmony.emotional_resonance.v1": InterpretationContract(
        interpretation_id="relationship.harmony.emotional_resonance.v1",
        context="relationship",
        signal=InterpretationSignal(category="harmony", type="sun_moon_harmony", strength=0.90),
        meaning=InterpretationMeaning(
            type="emotional_resonance",
            intensity="high",
            human_meaning=["deep emotional comfort", "instinctive mutual understanding", "natural acceptance"],
        ),
    ),
    "relationship.harmony.core_harmony.v1": InterpretationContract(
        interpretation_id="relationship.harmony.core_harmony.v1",
        context="relationship",
        signal=InterpretationSignal(category="harmony", type="sun_sun_harmony", strength=0.85),
        meaning=InterpretationMeaning(
            type="core_harmony",
            intensity="high",
            human_meaning=["alignment on foundational worldview", "validation of core identity", "easy coexistence"],
        ),
    ),
    "relationship.harmony.gentle_affinity.v1": InterpretationContract(
        interpretation_id="relationship.harmony.gentle_affinity.v1",
        context="relationship",
        signal=InterpretationSignal(category="harmony", type="moon_venus_harmony", strength=0.80),
        meaning=InterpretationMeaning(
            type="gentle_affinity",
            intensity="high",
            human_meaning=["tender emotional appreciation", "soothing cozy comfort", "intuitive protective care"],
        ),
    ),
    "relationship.harmony.generous_affection.v1": InterpretationContract(
        interpretation_id="relationship.harmony.generous_affection.v1",
        context="relationship",
        signal=InterpretationSignal(category="harmony", type="venus_jupiter_harmony", strength=0.85),
        meaning=InterpretationMeaning(
            type="generous_affection",
            intensity="high",
            human_meaning=["open-hearted appreciation", "celebrating each other without envy", "social generosity"],
        ),
    ),
    "relationship.harmony.deep_empathy.v1": InterpretationContract(
        interpretation_id="relationship.harmony.deep_empathy.v1",
        context="relationship",
        signal=InterpretationSignal(category="harmony", type="moon_moon_harmony", strength=0.85),
        meaning=InterpretationMeaning(
            type="synchronized_rhythms",
            intensity="high",
            human_meaning=["identical emotional pacing", "unspoken telepathic comfort", "shared private haven"],
        ),
    ),
    "relationship.harmony.intuitive_communion.v1": InterpretationContract(
        interpretation_id="relationship.harmony.intuitive_communion.v1",
        context="relationship",
        signal=InterpretationSignal(category="harmony", type="moon_neptune_aspect", strength=0.80),
        meaning=InterpretationMeaning(
            type="poetic_empathy",
            intensity="high",
            human_meaning=["transcendent emotional sensitivity", "intuitive forgiveness", "delicate mutual solace"],
        ),
    ),
    "relationship.harmony.transformative_depth.v1": InterpretationContract(
        interpretation_id="relationship.harmony.transformative_depth.v1",
        context="relationship",
        signal=InterpretationSignal(category="harmony", type="moon_pluto_aspect", strength=0.85),
        meaning=InterpretationMeaning(
            type="unfiltered_vulnerability",
            intensity="high",
            human_meaning=["intense psychological closeness", "fearless exploration of shadow sides", "unshakable trust"],
        ),
    ),

    # Growth & Dynamic Tension Dynamics
    "relationship.growth.complementary_balance.v1": InterpretationContract(
        interpretation_id="relationship.growth.complementary_balance.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="sun_moon_opposition", strength=0.75),
        meaning=InterpretationMeaning(
            type="complementary_balance",
            intensity="high",
            human_meaning=["polar perspectives that balance out", "counterweight to habits", "growth via creative contrast"],
        ),
    ),
    "relationship.growth.dynamic_emotional_tension.v1": InterpretationContract(
        interpretation_id="relationship.growth.dynamic_emotional_tension.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="sun_moon_square", strength=0.65),
        meaning=InterpretationMeaning(
            type="dynamic_emotional_tension",
            intensity="medium",
            human_meaning=["divergent emotional processing styles", "pacing adjustments needed", "growth preventing stagnation"],
        ),
    ),
    "relationship.growth.contrasting_perspectives.v1": InterpretationContract(
        interpretation_id="relationship.growth.contrasting_perspectives.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="sun_sun_opposition", strength=0.70),
        meaning=InterpretationMeaning(
            type="contrasting_perspectives",
            intensity="medium",
            human_meaning=["mirroring each other's blind spots", "stimulating debate", "fascination with opposite angles"],
        ),
    ),
    "relationship.growth.ego_friction.v1": InterpretationContract(
        interpretation_id="relationship.growth.ego_friction.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="sun_sun_square", strength=0.65),
        meaning=InterpretationMeaning(
            type="ego_friction",
            intensity="medium",
            human_meaning=["strong wills negotiating territory", "constructive boundaries", "sharpening individual goals"],
        ),
    ),
    "relationship.growth.pacing_tension.v1": InterpretationContract(
        interpretation_id="relationship.growth.pacing_tension.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="saturn_square_personal", strength=0.65),
        meaning=InterpretationMeaning(
            type="pacing_tension",
            intensity="medium",
            human_meaning=["tension between impulse and patience", "learning structural discipline", "timing calibrations"],
        ),
    ),
    "relationship.growth.dynamic_spark.v1": InterpretationContract(
        interpretation_id="relationship.growth.dynamic_spark.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="mars_sun_square", strength=0.70),
        meaning=InterpretationMeaning(
            type="dynamic_spark",
            intensity="medium",
            human_meaning=["playful competitive drive", "energized debates that spur action", "refusal of boredom"],
        ),
    ),
    "relationship.growth.emotional_divergence.v1": InterpretationContract(
        interpretation_id="relationship.growth.emotional_divergence.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="moon_moon_contrast", strength=0.65),
        meaning=InterpretationMeaning(
            type="contrasting_emotional_styles",
            intensity="medium",
            human_meaning=["distinct stress coping mechanisms", "learning each other's recovery vocabulary", "constructive patience"],
        ),
    ),
    "relationship.growth.power_clash.v1": InterpretationContract(
        interpretation_id="relationship.growth.power_clash.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="mars_pluto_aspect", strength=0.75),
        meaning=InterpretationMeaning(
            type="willpower_crucible",
            intensity="high",
            human_meaning=["unyielding resolve on both sides", "refusal to be dominated", "deep transformative breakthrough"],
        ),
    ),
    "relationship.growth.sobering_realism.v1": InterpretationContract(
        interpretation_id="relationship.growth.sobering_realism.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="venus_saturn_aspect", strength=0.70),
        meaning=InterpretationMeaning(
            type="deliberate_commitment",
            intensity="medium",
            human_meaning=["measured affection", "high standards for emotional security", "value built on substance over flash"],
        ),
    ),
    "relationship.growth.strategic_resistance.v1": InterpretationContract(
        interpretation_id="relationship.growth.strategic_resistance.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="mars_saturn_tension", strength=0.70),
        meaning=InterpretationMeaning(
            type="endurance_testing",
            intensity="medium",
            human_meaning=["clash between acceleration and caution", "building durable working methods through trial"],
        ),
    ),
    "relationship.growth.limitless_ambition.v1": InterpretationContract(
        interpretation_id="relationship.growth.limitless_ambition.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="sun_jupiter_expansion", strength=0.80),
        meaning=InterpretationMeaning(
            type="audacious_expansion",
            intensity="high",
            human_meaning=["mutual encouragement of grand ventures", "challenging small thinking", "broad horizons"],
        ),
    ),

    # Communication Dynamics
    "relationship.communication.intellectual_flow.v1": InterpretationContract(
        interpretation_id="relationship.communication.intellectual_flow.v1",
        context="relationship",
        signal=InterpretationSignal(category="communication", type="mercury_mercury_harmony", strength=0.85),
        meaning=InterpretationMeaning(
            type="intellectual_flow",
            intensity="high",
            human_meaning=["rapid conversational ping-pong", "shared cognitive humor", "effortless idea generation"],
        ),
    ),
    "relationship.communication.mutual_understanding.v1": InterpretationContract(
        interpretation_id="relationship.communication.mutual_understanding.v1",
        context="relationship",
        signal=InterpretationSignal(category="communication", type="sun_mercury_harmony", strength=0.75),
        meaning=InterpretationMeaning(
            type="mutual_understanding",
            intensity="medium",
            human_meaning=["clarity in articulating plans", "feeling genuinely heard", "collaborative problem solving"],
        ),
    ),
    "relationship.communication.intuitive_listening.v1": InterpretationContract(
        interpretation_id="relationship.communication.intuitive_listening.v1",
        context="relationship",
        signal=InterpretationSignal(category="communication", type="mercury_moon_harmony", strength=0.80),
        meaning=InterpretationMeaning(
            type="empathetic_dialogue",
            intensity="high",
            human_meaning=["translating feelings into clear thoughts", "tactful sensitivity", "emotionally attuned dialogue"],
        ),
    ),
    "relationship.communication.sharp_debate.v1": InterpretationContract(
        interpretation_id="relationship.communication.sharp_debate.v1",
        context="relationship",
        signal=InterpretationSignal(category="communication", type="mercury_mars_aspect", strength=0.75),
        meaning=InterpretationMeaning(
            type="intellectual_sparring",
            intensity="high",
            human_meaning=["rapid-fire intellectual challenge", "zero conversational boredom", "stimulating debate"],
        ),
    ),
    "relationship.communication.grounded_deliberation.v1": InterpretationContract(
        interpretation_id="relationship.communication.grounded_deliberation.v1",
        context="relationship",
        signal=InterpretationSignal(category="communication", type="mercury_saturn_aspect", strength=0.75),
        meaning=InterpretationMeaning(
            type="rigorous_thought",
            intensity="medium",
            human_meaning=["structured analytical exchanges", "meticulous problem solving", "holding each other to facts"],
        ),
    ),
    "relationship.communication.unconventional_spark.v1": InterpretationContract(
        interpretation_id="relationship.communication.unconventional_spark.v1",
        context="relationship",
        signal=InterpretationSignal(category="communication", type="mercury_uranus_aspect", strength=0.80),
        meaning=InterpretationMeaning(
            type="breakthrough_ideation",
            intensity="high",
            human_meaning=["quirky off-the-wall banter", "spontaneous eureka moments", "disrupting boring small talk"],
        ),
    ),

    # Stability & Notice Dynamics
    "relationship.stability.shared_optimism.v1": InterpretationContract(
        interpretation_id="relationship.stability.shared_optimism.v1",
        context="relationship",
        signal=InterpretationSignal(category="stability", type="jupiter_harmony", strength=0.85),
        meaning=InterpretationMeaning(
            type="shared_optimism",
            intensity="high",
            human_meaning=["expansive mutual horizons", "generous humor", "collective resilience in tough spots"],
        ),
    ),
    "relationship.stability.long_term_grounding.v1": InterpretationContract(
        interpretation_id="relationship.stability.long_term_grounding.v1",
        context="relationship",
        signal=InterpretationSignal(category="stability", type="saturn_trine_personal", strength=0.85),
        meaning=InterpretationMeaning(
            type="long_term_grounding",
            intensity="high",
            human_meaning=["structural reliability", "commitments outlasting novelty", "mature mutual accountability"],
        ),
    ),
    "relationship.stability.generous_comfort.v1": InterpretationContract(
        interpretation_id="relationship.stability.generous_comfort.v1",
        context="relationship",
        signal=InterpretationSignal(category="stability", type="moon_jupiter_harmony", strength=0.80),
        meaning=InterpretationMeaning(
            type="emotional_abundance",
            intensity="high",
            human_meaning=["instinctive forgiveness", "lighthearted emotional recovery", "generous domestic comfort"],
        ),
    ),
    "relationship.stability.architectural_anchor.v1": InterpretationContract(
        interpretation_id="relationship.stability.architectural_anchor.v1",
        context="relationship",
        signal=InterpretationSignal(category="stability", type="sun_saturn_grounding", strength=0.85),
        meaning=InterpretationMeaning(
            type="bedrock_durability",
            intensity="high",
            human_meaning=["dependable loyalty", "navigating reality without illusions", "building an enduring alliance"],
        ),
    ),
    "relationship.notice.independent_dynamics.v1": InterpretationContract(
        interpretation_id="relationship.notice.independent_dynamics.v1",
        context="relationship",
        signal=InterpretationSignal(category="notice", type="insufficient_aspects", strength=0.50),
        meaning=InterpretationMeaning(
            type="independent_dynamics",
            intensity="low",
            human_meaning=["unencumbered autonomy", "minimal reactive drama", "relationship built on conscious choice"],
        ),
    ),

    # Macro Synergy Contracts
    "relationship.overall.exceptional_flow.v1": InterpretationContract(
        interpretation_id="relationship.overall.exceptional_flow.v1",
        context="relationship",
        signal=InterpretationSignal(category="harmony", type="score_high", strength=0.92),
        meaning=InterpretationMeaning(
            type="exceptional_flow",
            intensity="high",
            human_meaning=["seamless cadence across multiple planes", "organic compatibility", "effortless rapport"],
        ),
    ),
    "relationship.overall.balanced_synergy.v1": InterpretationContract(
        interpretation_id="relationship.overall.balanced_synergy.v1",
        context="relationship",
        signal=InterpretationSignal(category="harmony", type="score_balanced", strength=0.78),
        meaning=InterpretationMeaning(
            type="balanced_synergy",
            intensity="medium",
            human_meaning=["healthy equilibrium between shared rhythm and distinct individuality"],
        ),
    ),
    "relationship.overall.stimulating_friction.v1": InterpretationContract(
        interpretation_id="relationship.overall.stimulating_friction.v1",
        context="relationship",
        signal=InterpretationSignal(category="growth", type="score_growth", strength=0.62),
        meaning=InterpretationMeaning(
            type="stimulating_friction",
            intensity="medium",
            human_meaning=["energy driven by dynamic contrast", "evolutionary catalyst preventing complacency"],
        ),
    ),
    "relationship.overall.independent_paths.v1": InterpretationContract(
        interpretation_id="relationship.overall.independent_paths.v1",
        context="relationship",
        signal=InterpretationSignal(category="notice", type="score_independent", strength=0.45),
        meaning=InterpretationMeaning(
            type="independent_paths",
            intensity="low",
            human_meaning=["sovereign parallel trajectories requiring conscious bridge-building"],
        ),
    ),

    # =============================================================
    # 7. FRIENDSHIP / PLATONIC (12 CONTRACTS)
    # =============================================================
    "friendship.chemistry.instant_rapport.v1": InterpretationContract(
        interpretation_id="friendship.chemistry.instant_rapport.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="friendship_chemistry", strength=0.85),
        meaning=InterpretationMeaning(
            type="instant_rapport",
            intensity="high",
            human_meaning=["immediate social ease", "zero awkwardness from minute one", "organic comfort"],
        ),
    ),
    "friendship.communication.effortless_banter.v1": InterpretationContract(
        interpretation_id="friendship.communication.effortless_banter.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="conversational_ease", strength=0.85),
        meaning=InterpretationMeaning(
            type="effortless_banter",
            intensity="high",
            human_meaning=["fluid ping-pong conversation", "natural punchlines", "never running out of things to say"],
        ),
    ),
    "friendship.communication.shared_absurdity.v1": InterpretationContract(
        interpretation_id="friendship.communication.shared_absurdity.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="shared_humor", strength=0.85),
        meaning=InterpretationMeaning(
            type="shared_absurdity",
            intensity="high",
            human_meaning=["matching sense of humor", "private inside jokes", "laughing at identical absurdities"],
        ),
    ),
    "friendship.harmony.synchronous_pace.v1": InterpretationContract(
        interpretation_id="friendship.harmony.synchronous_pace.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="social_rhythm", strength=0.80),
        meaning=InterpretationMeaning(
            type="synchronous_pace",
            intensity="high",
            human_meaning=["matching social battery", "effortless scheduling", "neither feels hurried or neglected"],
        ),
    ),
    "friendship.stability.unconditional_cushion.v1": InterpretationContract(
        interpretation_id="friendship.stability.unconditional_cushion.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="mutual_support", strength=0.85),
        meaning=InterpretationMeaning(
            type="unconditional_cushion",
            intensity="high",
            human_meaning=["practical support without judgment", "grounded listening", "dependable crisis buffer"],
        ),
    ),
    "friendship.stability.quiet_loyalty.v1": InterpretationContract(
        interpretation_id="friendship.stability.quiet_loyalty.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="trust", strength=0.85),
        meaning=InterpretationMeaning(
            type="quiet_loyalty",
            intensity="high",
            human_meaning=["low-maintenance connection", "picking up right where left off", "unshakeable trust"],
        ),
    ),
    "friendship.notice.autonomous_bond.v1": InterpretationContract(
        interpretation_id="friendship.notice.autonomous_bond.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="independence", strength=0.70),
        meaning=InterpretationMeaning(
            type="autonomous_bond",
            intensity="medium",
            human_meaning=["zero clinginess", "sovereign mutual respect", "celebrating individual freedom"],
        ),
    ),
    "friendship.social.crew_catalyst.v1": InterpretationContract(
        interpretation_id="friendship.social.crew_catalyst.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="group_compatibility", strength=0.80),
        meaning=InterpretationMeaning(
            type="crew_catalyst",
            intensity="high",
            human_meaning=["elevating the room's energy together", "catalyzing social gatherings", "fun team presence"],
        ),
    ),
    "friendship.communication.intellectual_sparring.v1": InterpretationContract(
        interpretation_id="friendship.communication.intellectual_sparring.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="intellectual_stimulation", strength=0.80),
        meaning=InterpretationMeaning(
            type="intellectual_sparring",
            intensity="high",
            human_meaning=["challenging ideas playfully", "recommending provocative books/media", "conceptual debates"],
        ),
    ),
    "friendship.harmony.judgment_free_refuge.v1": InterpretationContract(
        interpretation_id="friendship.harmony.judgment_free_refuge.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="emotional_comfort", strength=0.85),
        meaning=InterpretationMeaning(
            type="judgment_free_refuge",
            intensity="high",
            human_meaning=["space to be completely unfiltered", "emotional safety", "embracing each other's quirks"],
        ),
    ),
    "friendship.growth.playful_rivalry.v1": InterpretationContract(
        interpretation_id="friendship.growth.playful_rivalry.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="playful_friction", strength=0.75),
        meaning=InterpretationMeaning(
            type="playful_rivalry",
            intensity="medium",
            human_meaning=["healthy competition that pushes both to grow", "roasting with love", "holding standards high"],
        ),
    ),
    "friendship.growth.opposite_strengths.v1": InterpretationContract(
        interpretation_id="friendship.growth.opposite_strengths.v1",
        context="friendship",
        signal=InterpretationSignal(category="friendship", type="complementary_personalities", strength=0.80),
        meaning=InterpretationMeaning(
            type="opposite_strengths",
            intensity="high",
            human_meaning=["covering each other's blind spots", "practical versus visionary balance", "mutual learning"],
        ),
    ),

    # =============================================================
    # 8. DAILY ENERGY (12 TRANSIT ARCHETYPE CONTRACTS)
    # Note: These represent content contracts prepared for future transit engine.
    # =============================================================
    "daily_energy.confidence.elevated.v1": InterpretationContract(
        interpretation_id="daily_energy.confidence.elevated.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="harmony", type="sun_mars_transit", strength=0.85),
        meaning=InterpretationMeaning(
            type="elevated_confidence",
            intensity="high",
            human_meaning=["surplus initiative", "decisiveness in high-visibility situations", "taking the front seat"],
        ),
    ),
    "daily_energy.communication.direct.v1": InterpretationContract(
        interpretation_id="daily_energy.communication.direct.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="communication", type="mercury_transit", strength=0.80),
        meaning=InterpretationMeaning(
            type="direct_communication",
            intensity="high",
            human_meaning=["sharp mental articulation", "low tolerance for ambiguous waffle", "rapid negotiations"],
        ),
    ),
    "daily_energy.focus.scattered.v1": InterpretationContract(
        interpretation_id="daily_energy.focus.scattered.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="growth", type="jupiter_mercury_transit", strength=0.60),
        meaning=InterpretationMeaning(
            type="scattered_focus",
            intensity="medium",
            human_meaning=["abundant divergent ideation", "deliberate focus needed to close loops", "idea overload"],
        ),
    ),
    "daily_energy.creativity.exploration.v1": InterpretationContract(
        interpretation_id="daily_energy.creativity.exploration.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="harmony", type="venus_neptune_transit", strength=0.80),
        meaning=InterpretationMeaning(
            type="creative_exploration",
            intensity="high",
            human_meaning=["imaginative flexibility", "aesthetic receptivity outside the usual routine", "fresh angles"],
        ),
    ),
    "daily_energy.clarity.strategic_patience.v1": InterpretationContract(
        interpretation_id="daily_energy.clarity.strategic_patience.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="communication", type="mercury_saturn_transit", strength=0.80),
        meaning=InterpretationMeaning(
            type="strategic_patience",
            intensity="high",
            human_meaning=["sober analytical clarity", "filtering signal from noise", "patient long-term planning"],
        ),
    ),
    "daily_energy.vitality.surging_drive.v1": InterpretationContract(
        interpretation_id="daily_energy.vitality.surging_drive.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="harmony", type="mars_jupiter_transit", strength=0.85),
        meaning=InterpretationMeaning(
            type="surging_drive",
            intensity="high",
            human_meaning=["high physical stamina", "tackling ambitious hurdles", "refusing to stay idle"],
        ),
    ),
    "daily_energy.receptivity.emotional_pause.v1": InterpretationContract(
        interpretation_id="daily_energy.receptivity.emotional_pause.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="growth", type="moon_transit_soft", strength=0.70),
        meaning=InterpretationMeaning(
            type="emotional_pause",
            intensity="medium",
            human_meaning=["lower social bandwidth", "recharging battery in quiet spaces", "observing rather than acting"],
        ),
    ),
    "daily_energy.restlessness.impulsive_edge.v1": InterpretationContract(
        interpretation_id="daily_energy.restlessness.impulsive_edge.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="growth", type="mars_uranus_transit", strength=0.75),
        meaning=InterpretationMeaning(
            type="impulsive_edge",
            intensity="high",
            human_meaning=["itching for sudden change", "craving disruption to routine", "fast unpredictable choices"],
        ),
    ),
    "daily_energy.social.magnetic_charm.v1": InterpretationContract(
        interpretation_id="daily_energy.social.magnetic_charm.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="harmony", type="sun_venus_transit", strength=0.85),
        meaning=InterpretationMeaning(
            type="magnetic_charm",
            intensity="high",
            human_meaning=["effortless social warmth", "disarming negotiations", "attracting goodwill without trying"],
        ),
    ),
    "daily_energy.discipline.grounded_execution.v1": InterpretationContract(
        interpretation_id="daily_energy.discipline.grounded_execution.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="stability", type="sun_saturn_transit", strength=0.85),
        meaning=InterpretationMeaning(
            type="grounded_execution",
            intensity="high",
            human_meaning=["getting practical tasks done", "mastering details", "quietly executing the backlog"],
        ),
    ),
    "daily_energy.introspection.deep_reset.v1": InterpretationContract(
        interpretation_id="daily_energy.introspection.deep_reset.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="growth", type="sun_pluto_transit", strength=0.75),
        meaning=InterpretationMeaning(
            type="deep_reset",
            intensity="high",
            human_meaning=["shedding obsolete habits", "confronting hard truths honestly", "quiet internal reinvention"],
        ),
    ),
    "daily_energy.curiosity.spontaneous_pivot.v1": InterpretationContract(
        interpretation_id="daily_energy.curiosity.spontaneous_pivot.v1",
        context="daily_energy",
        signal=InterpretationSignal(category="harmony", type="mercury_uranus_transit", strength=0.80),
        meaning=InterpretationMeaning(
            type="spontaneous_pivot",
            intensity="high",
            human_meaning=["unexpected lightbulb realizations", "testing fresh workflows", "cognitive breakthrough"],
        ),
    ),
}
