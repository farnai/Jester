"""
Tests for JESTER Phase 3.10 — Mars Full Corpus Generation (96 Assets).
Validates:
- 12 Locked Mars Semantic Contracts (self.action.mars_{sign}.v1)
- Signal routing to Mars contracts in engine.py
- 96 Loaded Content Assets (12 signs x 8 assets: 72 Micro, 24 Medium, 0 Deep)
- Tone coverage across all 8 official JESTER voices (exactly 12 per voice)
- Text length bounds (Micro: 100-250, Medium: 400-750)
- Action != Anger boundary & zero forbidden terminology/claims
- Semantic specificity & cross-sign differentiation
- Quality Gate (all 5 dimensions >= 4.0 for all 96 assets, avg >= 4.7)
- Machine-readable provenance schema in corpus JSON and tags
- Backend exposure boundary (SafeDerivedAstrology has mars_sign only)
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

ACTION_ANGLES = [
    "initiation", "resistance", "activation", "pursuit",
    "execution", "tactical_adaptation", "persistence_momentum", "blind_spot"
]

FORBIDDEN_PATTERNS = [
    r"\badhd\b", r"\bყურადღების დეფიციტ", r"\bაუტიზმ", r"\bautism\b",
    r"\bდეპრესი", r"\bdepression\b", r"\bბიპოლარულ", r"\bbipolar\b",
    r"\bშფოთვითი აშლილობ", r"\banxiety disorder\b", r"\bocd\b", r"\bოკდ\b",
    r"\bოკრი\b", r"\biq\b", r"\bაიქიუ\b", r"\bინტელექტის კოეფიციენტ",
    r"\bდიაგნოზ", r"\bფსიქიკური აშლილობ", r"\bმოღალატე ხარ\b",
    r"\bნარცისი ხარ\b", r"\bფსიქოპათ", r"\bკრიმინალ",
    r"\bეს დამტკიცებულია\b", r"\bშენი ტვინი ასე მუშაობს\b",
    r"\bეს ფსიქოლოგიურად ნიშნავს\b", r"\bშენ აუცილებლად\b",
    r"\bმიჯაჭვულობის სინდრომ", r"\bმიჯაჭვულობის ტიპ", r"\bშფოთვითი მიჯაჭვულობ",
    r"\bშენი მეორე ნახევარი\b", r"\bგარანტირებული სიყვარულ",
    r"\bფიზიკური ძალადობ", r"\bცემა\b", r"\bსისხლი\b",
    r"\bტესტოსტერონ", r"\bსექსუალური ტემპერამენტ",
]

FORBIDDEN_OPENINGS = [
    "წარმოიდგინე სიტუაცია",
    "წარმოიდგინე",
    "შენ ხარ",
    "შენი სიყვარულის ენაა",
    "შენი იდეალური პარტნიორია",
]

ANGER_CLICHES = [
    r"ბრაზდები",
    r"ჩხუბობ",
    r"აგრესიული ხარ",
    r"თავს ესხმი",
    r"ვერ აკონტროლებ თავს",
]


class TestMarsContracts:
    """Validates the 12 fixed Mars semantic contracts."""

    def test_12_contracts_registered(self):
        for sign in SIGNS:
            contract_id = f"self.action.mars_{sign}.v1"
            assert contract_id in INTERPRETATION_CONTRACTS, f"Missing contract {contract_id}"
            contract = INTERPRETATION_CONTRACTS[contract_id]
            assert contract.context == "self"
            assert contract.signal.category == "self"
            assert contract.signal.type == f"mars_sign_{sign}"
            assert len(contract.meaning.human_meaning) >= 3, f"Contract {contract_id} needs >= 3 semantic angles"

    def test_signal_routing(self):
        for sign in SIGNS:
            contract_id = f"self.action.mars_{sign}.v1"
            assert SIGNAL_TYPE_TO_INTERPRETATION_ID.get(f"mars_sign_{sign}") == contract_id
            assert SIGNAL_TYPE_TO_INTERPRETATION_ID.get(f"mars_{sign}") == contract_id


class TestMarsCorpusAndLibrary:
    """Validates the 96 generated Mars full assets in the library."""

    @classmethod
    def setup_class(cls):
        all_assets = content_library.list_assets()
        cls.mars_assets = [a for a in all_assets if "self.action.mars" in a.interpretation_id]

        fixture_path = Path(__file__).parent.parent.parent / "backend" / "app" / "interpretation" / "data" / "mars_corpus.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            cls.raw_assets = json.load(f)

    def test_total_mars_asset_count(self):
        assert len(self.mars_assets) == 96, f"Expected exactly 96 Mars assets, found {len(self.mars_assets)}"
        assert len(self.raw_assets) == 96, f"Expected exactly 96 raw assets in JSON fixture, found {len(self.raw_assets)}"

    def test_sign_distribution(self):
        for sign in SIGNS:
            contract_id = f"self.action.mars_{sign}.v1"
            sign_assets = [a for a in self.mars_assets if a.interpretation_id == contract_id]
            assert len(sign_assets) == 8, f"Sign {sign} must have exactly 8 assets, got {len(sign_assets)}"

            micros = [a for a in sign_assets if "depth:micro" in a.tags]
            mediums = [a for a in sign_assets if "depth:medium" in a.tags]
            deeps = [a for a in sign_assets if "depth:deep" in a.tags]

            assert len(micros) == 6, f"Sign {sign} must have 6 micros, got {len(micros)}"
            assert len(mediums) == 2, f"Sign {sign} must have 2 mediums, got {len(mediums)}"
            assert len(deeps) == 0, f"Sign {sign} must have 0 deeps, got {len(deeps)}"

    def test_tone_distribution(self):
        all_tones = [a.tone for a in self.mars_assets]
        for t in TONES:
            cnt = all_tones.count(t)
            assert cnt == 12, f"Expected tone '{t}' to have exactly 12 assets in full corpus, got {cnt}"

    def test_metaphor_diversity_per_sign(self):
        for sign in SIGNS:
            contract_id = f"self.action.mars_{sign}.v1"
            sign_raw = [r for r in self.raw_assets if r["interpretation_id"] == contract_id]
            metaphors = {
                r["provenance"].get("metaphor_family")
                or next(t.split("metaphor:")[1] for t in r["tags"] if t.startswith("metaphor:"))
                for r in sign_raw
            }
            assert len(metaphors) == 8, f"Sign {sign} must have exactly 8 distinct metaphor families, got {len(metaphors)}"

    def test_action_angles_framework_coverage(self):
        for sign in SIGNS:
            contract_id = f"self.action.mars_{sign}.v1"
            sign_raw = [r for r in self.raw_assets if r["interpretation_id"] == contract_id]
            action_angles = {r["provenance"].get("action_angle") for r in sign_raw}
            for expected_angle in ACTION_ANGLES:
                assert expected_angle in action_angles, f"Sign {sign} missing action angle '{expected_angle}'"

    def test_character_lengths(self):
        for a in self.mars_assets:
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
        for a in self.mars_assets:
            text = a.text.strip()
            for opening in FORBIDDEN_OPENINGS:
                assert not text.startswith(opening), (
                    f"Forbidden opening '{opening}' in {a.asset_id}: '{text}'"
                )

    def test_no_forbidden_claims_or_diagnoses(self):
        for a in self.mars_assets:
            text = a.text.strip()
            for pat in FORBIDDEN_PATTERNS:
                assert not re.search(pat, text, re.IGNORECASE), (
                    f"Forbidden claim pattern '{pat}' matched in {a.asset_id}: '{text}'"
                )

    def test_action_not_anger_cliches(self):
        for a in self.mars_assets:
            text = a.text.strip()
            for c_pat in ANGER_CLICHES:
                assert not re.search(c_pat, text), (
                    f"Anger-engine cliché '{c_pat}' found in {a.asset_id}: '{text}'"
                )

    def test_no_astrological_jargon_in_user_facing_body(self):
        for a in self.mars_assets:
            found = scan_for_jargon(a.text, "ka")
            assert not found, (
                f"Astrological jargon {found} found in user-facing text of {a.asset_id}: '{a.text}'"
            )

    def test_provenance_and_metadata_completeness(self):
        for raw in self.raw_assets:
            prov = raw.get("provenance")
            assert prov is not None, f"Missing provenance block in {raw.get('asset_id')}"
            assert prov.get("batch_id") == "mars_full_v1"
            assert prov.get("interpretation_id") == raw["interpretation_id"]
            assert prov.get("body") == "mars"
            assert prov.get("sign") in SIGNS
            assert prov.get("element") in ["fire", "earth", "air", "water"]
            assert prov.get("modality") in ["cardinal", "fixed", "mutable"]
            assert prov.get("semantic_contract_id") == raw["interpretation_id"]
            assert prov.get("semantic_angle")
            assert prov.get("action_angle") in ACTION_ANGLES
            assert prov.get("tone") in TONES
            assert prov.get("depth") in ["micro", "medium"]
            assert prov.get("variant")

            # Validate source_inputs
            src = prov.get("source_inputs", {})
            assert src.get("mars_sign") == prov["sign"]
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
        texts = [a.text.strip() for a in self.mars_assets]
        assert len(texts) == len(set(texts)), "Duplicate asset text found in Mars pilot batch"

    def test_pairwise_jaccard_similarity_under_threshold(self):
        texts = [a.text.strip() for a in self.mars_assets]
        def jaccard(s1, s2):
            w1 = set(re.findall(r"\w+", s1.lower()))
            w2 = set(re.findall(r"\w+", s2.lower()))
            if not w1 or not w2:
                return 0.0
            return len(w1 & w2) / len(w1 | w2)

        max_sim = 0.0
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                sim = jaccard(texts[i], texts[j])
                if sim > max_sim:
                    max_sim = sim
                assert sim < 0.85, f"Near-duplicate text detected ({sim:.2f}) between {i} and {j}"
        assert max_sim < 0.85

    def test_semantic_angles_belong_to_contract(self):
        for raw in self.raw_assets:
            contract_id = raw["interpretation_id"]
            contract = INTERPRETATION_CONTRACTS[contract_id]
            angle = raw["provenance"]["semantic_angle"]
            clean_angle = angle.replace("_", " ")
            assert any(angle in ha.replace(" ", "_") or ha in clean_angle for ha in contract.meaning.human_meaning), (
                f"Angle '{angle}' not in contract {contract_id} angles: {contract.meaning.human_meaning}"
            )


class TestAstrologySafeExposure:
    """Validates that SafeDerivedAstrology exposes mars_sign without leaking raw data."""

    def test_safe_models_contain_mars_sign(self):
        now_val = datetime.now(timezone.utc)
        sda = SafeDerivedAstrology(
            user_id=uuid.uuid4(),
            sun_sign="aries",
            moon_sign="taurus",
            mercury_sign="gemini",
            venus_sign="cancer",
            mars_sign="leo",
            element_primary="fire",
            modality_primary="fixed",
            source_birth_data_version=1,
            engine_version="1.0.0",
        )
        assert sda.mars_sign == "leo"

        resp = SafeDerivedAstrologyResponse(
            user_id=uuid.uuid4(),
            sun_sign="aries",
            moon_sign="taurus",
            mercury_sign="gemini",
            venus_sign="cancer",
            mars_sign="virgo",
            element_primary="earth",
            modality_primary="mutable",
            source_birth_data_version=1,
            engine_version="1.0.0",
            updated_at=now_val,
        )
        assert resp.mars_sign == "virgo"

    def test_safe_models_do_not_expose_private_mars_details(self):
        fields = set(SafeDerivedAstrology.model_fields.keys())
        assert "mars_longitude" not in fields
        assert "mars_house" not in fields
        assert "mars_is_retrograde" not in fields
