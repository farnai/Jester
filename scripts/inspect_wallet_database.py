import sys
import psycopg
from psycopg.rows import dict_row

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = psycopg.connect("postgresql://postgres:postgres@127.0.0.1:54322/postgres")

with conn.cursor(row_factory=dict_row) as cur:
    # 1. Total Wallets
    cur.execute("SELECT COUNT(*) AS total_wallets FROM public.wallets;")
    total_wallets = cur.fetchone()["total_wallets"]

    # 2. Wallets with initial grant
    cur.execute("""
        SELECT 
            w.user_id,
            u.email,
            p.display_name,
            w.balance,
            (SELECT COUNT(*) FROM public.wallet_transactions t 
             WHERE t.user_id = w.user_id AND t.transaction_type = 'initial_mvp_grant') AS grant_tx_count,
            (SELECT COUNT(*) FROM public.wallet_transactions t 
             WHERE t.user_id = w.user_id) AS total_tx_count
        FROM public.wallets w
        JOIN auth.users u ON u.id = w.user_id
        LEFT JOIN public.profiles p ON p.id = w.user_id
        WHERE u.email NOT LIKE '%test%' AND u.email NOT LIKE '%fixtures%'
        ORDER BY w.created_at ASC;
    """)
    real_wallets = cur.fetchall()

    # 3. Check for any duplicate grants across the whole table
    cur.execute("""
        SELECT user_id, transaction_type, reference_id, COUNT(*) AS count
        FROM public.wallet_transactions
        WHERE reference_id IS NOT NULL
        GROUP BY user_id, transaction_type, reference_id
        HAVING COUNT(*) > 1;
    """)
    duplicate_references = cur.fetchall()

    print(f"=== JESTER LOCAL DATABASE WALLETS AUDIT ===")
    print(f"Total Wallets (including isolated test suites): {total_wallets}")
    print(f"Eligible Real / Demo Application Wallets: {len(real_wallets)}")
    print(f"Duplicate Idempotent Transactions Detected: {len(duplicate_references)}")
    print("\n--- Real Application Users Balances & Grants ---")
    for r in real_wallets:
        print(f"Email: {r['email']:<28} | Name: {str(r['display_name']):<18} | Balance: {r['balance']} ✦ | Grants: {r['grant_tx_count']} | Total TXs: {r['total_tx_count']}")

    # 4. Check Entitlements
    cur.execute("""
        SELECT e.user_id, u.email, e.item_type, e.item_key, e.unlocked_at
        FROM public.entitlements e
        JOIN auth.users u ON u.id = e.user_id
        ORDER BY e.unlocked_at DESC;
    """)
    entitlements = cur.fetchall()
    print(f"\n--- Active Entitlements ({len(entitlements)}) ---")
    for e in entitlements[:15]:
        print(f"User: {e['email']:<25} | Item: {e['item_type']} -> {e['item_key']} | Unlocked At: {e['unlocked_at']}")
