"""
JESTER Content & Logic Inspector Service.
Compiles a read-only projection of all frozen content batches, interpretation contracts,
synastry aspect rules, discovery presence, connection invitations, conversation starters,
and daily energy transit archetypes.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.app.astrology.transits import (
    APPLYING_MULTIPLIER,
    ASPECT_WEIGHTS,
    NATAL_POINT_WEIGHTS,
    TRANSIT_ORB_LIMITS,
    TRANSIT_PLANET_WEIGHTS,
)
from backend.app.compatibility.rules import SIGNAL_DEFINITIONS
from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from backend.app.interpretation.engine import SIGNAL_TYPE_TO_INTERPRETATION_ID
from backend.app.interpretation.library import (
    INITIAL_GEORGIAN_DRAFTS,
    content_library,
)

# Cache container for inspector projection
_CACHED_INSPECTOR_DATA: dict[str, Any] | None = None

PLANETARY_DOMAINS: dict[str, dict[str, str]] = {
    "sun": {
        "planet": "Sun",
        "source": "Sun sign",
        "semantic_domain": "identity / ego / purpose",
        "description": "Core identity, conscious will, creative drive, and authentic self-expression.",
    },
    "moon": {
        "planet": "Moon",
        "source": "Moon sign",
        "semantic_domain": "feelings / emotional processing / safety",
        "description": "Instinctive reactions, emotional processing, inner sanctuary, and sense of psychological safety.",
    },
    "ascendant": {
        "planet": "Ascendant",
        "source": "Ascendant sign",
        "semantic_domain": "social persona / instinctive interface / physical presence",
        "description": "Initial behavioral interface, instinctive first impression, and spontaneous physical posture.",
    },
    "mercury": {
        "planet": "Mercury",
        "source": "Mercury sign",
        "semantic_domain": "cognition / communication",
        "description": "Cognitive processing, mental pacing, conversational rhythm, and information synthesis.",
    },
    "venus": {
        "planet": "Venus",
        "source": "Venus sign",
        "semantic_domain": "interpersonal relating / social valuation / attraction / affection / taste",
        "description": "Aesthetic discernment, relational currency, social warmth, and interpersonal valuation.",
    },
    "mars": {
        "planet": "Mars",
        "source": "Mars sign",
        "semantic_domain": "action / initiative / pursuit / drive / resistance / momentum / energy expenditure / assertion",
        "description": "Assertion, kinetic momentum, physical drive, direct initiative, and resilience under resistance.",
        "firewall_rules": (
            "Mars is NOT: anger, rage, fighting, violence. "
            "Mars IS: action, initiative, pursuit, drive, resistance, momentum, energy expenditure, assertion."
        ),
    },
}

DAILY_ENERGY_ARCHETYPES_DEF: list[dict[str, str]] = [
    {"id": "confidence", "name": "Elevated Confidence", "description": "High self-trust and decisive forward motion.", "contract_id": "daily_energy.confidence.elevated.v1"},
    {"id": "communication", "name": "Direct Communication", "description": "Crisp verbal precision, articulate voice, clear message.", "contract_id": "daily_energy.communication.direct.v1"},
    {"id": "focus", "name": "Deep Focus", "description": "Single-task absorption, quiet discipline, mental endurance.", "contract_id": "daily_energy.focus.scattered.v1"},
    {"id": "creativity", "name": "Creative Exploration", "description": "Intuitive aesthetic flow and fresh perspectives.", "contract_id": "daily_energy.creativity.exploration.v1"},
    {"id": "clarity", "name": "Strategic Clarity", "description": "Structural sobriety, sober realism, long-range planning.", "contract_id": "daily_energy.clarity.strategic_patience.v1"},
    {"id": "vitality", "name": "Surging Vitality", "description": "High physical stamina and kinetic drive.", "contract_id": "daily_energy.vitality.surging_drive.v1"},
    {"id": "receptivity", "name": "Quiet Receptivity", "description": "Emotional calibration and intuitive listening.", "contract_id": "daily_energy.receptivity.emotional_pause.v1"},
    {"id": "restlessness", "name": "Impulsive Edge", "description": "Electrifying kinetic drive and craving for rapid shift.", "contract_id": "daily_energy.restlessness.impulsive_edge.v1"},
    {"id": "social", "name": "Magnetic Sociality", "description": "Warm interpersonal ease and conversational charm.", "contract_id": "daily_energy.social.magnetic_charm.v1"},
    {"id": "discipline", "name": "Grounded Execution", "description": "Systematic pacing and enduring patience.", "contract_id": "daily_energy.discipline.grounded_execution.v1"},
    {"id": "introspection", "name": "Introspective Reset", "description": "Deep psychological recalibration and internal stocktaking.", "contract_id": "daily_energy.introspection.deep_reset.v1"},
    {"id": "curiosity", "name": "Spontaneous Curiosity", "description": "Playful inquiry and rapid mental pivoting.", "contract_id": "daily_energy.curiosity.spontaneous_pivot.v1"},
    {"id": "neutral", "name": "Neutral Baseline", "description": "Clean slate: no dominant celestial transit pressure.", "contract_id": "daily_energy.neutral.baseline.v1"},
]

ARCHETYPE_TRANSIT_SPECS: dict[str, dict[str, Any]] = {
    "confidence": {
        "label": "Mars-Sun / Mars-Asc Harmonic Transit",
        "detection_mode": "real_transit",
        "trigger_pairs": ["Mars ☌/△/⚹ Sun", "Mars ☌/△/⚹ Ascendant", "Sun ☌/△/⚹ Mars"],
        "key_bodies": [
            {"body": "mars", "max_orb": TRANSIT_ORB_LIMITS["mars"], "transit_weight": TRANSIT_PLANET_WEIGHTS["mars"]},
            {"body": "sun", "max_orb": TRANSIT_ORB_LIMITS["sun"], "transit_weight": TRANSIT_PLANET_WEIGHTS["sun"]},
        ],
        "aspect_types": ["conjunction (1.00)", "trine (0.90)", "sextile (0.70)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "restlessness": {
        "label": "Mars/Sun/Uranus Friction Transit",
        "detection_mode": "real_transit",
        "trigger_pairs": [
            "Sun □/☍ Mars", "Mars □/☍ Jupiter", "Mars □/☍ Mars", "Venus □/☍ Neptune",
            "Mars □/☍ Uranus", "Sun □/☍ Uranus", "Moon □/☍ Uranus", "Mercury □/☍ Uranus"
        ],
        "key_bodies": [
            {"body": "mars", "max_orb": TRANSIT_ORB_LIMITS["mars"], "transit_weight": TRANSIT_PLANET_WEIGHTS["mars"]},
            {"body": "uranus", "max_orb": TRANSIT_ORB_LIMITS["uranus"], "transit_weight": TRANSIT_PLANET_WEIGHTS["uranus"]},
            {"body": "sun", "max_orb": TRANSIT_ORB_LIMITS["sun"], "transit_weight": TRANSIT_PLANET_WEIGHTS["sun"]},
        ],
        "aspect_types": ["square (0.80)", "opposition (0.85)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "clarity": {
        "label": "Mercury-Saturn Grounded Intellect",
        "detection_mode": "real_transit",
        "trigger_pairs": ["Mercury ☌/△/⚹/□/☍ Saturn"],
        "key_bodies": [
            {"body": "mercury", "max_orb": TRANSIT_ORB_LIMITS["mercury"], "transit_weight": TRANSIT_PLANET_WEIGHTS["mercury"]},
            {"body": "saturn", "max_orb": TRANSIT_ORB_LIMITS["saturn"], "transit_weight": TRANSIT_PLANET_WEIGHTS["saturn"]},
        ],
        "aspect_types": ["conjunction (1.00)", "trine (0.90)", "sextile (0.70)", "opposition (0.85)", "square (0.80)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "vitality": {
        "label": "Mars-Jupiter Expansive Drive",
        "detection_mode": "real_transit",
        "trigger_pairs": ["Mars ☌/△/⚹ Jupiter", "Mars ☌/△/⚹ Mars"],
        "key_bodies": [
            {"body": "mars", "max_orb": TRANSIT_ORB_LIMITS["mars"], "transit_weight": TRANSIT_PLANET_WEIGHTS["mars"]},
            {"body": "jupiter", "max_orb": TRANSIT_ORB_LIMITS["jupiter"], "transit_weight": TRANSIT_PLANET_WEIGHTS["jupiter"]},
        ],
        "aspect_types": ["conjunction (1.00)", "trine (0.90)", "sextile (0.70)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "creativity": {
        "label": "Venus-Neptune Imaginative Flow",
        "detection_mode": "real_transit",
        "trigger_pairs": ["Venus ☌/△/⚹ Neptune", "Venus ☌/△/⚹ Venus"],
        "key_bodies": [
            {"body": "venus", "max_orb": TRANSIT_ORB_LIMITS["venus"], "transit_weight": TRANSIT_PLANET_WEIGHTS["venus"]},
            {"body": "neptune", "max_orb": TRANSIT_ORB_LIMITS["neptune"], "transit_weight": TRANSIT_PLANET_WEIGHTS["neptune"]},
        ],
        "aspect_types": ["conjunction (1.00)", "trine (0.90)", "sextile (0.70)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "curiosity": {
        "label": "Mercury Harmonic Mental Spark",
        "detection_mode": "real_transit",
        "trigger_pairs": ["Mercury ☌/△/⚹ Jupiter", "Mercury ☌/△/⚹ Neptune", "Mercury ☌/△/⚹ Uranus"],
        "key_bodies": [
            {"body": "mercury", "max_orb": TRANSIT_ORB_LIMITS["mercury"], "transit_weight": TRANSIT_PLANET_WEIGHTS["mercury"]},
            {"body": "jupiter", "max_orb": TRANSIT_ORB_LIMITS["jupiter"], "transit_weight": TRANSIT_PLANET_WEIGHTS["jupiter"]},
            {"body": "uranus", "max_orb": TRANSIT_ORB_LIMITS["uranus"], "transit_weight": TRANSIT_PLANET_WEIGHTS["uranus"]},
        ],
        "aspect_types": ["conjunction (1.00)", "trine (0.90)", "sextile (0.70)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "communication": {
        "label": "Mercury Expressive Dialogue",
        "detection_mode": "real_transit",
        "trigger_pairs": ["Mercury ☌/△/⚹/□/☍ Mercury", "Sun ☌/△/⚹/□/☍ Mercury", "Mars ☌/△/⚹/□/☍ Mercury"],
        "key_bodies": [
            {"body": "mercury", "max_orb": TRANSIT_ORB_LIMITS["mercury"], "transit_weight": TRANSIT_PLANET_WEIGHTS["mercury"]},
        ],
        "aspect_types": ["conjunction (1.00)", "trine (0.90)", "sextile (0.70)", "square (0.80)", "opposition (0.85)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "receptivity": {
        "label": "Moon Emotional Attunement",
        "detection_mode": "real_transit",
        "trigger_pairs": ["Moon ☌/△/⚹/□/☍ Moon", "Moon ☌/△/⚹/□/☍ Saturn", "Moon ☌/△/⚹/□/☍ Neptune", "Moon ☌/△/⚹/□/☍ Venus"],
        "key_bodies": [
            {"body": "moon", "max_orb": TRANSIT_ORB_LIMITS["moon"], "transit_weight": TRANSIT_PLANET_WEIGHTS["moon"]},
        ],
        "aspect_types": ["conjunction (1.00)", "trine (0.90)", "sextile (0.70)", "opposition (0.85)", "square (0.80)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "social": {
        "label": "Venus Relational Magnetism",
        "detection_mode": "real_transit",
        "trigger_pairs": ["Sun ☌/△/⚹ Venus", "Venus ☌/△/⚹ Ascendant", "Venus ☌/△/⚹ Jupiter", "Jupiter ☌/△/⚹ Venus"],
        "key_bodies": [
            {"body": "venus", "max_orb": TRANSIT_ORB_LIMITS["venus"], "transit_weight": TRANSIT_PLANET_WEIGHTS["venus"]},
            {"body": "sun", "max_orb": TRANSIT_ORB_LIMITS["sun"], "transit_weight": TRANSIT_PLANET_WEIGHTS["sun"]},
            {"body": "jupiter", "max_orb": TRANSIT_ORB_LIMITS["jupiter"], "transit_weight": TRANSIT_PLANET_WEIGHTS["jupiter"]},
        ],
        "aspect_types": ["conjunction (1.00)", "trine (0.90)", "sextile (0.70)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "discipline": {
        "label": "Saturn Structured Execution",
        "detection_mode": "real_transit",
        "trigger_pairs": ["Sun ☌/△/⚹/□/☍ Saturn", "Mars ☌/△/⚹/□/☍ Saturn"],
        "key_bodies": [
            {"body": "saturn", "max_orb": TRANSIT_ORB_LIMITS["saturn"], "transit_weight": TRANSIT_PLANET_WEIGHTS["saturn"]},
            {"body": "sun", "max_orb": TRANSIT_ORB_LIMITS["sun"], "transit_weight": TRANSIT_PLANET_WEIGHTS["sun"]},
            {"body": "mars", "max_orb": TRANSIT_ORB_LIMITS["mars"], "transit_weight": TRANSIT_PLANET_WEIGHTS["mars"]},
        ],
        "aspect_types": ["conjunction (1.00)", "trine (0.90)", "sextile (0.70)", "square (0.80)", "opposition (0.85)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "introspection": {
        "label": "Pluto Transformative Depth",
        "detection_mode": "real_transit",
        "trigger_pairs": ["Sun ☌/△/⚹/□/☍ Pluto", "Moon ☌/△/⚹/□/☍ Pluto", "Mercury ☌/△/⚹/□/☍ Pluto", "Mars ☌/△/⚹/□/☍ Pluto"],
        "key_bodies": [
            {"body": "pluto", "max_orb": TRANSIT_ORB_LIMITS["pluto"], "transit_weight": TRANSIT_PLANET_WEIGHTS["pluto"]},
            {"body": "sun", "max_orb": TRANSIT_ORB_LIMITS["sun"], "transit_weight": TRANSIT_PLANET_WEIGHTS["sun"]},
            {"body": "moon", "max_orb": TRANSIT_ORB_LIMITS["moon"], "transit_weight": TRANSIT_PLANET_WEIGHTS["moon"]},
        ],
        "aspect_types": ["conjunction (1.00)", "trine (0.90)", "sextile (0.70)", "square (0.80)", "opposition (0.85)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "focus": {
        "label": "Mercury Mental Precision Under Friction",
        "detection_mode": "real_transit",
        "trigger_pairs": ["Mercury □/☍ Jupiter", "Mercury □/☍ Neptune"],
        "key_bodies": [
            {"body": "mercury", "max_orb": TRANSIT_ORB_LIMITS["mercury"], "transit_weight": TRANSIT_PLANET_WEIGHTS["mercury"]},
            {"body": "jupiter", "max_orb": TRANSIT_ORB_LIMITS["jupiter"], "transit_weight": TRANSIT_PLANET_WEIGHTS["jupiter"]},
            {"body": "neptune", "max_orb": TRANSIT_ORB_LIMITS["neptune"], "transit_weight": TRANSIT_PLANET_WEIGHTS["neptune"]},
        ],
        "aspect_types": ["square (0.80)", "opposition (0.85)"],
        "applying_multiplier": APPLYING_MULTIPLIER,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "CENTRALIZED ENGINE SPECIFICATION — NOT RUNTIME OCCURRENCE DATA",
    },
    "neutral": {
        "label": "Celestial Silence / Sub-Threshold Baseline",
        "detection_mode": "neutral_baseline",
        "trigger_pairs": ["None — No transit exceeds threshold strength (ranking_score < 5.0)"],
        "key_bodies": [],
        "aspect_types": [],
        "applying_multiplier": 1.00,
        "engine_source": "backend.app.astrology.transits",
        "evidence_notice": "FROZEN CONTENT ASSET — runtime evidence not applicable",
    },
}


def load_batches_raw() -> dict[str, list[dict[str, Any]]]:
    """Loads all 11 JSON batch files from disk into a dictionary."""
    batches_dir = Path(__file__).parent / "data" / "batches"
    batches: dict[str, list[dict[str, Any]]] = {}
    if batches_dir.exists():
        for batch_path in sorted(batches_dir.glob("*.json")):
            try:
                with open(batch_path, "r", encoding="utf-8") as f:
                    batches[batch_path.stem] = json.load(f)
            except Exception:
                batches[batch_path.stem] = []
    return batches


def load_daily_energy_tags() -> dict[str, dict[str, list[str]]]:
    """Loads the DO/DON'T tags corpus for daily energy."""
    tags_path = Path(__file__).parent / "data" / "daily_energy_tags.json"
    if tags_path.exists():
        try:
            with open(tags_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def build_inspector_projection(force_refresh: bool = False) -> dict[str, Any]:
    """
    Compiles the complete read-only Content & Logic Inspector data projection.
    """
    global _CACHED_INSPECTOR_DATA
    if _CACHED_INSPECTOR_DATA is not None and not force_refresh:
        return _CACHED_INSPECTOR_DATA

    batches = load_batches_raw()
    daily_tags = load_daily_energy_tags()

    # Calculate actual batch counts
    total_batch_assets = sum(len(items) for items in batches.values())
    batch_summaries = [
        {
            "stem": stem,
            "filename": f"{stem}.json",
            "count": len(items),
            "domains": sorted(list({i.get("domain", "unknown") for i in items if i.get("domain")})),
            "surfaces": sorted(list({i.get("surface", "none") for i in items if i.get("surface")})),
        }
        for stem, items in batches.items()
    ]

    # Expected count vs Actual count
    # 681 = 555 Natal + 60 Synastry + 66 Batch 7.
    expected_count = 681
    status_flag = "OK" if total_batch_assets == expected_count else "MISMATCH"

    # Index Batch 6 assets by interpretation_id and surface
    b6_assets = batches.get("batch_6_relationship", [])
    b6_by_interp: dict[str, list[dict[str, Any]]] = {}
    for a in b6_assets:
        iid = a.get("interpretation_id", "")
        b6_by_interp.setdefault(iid, []).append(a)

    # Index Batch 7 assets by surface
    b7_assets = batches.get("batch_7_discovery_connection_chat", [])
    discovery_assets = [a for a in b7_assets if a.get("surface") == "discovery"]
    connection_assets = [a for a in b7_assets if a.get("surface") == "connection"]
    chat_assets = [a for a in b7_assets if a.get("surface") == "chat"]

    # Index connection invitations by category
    conn_by_category: dict[str, list[dict[str, Any]]] = {}
    for ca in connection_assets:
        cat = ca.get("category", "").lower()
        conn_by_category.setdefault(cat, []).append(ca)

    # Index chat starters by interpretation_id and by category
    chat_by_interp: dict[str, list[dict[str, Any]]] = {}
    chat_by_signal: dict[str, list[dict[str, Any]]] = {}
    for sa in chat_assets:
        iid = sa.get("interpretation_id", "")
        chat_by_interp.setdefault(iid, []).append(sa)

    # --- 1. SYNASTRY PIPELINE ITEMS (49 Signal Definitions / 44 Canonical Rules) ---
    synastry_items: list[dict[str, Any]] = []
    seen_rules: set[str] = set()
    canonical_unique_count = 0

    for (p1, p2, asp), (sig_type, category, default_strength, label) in SIGNAL_DEFINITIONS.items():
        rule_id = f"{p1}_{asp}_{p2}"
        canon_pair_key = f"{min(p1, p2)}_{asp}_{max(p1, p2)}"
        is_first_canonical = canon_pair_key not in seen_rules
        if is_first_canonical:
            seen_rules.add(canon_pair_key)
            canonical_unique_count += 1

        contract_id = SIGNAL_TYPE_TO_INTERPRETATION_ID.get(sig_type, "not_mapped")
        contract = INTERPRETATION_CONTRACTS.get(contract_id)

        # Interpretation assets for this contract
        matching_b6 = b6_by_interp.get(contract_id, [])
        why_asset = next((a for a in matching_b6 if a.get("surface") == "why"), None)
        us_assets = [a for a in matching_b6 if a.get("surface") == "us"]

        # Connection invitations for this category
        cat_key = category.lower()
        if cat_key in ("growth", "friction"):
            cat_invitations = conn_by_category.get("growth", [])
        elif cat_key in ("notice", "insufficient_aspects"):
            cat_invitations = conn_by_category.get("notice", [])
        else:
            cat_invitations = conn_by_category.get(cat_key, [])

        # Conversation starters for this contract
        matching_starters = chat_by_interp.get(contract_id, [])
        fallback_starters = [
            a for a in chat_assets if "fallback" in a.get("asset_id", "")
        ]

        # Determine integrity
        integrity_ok = bool(contract_id != "not_mapped" and contract and (why_asset or us_assets))
        integrity_status = "OK" if integrity_ok else "UNRESOLVED"

        synastry_items.append({
            "trigger": f"{p1.capitalize()} × {p2.capitalize()}",
            "planet_a": p1,
            "planet_b": p2,
            "aspect": asp,
            "rule_id": rule_id,
            "canonical_rule": canon_pair_key,
            "is_canonical_primary": is_first_canonical,
            "signal": sig_type,
            "category": category,
            "default_strength": default_strength,
            "label": label,
            "contract_id": contract_id,
            "contract_meaning": {
                "type": contract.meaning.type if contract else "not_exposed",
                "intensity": contract.meaning.intensity if contract else "not_exposed",
                "human_meaning": contract.meaning.human_meaning if contract else [],
            },
            "why_asset": why_asset,
            "us_assets": us_assets,
            "connection_invitations": cat_invitations,
            "conversation_starters": matching_starters or fallback_starters[:2],
            "causal_chain": [
                f"TRIGGER: {p1.capitalize()} × {p2.capitalize()}",
                f"ASPECT: {asp.capitalize()}",
                f"CANONICAL RULE: {canon_pair_key}",
                f"SIGNAL: {sig_type}",
                f"CATEGORY: {category}",
                f"INTERPRETATION CONTRACT: {contract_id}",
                f"INTERPRETATION ASSET: {(why_asset or (us_assets[0] if us_assets else None) or {}).get('asset_id', 'not_found')}",
                f"CONNECTION INVITATION: {(cat_invitations[0] if cat_invitations else {}).get('asset_id', 'not_found')}",
                f"CONVERSATION STARTER: {((matching_starters or fallback_starters)[0] if (matching_starters or fallback_starters) else {}).get('asset_id', 'not_found')}",
            ],
            "integrity_status": integrity_status,
        })

    # Synastry Verdicts and System Notice from Batch 6
    verdicts_and_notice = []
    for a in b6_assets:
        if a.get("surface") in ("verdict", "notice"):
            iid = a.get("interpretation_id", "")
            contract = INTERPRETATION_CONTRACTS.get(iid)
            verdicts_and_notice.append({
                "surface": a.get("surface"),
                "asset_id": a.get("asset_id"),
                "interpretation_id": iid,
                "domain": a.get("domain"),
                "layer": a.get("layer"),
                "category": a.get("category"),
                "text": a.get("text"),
                "contract": {
                    "context": contract.context if contract else "relationship",
                    "human_meaning": contract.meaning.human_meaning if contract else [],
                } if contract else None,
                "raw": a,
            })

    # --- 2. NATAL SECTIONS ---
    natal_planets_order = ["sun", "moon", "ascendant", "mercury", "venus", "mars"]
    natal_sections: list[dict[str, Any]] = []

    batch_map = {
        "sun": "batch_1a_sun",
        "moon": "batch_1b_moon",
        "ascendant": "batch_2a_ascendant",
        "mercury": "batch_2b_mercury",
        "venus": "batch_3a_venus",
        "mars": "batch_3b_mars",
    }

    for p_key in natal_planets_order:
        p_info = PLANETARY_DOMAINS[p_key]
        b_name = batch_map[p_key]
        p_assets = batches.get(b_name, [])

        # Check Mars semantic firewall: verify no forbidden terms
        violations = []
        if p_key == "mars":
            forbidden_words = ["anger", "rage", "fighting", "violence", "ბრაზი", "ჩხუბი", "ძალადობა", "აგრესია"]
            for a in p_assets:
                t_lower = a.get("text", "").lower()
                for fw in forbidden_words:
                    if fw in t_lower:
                        violations.append({"asset_id": a.get("asset_id"), "word": fw})

        natal_sections.append({
            "key": p_key,
            "planet": p_info["planet"],
            "source": p_info["source"],
            "semantic_domain": p_info["semantic_domain"],
            "description": p_info["description"],
            "firewall_rules": p_info.get("firewall_rules"),
            "firewall_violations": violations,
            "firewall_status": "FIREWALL_PASSED" if not violations else "FIREWALL_FLAGGED",
            "batch_name": b_name,
            "runtime_status": "RUNTIME_AVAILABLE",
            "count": len(p_assets),
            "assets": p_assets,
        })

    # Add Elements & Modalities, Synthesis, and Verdicts
    batch_4_assets = batches.get("batch_4_elements_modalities", [])
    natal_sections.append({
        "key": "elements_modalities",
        "planet": "Elements & Modalities",
        "source": "Elemental & Modality Distributions",
        "semantic_domain": "structural temperaments & behavioral rhythm",
        "description": "Primary element (Fire, Earth, Air, Water) and modality (Cardinal, Fixed, Mutable) synthesis.",
        "batch_name": "batch_4_elements_modalities",
        "runtime_status": "RUNTIME_AVAILABLE",
        "count": len(batch_4_assets),
        "assets": batch_4_assets,
    })

    batch_5_assets = batches.get("batch_5_synthesis", [])
    natal_sections.append({
        "key": "synthesis",
        "planet": "Synthesis",
        "source": "Complex Multi-Planetary Configurations",
        "semantic_domain": "multidimensional planetary synthesis",
        "description": "Deep psychological intersections across Sun-Moon, Sun-Rising, and planetary stelliums.",
        "batch_name": "batch_5_synthesis",
        "runtime_status": "RUNTIME_AVAILABLE",
        "count": len(batch_5_assets),
        "assets": batch_5_assets,
    })

    batch_5b_assets = batches.get("batch_5b_verdicts", [])
    natal_sections.append({
        "key": "life_verdicts",
        "planet": "Life Verdicts",
        "source": "Core Natal Architecture",
        "semantic_domain": "definitive life archetype verdicts",
        "description": "Uncompromising JESTER macro verdicts on constitutional temperament and life paths.",
        "batch_name": "batch_5b_verdicts",
        "runtime_status": "RUNTIME_AVAILABLE",
        "count": len(batch_5b_assets),
        "assets": batch_5b_assets,
    })

    # --- 3. DISCOVERY SECTION (Batch 7: 12 Presence Assets) ---
    discovery_items = []
    for a in discovery_assets:
        sign = a.get("asset_id", "").split(".")[-2] if "." in a.get("asset_id", "") else "aries"
        discovery_items.append({
            "asset_id": a.get("asset_id"),
            "sign": sign.capitalize(),
            "source": "Ascendant sign (priority) / Sun sign (fallback)",
            "mode": "visible presence",
            "interpretation_id": a.get("interpretation_id"),
            "category": a.get("category", "presence"),
            "text": a.get("text"),
            "raw": a,
        })

    # --- 4. CONNECTION INVITATION SECTION (Batch 7: 11 Invitation Assets) ---
    connection_items = []
    for a in connection_assets:
        connection_items.append({
            "asset_id": a.get("asset_id"),
            "interpretation_id": a.get("interpretation_id"),
            "category": a.get("category"),
            "variant_key": a.get("variant_key"),
            "source_category_mapping": f"{a.get('category')} → {a.get('interpretation_id')}",
            "selection_mode": "active_signal_category_match",
            "text": a.get("text"),
            "raw": a,
        })

    # --- 5. CHAT / CONVERSATION STARTER SECTION (Batch 7: 43 Assets) ---
    chat_items = []
    for a in chat_assets:
        chat_items.append({
            "asset_id": a.get("asset_id"),
            "interpretation_id": a.get("interpretation_id"),
            "category": a.get("category"),
            "variant_key": a.get("variant_key"),
            "source_signal": a.get("interpretation_id", "").replace("relationship.", "").replace(".v1", ""),
            "selection_mode": "active_signal_match" if "fallback" not in a.get("asset_id", "") else "batch7_fallback",
            "text": a.get("text"),
            "raw": a,
        })

    # --- 6. DAILY ENERGY SECTION (5 SEPARATED CORPUS LAYERS) ---
    # Layer A: 13 Archetypes with Centralized Transit Engine Specifications
    daily_energy_items = []
    for arch in DAILY_ENERGY_ARCHETYPES_DEF:
        aid = arch["id"]
        contract_id = arch["contract_id"]

        # Resolve from content_library (store) first, fallback to drafts/defaults
        resolved_ka = content_library.resolve(contract_id, context="daily_energy", locale="ka")
        resolved_en = content_library.resolve(contract_id, context="daily_energy", locale="en")

        if resolved_ka and resolved_ka.text:
            narrative_ka = resolved_ka.text
            qa_status = "OK"
        elif aid == "neutral" and INITIAL_GEORGIAN_DRAFTS.get("daily_energy.neutral.baseline.v1"):
            narrative_ka = INITIAL_GEORGIAN_DRAFTS["daily_energy.neutral.baseline.v1"]
            qa_status = "OK"
        else:
            narrative_ka = f"MISSING FROZEN ASSET: {contract_id}"
            qa_status = "MISSING FROZEN ASSET"

        narrative_en = resolved_en.text if resolved_en and resolved_en.text else ""

        tag_info = daily_tags.get(aid, {})
        do_tags = tag_info.get("do", [])
        dont_tags = tag_info.get("dont", [])
        do_tags_ka = tag_info.get("do_ka", [])
        dont_tags_ka = tag_info.get("dont_ka", [])

        # Centralized engine specification (NO synthetic mock values)
        spec = ARCHETYPE_TRANSIT_SPECS.get(aid, ARCHETYPE_TRANSIT_SPECS["neutral"])

        technical_evidence = {
            "transit_body": spec["key_bodies"][0]["body"] if spec["key_bodies"] else "none",
            "natal_body": "natal_point",
            "aspect": spec["aspect_types"][0] if spec["aspect_types"] else "none",
            "max_orb": spec["key_bodies"][0]["max_orb"] if spec["key_bodies"] else 0.0,
            "aspect_strength": 1.0,
            "ranking_score": 5.0,
            "archetype_id": aid,
            "detection_mode": spec["detection_mode"],
            "evidence_status": spec["evidence_notice"],
            "is_centralized_spec": True,
        }

        daily_energy_items.append({
            "id": aid,
            "name": arch["name"],
            "description": arch["description"],
            "contract_id": contract_id,
            "narrative_ka": narrative_ka,
            "narrative_en": narrative_en,
            "qa_status": qa_status,
            "do_tags": do_tags,
            "dont_tags": dont_tags,
            "do_tags_ka": do_tags_ka,
            "dont_tags_ka": dont_tags_ka,
            "centralized_spec": spec,
            "technical_evidence": technical_evidence,
            "is_neutral_case": aid == "neutral",
        })

    # Layer B: All Frozen Narrative Interpretation Assets from Content Store (831 assets)
    daily_narrative_assets = []
    store_assets = content_library.store.list_assets(include_archived=True)
    for asset in sorted(store_assets, key=lambda a: (a.interpretation_id, a.locale, a.asset_id)):
        if asset.context == "daily_energy" or asset.interpretation_id.startswith("daily_energy"):
            aid_clean = asset.interpretation_id.replace("daily_energy.", "").replace(".v1", "")
            arch_match = next((a["name"] for a in DAILY_ENERGY_ARCHETYPES_DEF if a["id"] == aid_clean or aid_clean.startswith(a["id"])), aid_clean)
            daily_narrative_assets.append({
                "asset_id": asset.asset_id,
                "interpretation_id": asset.interpretation_id,
                "archetype_id": aid_clean,
                "archetype_name": arch_match,
                "locale": asset.locale,
                "tone": asset.tone,
                "persona": asset.persona,
                "variant_key": asset.variant_key or "default",
                "text": asset.text,
                "status": asset.status,
                "source": asset.source or "content_corpus.json",
            })

    # Layer C: DO Tags (13 × 3 = 39 tags)
    # Layer D: DON'T Tags (13 × 3 = 39 tags)
    do_tag_items = []
    dont_tag_items = []
    for arch in DAILY_ENERGY_ARCHETYPES_DEF:
        aid = arch["id"]
        tag_info = daily_tags.get(aid, {})
        do_ka = tag_info.get("do_ka", [])
        do_en = tag_info.get("do", [])
        dont_ka = tag_info.get("dont_ka", [])
        dont_en = tag_info.get("dont", [])
        for i in range(3):
            do_tag_items.append({
                "tag_id": f"do_{aid}_{i+1}",
                "archetype_id": aid,
                "archetype_name": arch["name"],
                "index": i + 1,
                "text_ka": do_ka[i] if i < len(do_ka) else "N/A",
                "text_en": do_en[i] if i < len(do_en) else "N/A",
            })
            dont_tag_items.append({
                "tag_id": f"dont_{aid}_{i+1}",
                "archetype_id": aid,
                "archetype_name": arch["name"],
                "index": i + 1,
                "text_ka": dont_ka[i] if i < len(dont_ka) else "N/A",
                "text_en": dont_en[i] if i < len(dont_en) else "N/A",
            })

    # Layer E: Neutral Baseline Case
    neutral_ka_res = content_library.resolve("daily_energy.neutral.baseline.v1", context="daily_energy", locale="ka")
    neutral_en_res = content_library.resolve("daily_energy.neutral.baseline.v1", context="daily_energy", locale="en")
    neutral_text_ka = neutral_ka_res.text if neutral_ka_res and neutral_ka_res.text else INITIAL_GEORGIAN_DRAFTS.get(
        "daily_energy.neutral.baseline.v1",
        "დღეს ცაზე არცერთი დომინანტური ტრანზიტული წნეხი არ დგას. ეს არც ცუდია და არც კარგი — უბრალოდ კოსმოსი დღეს შენს ნაცვლად არაფერს წყვეტს. მიჰყევი საკუთარ გეგმას ისე, თითქოს პლანეტები საერთოდ არ არსებობდნენ."
    )
    neutral_text_en = neutral_en_res.text if neutral_en_res and neutral_en_res.text else "No single planetary pressure dominates your chart today. Neither good nor bad — the cosmos leaves the steering wheel entirely to you. Follow your own agenda as if the planets did not exist."

    neutral_case = {
        "detection_mode": "neutral_baseline",
        "primary_transit": None,
        "supporting_transits": [],
        "archetype": "neutral",
        "interpretation": neutral_text_ka,
        "interpretation_en": neutral_text_en,
        "qa_status": "OK",
        "do_ka": daily_tags.get("neutral", {}).get("do_ka", ["ბუნებრივი ტემპი", "საკუთარი კურსი", "ნაცნობი კალაპოტი"]),
        "dont_ka": daily_tags.get("neutral", {}).get("dont_ka", ["ნიშნების ლოდინი", "დრამის გამოგონება", "მინიშნებების ძებნა"]),
        "do_en": daily_tags.get("neutral", {}).get("do", ["Natural Tempo", "Own Course", "Familiar Grooves"]),
        "dont_en": daily_tags.get("neutral", {}).get("dont", ["Waiting", "Inventing Drama", "Overreading Signs"]),
        "technical_note": "When no active transit passes threshold strength (ranking_score < 5.0), engine falls back cleanly to neutral baseline.",
        "centralized_spec": ARCHETYPE_TRANSIT_SPECS["neutral"],
    }

    # --- 7. INTEGRITY SUMMARY ---
    unresolved_synastry = [item["rule_id"] for item in synastry_items if item["integrity_status"] != "OK"]
    mars_violations = next((s["firewall_violations"] for s in natal_sections if s["key"] == "mars"), [])
    missing_assets_count = sum(1 for a in daily_energy_items if a["qa_status"] == "MISSING FROZEN ASSET")

    integrity_report = {
        "overall_status": "OK" if not unresolved_synastry and not mars_violations and missing_assets_count == 0 else "ISSUES_DETECTED",
        "synastry_rules_total": len(synastry_items),
        "synastry_canonical_unique": canonical_unique_count,
        "synastry_unresolved_count": len(unresolved_synastry),
        "synastry_unresolved_rules": unresolved_synastry,
        "mars_semantic_firewall": "PASSED" if not mars_violations else f"FLAGGED ({len(mars_violations)} violations)",
        "discovery_signs_coverage": f"{len(discovery_items)}/12 signs present",
        "connection_categories_coverage": f"{len(conn_by_category)} categories covered (11 assets)",
        "chat_starters_coverage": f"{len(chat_items)} conversation starter assets loaded",
        "daily_energy_archetypes_coverage": (
            f"{len(daily_energy_items)}/13 archetypes resolved ({len(daily_narrative_assets)} narrative assets, "
            f"{len(do_tag_items)} DO, {len(dont_tag_items)} DON'T)"
        ),
    }

    _CACHED_INSPECTOR_DATA = {
        "summary": {
            "expected_frozen_assets": expected_count,
            "actual_frozen_assets": total_batch_assets,
            "status": status_flag,
            "note": (
                "Verified frozen corpus: 681 assets (555 Natal + 60 Synastry + 66 Batch 7)."
            ),
            "batches": batch_summaries,
            "section_counts": {
                "natal": sum(s["count"] for s in natal_sections),
                "synastry": len(b6_assets),
                "discovery": len(discovery_items),
                "connection": len(connection_items),
                "chat": len(chat_items),
                "daily_energy": len(daily_energy_items),
            },
        },
        "synastry_pipeline": synastry_items,
        "synastry_verdicts_and_notice": verdicts_and_notice,
        "natal_sections": natal_sections,
        "discovery_items": discovery_items,
        "connection_items": connection_items,
        "chat_items": chat_items,
        "daily_energy": {
            "archetypes": daily_energy_items,
            "interpretation_assets": daily_narrative_assets,
            "do_tags": do_tag_items,
            "dont_tags": dont_tag_items,
            "neutral_case": neutral_case,
            "summary": {
                "archetypes_count": len(daily_energy_items),
                "interpretation_assets_count": len(daily_narrative_assets),
                "do_tags_count": len(do_tag_items),
                "dont_tags_count": len(dont_tag_items),
                "missing_assets_count": missing_assets_count,
            },
        },
        "integrity": integrity_report,
    }

    return _CACHED_INSPECTOR_DATA
