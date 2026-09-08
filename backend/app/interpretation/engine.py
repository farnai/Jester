"""
Deterministic Meaning Engine for Jester.
Maps structured astrological signals to semantic meaning contracts and resolves final text.
Decouples astronomical truth from user-facing copy.
"""
import hashlib
from typing import Any

from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from backend.app.interpretation.library import content_library
from backend.app.interpretation.models import (
    DeepAnalysisBlock,
    DeepAnalysisPayload,
    InterpretationContract,
    ResolvedInterpretation,
)

SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
]
ELEMENTS = ["fire", "earth", "air", "water"]
MODALITIES = ["cardinal", "fixed", "mutable"]

# Deterministic signal-type to stable interpretation-id mapping
SIGNAL_TYPE_TO_INTERPRETATION_ID: dict[str, str] = {
    # -------------------------------------------------------------
    # 1. Synastry Core Aspects
    # -------------------------------------------------------------
    # Sun - Moon
    "sun_trine_moon": "relationship.harmony.emotional_resonance.v1",
    "sun_sextile_moon": "relationship.harmony.emotional_resonance.v1",
    "sun_conjunction_moon": "relationship.harmony.emotional_resonance.v1",
    "sun_moon_harmony": "relationship.harmony.emotional_resonance.v1",
    "sun_opposite_moon": "relationship.growth.complementary_balance.v1",
    "sun_moon_opposition": "relationship.growth.complementary_balance.v1",
    "sun_square_moon": "relationship.growth.dynamic_emotional_tension.v1",
    "sun_moon_square": "relationship.growth.dynamic_emotional_tension.v1",

    # Sun - Sun
    "sun_trine_sun": "relationship.harmony.core_harmony.v1",
    "sun_sextile_sun": "relationship.harmony.core_harmony.v1",
    "sun_conjunction_sun": "relationship.harmony.core_harmony.v1",
    "sun_sun_harmony": "relationship.harmony.core_harmony.v1",
    "sun_opposite_sun": "relationship.growth.contrasting_perspectives.v1",
    "sun_sun_opposition": "relationship.growth.contrasting_perspectives.v1",
    "sun_square_sun": "relationship.growth.ego_friction.v1",
    "sun_sun_square": "relationship.growth.ego_friction.v1",

    # Venus - Mars
    "venus_conjunction_mars": "relationship.attraction.strong_chemistry.v1",
    "venus_opposite_mars": "relationship.attraction.strong_chemistry.v1",
    "venus_trine_mars": "relationship.attraction.strong_chemistry.v1",
    "venus_sextile_mars": "relationship.attraction.strong_chemistry.v1",
    "venus_square_mars": "relationship.attraction.strong_chemistry.v1",
    "venus_mars_aspect": "relationship.attraction.strong_chemistry.v1",
    "strong_chemistry": "relationship.attraction.strong_chemistry.v1",
    "magnetic_chemistry": "relationship.attraction.magnetic_chemistry.v1",

    # Sun - Venus
    "sun_conjunction_venus": "relationship.attraction.warm_affection.v1",
    "sun_trine_venus": "relationship.attraction.warm_affection.v1",
    "sun_sextile_venus": "relationship.attraction.warm_affection.v1",
    "sun_venus_harmony": "relationship.attraction.warm_affection.v1",

    # Moon - Venus
    "moon_conjunction_venus": "relationship.harmony.gentle_affinity.v1",
    "moon_trine_venus": "relationship.harmony.gentle_affinity.v1",
    "moon_sextile_venus": "relationship.harmony.gentle_affinity.v1",
    "moon_venus_harmony": "relationship.harmony.gentle_affinity.v1",
    "moon_opposite_venus": "relationship.growth.emotional_divergence.v1",
    "moon_opposition_venus": "relationship.growth.emotional_divergence.v1",
    "moon_square_venus": "relationship.growth.emotional_divergence.v1",

    # Mercury - Venus
    "mercury_venus_harmony": "relationship.attraction.aesthetic_harmony.v1",
    "mercury_trine_venus": "relationship.attraction.aesthetic_harmony.v1",
    "mercury_sextile_venus": "relationship.attraction.aesthetic_harmony.v1",
    "mercury_conjunction_venus": "relationship.attraction.aesthetic_harmony.v1",

    # Moon - Ascendant
    "ascendant_trine_moon": "relationship.harmony.deep_empathy.v1",
    "ascendant_conjunction_moon": "relationship.harmony.deep_empathy.v1",
    "ascendant_sextile_moon": "relationship.harmony.deep_empathy.v1",
    "moon_ascendant_harmony": "relationship.harmony.deep_empathy.v1",

    # Sun - Ascendant
    "ascendant_trine_sun": "relationship.attraction.bold_momentum.v1",
    "ascendant_conjunction_sun": "relationship.attraction.bold_momentum.v1",
    "sun_ascendant_harmony": "relationship.attraction.bold_momentum.v1",

    "mercury_trine_mercury": "relationship.communication.intellectual_flow.v1",
    "mercury_sextile_mercury": "relationship.communication.intellectual_flow.v1",
    "mercury_conjunction_mercury": "relationship.communication.intellectual_flow.v1",
    "mercury_mercury_harmony": "relationship.communication.intellectual_flow.v1",

    # Sun - Mercury
    "sun_trine_mercury": "relationship.communication.mutual_understanding.v1",
    "sun_sextile_mercury": "relationship.communication.mutual_understanding.v1",
    "sun_conjunction_mercury": "relationship.communication.mutual_understanding.v1",
    "sun_mercury_harmony": "relationship.communication.mutual_understanding.v1",

    # Saturn Squares
    "mars_square_saturn": "relationship.growth.pacing_tension.v1",
    "sun_square_saturn": "relationship.growth.pacing_tension.v1",
    "moon_square_saturn": "relationship.growth.pacing_tension.v1",
    "saturn_square_personal": "relationship.growth.pacing_tension.v1",

    # Mars - Sun
    "mars_square_sun": "relationship.growth.dynamic_spark.v1",
    "sun_square_mars": "relationship.growth.dynamic_spark.v1",
    "sun_trine_mars": "relationship.attraction.energized_collaboration.v1",
    "sun_conjunction_mars": "relationship.attraction.dynamic_drive.v1",

    # Jupiter Aspects
    "sun_trine_jupiter": "relationship.stability.shared_optimism.v1",
    "sun_conjunction_jupiter": "relationship.stability.shared_optimism.v1",
    "moon_trine_jupiter": "relationship.stability.shared_optimism.v1",
    "jupiter_harmony": "relationship.stability.shared_optimism.v1",
    "venus_trine_jupiter": "relationship.harmony.generous_affection.v1",
    "venus_conjunction_jupiter": "relationship.harmony.generous_affection.v1",
    "venus_jupiter_harmony": "relationship.harmony.generous_affection.v1",

    # Venus - Pluto
    "venus_trine_pluto": "relationship.attraction.intense_magnetism.v1",
    "venus_conjunction_pluto": "relationship.attraction.intense_magnetism.v1",
    "venus_opposite_pluto": "relationship.attraction.intense_magnetism.v1",
    "venus_pluto_aspect": "relationship.attraction.intense_magnetism.v1",

    # Saturn Trines
    "saturn_trine_sun": "relationship.stability.long_term_grounding.v1",
    "saturn_trine_moon": "relationship.stability.long_term_grounding.v1",
    "saturn_trine_venus": "relationship.stability.long_term_grounding.v1",
    "saturn_trine_personal": "relationship.stability.long_term_grounding.v1",

    # Notice & Macro
    "insufficient_aspects": "relationship.notice.independent_dynamics.v1",
    "score_high": "relationship.overall.exceptional_flow.v1",
    "score_balanced": "relationship.overall.balanced_synergy.v1",
    "score_growth": "relationship.overall.stimulating_friction.v1",
    "score_independent": "relationship.overall.independent_paths.v1",

    # -------------------------------------------------------------
    # 2. Expanded Engine-Supported Synastry Aspects
    # -------------------------------------------------------------
    "mars_mars_friction": "relationship.attraction.mars_friction.v1",
    "mars_square_mars": "relationship.attraction.mars_friction.v1",
    "mars_opposite_mars": "relationship.attraction.mars_friction.v1",
    "mars_conjunction_mars": "relationship.attraction.mars_friction.v1",

    "venus_uranus_aspect": "relationship.attraction.electric_fascination.v1",
    "venus_trine_uranus": "relationship.attraction.electric_fascination.v1",
    "venus_square_uranus": "relationship.attraction.electric_fascination.v1",
    "venus_opposite_uranus": "relationship.attraction.electric_fascination.v1",
    "venus_conjunction_uranus": "relationship.attraction.electric_fascination.v1",

    "moon_mars_attraction": "relationship.attraction.instinctive_heat.v1",
    "moon_trine_mars": "relationship.attraction.instinctive_heat.v1",
    "moon_square_mars": "relationship.attraction.instinctive_heat.v1",
    "moon_opposite_mars": "relationship.attraction.instinctive_heat.v1",
    "moon_conjunction_mars": "relationship.attraction.instinctive_heat.v1",

    "venus_venus_harmony": "relationship.attraction.aesthetic_harmony.v1",
    "venus_trine_venus": "relationship.attraction.aesthetic_harmony.v1",
    "venus_sextile_venus": "relationship.attraction.aesthetic_harmony.v1",
    "venus_conjunction_venus": "relationship.attraction.aesthetic_harmony.v1",

    "venus_ascendant_harmony": "relationship.attraction.magnetic_presence.v1",
    "venus_trine_ascendant": "relationship.attraction.magnetic_presence.v1",
    "venus_conjunction_ascendant": "relationship.attraction.magnetic_presence.v1",

    "mars_ascendant_aspect": "relationship.attraction.bold_momentum.v1",
    "mars_trine_ascendant": "relationship.attraction.bold_momentum.v1",
    "mars_conjunction_ascendant": "relationship.attraction.bold_momentum.v1",

    "moon_moon_harmony": "relationship.harmony.deep_empathy.v1",
    "moon_trine_moon": "relationship.harmony.deep_empathy.v1",
    "moon_sextile_moon": "relationship.harmony.deep_empathy.v1",
    "moon_conjunction_moon": "relationship.harmony.deep_empathy.v1",

    "moon_neptune_aspect": "relationship.harmony.intuitive_communion.v1",
    "moon_trine_neptune": "relationship.harmony.intuitive_communion.v1",
    "moon_conjunction_neptune": "relationship.harmony.intuitive_communion.v1",

    "moon_pluto_aspect": "relationship.harmony.transformative_depth.v1",
    "moon_trine_pluto": "relationship.harmony.transformative_depth.v1",
    "moon_conjunction_pluto": "relationship.harmony.transformative_depth.v1",

    "moon_moon_contrast": "relationship.growth.emotional_divergence.v1",
    "moon_square_moon": "relationship.growth.emotional_divergence.v1",
    "moon_opposite_moon": "relationship.growth.emotional_divergence.v1",
    "moon_opposition_moon": "relationship.growth.emotional_divergence.v1",

    "mercury_moon_harmony": "relationship.communication.intuitive_listening.v1",
    "mercury_trine_moon": "relationship.communication.intuitive_listening.v1",
    "mercury_sextile_moon": "relationship.communication.intuitive_listening.v1",
    "mercury_conjunction_moon": "relationship.communication.intuitive_listening.v1",

    "mercury_mars_aspect": "relationship.communication.sharp_debate.v1",
    "mercury_trine_mars": "relationship.communication.sharp_debate.v1",
    "mercury_square_mars": "relationship.communication.sharp_debate.v1",
    "mercury_opposite_mars": "relationship.communication.sharp_debate.v1",

    "mercury_saturn_aspect": "relationship.communication.grounded_deliberation.v1",
    "mercury_trine_saturn": "relationship.communication.grounded_deliberation.v1",
    "mercury_square_saturn": "relationship.communication.grounded_deliberation.v1",

    "mercury_uranus_aspect": "relationship.communication.unconventional_spark.v1",
    "mercury_trine_uranus": "relationship.communication.unconventional_spark.v1",
    "mercury_conjunction_uranus": "relationship.communication.unconventional_spark.v1",

    "mars_pluto_aspect": "relationship.growth.power_clash.v1",
    "mars_square_pluto": "relationship.growth.power_clash.v1",
    "mars_opposite_pluto": "relationship.growth.power_clash.v1",
    "mars_conjunction_pluto": "relationship.growth.power_clash.v1",

    "venus_saturn_aspect": "relationship.growth.sobering_realism.v1",
    "venus_square_saturn": "relationship.growth.sobering_realism.v1",
    "venus_opposite_saturn": "relationship.growth.sobering_realism.v1",

    "mars_saturn_tension": "relationship.growth.strategic_resistance.v1",
    "mars_opposite_saturn": "relationship.growth.strategic_resistance.v1",

    "sun_jupiter_expansion": "relationship.growth.limitless_ambition.v1",
    "sun_square_jupiter": "relationship.growth.limitless_ambition.v1",
    "sun_opposite_jupiter": "relationship.growth.limitless_ambition.v1",

    "moon_jupiter_harmony": "relationship.stability.generous_comfort.v1",
    "moon_sextile_jupiter": "relationship.stability.generous_comfort.v1",
    "moon_conjunction_jupiter": "relationship.stability.generous_comfort.v1",

    "sun_saturn_grounding": "relationship.stability.architectural_anchor.v1",
    "sun_conjunction_saturn": "relationship.stability.architectural_anchor.v1",
    "sun_sextile_saturn": "relationship.stability.architectural_anchor.v1",

    # -------------------------------------------------------------
    # 3. Dedicated Friendship Signals
    # -------------------------------------------------------------
    "friendship_chemistry": "friendship.chemistry.instant_rapport.v1",
    "conversational_ease": "friendship.communication.effortless_banter.v1",
    "shared_humor": "friendship.communication.shared_absurdity.v1",
    "social_rhythm": "friendship.harmony.synchronous_pace.v1",
    "mutual_support": "friendship.stability.unconditional_cushion.v1",
    "trust": "friendship.stability.quiet_loyalty.v1",
    "independence": "friendship.notice.autonomous_bond.v1",
    "group_compatibility": "friendship.social.crew_catalyst.v1",
    "intellectual_stimulation": "friendship.communication.intellectual_sparring.v1",
    "emotional_comfort": "friendship.harmony.judgment_free_refuge.v1",
    "playful_friction": "friendship.growth.playful_rivalry.v1",
    "complementary_personalities": "friendship.growth.opposite_strengths.v1",

    # -------------------------------------------------------------
    # 4. Daily Energy Transit Archetype Signals
    # -------------------------------------------------------------
    "sun_mars_transit": "daily_energy.confidence.elevated.v1",
    "mercury_transit": "daily_energy.communication.direct.v1",
    "jupiter_mercury_transit": "daily_energy.focus.scattered.v1",
    "venus_neptune_transit": "daily_energy.creativity.exploration.v1",
    "mercury_saturn_transit": "daily_energy.clarity.strategic_patience.v1",
    "mars_jupiter_transit": "daily_energy.vitality.surging_drive.v1",
    "moon_transit_soft": "daily_energy.receptivity.emotional_pause.v1",
    "mars_uranus_transit": "daily_energy.restlessness.impulsive_edge.v1",
    "sun_venus_transit": "daily_energy.social.magnetic_charm.v1",
    "sun_saturn_transit": "daily_energy.discipline.grounded_execution.v1",
    "sun_pluto_transit": "daily_energy.introspection.deep_reset.v1",
    "mercury_uranus_transit": "daily_energy.curiosity.spontaneous_pivot.v1",
}

# Add Self / Me Natal Mappings (Sun, Moon, Rising, Elements, Modalities)
for _s in SIGNS:
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"sun_sign_{_s}"] = f"self.identity.sun_{_s}.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"sun_{_s}"] = f"self.identity.sun_{_s}.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"moon_sign_{_s}"] = f"self.emotional.moon_{_s}.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"moon_{_s}"] = f"self.emotional.moon_{_s}.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"ascendant_sign_{_s}"] = f"self.persona.rising_{_s}.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"rising_{_s}"] = f"self.persona.rising_{_s}.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"mercury_sign_{_s}"] = f"self.cognition.mercury_{_s}.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"mercury_{_s}"] = f"self.cognition.mercury_{_s}.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"venus_sign_{_s}"] = f"self.relation.venus_{_s}.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"venus_{_s}"] = f"self.relation.venus_{_s}.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"mars_sign_{_s}"] = f"self.action.mars_{_s}.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"mars_{_s}"] = f"self.action.mars_{_s}.v1"

for _e in ELEMENTS:
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"element_dominant_{_e}"] = f"self.element.{_e}_dominant.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"element_{_e}"] = f"self.element.{_e}_dominant.v1"

for _m in MODALITIES:
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"modality_dominant_{_m}"] = f"self.modality.{_m}_dominant.v1"
    SIGNAL_TYPE_TO_INTERPRETATION_ID[f"modality_{_m}"] = f"self.modality.{_m}_dominant.v1"


class InterpretationEngine:
    """
    Deterministic translation engine converting astronomical signals into human meaning and user copy.
    """
    def __init__(self) -> None:
        self.library = content_library

    def get_contract(self, interpretation_id: str) -> InterpretationContract | None:
        """Returns the formal contract definition for a given interpretation ID."""
        return INTERPRETATION_CONTRACTS.get(interpretation_id)

    def signal_to_interpretation_id(self, signal_type: str) -> str | None:
        """
        Maps a deterministic signal identifier (from compatibility rules or natal) to a content interpretation ID.
        Returns None if signal is unrecognized, strictly preventing hallucinated meanings.
        """
        return SIGNAL_TYPE_TO_INTERPRETATION_ID.get(signal_type.lower())

    def resolve_signal(
        self,
        signal: dict[str, Any],
        context: str | None = None,
        locale: str = "ka",
        tone: str | None = None,
        persona: str = "jester",
        variant_key: str | None = None,
        seed: str | None = None,
        exclude_asset_ids: set[str] | None = None,
    ) -> ResolvedInterpretation | None:
        """
        Resolves a single signal dictionary into a user-facing ResolvedInterpretation
        using Content Architecture V2 multi-asset resolution.
        """
        sig_type = signal.get("type", "")
        interp_id = self.signal_to_interpretation_id(sig_type)
        if not interp_id:
            return None

        # Resolve via V2 multi-asset resolver
        resolved = self.library.resolve(
            interpretation_id=interp_id,
            context=context,
            locale=locale,
            tone=tone,
            persona=persona,
            variant_key=variant_key,
            seed=seed,
            exclude_asset_ids=exclude_asset_ids,
        )
        if resolved:
            return resolved

        # Fallback to legacy resolve_text
        return self.library.resolve_text(interp_id)

    def resolve_signals(
        self,
        signals: list[dict[str, Any]],
        context: str | None = None,
        locale: str = "ka",
        tone: str | None = None,
        seed: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Enriches a list of compatibility signals with structured interpretation data.
        Does not mutate input in place; returns a new enriched list.
        """
        enriched: list[dict[str, Any]] = []
        for sig in signals:
            item = dict(sig)
            resolved = self.resolve_signal(
                signal=sig,
                context=context or sig.get("category"),
                locale=locale,
                tone=tone,
                seed=seed,
            )
            if resolved:
                item["interpretation"] = resolved.model_dump()
                item["interpretation_id"] = resolved.id
            enriched.append(item)
        return enriched

    def resolve_natal_profile(
        self,
        profile: Any,
        locale: str = "ka",
        tone: str | None = None,
        seed: str | None = None,
    ) -> list[ResolvedInterpretation]:
        """
        Deterministic resolution of a user's SafeDerivedAstrology profile into Self/Me interpretations:
        - Sun sign identity
        - Moon sign emotional processing
        - Ascendant social persona (if known)
        - Dominant element
        - Dominant modality
        """
        # Handle dict or Pydantic model
        if hasattr(profile, "model_dump"):
            data = profile.model_dump()
        elif isinstance(profile, dict):
            data = profile
        else:
            data = vars(profile)

        results: list[ResolvedInterpretation] = []

        sun = data.get("sun_sign")
        if sun:
            res = self.library.resolve(
                interpretation_id=f"self.identity.sun_{sun.lower()}.v1",
                context="self",
                locale=locale,
                tone=tone,
                seed=seed,
            )
            if res:
                results.append(res)

        moon = data.get("moon_sign")
        if moon:
            res = self.library.resolve(
                interpretation_id=f"self.emotional.moon_{moon.lower()}.v1",
                context="self",
                locale=locale,
                tone=tone,
                seed=seed,
            )
            if res:
                results.append(res)

        rising = data.get("ascendant_sign")
        if rising:
            res = self.library.resolve(
                interpretation_id=f"self.persona.rising_{rising.lower()}.v1",
                context="self",
                locale=locale,
                tone=tone,
                seed=seed,
            )
            if res:
                results.append(res)

        mercury = data.get("mercury_sign")
        if mercury:
            res = self.library.resolve(
                interpretation_id=f"self.cognition.mercury_{mercury.lower()}.v1",
                context="self",
                locale=locale,
                tone=tone,
                seed=seed,
            )
            if res:
                results.append(res)

        venus = data.get("venus_sign")
        if venus:
            res = self.library.resolve(
                interpretation_id=f"self.relation.venus_{venus.lower()}.v1",
                context="self",
                locale=locale,
                tone=tone,
                seed=seed,
            )
            if res:
                results.append(res)

        mars = data.get("mars_sign")
        if mars:
            res = self.library.resolve(
                interpretation_id=f"self.action.mars_{mars.lower()}.v1",
                context="self",
                locale=locale,
                tone=tone,
                seed=seed,
            )
            if res:
                results.append(res)

        elem = data.get("element_primary")
        if elem:
            res = self.library.resolve(
                interpretation_id=f"self.element.{elem.lower()}_dominant.v1",
                context="self",
                locale=locale,
                tone=tone,
                seed=seed,
            )
            if res:
                results.append(res)

        mod = data.get("modality_primary")
        if mod:
            res = self.library.resolve(
                interpretation_id=f"self.modality.{mod.lower()}_dominant.v1",
                context="self",
                locale=locale,
                tone=tone,
                seed=seed,
            )
            if res:
                results.append(res)

        return results

    def get_primary_relationship_interpretation(
        self,
        score: float,
        signals: list[dict[str, Any]],
        context: str = "relationship",
        locale: str = "ka",
        tone: str | None = None,
        seed: str | None = None,
        used_interpretation_ids: set[str] | None = None,
        used_signal_types: set[str] | None = None,
        used_asset_ids: set[str] | None = None,
    ) -> ResolvedInterpretation:
        """
        Synthesizes the overarching primary relationship interpretation based on
        overall compatibility score tier and highest-importance signal.
        Supports feed-level deduplication across candidates via used_interpretation_ids,
        used_signal_types, and used_asset_ids while strictly preserving astrological truth.
        """
        if signals:
            resolvable_signals: list[dict[str, Any]] = []
            for sig in signals:
                sig_type = sig.get("type", "")
                interp_id = self.signal_to_interpretation_id(sig_type)
                if interp_id and self.library.list_assets(interpretation_id=interp_id, locale=locale or "ka"):
                    resolvable_signals.append(sig)

            if resolvable_signals:
                has_feed_tracking = (
                    used_interpretation_ids is not None
                    or used_signal_types is not None
                    or used_asset_ids is not None
                )

                if has_feed_tracking:
                    # Deduplication Priority 1 & 2:
                    # Find highest-ranking signal whose interpretation ID and signal type
                    # have NOT been used in the feed.
                    chosen_signal = None
                    for sig in resolvable_signals:
                        st = sig.get("type", "").lower()
                        iid = self.signal_to_interpretation_id(st)
                        if not iid:
                            continue
                        if used_interpretation_ids is not None and iid in used_interpretation_ids:
                            continue
                        if used_signal_types is not None and st in used_signal_types:
                            continue
                        chosen_signal = sig
                        break

                    if chosen_signal:
                        resolved = self.resolve_signal(
                            signal=chosen_signal,
                            context=context,
                            locale=locale,
                            tone=tone,
                            seed=seed,
                            exclude_asset_ids=used_asset_ids,
                        )
                        if resolved:
                            if used_interpretation_ids is not None:
                                used_interpretation_ids.add(resolved.id)
                            if used_signal_types is not None:
                                used_signal_types.add(chosen_signal.get("type", "").lower())
                            if used_asset_ids is not None and resolved.content_asset_id:
                                used_asset_ids.add(resolved.content_asset_id)
                            return resolved

                    # Deduplication Priority 3:
                    # If all signals map to already-used interpretation contracts, find the
                    # highest-ranking signal that has an unused content asset variant in the corpus.
                    if used_asset_ids is not None:
                        for sig in resolvable_signals:
                            st = sig.get("type", "").lower()
                            iid = self.signal_to_interpretation_id(st)
                            if not iid:
                                continue
                            assets = self.library.list_assets(interpretation_id=iid, locale=locale or "ka")
                            unused = [
                                a for a in assets
                                if a.asset_id not in used_asset_ids
                                and (a.context == context or a.context == "relationship")
                                and a.text and a.text.strip()
                            ]
                            if unused:
                                resolved = self.resolve_signal(
                                    signal=sig,
                                    context=context,
                                    locale=locale,
                                    tone=tone,
                                    seed=seed,
                                    exclude_asset_ids=used_asset_ids,
                                )
                                if resolved:
                                    if used_interpretation_ids is not None:
                                        used_interpretation_ids.add(resolved.id)
                                    if used_signal_types is not None:
                                        used_signal_types.add(st)
                                    if used_asset_ids is not None and resolved.content_asset_id:
                                        used_asset_ids.add(resolved.content_asset_id)
                                    return resolved

                    # Deduplication Priority 4:
                    # All variants across all candidate signals are exhausted in this feed.
                    # Fall back to deterministic selection without fabricating non-existent aspects.
                    top_slice = resolvable_signals[:3]
                    if len(top_slice) == 1 or not seed:
                        chosen_signal = top_slice[0]
                    else:
                        hash_val = int(hashlib.sha256(f"{seed}:hook_signal_select".encode()).hexdigest(), 16)
                        chosen_signal = top_slice[hash_val % len(top_slice)]

                    resolved = self.resolve_signal(
                        signal=chosen_signal,
                        context=context,
                        locale=locale,
                        tone=tone,
                        seed=seed,
                    )
                    if resolved:
                        if used_interpretation_ids is not None:
                            used_interpretation_ids.add(resolved.id)
                        if used_signal_types is not None:
                            used_signal_types.add(chosen_signal.get("type", "").lower())
                        if used_asset_ids is not None and resolved.content_asset_id:
                            used_asset_ids.add(resolved.content_asset_id)
                        return resolved

                else:
                    # Non-feed / single-comparison evaluation (preserving exact existing behavior)
                    top_slice = resolvable_signals[:3]
                    if len(top_slice) == 1 or not seed:
                        chosen_signal = top_slice[0]
                    else:
                        hash_val = int(hashlib.sha256(f"{seed}:hook_signal_select".encode()).hexdigest(), 16)
                        chosen_signal = top_slice[hash_val % len(top_slice)]

                    resolved = self.resolve_signal(
                        signal=chosen_signal,
                        context=context,
                        locale=locale,
                        tone=tone,
                        seed=seed,
                    )
                    if resolved:
                        return resolved

        # Fallback to holistic score bracket
        if score >= 85.0:
            interp_id = "relationship.overall.exceptional_flow.v1"
        elif score >= 70.0:
            interp_id = "relationship.overall.balanced_synergy.v1"
        elif score >= 50.0:
            interp_id = "relationship.overall.stimulating_friction.v1"
        else:
            interp_id = "relationship.overall.independent_paths.v1"

        resolved = self.library.resolve(
            interpretation_id=interp_id,
            context=context,
            locale=locale,
            tone=tone,
            seed=seed,
            exclude_asset_ids=used_asset_ids,
        ) or self.library.resolve_text(interp_id)

        if resolved:
            if used_interpretation_ids is not None:
                used_interpretation_ids.add(resolved.id)
            if used_asset_ids is not None and resolved.content_asset_id:
                used_asset_ids.add(resolved.content_asset_id)
            return resolved

        # Safety fallback
        return ResolvedInterpretation(
            id=interp_id,
            text="საინტერესო კავშირია — დაკვირვება და ურთიერთგაგება საუკეთესო შედეგს მოიტანს.",
            content_status="ai_draft",
            language=locale,
            locale=locale,
            context=context,
        )

    def build_deep_analysis_payload(
        self,
        score: float,
        signals: list[dict[str, Any]],
        evidence_trace: list[dict[str, Any]] | None = None,
        confidence: float = 1.0,
        locale: str = "ka",
        tone: str | None = None,
        seed: str | None = None,
    ) -> DeepAnalysisPayload:
        """
        Deep Analysis architectural pipeline:
        Synastry Evidence -> Ranked Signals -> Interpretation Contracts -> JESTER Voice -> Deep Analysis narrative blocks.
        Traceability to deterministic evidence is strictly preserved.
        """
        primary = self.get_primary_relationship_interpretation(
            score=score,
            signals=signals,
            context="deep_analysis",
            locale=locale,
            tone=tone,
            seed=seed,
        )
        blocks: list[DeepAnalysisBlock] = []

        for sig in signals:
            resolved = self.resolve_signal(
                signal=sig,
                context="deep_analysis",
                locale=locale,
                tone=tone,
                seed=seed,
            )
            if resolved:
                contract = self.get_contract(resolved.id)
                dim = contract.signal.category if contract else (sig.get("category") or "connection")
                blocks.append(
                    DeepAnalysisBlock(
                        interpretation_id=resolved.id,
                        dimension=dim,
                        resolved_text=resolved.text,
                        evidence_aspects=sig.get("source_aspects") or [],
                        content_status=resolved.content_status,
                        content_asset_id=resolved.content_asset_id,
                        tone=resolved.tone,
                    )
                )

        return DeepAnalysisPayload(
            primary_interpretation=primary,
            blocks=blocks,
            overall_score=score,
            data_confidence=confidence,
        )

    def resolve_daily_energy(
        self,
        energy_type: str,
        locale: str = "ka",
        tone: str | None = None,
        seed: str | None = None,
    ) -> ResolvedInterpretation | None:
        """
        Resolves a daily energy transit archetype into an interpretation.
        """
        valid_map = {
            "confidence": "daily_energy.confidence.elevated.v1",
            "communication": "daily_energy.communication.direct.v1",
            "focus": "daily_energy.focus.scattered.v1",
            "creativity": "daily_energy.creativity.exploration.v1",
            "clarity": "daily_energy.clarity.strategic_patience.v1",
            "vitality": "daily_energy.vitality.surging_drive.v1",
            "receptivity": "daily_energy.receptivity.emotional_pause.v1",
            "restlessness": "daily_energy.restlessness.impulsive_edge.v1",
            "social": "daily_energy.social.magnetic_charm.v1",
            "discipline": "daily_energy.discipline.grounded_execution.v1",
            "introspection": "daily_energy.introspection.deep_reset.v1",
            "curiosity": "daily_energy.curiosity.spontaneous_pivot.v1",
            "sun_mars_transit": "daily_energy.confidence.elevated.v1",
            "mercury_transit": "daily_energy.communication.direct.v1",
            "jupiter_mercury_transit": "daily_energy.focus.scattered.v1",
            "venus_neptune_transit": "daily_energy.creativity.exploration.v1",
            "mercury_saturn_transit": "daily_energy.clarity.strategic_patience.v1",
            "mars_jupiter_transit": "daily_energy.vitality.surging_drive.v1",
            "moon_transit_soft": "daily_energy.receptivity.emotional_pause.v1",
            "mars_uranus_transit": "daily_energy.restlessness.impulsive_edge.v1",
            "sun_venus_transit": "daily_energy.social.magnetic_charm.v1",
            "sun_saturn_transit": "daily_energy.discipline.grounded_execution.v1",
            "sun_pluto_transit": "daily_energy.introspection.deep_reset.v1",
            "mercury_uranus_transit": "daily_energy.curiosity.spontaneous_pivot.v1",
        }
        interp_id = valid_map.get(energy_type.lower())
        if not interp_id:
            return None

        return self.library.resolve(
            interpretation_id=interp_id,
            context="daily_energy",
            locale=locale,
            tone=tone,
            seed=seed,
        ) or self.library.resolve_text(interp_id)


# Global singleton engine
interpretation_engine = InterpretationEngine()
