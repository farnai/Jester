"""
Tests for JESTER Phase 3.4 — Mercury Full Content Batch & Astrological Provenance.
Validates:
- 12 Fixed Semantic Contracts (self.cognition.mercury_{sign}.v1)
- Signal routing to Mercury contracts
- 96 Loaded Content Assets (12 signs x 8 assets: 72 Micro, 24 Medium, 0 Deep)
- Tone distribution (all 8 JESTER tones present, 1 per sign)
- Text length constraints (Micro: 100-250, Medium: 400-750)
- Astrological claim discipline & forbidden terminology/claims
- Semantic specificity & cross-sign differentiation
- Quality Gate (all 5 dimensions >= 4.0 for all 96 assets)
- Machine-readable provenance schema in corpus JSON and tags
- Backend exposure boundary (SafeDerivedAstrology has mercury_sign only)
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import uuid
import pytest

from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from backend.app.interpretation.engine import SIGNAL_TYPE_TO_INTERPRETATION_ID
from backend.app.interpretation.library import content_library
from backend.app.astrology.models import SafeDerivedAstrology, SafeDerivedAstrologyResponse
from scripts.corpus_builders.common import scan_for_jargon

SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

TONES = [
    "snarky", "mocking", "unfiltered", "cocky",
    "dramatic", "conversational", "unexpected", "jester"
]

FORBIDDEN_PATTERNS = [
    r"\badhd\b", r"\bყურადღების დეფიციტ", r"\bაუტიზმ", r"\bautism\b",
    r"\bდეპრესი", r"\bdepression\b", r"\bბიპოლარულ", r"\bbipolar\b",
    r"\bშფოთვითი აშლილობ", r"\banxiety disorder\b", r"\bocd\b", r"\bოკდ\b",
    r"\bოკრი\b", r"\biq\b", r"\bაიქიუ\b", r"\bინტელექტის კოეფიციენტ",
    r"\bდიაგნოზ", r"\bფსიქიკური აშლილობ", r"\bმატყუარა ხარ\b",
    r"\bნარცისი ხარ\b", r"\bფსიქოპათ", r"\bკრიმინალ",
    r"\bეს დამტკიცებულია\b", r"\bშენი ტვინი ასე მუშაობს\b",
    r"\bეს ფსიქოლოგიურად ნიშნავს\b", r"\bშენ აუცილებლად\b",
]

FORBIDDEN_OPENINGS = [
    "წარმოიდგინე სიტუაცია",
    "წარმოიდგინე",
    "შენ ხარ",
]


class TestMercuryContracts:
    """Validates the 12 fixed Mercury semantic contracts."""

    def test_12_contracts_registered(self):
        for sign in SIGNS:
            contract_id = f"self.cognition.mercury_{sign}.v1"
            assert contract_id in INTERPRETATION_CONTRACTS, f"Missing contract {contract_id}"
            contract = INTERPRETATION_CONTRACTS[contract_id]
            assert contract.context == "self"
            assert contract.signal.category == "self"
            assert contract.signal.type == f"mercury_sign_{sign}"
            assert len(contract.meaning.human_meaning) >= 3, f"Contract {contract_id} needs >= 3 semantic angles"

    def test_signal_routing(self):
        for sign in SIGNS:
            contract_id = f"self.cognition.mercury_{sign}.v1"
            assert SIGNAL_TYPE_TO_INTERPRETATION_ID.get(f"mercury_sign_{sign}") == contract_id
            assert SIGNAL_TYPE_TO_INTERPRETATION_ID.get(f"mercury_{sign}") == contract_id


class TestMercuryCorpusAndLibrary:
    """Validates the 96 generated Mercury assets in the library."""

    @classmethod
    def setup_class(cls):
        all_assets = content_library.list_assets()
        cls.mercury_assets = [a for a in all_assets if "mercury" in a.interpretation_id]
        
        # Also load raw JSON fixture for full provenance inspection
        fixture_path = Path(__file__).parent.parent.parent / "backend" / "app" / "interpretation" / "data" / "mercury_corpus.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            cls.raw_assets = json.load(f)

    def test_total_mercury_asset_count(self):
        assert len(self.mercury_assets) == 96, f"Expected exactly 96 Mercury assets, found {len(self.mercury_assets)}"
        assert len(self.raw_assets) == 96, f"Expected exactly 96 raw assets in JSON fixture, found {len(self.raw_assets)}"

    def test_sign_distribution(self):
        for sign in SIGNS:
            contract_id = f"self.cognition.mercury_{sign}.v1"
            sign_assets = [a for a in self.mercury_assets if a.interpretation_id == contract_id]
            assert len(sign_assets) == 8, f"Sign {sign} must have exactly 8 assets, got {len(sign_assets)}"
            
            micros = [a for a in sign_assets if "depth:micro" in a.tags]
            mediums = [a for a in sign_assets if "depth:medium" in a.tags]
            deeps = [a for a in sign_assets if "depth:deep" in a.tags]

            assert len(micros) == 6, f"Sign {sign} must have 6 micros, got {len(micros)}"
            assert len(mediums) == 2, f"Sign {sign} must have 2 mediums, got {len(mediums)}"
            assert len(deeps) == 0, f"Sign {sign} must have 0 deeps, got {len(deeps)}"

    def test_tone_distribution(self):
        from collections import Counter
        tone_counts = Counter(a.tone for a in self.mercury_assets)
        for t in TONES:
            assert tone_counts[t] == 12, f"Expected 12 of tone '{t}', got {tone_counts[t]}"

        # Exactly 1 of each tone per sign
        for sign in SIGNS:
            contract_id = f"self.cognition.mercury_{sign}.v1"
            sign_tones = {a.tone for a in self.mercury_assets if a.interpretation_id == contract_id}
            assert len(sign_tones) == 8, f"Sign {sign} must contain all 8 tones, found: {sign_tones}"

    def test_character_lengths(self):
        for a in self.mercury_assets:
            text = a.text.strip()
            char_len = len(text)
            if "depth:micro" in a.tags:
                assert 100 <= char_len <= 250, (
                    f"Micro length violation ({char_len} chars) for {a.asset_id}: '{text}'"
                )
            elif "depth:medium" in a.tags:
                assert 400 <= char_len <= 750, (
                    f"Medium length violation ({char_len} chars) for {a.asset_id}: '{text}'"
                )

    def test_no_forbidden_openings(self):
        for a in self.mercury_assets:
            text = a.text.strip()
            for opening in FORBIDDEN_OPENINGS:
                assert not text.startswith(opening), (
                    f"Forbidden opening '{opening}' in {a.asset_id}: '{text}'"
                )

    def test_no_forbidden_claims_or_diagnoses(self):
        for a in self.mercury_assets:
            text = a.text.strip()
            for pat in FORBIDDEN_PATTERNS:
                assert not re.search(pat, text, re.IGNORECASE), (
                    f"Forbidden claim pattern '{pat}' matched in {a.asset_id}: '{text}'"
                )

    def test_no_astrological_jargon_in_user_facing_body(self):
        for a in self.mercury_assets:
            found = scan_for_jargon(a.text, "ka")
            assert not found, (
                f"Astrological jargon {found} found in user-facing text of {a.asset_id}: '{a.text}'"
            )

    def test_provenance_and_metadata_completeness(self):
        for raw in self.raw_assets:
            prov = raw.get("provenance")
            assert prov is not None, f"Missing provenance block in {raw.get('asset_id')}"
            assert prov.get("batch_id") == "mercury_full_v1"
            assert prov.get("interpretation_id") == raw["interpretation_id"]
            assert prov.get("body") == "mercury"
            assert prov.get("sign") in SIGNS
            assert prov.get("element") in ["fire", "earth", "air", "water"]
            assert prov.get("modality") in ["cardinal", "fixed", "mutable"]
            assert prov.get("semantic_contract_id") == raw["interpretation_id"]
            assert prov.get("semantic_angle")
            assert prov.get("tone") in TONES
            assert prov.get("depth") in ["micro", "medium"]
            assert prov.get("variant")

            # Validate source_inputs
            src = prov.get("source_inputs", {})
            assert src.get("mercury_sign") == prov["sign"]
            assert src.get("element") == prov["element"]
            assert src.get("modality") == prov["modality"]

            # Validate Quality Gate: all 5 dimensions >= 4.0
            qg = prov.get("quality_gate", {})
            assert qg.get("status") == "passed"
            for dim in [
                "astrological_grounding",
                "semantic_specificity",
                "jester_voice",
                "natural_georgian",
                "originality",
            ]:
                score = qg.get(dim, 0.0)
                assert score >= 4.0, (
                    f"Quality Gate violation in {raw['asset_id']}: {dim} = {score} (< 4.0)"
                )

    def test_no_duplicate_bodies(self):
        texts = [a.text.strip() for a in self.mercury_assets]
        assert len(texts) == len(set(texts)), "Duplicate asset text found in Mercury batch"

    def test_metaphor_diversity_per_sign(self):
        for sign in SIGNS:
            sign_raw = [r for r in self.raw_assets if r["provenance"]["sign"] == sign]
            metaphors = set()
            for r in sign_raw:
                notes = json.loads(r["internal_notes"])
                metaphors.add(notes.get("metaphor_family"))
            assert len(metaphors) >= 6, (
                f"Sign {sign} must have at least 6 distinct metaphor families, got {len(metaphors)}: {metaphors}"
            )


class TestAstrologySafeExposure:
    """Validates that SafeDerivedAstrology exposes mercury_sign without leaking raw data."""

    def test_safe_models_contain_mercury_sign(self):
        now_val = datetime.now(timezone.utc)
        sda = SafeDerivedAstrology(
            user_id=uuid.uuid4(),
            sun_sign="aries",
            moon_sign="taurus",
            mercury_sign="gemini",
            element_primary="fire",
            modality_primary="cardinal",
            source_birth_data_version=1,
            engine_version="1.0.0",
        )
        assert sda.mercury_sign == "gemini"

        resp = SafeDerivedAstrologyResponse(
            user_id=uuid.uuid4(),
            sun_sign="aries",
            moon_sign="taurus",
            mercury_sign="cancer",
            element_primary="water",
            modality_primary="cardinal",
            source_birth_data_version=1,
            engine_version="1.0.0",
            updated_at=now_val,
        )
        assert resp.mercury_sign == "cancer"

    def test_safe_models_do_not_expose_private_mercury_details(self):
        fields = set(SafeDerivedAstrology.model_fields.keys())
        assert "mercury_longitude" not in fields
        assert "mercury_house" not in fields
        assert "mercury_is_retrograde" not in fields
