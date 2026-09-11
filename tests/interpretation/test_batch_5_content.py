"""
Tests for JESTER Batch 5 — Phase 1: Luminary Elemental Dynamics (16 Combinations, 64 Assets).
Validates:
- 16 Sun Element x Moon Element combinations
- 64 Total assets: 32 Micro (100-250 chars) and 32 Medium (400-750 chars)
- Approved semantic angles: internal_civil_war, coexistence_paradox
- Domain is 'self', layer is 'synthesis'
- Exactly 64 unique 2-word openings
- False respect controlled between 20% and 30%
- Zero Latin characters, zero asterisks, zero parentheses
- Zero pseudo-psychological / trauma causality words
"""
import json
from pathlib import Path
import re
import pytest

BATCH_FILE = Path(__file__).parents[2] / "backend" / "app" / "interpretation" / "data" / "batches" / "batch_5_synthesis.json"

EXPECTED_COMBINATIONS = [
    "fire_fire", "fire_earth", "fire_air", "fire_water",
    "earth_fire", "earth_earth", "earth_air", "earth_water",
    "air_fire", "air_earth", "air_air", "air_water",
    "water_fire", "water_earth", "water_air", "water_water"
]

EXPECTED_ANGLES = {
    "micro_01": "internal_civil_war",
    "micro_02": "coexistence_paradox",
    "med_01": "internal_civil_war",
    "med_02": "coexistence_paradox"
}

FORBIDDEN_WORDS = [
    "ბავშვობაში", "ტრავმა", "ტრავმის", "მიტოვების", "abandonment",
    "ქვეცნობიერად გეშინია", "ქვეცნობიერი შიში", "დიაგნოზი"
]


@pytest.fixture(scope="module")
def batch_5_assets():
    assert BATCH_FILE.exists(), f"Batch 5 file not found at {BATCH_FILE}"
    with open(BATCH_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def test_batch_5_total_count(batch_5_assets):
    assert len(batch_5_assets) == 64, f"Expected exactly 64 assets, got {len(batch_5_assets)}"


def test_batch_5_combinations_and_suffixes(batch_5_assets):
    comb_counts = {c: 0 for c in EXPECTED_COMBINATIONS}
    seen_ids = set()

    for asset in batch_5_assets:
        aid = asset["asset_id"]
        iid = asset["interpretation_id"]
        assert aid not in seen_ids, f"Duplicate asset_id {aid}"
        seen_ids.add(aid)

        assert asset["domain"] == "self"
        assert asset["layer"] == "synthesis"

        match = re.match(r"^self\.synthesis\.element_dynamic\.([a-z_]+)\.v1$", iid)
        assert match, f"Invalid interpretation_id: {iid}"
        comb = match.group(1)
        assert comb in comb_counts, f"Unexpected combination: {comb}"
        comb_counts[comb] += 1

        suffix = aid.split(".")[-1]
        assert suffix in EXPECTED_ANGLES, f"Unexpected suffix {suffix} in {aid}"
        assert asset["semantic_angle"] == EXPECTED_ANGLES[suffix]

    for comb, count in comb_counts.items():
        assert count == 4, f"Combination {comb} has {count} assets instead of 4"


def test_batch_5_depths_and_lengths(batch_5_assets):
    micros = [a for a in batch_5_assets if a["depth"] == "micro"]
    mediums = [a for a in batch_5_assets if a["depth"] == "medium"]

    assert len(micros) == 32
    assert len(mediums) == 32

    for a in micros:
        t_len = len(a["text"].strip())
        assert 100 <= t_len <= 250, f"{a['asset_id']}: micro length {t_len} not in [100, 250]"

    for a in mediums:
        t_len = len(a["text"].strip())
        assert 400 <= t_len <= 750, f"{a['asset_id']}: medium length {t_len} not in [400, 750]"


def test_batch_5_false_respect_ratio(batch_5_assets):
    fr_count = sum(1 for a in batch_5_assets if a.get("false_respect_used", False))
    pct = (fr_count / len(batch_5_assets)) * 100
    assert 20.0 <= pct <= 30.0, f"False respect {pct:.1f}% ({fr_count}/{len(batch_5_assets)}) outside [20%, 30%]"


def test_batch_5_opening_uniqueness(batch_5_assets):
    openings = {}
    for a in batch_5_assets:
        words = a["text"].strip().split()
        assert len(words) >= 2, f"{a['asset_id']} has less than 2 words"
        op = f"{words[0]} {words[1]}"
        openings.setdefault(op, []).append(a["asset_id"])

    dups = {op: aids for op, aids in openings.items() if len(aids) > 1}
    assert not dups, f"Duplicate openings found: {dups}"
    assert len(openings) == 64


def test_batch_5_cleanliness_and_firewall(batch_5_assets):
    for a in batch_5_assets:
        text = a["text"]
        aid = a["asset_id"]

        assert "(" not in text and ")" not in text, f"{aid} contains parentheses"
        assert "*" not in text, f"{aid} contains asterisks"

        latin = re.findall(r"[a-zA-Z]", text)
        assert not latin, f"{aid} contains Latin characters: {set(latin)}"

        for fw in FORBIDDEN_WORDS:
            assert fw not in text, f"{aid} contains forbidden phrase '{fw}'"
