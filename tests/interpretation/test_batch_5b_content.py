"""
Tests for JESTER Batch 5B — 12 Life Verdicts / Chart-Level Synthesis (12 Archetypes, 60 Assets).
Validates:
- 12 Archetypes (element_primary x modality_primary)
- 60 Total assets: 36 Micro (100-250 chars) and 24 Medium (400-750 chars)
- Approved semantic angles: holistic_blind_spot, signature_paradox
- Domain is 'self', layer is 'verdict'
- Stable IDs: self.verdict.archetype_<archetype>.v1.{micro_01..03, medium_01..02}
- Exactly 60 unique 2-word openings
- False respect controlled between 20% and 30% (exactly 12/60 = 20.0%)
- Zero Latin characters, zero asterisks, zero parentheses, zero meta-language ('არქეტიპი')
- Zero pseudo-psychological / trauma causality words
"""
import json
from pathlib import Path
import re
import pytest

BATCH_FILE = Path(__file__).parents[2] / "backend" / "app" / "interpretation" / "data" / "batches" / "batch_5b_verdicts.json"

EXPECTED_ARCHETYPES = [
    "cardinal_fire", "fixed_fire", "mutable_fire",
    "cardinal_earth", "fixed_earth", "mutable_earth",
    "cardinal_air", "fixed_air", "mutable_air",
    "cardinal_water", "fixed_water", "mutable_water"
]

EXPECTED_SUFFIXES = {
    "micro_01": {"depth": "micro", "angle": "holistic_blind_spot", "min_len": 100, "max_len": 250},
    "micro_02": {"depth": "micro", "angle": "signature_paradox", "min_len": 100, "max_len": 250},
    "micro_03": {"depth": "micro", "angle": "holistic_blind_spot", "min_len": 100, "max_len": 250},
    "medium_01": {"depth": "medium", "angle": "holistic_blind_spot", "min_len": 400, "max_len": 750},
    "medium_02": {"depth": "medium", "angle": "signature_paradox", "min_len": 400, "max_len": 750},
}

FORBIDDEN_WORDS = [
    "ბავშვობაში", "ტრავმა", "ტრავმის", "მიტოვების", "abandonment",
    "ქვეცნობიერად გეშინია", "ქვეცნობიერი შიში", "დიაგნოზი", "არქეტიპი"
]


@pytest.fixture(scope="module")
def batch_5b_assets():
    assert BATCH_FILE.exists(), f"Batch 5B file not found at {BATCH_FILE}"
    with open(BATCH_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def test_batch_5b_total_count(batch_5b_assets):
    assert len(batch_5b_assets) == 60, f"Expected exactly 60 assets, got {len(batch_5b_assets)}"


def test_batch_5b_archetypes_and_suffixes(batch_5b_assets):
    arch_counts = {a: 0 for a in EXPECTED_ARCHETYPES}
    seen_ids = set()

    for asset in batch_5b_assets:
        aid = asset["asset_id"]
        iid = asset["interpretation_id"]
        assert aid not in seen_ids, f"Duplicate asset_id {aid}"
        seen_ids.add(aid)

        assert asset["domain"] == "self"
        assert asset["layer"] == "verdict"
        assert asset["tone"] == "jester"

        match = re.match(r"^self\.verdict\.archetype_([a-z_]+)\.v1$", iid)
        assert match, f"Invalid interpretation_id: {iid}"
        arch = match.group(1)
        assert arch in arch_counts, f"Unexpected archetype: {arch}"
        arch_counts[arch] += 1

        suffix = aid.split(".")[-1]
        assert suffix in EXPECTED_SUFFIXES, f"Unexpected suffix {suffix} in {aid}"
        rule = EXPECTED_SUFFIXES[suffix]
        assert asset["semantic_angle"] == rule["angle"]
        assert asset["depth"] == rule["depth"]

    for arch, count in arch_counts.items():
        assert count == 5, f"Archetype {arch} has {count} assets instead of 5"


def test_batch_5b_depths_and_lengths(batch_5b_assets):
    micros = [a for a in batch_5b_assets if a["depth"] == "micro"]
    mediums = [a for a in batch_5b_assets if a["depth"] == "medium"]

    assert len(micros) == 36
    assert len(mediums) == 24

    for a in micros:
        t_len = len(a["text"].strip())
        assert 100 <= t_len <= 250, f"{a['asset_id']}: micro length {t_len} not in [100, 250]"

    for a in mediums:
        t_len = len(a["text"].strip())
        assert 400 <= t_len <= 750, f"{a['asset_id']}: medium length {t_len} not in [400, 750]"


def test_batch_5b_false_respect_ratio(batch_5b_assets):
    fr_count = sum(1 for a in batch_5b_assets if a.get("false_respect_used", False))
    pct = (fr_count / len(batch_5b_assets)) * 100
    assert 20.0 <= pct <= 30.0, f"False respect {pct:.1f}% ({fr_count}/{len(batch_5b_assets)}) outside [20%, 30%]"


def test_batch_5b_opening_uniqueness(batch_5b_assets):
    openings = {}
    for a in batch_5b_assets:
        words = a["text"].strip().split()
        assert len(words) >= 2, f"{a['asset_id']} has less than 2 words"
        op = f"{words[0]} {words[1]}"
        openings.setdefault(op, []).append(a["asset_id"])

    dups = {op: aids for op, aids in openings.items() if len(aids) > 1}
    assert not dups, f"Duplicate openings found: {dups}"
    assert len(openings) == 60


def test_batch_5b_cleanliness_and_firewall(batch_5b_assets):
    for a in batch_5b_assets:
        text = a["text"]
        aid = a["asset_id"]

        assert "(" not in text and ")" not in text, f"{aid} contains parentheses"
        assert "*" not in text, f"{aid} contains asterisks"

        latin = re.findall(r"[a-zA-Z]", text)
        assert not latin, f"{aid} contains Latin characters: {set(latin)}"

        for fw in FORBIDDEN_WORDS:
            assert fw not in text, f"{aid} contains forbidden phrase '{fw}'"
