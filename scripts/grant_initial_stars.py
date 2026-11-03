"""
Initial 1,000 Stars Grant Script for Local Development / QA.
Strictly guarded to run ONLY on verified local databases (127.0.0.1 / localhost).
Idempotent: will never duplicate stars on repeated executions.
Filters out all ~2,000 automated test fixtures and grants stars only to real/demo application users.
"""
import os
import sys
import uuid
from urllib.parse import urlparse
import psycopg
from psycopg.rows import dict_row

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.app.config import get_settings
from backend.app.wallet.service import grant_stars, get_or_create_wallet

GRANT_AMOUNT = 1000
TRANSACTION_TYPE = "initial_mvp_grant"
REFERENCE_ID = "initial_mvp_grant:grant_v1"
DESCRIPTION_KA = "საწყისი MVP საჩუქარი (1,000 ✦)"

# Test fixture email patterns to strictly exclude
SYNTHETIC_TEST_PATTERNS = [
    "clock_", "iat_", "warm_", "rapid_", "audit_", "step", "photo_", "exact_",
    "approx_", "unk_", "place_", "live_", "interests_", "resume_", "wave",
    "finish_", "oauth_", "reg_init_", "idemp_", "constraint_", "bad1_", "bad2_",
    "register_", "duplicate_", "pwd_reset_", "unverified_", "incomplete_",
    "complete_", "derive_", "no_overwrite_", "nodetest_", "testuser", "repro_fast_",
    "jester_qa_", "@example.invalid", "privaterelay.appleid.com", "@jester.test",
    "@jester.local"
]


def verify_local_environment() -> str:
    """
    Enforces strict environmental safety. Rejects staging/production or non-local database targets.
    """
    settings = get_settings()
    if settings.is_production:
        raise RuntimeError("CRITICAL SAFETY CHECK FAILED: ENV=production is active. Initial grant aborted.")

    db_url = settings.DATABASE_URL
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set.")

    # Parse host
    # Handles postgresql://...
    parsed = urlparse(db_url)
    hostname = parsed.hostname or ""
    port = parsed.port or 5432

    allowed_local_hosts = ["127.0.0.1", "localhost", "::1"]
    if hostname not in allowed_local_hosts:
        raise RuntimeError(
            f"CRITICAL SAFETY CHECK FAILED: Target database host '{hostname}' is not a local environment! "
            f"Allowed hosts: {allowed_local_hosts}. Initial grant aborted."
        )

    print(f"[ENV OK] Verified safe local database: {hostname}:{port}")
    return db_url


def is_synthetic_test_email(email: str) -> bool:
    low = email.lower()
    return any(pattern in low for pattern in SYNTHETIC_TEST_PATTERNS)


def run_grant():
    db_url = verify_local_environment()

    conn = psycopg.connect(db_url, autocommit=True, row_factory=dict_row)
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM auth.users;")
        total_auth_users = cur.fetchone()["cnt"]

        # Fetch all users
        cur.execute("SELECT id, email, created_at FROM auth.users ORDER BY created_at ASC;")
        all_users = cur.fetchall()

        # Fetch existing real profile IDs
        cur.execute("SELECT id, display_name FROM public.profiles;")
        profile_map = {row["id"]: row["display_name"] for row in cur.fetchall()}

    eligible_accounts = []
    excluded_accounts_count = 0

    for u in all_users:
        uid = u["id"]
        email = u["email"] or ""

        # Criteria for Real / Active Application Profile:
        # 1. Must exist in public.profiles OR be explicitly designated core dev/demo accounts
        # 2. Must NOT match synthetic test fixture patterns
        has_profile = uid in profile_map
        is_synthetic = is_synthetic_test_email(email)

        # Core accounts that are always eligible
        is_core_account = email in [
            "dev@jester.app", "dev-alias@jester.app", "demo_user@jester.app",
            "farna@gmail.com", "farna@yahoo.com", "farna1@gmail.com"
        ]

        if (has_profile or is_core_account) and not is_synthetic:
            eligible_accounts.append({
                "id": uid,
                "email": email,
                "display_name": profile_map.get(uid, email.split("@")[0]),
            })
        else:
            excluded_accounts_count += 1

    print("\n" + "=" * 65)
    print("JESTER MVP STARS INITIAL GRANT AUDIT")
    print("=" * 65)
    print(f"Total auth.users in database:    {total_auth_users}")
    print(f"Excluded test fixtures:          {excluded_accounts_count}")
    print(f"Eligible application accounts:   {len(eligible_accounts)}")
    print("=" * 65)

    granted_count = 0
    already_granted_count = 0

    for acc in eligible_accounts:
        uid = acc["id"]
        res = grant_stars(
            user_id=uid,
            amount=GRANT_AMOUNT,
            transaction_type=TRANSACTION_TYPE,
            description_ka=DESCRIPTION_KA,
            db=conn,
            reference_id=REFERENCE_ID,
            metadata={"granted_by": "initial_mvp_grant_script"},
        )
        if res["already_granted"]:
            already_granted_count += 1
            print(f"  [SKIPPED] {acc['display_name']} ({acc['email']}) -> Already granted (Balance: {res['balance']} ✦)")
        else:
            granted_count += 1
            print(f"  [GRANTED] {acc['display_name']} ({acc['email']}) -> +{GRANT_AMOUNT} ✦ (New Balance: {res['balance']} ✦)")

    conn.close()

    print("\n" + "=" * 65)
    print(f"GRANT SUMMARY: {granted_count} newly credited, {already_granted_count} already had grant.")
    print("=" * 65)


if __name__ == "__main__":
    run_grant()

