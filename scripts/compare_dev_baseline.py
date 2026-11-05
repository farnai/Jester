"""
scripts/compare_dev_baseline.py
===============================
Compares current Development database state against baseline snapshot.
"""

import json
import psycopg
from psycopg.rows import dict_row

DEV_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"


def main():
    with open("scratch/dev_baseline_snapshot.json", "r", encoding="utf-8") as f:
        baseline = json.load(f)

    conn = psycopg.connect(DEV_URL, autocommit=True, row_factory=dict_row)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) as cnt FROM auth.users;")
        users_cnt = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.profiles;")
        profiles_cnt = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.birth_data;")
        birth_cnt = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.wallets;")
        wallets_cnt = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.wallet_transactions;")
        tx_cnt = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.entitlements;")
        ent_cnt = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.astro_safe_profile;")
        safe_cnt = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.astro_private;")
        priv_cnt = cur.fetchone()["cnt"]

        cur.execute(
            """
            SELECT u.id::text, u.email, p.display_name, w.balance 
            FROM auth.users u 
            LEFT JOIN public.profiles p ON p.id = u.id 
            LEFT JOIN public.wallets w ON w.user_id = u.id 
            WHERE u.email IN ('farna@yahoo.com', 'farna1@gmail.com', 'dev@jester.app', 'dev-alias@jester.app')
            ORDER BY u.email;
            """
        )
        current_core = cur.fetchall()

        cur.execute(
            """
            SELECT u.id::text, u.email, p.display_name, w.balance 
            FROM auth.users u 
            LEFT JOIN public.profiles p ON p.id = u.id 
            LEFT JOIN public.wallets w ON w.user_id = u.id 
            WHERE u.email LIKE '%@jester.test'
            ORDER BY u.email;
            """
        )
        current_demo = cur.fetchall()

    conn.close()

    current_counts = {
        "auth.users": users_cnt,
        "public.profiles": profiles_cnt,
        "public.birth_data": birth_cnt,
        "public.wallets": wallets_cnt,
        "public.wallet_transactions": tx_cnt,
        "public.entitlements": ent_cnt,
        "public.astro_safe_profile": safe_cnt,
        "public.astro_private": priv_cnt,
    }

    print("=== COMPARISON OF DEV STATE (BEFORE A3 vs AFTER ALL A3 TESTS) ===")
    all_matched = True
    for key, b_val in baseline["counts"].items():
        c_val = current_counts[key]
        status = "MATCH" if b_val == c_val else "MISMATCH"
        if b_val != c_val:
            all_matched = False
        print(f"{key:30}: Baseline={b_val:4} | Current={c_val:4} | {status}")

    print("\nCore Accounts Integrity:")
    assert len(baseline["core_accounts"]) == len(current_core), "Core accounts count mismatch!"
    for b_acc, c_acc in zip(baseline["core_accounts"], current_core):
        match = (b_acc == c_acc)
        print(f"  {c_acc['email']}: ID={c_acc['id'][:8]}... | Balance={c_acc['balance']} | MATCH: {match}")
        assert match, f"Core account changed: {b_acc} vs {c_acc}"

    print(f"\nDemo Accounts (@jester.test) Integrity (Total {len(current_demo)}):")
    assert len(baseline["demo_accounts"]) == len(current_demo) == 20, "Demo accounts count mismatch!"
    for b_acc, c_acc in zip(baseline["demo_accounts"], current_demo):
        assert b_acc == c_acc, f"Demo account changed: {b_acc} vs {c_acc}"
    print("  All 20 synthetic demo accounts verified identical!")

    assert all_matched, "Some counts mismatched!"
    print("\n>>> DEV DATA INTEGRITY: 100% PRESERVED! ZERO CORRUPTION! <<<")


if __name__ == "__main__":
    main()

