"""
scripts/record_dev_baseline.py
==============================
Records detailed baseline snapshot of Development database.
"""

import json
import psycopg
from psycopg.rows import dict_row

DEV_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"


def main():
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

        # Core accounts
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
        core_accounts = cur.fetchall()

        # 20 Demo accounts
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
        demo_accounts = cur.fetchall()

    conn.close()

    baseline = {
        "counts": {
            "auth.users": users_cnt,
            "public.profiles": profiles_cnt,
            "public.birth_data": birth_cnt,
            "public.wallets": wallets_cnt,
            "public.wallet_transactions": tx_cnt,
            "public.entitlements": ent_cnt,
            "public.astro_safe_profile": safe_cnt,
            "public.astro_private": priv_cnt,
        },
        "core_accounts": core_accounts,
        "demo_accounts": demo_accounts,
    }

    with open("scratch/dev_baseline_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2, default=str)

    print("Recorded DEV Baseline Snapshot:")
    print(f"Users: {users_cnt}, Profiles: {profiles_cnt}, Wallets: {wallets_cnt}")
    print(f"Core accounts tracked: {len(core_accounts)}")
    print(f"Demo accounts tracked: {len(demo_accounts)}")


if __name__ == "__main__":
    main()

