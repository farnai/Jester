"""
Content Library & Voice Registry for Jester (Architecture V2).
Provides a storage-agnostic content store, multi-variant/multi-tone assets,
and a deterministic resolver with approved-first prioritization and variant rotation.
"""
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import threading
from typing import Any

from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from backend.app.interpretation.models import (
    ContentAsset,
    ContentAssetCreatePayload,
    ContentAssetUpdatePayload,
    ContentInventoryItem,
    ContentRecord,
    ContentSlot,
    ContentStatus,
    ResolvedInterpretation,
)
from backend.app.interpretation.seed_data import SEED_CONTENT_ASSETS

# Initial Pre-seeded Georgian AI Draft Content Library (preserved for backward compatibility)
INITIAL_GEORGIAN_DRAFTS: dict[str, str] = {
    "relationship.attraction.strong_chemistry.v1": (
        "აქ მიზიდულობას ზედმეტი ახსნა ნამდვილად არ სჭირდება."
    ),
    "relationship.attraction.strong_chemistry.v2": (
        "მიზიდულობა იმდენად აშკარაა, რომ სიტყვები მხოლოდ ფონია."
    ),
    "relationship.attraction.magnetic_chemistry.v1": (
        "აქ ნაპერწკლები ისე მარტივად ჩნდება, რომ ცეცხლმაქრი სად დევს, წინასწარ უნდა იცოდეთ."
    ),
    "relationship.harmony.emotional_resonance.v1": (
        "ერთმანეთის უსიტყვოდ გაგება კარგია, ოღონდ ხანდახან ხმამაღლა ლაპარაკიც არ დაგავიწყდეთ."
    ),
    "relationship.growth.complementary_balance.v1": (
        "სრულიად განსხვავებული კუთხიდან უყურებთ სამყაროს, რაც საინტერესოა, სანამ გადაწყვეტთ, ვინ მართავს მანქანას."
    ),
    "relationship.growth.dynamic_emotional_tension.v1": (
        "ემოციური ტემპერატურა ხშირად იცვლება. მოსაწყენად ნამდვილად არ გეცლებათ, მთავარია დრამა კომედიაში არ აგერიოთ."
    ),
    "relationship.harmony.core_harmony.v1": (
        "ცხოვრების მთავარ საკითხებში ერთ ტალღაზე ხართ — თითქოს ერთი და იგივე წესების წიგნი წაგიკითხავთ."
    ),
    "relationship.growth.contrasting_perspectives.v1": (
        "ორივე სარკის სხვადასხვა მხარეს დგახართ: მსგავსებას ხედავთ, მაგრამ ხედვის კუთხე მაინც განსხვავებულია."
    ),
    "relationship.growth.ego_friction.v1": (
        "ორ ლიდერს ერთ ოთახში ხანდახან სივრცე არ ჰყოფნის. კომპრომისი აქ სისუსტე კი არა, სტრატეგიული გამარჯვებაა."
    ),
    "relationship.attraction.warm_affection.v1": (
        "თქვენს ურთიერთობაში სიმყუდროვე და ბუნებრივი სითბოა — ისეთი, ცივ დღეს ცხელი ჩაი რომ მოგიტანონ."
    ),
    "relationship.harmony.gentle_affinity.v1": (
        "ერთმანეთის განწყობას წამებში ამჩნევთ. მთავარია, სხვისი დარდი საკუთარ პასუხისმგებლობად არ აქციოთ."
    ),
    "relationship.communication.intellectual_flow.v1": (
        "თქვენი დიალოგი პინგ-პონგის ფინალს ჰგავს — აზრები ისე სწრაფად იცვლება, მაყურებელს თავბრუ დაეხვევა."
    ),
    "relationship.communication.mutual_understanding.v1": (
        "აზრების გაზიარება აქ ძალდატანების გარეშე ხდება — თითქოს საერთო შიდა ხუმრობების ლექსიკონი გაქვთ."
    ),
    "relationship.growth.pacing_tension.v1": (
        "ერთს აჩქარება უნდა, მეორეს — ყველაფრის გადამოწმება. თუ ტემპზე შეთანხმდებით, მთებს გადადგამთ."
    ),
    "relationship.growth.dynamic_spark.v1": (
        "ყოველთვის მოიძებნება თემა, რაზეც კამათი აზარტში გადავა. მთავარია, გამარჯვებული ვახშამზე პატიჟებდეს."
    ),
    "relationship.attraction.energized_collaboration.v1": (
        "როცა რაღაცის გაკეთებას ერთად გადაწყვეტთ, ენერგია ორმაგდება. იდეიდან მოქმედებამდე მანძილი მინიმალურია."
    ),
    "relationship.attraction.dynamic_drive.v1": (
        "ორივეს მოქმედება გიყვართ, ამიტომ ერთად დგომისას იშვიათად ზიხართ უსაქმოდ."
    ),
    "relationship.stability.shared_optimism.v1": (
        "ერთად ყოფნისას პრობლემები პატარავდება, ხოლო გეგმები — გრანდიოზული ხდება. ოპტიმიზმი გადამდებია."
    ),
    "relationship.harmony.generous_affection.v1": (
        "ერთმანეთის გახარება გსიამოვნებთ და კომპლიმენტებსაც არ იშურებთ. ასეთ გარემოში გაზრდა მარტივია."
    ),
    "relationship.attraction.intense_magnetism.v1": (
        "ზედაპირული საუბრები აქ არ გამოვა — მიზიდულობა იმდენად ღრმაა, რომ პირველივე წუთიდან არსს ეხებით."
    ),
    "relationship.stability.long_term_grounding.v1": (
        "ეს ის კავშირია, სადაც დაპირება ცარიელი სიტყვა არ არის. საიმედოობა დღეს იშვიათი ფუფუნებაა."
    ),
    "relationship.notice.independent_dynamics.v1": (
        "ერთმანეთის პირად სივრცეს ბუნებრივად უფრთხილდებით. თავისუფლება აქ კავშირს კი არ ასუსტებს, აძლიერებს."
    ),
    "relationship.overall.exceptional_flow.v1": (
        "იშვიათი ჰარმონია: თითქოს ერთი და იმავე ტალღაზე მაუწყებლობთ, ხარვეზების გარეშე."
    ),
    "relationship.overall.balanced_synergy.v1": (
        "ჯანსაღი ბალანსი მსგავსებასა და განსხვავებას შორის — ზუსტად ის, რაც ურთიერთობას ცოცხალს ტოვებს."
    ),
    "relationship.overall.stimulating_friction.v1": (
        "აქ ენერგია კონტრასტებიდან იბადება. მოსაწყენი არასდროს იქნება, თუ ერთმანეთის მოსმენას ისწავლით."
    ),
    "relationship.overall.independent_paths.v1": (
        "ორი დამოუკიდებელი სამყარო. საერთო ენის პოვნა შეგნებულ ძალისხმევას მოითხოვს, მაგრამ შეუძლებელი არაფერია."
    ),
    "daily_energy.confidence.elevated.v1": (
        "დღეს შენი თავდაჯერება ოთახში შენზე ხუთი წუთით ადრე შემოდის. გამოიყენე, ოღონდ სხვებსაც დაუტოვე ჟანგბადი."
    ),
    "daily_energy.communication.direct.v1": (
        "სიტყვებს დღეს პირდაპირ მიზანში ისვრი. მთავარია, შემთხვევით მოკავშირე არ გაგეპაროს სამიზნეში."
    ),
    "daily_energy.focus.scattered.v1": (
        "იდეები იმდენია, რომ ყურადღება იფანტება. აირჩიე ერთი და ბოლომდე მიიყვანე — დანარჩენი არსად გაიქცევა."
    ),
    "daily_energy.creativity.exploration.v1": (
        "დღეს ჩვეული მარშრუტიდან გადახვევა საუკეთესო გადაწყვეტილებაა. ახალი ხედვა მოულოდნელ ადგილას იმალება."
    ),
}


# =============================================================================
# Abstract Content Store Interface
# =============================================================================
class ContentStore(ABC):
    """
    Storage-agnostic boundary defining content asset persistence operations.
    Allows transparent migration from in-memory to PostgreSQL / Headless CMS.
    """

    @abstractmethod
    def get_asset(self, asset_id: str) -> ContentAsset | None:
        pass

    @abstractmethod
    def list_assets(
        self,
        interpretation_id: str | None = None,
        locale: str | None = None,
        context: str | None = None,
        tone: str | None = None,
        status: ContentStatus | None = None,
        include_archived: bool = False,
    ) -> list[ContentAsset]:
        pass

    @abstractmethod
    def save_asset(self, asset: ContentAsset) -> ContentAsset:
        pass

    @abstractmethod
    def delete_asset(self, asset_id: str) -> bool:
        pass

    @abstractmethod
    def archive_asset(self, asset_id: str) -> ContentAsset | None:
        pass


# =============================================================================
# In-Memory Content Store Implementation
# =============================================================================
class InMemoryContentStore(ContentStore):
    """
    High-performance, thread-safe in-memory asset store.
    Capable of holding tens of thousands of assets with sub-millisecond retrieval.
    """

    def __init__(self, seed_assets: list[ContentAsset] | None = None) -> None:
        self._lock = threading.RLock()
        self._assets: dict[str, ContentAsset] = {}
        self._by_interpretation: dict[str, set[str]] = {}

        # Seed initial assets
        initial = seed_assets if seed_assets is not None else SEED_CONTENT_ASSETS
        for asset in initial:
            self.save_asset(asset)

        # Ingest large-scale JSON corpus fixture if present
        if seed_assets is None:
            self._load_corpus_fixture()

    def _load_corpus_fixture(self) -> None:
        """Ingests large-scale AI content corpus from JSON fixture if present."""
        fixture_path = Path(__file__).parent / "data" / "content_corpus.json"
        if fixture_path.exists():
            try:
                with open(fixture_path, "r", encoding="utf-8") as f:
                    raw_items = json.load(f)
                for item in raw_items:
                    aid = item.get("asset_id")
                    if aid and aid not in self._assets:
                        # Reconstitute datetime fields
                        if "created_at" in item and isinstance(item["created_at"], str):
                            item["created_at"] = datetime.fromisoformat(item["created_at"])
                        if "updated_at" in item and isinstance(item["updated_at"], str):
                            item["updated_at"] = datetime.fromisoformat(item["updated_at"])
                        asset = ContentAsset(**item)
                        self.save_asset(asset)
            except Exception:
                pass

    def get_asset(self, asset_id: str) -> ContentAsset | None:
        with self._lock:
            asset = self._assets.get(asset_id)
            return asset.model_copy() if asset else None

    def list_assets(
        self,
        interpretation_id: str | None = None,
        locale: str | None = None,
        context: str | None = None,
        tone: str | None = None,
        status: ContentStatus | None = None,
        include_archived: bool = False,
    ) -> list[ContentAsset]:
        with self._lock:
            if interpretation_id:
                candidate_ids = self._by_interpretation.get(interpretation_id, set())
                candidates = [self._assets[aid] for aid in candidate_ids if aid in self._assets]
            else:
                candidates = list(self._assets.values())

            results: list[ContentAsset] = []
            for a in candidates:
                if not include_archived and a.archived:
                    continue
                if locale and a.locale != locale:
                    continue
                if context and a.context != context:
                    continue
                if tone and a.tone != tone:
                    continue
                if status and a.status != status:
                    continue
                results.append(a)

            # Default sort: priority DESC, version DESC, asset_id ASC
            results.sort(key=lambda x: (-x.priority, -x.version, x.asset_id))
            return results

    def save_asset(self, asset: ContentAsset) -> ContentAsset:
        with self._lock:
            asset_copy = asset.model_copy()
            asset_copy.updated_at = datetime.now(timezone.utc)
            self._assets[asset.asset_id] = asset_copy

            if asset.interpretation_id not in self._by_interpretation:
                self._by_interpretation[asset.interpretation_id] = set()
            self._by_interpretation[asset.interpretation_id].add(asset.asset_id)

            return asset_copy.model_copy()

    def delete_asset(self, asset_id: str) -> bool:
        with self._lock:
            asset = self._assets.pop(asset_id, None)
            if not asset:
                return False
            interp_set = self._by_interpretation.get(asset.interpretation_id)
            if interp_set and asset_id in interp_set:
                interp_set.remove(asset_id)
            return True

    def archive_asset(self, asset_id: str) -> ContentAsset | None:
        with self._lock:
            asset = self._assets.get(asset_id)
            if not asset:
                return None
            asset.archived = True
            asset.status = "archived"
            asset.updated_at = datetime.now(timezone.utc)
            return deepcopy(asset)


# Domain context families
INTERPERSONAL_CONTEXTS = {
    "relationship",
    "friendship",
    "business",
    "deep_analysis",
    "discovery",
    "onboarding",
    "share",
    "notification",
}
PERSONAL_CONTEXTS = {"daily_energy", "self", "natal"}


# =============================================================================
# Deterministic Multi-Asset Content Resolver
# =============================================================================
class ContentResolver:
    """
    Deterministic resolution engine matching signals/interpretations to content assets.
    Enforces priority hierarchy (Approved > Active Experiment > AI Draft > Fallback)
    and deterministic variant rotation across reloads.
    """

    def __init__(self, store: ContentStore) -> None:
        self.store = store

    def resolve(
        self,
        interpretation_id: str,
        context: str | None = None,
        locale: str = "ka",
        tone: str | None = None,
        persona: str = "jester",
        variant_key: str | None = None,
        seed: str | None = None,
        include_experimental: bool = False,
    ) -> ResolvedInterpretation | None:
        target_id = interpretation_id
        contract = INTERPRETATION_CONTRACTS.get(target_id)
        effective_locale = locale or "ka"

        # 1. Version fallback (e.g. foo.v3 -> foo.v1)
        if not contract and "." in target_id:
            base = target_id.rsplit(".", 1)[0]
            fallback_v1 = f"{base}.v1"
            if fallback_v1 in INTERPRETATION_CONTRACTS:
                target_id = fallback_v1
                contract = INTERPRETATION_CONTRACTS.get(target_id)

        contract_context = contract.context if contract else "relationship"
        req_context = context or contract_context

        # Domain boundary protection:
        # A personal context (e.g. daily_energy) must NEVER resolve a relational contract,
        # and a relational context must NEVER resolve a personal contract.
        is_contract_relational = contract_context in INTERPERSONAL_CONTEXTS
        is_req_personal = req_context in PERSONAL_CONTEXTS
        is_contract_personal = contract_context in PERSONAL_CONTEXTS

        if is_contract_relational and is_req_personal:
            # Strictly prevent serving relationship text in personal daily energy
            return None
        if is_contract_personal and not is_req_personal:
            # Strictly prevent serving daily transit energy in relational comparisons
            return None

        # 2. Query candidates strictly for (target_id, effective_locale)
        candidates = self.store.list_assets(
            interpretation_id=target_id,
            locale=effective_locale,
            include_archived=False,
        )

        # 3. Context matching & safe fallback within compatible domain family
        context_candidates = [c for c in candidates if c.context == req_context]
        if not context_candidates and candidates:
            if is_contract_relational:
                # Fall back to canonical relationship context
                context_candidates = [c for c in candidates if c.context == "relationship"]
            elif is_contract_personal:
                context_candidates = [c for c in candidates if c.context == contract_context]
        candidates = context_candidates

        # 4. Locale fallback:
        # If an unsupported foreign locale is requested (e.g. 'de', 'fr'), fall back to primary 'ka'.
        # BUT if Georgian ('ka') is requested and has no assets, DO NOT silently fall back to English!
        # Georgian is the active user-facing language; English is completely isolated.
        if not candidates and effective_locale not in ("ka", "en"):
            candidates = self.store.list_assets(
                interpretation_id=target_id,
                locale="ka",
                include_archived=False,
            )
            if req_context:
                ctx_fallbacks = [c for c in candidates if c.context == req_context]
                if not ctx_fallbacks and is_contract_relational:
                    ctx_fallbacks = [c for c in candidates if c.context == "relationship"]
                if ctx_fallbacks:
                    candidates = ctx_fallbacks

        if not candidates:
            return None

        # 5. Tone matching with safe fallback:
        # If specific tone requested, filter candidates that match tone first.
        # If no candidates match, filter out extreme/roast tones (e.g. 'savage') unless savage was explicitly requested.
        tone_pool = candidates
        if tone:
            tone_matched = [c for c in candidates if c.tone.lower() == tone.lower()]
            if tone_matched:
                tone_pool = tone_matched
            else:
                # Safe fallback: exclude 'savage' if user didn't request savage
                safe_fallback_pool = [c for c in candidates if c.tone.lower() != "savage"]
                if safe_fallback_pool:
                    # Prefer witty if present
                    witty_preferred = [c for c in safe_fallback_pool if c.tone.lower() == "witty"]
                    tone_pool = witty_preferred or safe_fallback_pool

        # 6. Status hierarchy filtering within tone_pool:
        # Tier 1: Approved / Winner
        # Tier 2: Experimental (if enabled)
        # Tier 3: AI Draft
        # Tier 4: Other non-archived drafts
        approved = [c for c in tone_pool if c.status in ("approved", "winner") and c.text and c.text.strip()]
        if approved:
            eligible_pool = approved
        else:
            experimental = (
                [c for c in tone_pool if c.status == "experimental" and c.text and c.text.strip()]
                if include_experimental
                else []
            )
            if experimental:
                eligible_pool = experimental
            else:
                ai_drafts = [c for c in tone_pool if c.status == "ai_draft" and c.text and c.text.strip()]
                if ai_drafts:
                    eligible_pool = ai_drafts
                else:
                    eligible_pool = [c for c in tone_pool if c.text and c.text.strip()]

        if not eligible_pool:
            return None

        # 7. Exact variant matching if requested
        if variant_key:
            variant_matched = [c for c in eligible_pool if c.variant_key == variant_key]
            if variant_matched:
                eligible_pool = variant_matched

        # Sort pool deterministically by priority DESC, version DESC, asset_id ASC
        eligible_pool.sort(key=lambda x: (-x.priority, -x.version, x.asset_id))

        # 8. Deterministic variant selection using seed
        # Same (seed, interp_id, context) -> guaranteed same variant
        if len(eligible_pool) == 1 or not seed:
            chosen = eligible_pool[0]
        else:
            hash_input = f"{seed}:{target_id}:{req_context}".encode("utf-8")
            hash_val = int(hashlib.sha256(hash_input).hexdigest(), 16)
            chosen = eligible_pool[hash_val % len(eligible_pool)]

        return ResolvedInterpretation(
            id=target_id,
            text=chosen.text.strip(),
            content_status=chosen.status,
            language=chosen.locale,
            content_asset_id=chosen.asset_id,
            context=chosen.context,
            locale=chosen.locale,
            tone=chosen.tone,
            persona=chosen.persona,
            variant_key=chosen.variant_key,
        )


# =============================================================================
# Unified High-Level Content Library Facade
# =============================================================================
class ContentLibrary:
    """
    Unified high-level content repository manager.
    Coordinates storage, resolver, legacy backward compatibility, and copywriter workflows.
    """

    def __init__(self, store: ContentStore | None = None) -> None:
        self.store = store or InMemoryContentStore()
        self.resolver = ContentResolver(self.store)
        self._lock = threading.RLock()
        self._legacy_records: dict[str, ContentRecord] = {}
        self._sync_legacy_records()

    def _sync_legacy_records(self) -> None:
        """Initializes legacy dual-slot ContentRecord objects for backward compatibility."""
        now = datetime.now(timezone.utc)
        for interp_id, contract in INTERPRETATION_CONTRACTS.items():
            draft_text = INITIAL_GEORGIAN_DRAFTS.get(
                interp_id,
                "საინტერესო კავშირია — დაკვირვება და ურთიერთგაგება საუკეთესო შედეგს მოიტანს.",
            )
            # Find any approved asset in the store
            assets = self.store.list_assets(interpretation_id=interp_id, locale="ka")
            approved = next((a for a in assets if a.status == "approved" and not a.archived), None)
            final_text = approved.text if approved else None
            final_status: ContentStatus = "approved" if approved else "not_reviewed"

            self._legacy_records[interp_id] = ContentRecord(
                interpretation_id=interp_id,
                meaning=contract.meaning.model_dump(),
                draft=ContentSlot(
                    text=draft_text,
                    status="ai_draft",
                    author="jester_ai_v1",
                    updated_at=now,
                ),
                final=ContentSlot(
                    text=final_text,
                    status=final_status,
                    author=approved.author if approved else None,
                    updated_at=approved.updated_at if approved else None,
                ),
            )

    # -------------------------------------------------------------------------
    # Backward Compatible V1 Methods
    # -------------------------------------------------------------------------
    def get_record(self, interpretation_id: str) -> ContentRecord | None:
        with self._lock:
            rec = self._legacy_records.get(interpretation_id)
            return deepcopy(rec) if rec else None

    def list_records(self) -> list[ContentRecord]:
        with self._lock:
            return [deepcopy(r) for r in self._legacy_records.values()]

    def resolve_text(self, interpretation_id: str) -> ResolvedInterpretation | None:
        """
        Backward compatible resolution method returning user-facing ResolvedInterpretation.
        """
        with self._lock:
            # If a legacy record exists and has an approved non-empty final text, honor it
            legacy = self._legacy_records.get(interpretation_id)
            if legacy and legacy.final.status == "approved" and legacy.final.text and legacy.final.text.strip():
                return ResolvedInterpretation(
                    id=interpretation_id,
                    text=legacy.final.text.strip(),
                    content_status="approved",
                    language="ka",
                    locale="ka",
                    context="relationship",
                )

            # If legacy record exists and final status is not approved, fallback cleanly to AI Draft
            resolved = self.resolver.resolve(interpretation_id=interpretation_id, locale="ka")
            if resolved:
                if legacy and legacy.final.status != "approved":
                    resolved.content_status = "ai_draft"
                return resolved

            # Fallback to legacy draft slot if registered
            if legacy and legacy.draft.text and legacy.draft.text.strip():
                return ResolvedInterpretation(
                    id=interpretation_id,
                    text=legacy.draft.text.strip(),
                    content_status="ai_draft",
                    language="ka",
                    locale="ka",
                    context="relationship",
                )

            return None

    def update_approved_copy(
        self,
        interpretation_id: str,
        text: str,
        author: str = "copywriter",
    ) -> ContentRecord:
        """
        Legacy copywriter update: updates approved copy for the interpretation.
        Saves as an approved ContentAsset and updates the legacy ContentRecord.
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            # Create/update as top-priority approved asset in V2 store
            asset_id = f"ca_approved_{interpretation_id.replace('.', '_')}"
            asset = ContentAsset(
                asset_id=asset_id,
                interpretation_id=interpretation_id,
                locale="ka",
                context="relationship",
                tone="witty",
                persona="jester",
                text=text.strip(),
                status="approved",
                version=2,
                priority=1000,
                source="copywriter",
                author=author,
                tags=["approved_override"],
                created_at=now,
                updated_at=now,
            )
            self.store.save_asset(asset)

            rec = self._legacy_records.get(interpretation_id)
            if not rec:
                rec = ContentRecord(
                    interpretation_id=interpretation_id,
                    meaning={},
                    draft=ContentSlot(text="", status="ai_draft", author="system", updated_at=now),
                    final=ContentSlot(text=text.strip(), status="approved", author=author, updated_at=now),
                )
                self._legacy_records[interpretation_id] = rec
            else:
                rec.final = ContentSlot(
                    text=text.strip(),
                    status="approved",
                    author=author,
                    updated_at=now,
                )

            return deepcopy(rec)

    def reset_to_draft(self, interpretation_id: str) -> ContentRecord:
        """
        Legacy reset: removes approved overrides, reverting resolution back to AI Draft.
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            # Delete any approved overrides created dynamically, and revert others
            for a in self.store.list_assets(interpretation_id=interpretation_id, include_archived=True):
                if a.asset_id.startswith("ca_approved_") or "approved_override" in a.tags:
                    self.store.delete_asset(a.asset_id)
                elif a.status in ("approved", "winner"):
                    a.status = "ai_draft"
                    self.store.save_asset(a)

            rec = self._legacy_records.get(interpretation_id)
            if not rec:
                raise KeyError(f"Interpretation '{interpretation_id}' not found")

            rec.final = ContentSlot(
                text=None,
                status="not_reviewed",
                author=None,
                updated_at=now,
            )
            return deepcopy(rec)


    # -------------------------------------------------------------------------
    # Content Architecture V2 APIs
    # -------------------------------------------------------------------------
    def resolve(
        self,
        interpretation_id: str,
        context: str | None = None,
        locale: str = "ka",
        tone: str | None = None,
        persona: str = "jester",
        variant_key: str | None = None,
        seed: str | None = None,
        include_experimental: bool = False,
    ) -> ResolvedInterpretation | None:
        """Primary V2 resolution entry point."""
        return self.resolver.resolve(
            interpretation_id=interpretation_id,
            context=context,
            locale=locale,
            tone=tone,
            persona=persona,
            variant_key=variant_key,
            seed=seed,
            include_experimental=include_experimental,
        )

    def get_asset(self, asset_id: str) -> ContentAsset | None:
        return self.store.get_asset(asset_id)

    def list_assets(
        self,
        interpretation_id: str | None = None,
        locale: str | None = None,
        context: str | None = None,
        tone: str | None = None,
        status: ContentStatus | None = None,
        include_archived: bool = False,
    ) -> list[ContentAsset]:
        return self.store.list_assets(
            interpretation_id=interpretation_id,
            locale=locale,
            context=context,
            tone=tone,
            status=status,
            include_archived=include_archived,
        )

    def create_asset(
        self,
        interpretation_id: str,
        payload: ContentAssetCreatePayload,
        author: str | None = None,
    ) -> ContentAsset:
        with self._lock:
            asset_id = f"ca_{interpretation_id.replace('.', '_')}_{payload.locale}_{payload.tone}_{int(datetime.now(timezone.utc).timestamp())}"
            now = datetime.now(timezone.utc)
            asset = ContentAsset(
                asset_id=asset_id,
                interpretation_id=interpretation_id,
                locale=payload.locale,
                context=payload.context,
                tone=payload.tone,
                persona=payload.persona,
                text=payload.text.strip(),
                status=payload.status,
                version=1,
                priority=payload.priority,
                variant_key=payload.variant_key,
                source="copywriter" if payload.status == "approved" else "ai",
                author=author or payload.author,
                tags=payload.tags,
                internal_notes=payload.internal_notes,
                experiment_id=payload.experiment_id,
                weight=payload.weight,
                created_at=now,
                updated_at=now,
            )
            saved = self.store.save_asset(asset)

            # Update legacy slot if approved
            if payload.status == "approved":
                rec = self._legacy_records.get(interpretation_id)
                if rec:
                    rec.final = ContentSlot(
                        text=payload.text.strip(),
                        status="approved",
                        author=author or payload.author,
                        updated_at=now,
                    )

            return saved

    def update_asset(self, asset_id: str, payload: ContentAssetUpdatePayload, author: str | None = None) -> ContentAsset:
        with self._lock:
            asset = self.store.get_asset(asset_id)
            if not asset:
                raise KeyError(f"Asset '{asset_id}' not found")

            now = datetime.now(timezone.utc)
            if payload.text is not None:
                asset.text = payload.text.strip()
                asset.version += 1
            if payload.status is not None:
                asset.status = payload.status
            if payload.locale is not None:
                asset.locale = payload.locale
            if payload.context is not None:
                asset.context = payload.context
            if payload.tone is not None:
                asset.tone = payload.tone
            if payload.persona is not None:
                asset.persona = payload.persona
            if payload.priority is not None:
                asset.priority = payload.priority
            if payload.variant_key is not None:
                asset.variant_key = payload.variant_key
            if payload.tags is not None:
                asset.tags = payload.tags
            if payload.archived is not None:
                asset.archived = payload.archived
                if payload.archived:
                    asset.status = "archived"
            if payload.internal_notes is not None:
                asset.internal_notes = payload.internal_notes
            if payload.experiment_id is not None:
                asset.experiment_id = payload.experiment_id
            if payload.weight is not None:
                asset.weight = payload.weight
            if author:
                asset.author = author

            asset.updated_at = now
            return self.store.save_asset(asset)

    def approve_asset(self, asset_id: str, author: str | None = None) -> ContentAsset:
        return self.update_asset(
            asset_id,
            ContentAssetUpdatePayload(status="approved", archived=False),
            author=author or "copywriter",
        )

    def archive_asset(self, asset_id: str) -> ContentAsset | None:
        with self._lock:
            return self.store.archive_asset(asset_id)

    def get_inventory(self) -> list[ContentInventoryItem]:
        """Generates a complete editorial inventory across all interpretation contracts."""
        with self._lock:
            items: list[ContentInventoryItem] = []
            for interp_id, contract in sorted(INTERPRETATION_CONTRACTS.items()):
                assets = self.store.list_assets(interpretation_id=interp_id, include_archived=True)
                locales = sorted(list({a.locale for a in assets}))
                tones = sorted(list({a.tone for a in assets if not a.archived}))
                approved_cnt = sum(1 for a in assets if a.status in ("approved", "winner") and not a.archived)
                ai_cnt = sum(1 for a in assets if a.status == "ai_draft" and not a.archived)
                archived_cnt = sum(1 for a in assets if a.archived)

                if approved_cnt > 0:
                    status_label = "APPROVED"
                elif ai_cnt > 0:
                    status_label = "AI_DRAFT"
                else:
                    status_label = "PENDING"

                items.append(
                    ContentInventoryItem(
                        interpretation_id=interp_id,
                        context=contract.context,
                        meaning_type=contract.meaning.type,
                        available_locales=locales or ["ka"],
                        available_tones=tones or ["witty"],
                        total_assets=len(assets),
                        approved_assets=approved_cnt,
                        ai_draft_assets=ai_cnt,
                        archived_assets=archived_cnt,
                        source_signal=contract.signal.type,
                        status=status_label,
                    )
                )
            return items


# Global singleton instance
content_library = ContentLibrary()
