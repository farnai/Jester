"""
Master Content Corpus Generator & QA Pipeline for JESTER V1.
Generates 5,000–10,000 production-ready AI_DRAFT Content Assets across 112 semantic contracts.
Enforces:
- 70-80% Georgian, 20-30% English distribution
- Multi-tone distribution (witty, playful, soft, bold, romantic, savage)
- Multi-context mapping (self, relationship, friendship, daily_energy, etc.)
- Strict zero-jargon filtering
- Exact duplicate and near-duplicate (<0.85 Jaccard similarity) rejection
- Outputs to backend/app/interpretation/data/content_corpus.json
"""
import json
from pathlib import Path
import sys

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from scripts.corpus_builders.common import build_assets_for_contract
from scripts.corpus_builders.daily_energy_contracts import get_daily_energy_contracts_data
from scripts.corpus_builders.friendship_contracts import get_friendship_contracts_data
from scripts.corpus_builders.relationship_contracts import get_relationship_contracts_data
from scripts.corpus_builders.self_contracts import get_self_contracts_data


def run_generator() -> None:
    print("=" * 70)
    print("JESTER V1 — Content Corpus Generation & QA Pipeline")
    print("=" * 70)

    # 1. Collect all contract seed data
    self_seeds = get_self_contracts_data()
    rel_seeds = get_relationship_contracts_data()
    friend_seeds = get_friendship_contracts_data()
    daily_seeds = get_daily_energy_contracts_data()

    all_seeds = self_seeds + rel_seeds + friend_seeds + daily_seeds
    print(f"Total Contract Seed Definitions: {len(all_seeds)}")
    print(f"  - Self / Me: {len(self_seeds)}")
    print(f"  - Relationship: {len(rel_seeds)}")
    print(f"  - Friendship: {len(friend_seeds)}")
    print(f"  - Daily Energy: {len(daily_seeds)}")

    # Verify all seed contracts exist in INTERPRETATION_CONTRACTS
    for seed in all_seeds:
        if seed.interpretation_id not in INTERPRETATION_CONTRACTS:
            print(f"WARNING: Seed contract '{seed.interpretation_id}' not found in INTERPRETATION_CONTRACTS!")

    existing_asset_texts: set[str] = set()
    all_seen_by_interp: dict[str, list[str]] = {}

    all_assets: list[dict] = []
    total_stats = {
        "generated": 0,
        "rejected_duplicate": 0,
        "rejected_near_duplicate": 0,
        "rejected_jargon": 0,
        "rejected_length": 0,
    }

    # 2. Build assets for each contract
    for seed in all_seeds:
        assets, stats = build_assets_for_contract(seed, existing_asset_texts, all_seen_by_interp)
        all_assets.extend(assets)
        for k, v in stats.items():
            total_stats[k] += v

    print("-" * 70)
    print("Generation & QA Statistics:")
    print(f"  Total Assets Generated: {total_stats['generated']}")
    print(f"  Rejected (Exact Duplicate): {total_stats['rejected_duplicate']}")
    print(f"  Rejected (Near-Duplicate >= 0.85): {total_stats['rejected_near_duplicate']}")
    print(f"  Rejected (Astrology Jargon): {total_stats['rejected_jargon']}")
    print(f"  Rejected (Invalid Length): {total_stats['rejected_length']}")

    # 3. Distributions
    by_locale: dict[str, int] = {}
    by_tone: dict[str, int] = {}
    by_context: dict[str, int] = {}
    by_contract: dict[str, int] = {}

    for a in all_assets:
        by_locale[a["locale"]] = by_locale.get(a["locale"], 0) + 1
        by_tone[a["tone"]] = by_tone.get(a["tone"], 0) + 1
        by_context[a["context"]] = by_context.get(a["context"], 0) + 1
        by_contract[a["interpretation_id"]] = by_contract.get(a["interpretation_id"], 0) + 1

    print("-" * 70)
    print("Locale Distribution:")
    for loc, cnt in sorted(by_locale.items()):
        pct = (cnt / len(all_assets)) * 100
        print(f"  {loc}: {cnt} ({pct:.1f}%)")

    print("-" * 70)
    print("Tone Distribution:")
    for t, cnt in sorted(by_tone.items(), key=lambda x: -x[1]):
        pct = (cnt / len(all_assets)) * 100
        print(f"  {t}: {cnt} ({pct:.1f}%)")

    print("-" * 70)
    print("Context Distribution:")
    for c, cnt in sorted(by_context.items(), key=lambda x: -x[1]):
        pct = (cnt / len(all_assets)) * 100
        print(f"  {c}: {cnt} ({pct:.1f}%)")

    # 4. Save to JSON fixture
    out_dir = root_dir / "backend" / "app" / "interpretation" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "content_corpus.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_assets, f, ensure_ascii=False, indent=2)

    file_size_mb = out_file.stat().st_size / (1024 * 1024)
    print("-" * 70)
    print(f"Successfully saved {len(all_assets)} Content Assets to:")
    print(f"  {out_file} ({file_size_mb:.2f} MB)")
    print("=" * 70)


if __name__ == "__main__":
    run_generator()
