"""
backend.app.tools.data_manager
==============================
Canonical Data Manager CLI for JESTER.

Supported Commands:
- list:   Display registered cohorts, categories, versions, environments, and status. (Read-only)
- status: Report catalog metadata and actual database state. (Read-only)
- verify: Validate catalog metadata and database integrity using A4 validator. (Read-only)
- plan:   Deterministic preview of a proposed seed operation. (Read-only)
- seed:   Safe, creation-only provisioning with explicit plan application. (Guarded)

Invariants:
1. No DELETE, TRUNCATE, or DROP operations.
2. Protected cohorts (protected-core-dev-v1, historical-unmanaged-dev) are strictly read-only.
3. Fail-closed multi-signal environment verification on all database connections.
4. Safe idempotency: repeated execution does not duplicate, overwrite, or mutate existing records.
"""

import argparse
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
import psycopg
from psycopg.rows import dict_row

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import get_settings
from backend.app.core.environment_verifier import (
    verify_environment_safety,
    EnvironmentSafetyError,
    APPROVED_TEST_DB_PORT,
    APPROVED_TEST_KONG_PORT,
    DEV_DB_PORT,
    DEV_KONG_PORT,
)
from backend.app.data_catalog import (
    load_catalog,
    get_cohort,
    list_cohorts,
    load_cohort_source,
    validate_catalog_metadata,
    validate_cohort_in_database,
    Cohort,
    CohortCategory,
    CohortStatus,
    CatalogSchema,
)
from backend.app.astrology.natal import recalculate_user_astrology
from backend.app.wallet.service import get_or_create_wallet

PROTECTED_COHORT_IDS = {"protected-core-dev-v1", "historical-unmanaged-dev"}


def get_environment_db_url(env_name: str) -> str:
    """Returns the verified database URL for the requested environment."""
    env = env_name.lower().strip()
    if env == "development":
        return os.environ.get(
            "DEV_DATABASE_URL",
            f"postgresql://postgres:postgres@127.0.0.1:{DEV_DB_PORT}/postgres",
        )
    elif env == "test":
        return os.environ.get(
            "TEST_DATABASE_URL",
            f"postgresql://postgres:postgres@127.0.0.1:{APPROVED_TEST_DB_PORT}/postgres",
        )
    else:
        raise ValueError(f"Unsupported environment '{env_name}'. Choose 'development' or 'test'.")


def get_verified_connection(env_name: str) -> psycopg.Connection:
    """Establishes a fail-closed connection with multi-signal environment verification."""
    env = env_name.lower().strip()
    os.environ["ENV"] = env
    db_url = get_environment_db_url(env)
    verify_environment_safety(db_url=db_url, expected_env=env)
    return psycopg.connect(db_url, autocommit=True, row_factory=dict_row)


# ==============================================================================
# COMMAND: LIST
# ==============================================================================
def cmd_list(args: argparse.Namespace) -> int:
    """Lists registered cohorts from the canonical catalog."""
    catalog = load_catalog()
    cohorts = list_cohorts(
        category=args.category,
        environment=args.env,
        status=args.status,
        catalog=catalog,
    )

    if args.json:
        data = [c.model_dump(mode="json") for c in cohorts]
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print("=" * 95)
    print(f"JESTER DATA CATALOG: COHORTS ({len(cohorts)} registered)")
    print("=" * 95)
    header = f"{'Cohort ID':<26} {'Category':<22} {'Ver':<7} {'Status':<10} {'Count':<7} {'Environments'}"
    print(header)
    print("-" * 95)
    for c in cohorts:
        envs = ", ".join(c.environment)
        status_tag = f"[{c.status.value.upper()}]"
        print(f"{c.id:<26} {c.category.value:<22} {c.version:<7} {status_tag:<10} {c.expected_count:<7} {envs}")
    print("=" * 95)
    return 0


# ==============================================================================
# COMMAND: STATUS
# ==============================================================================
def cmd_status(args: argparse.Namespace) -> int:
    """Reports catalog status and checks actual database provisioning state."""
    catalog = load_catalog()
    target_env = args.env or "development"

    try:
        conn = get_verified_connection(target_env)
    except Exception as e:
        print(f"CRITICAL: Failed to connect to '{target_env}' database: {e}")
        return 1

    with conn.cursor() as cur:
        cur.execute("SELECT count(*) as cnt FROM auth.users;")
        total_users = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.profiles;")
        total_profiles = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.birth_data;")
        total_birth_data = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.wallets;")
        total_wallets = cur.fetchone()["cnt"]

    # Filter cohorts for this environment
    cohorts_to_check = [
        c for c in catalog.cohorts
        if target_env in c.environment and (not args.cohort or c.id == args.cohort)
    ]

    declared_cohort_members: set[str] = set()
    cohort_reports: List[Dict[str, Any]] = []

    for cohort in cohorts_to_check:
        report = validate_cohort_in_database(cohort, conn, base_dir=PROJECT_ROOT)
        actual_found = 0
        missing_count = 0
        state = "NOT_PROVISIONED"

        if cohort.source.endswith(".json"):
            try:
                sources = load_cohort_source(cohort, base_dir=PROJECT_ROOT)
                emails = [r["email"] for r in sources if "email" in r]
                declared_cohort_members.update(emails)
                with conn.cursor() as cur:
                    cur.execute("SELECT count(*) as cnt FROM auth.users WHERE email = ANY(%s);", (emails,))
                    actual_found = cur.fetchone()["cnt"]
                missing_count = max(0, cohort.expected_count - actual_found)
                if actual_found == cohort.expected_count and report.valid:
                    state = "PROVISIONED_AND_VALID"
                elif actual_found > 0:
                    state = f"PARTIAL ({actual_found}/{cohort.expected_count})"
            except Exception:
                pass
        else:
            state = "NOT_APPLICABLE (Test module source)"

        cohort_reports.append({
            "cohort_id": cohort.id,
            "category": cohort.category.value,
            "status": cohort.status.value,
            "expected_count": cohort.expected_count,
            "actual_found": actual_found,
            "missing_count": missing_count,
            "state": state,
            "valid": report.valid,
            "issues_count": len(report.issues),
        })

    # Unmanaged / Unknown accounts calculation
    unmanaged_count = 0
    if target_env == "development":
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) as cnt FROM auth.users WHERE email NOT LIKE '%@jester.test' AND email NOT IN ('dev@jester.app', 'dev-alias@jester.app', 'farna@yahoo.com', 'farna1@gmail.com');")
            unmanaged_count = cur.fetchone()["cnt"]

    conn.close()

    if args.json:
        result = {
            "environment": target_env,
            "database_metrics": {
                "total_users": total_users,
                "total_profiles": total_profiles,
                "total_birth_data": total_birth_data,
                "total_wallets": total_wallets,
                "unmanaged_identities_count": unmanaged_count,
            },
            "cohorts": cohort_reports,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print("=" * 80)
    print(f"JESTER DATABASE & COHORT STATUS: [{target_env.upper()}]")
    print("=" * 80)
    print(f"Total Users:      {total_users:<6} | Total Profiles: {total_profiles}")
    print(f"Total Birth Data: {total_birth_data:<6} | Total Wallets:  {total_wallets}")
    if unmanaged_count > 0:
        print(f"Historical / Unmanaged Identities: {unmanaged_count} (Protected from unauthorized deletion)")
    print("-" * 80)
    print(f"{'Cohort ID':<26} {'Category':<18} {'Expected':<9} {'Found':<7} {'State'}")
    print("-" * 80)
    for cr in cohort_reports:
        print(f"{cr['cohort_id']:<26} {cr['category']:<18} {cr['expected_count']:<9} {cr['actual_found']:<7} {cr['state']}")
    print("=" * 80)
    return 0


# ==============================================================================
# COMMAND: VERIFY
# ==============================================================================
def cmd_verify(args: argparse.Namespace) -> int:
    """Verifies catalog schemas, dependencies, and database integrity."""
    catalog = load_catalog()
    print("=" * 80)
    print("JESTER DATA CATALOG: INTEGRITY VERIFICATION")
    print("=" * 80)

    # 1. In-memory metadata verification
    meta_report = validate_catalog_metadata(catalog, base_dir=PROJECT_ROOT)
    print(f"Metadata Validation: {'PASSED' if meta_report.valid else 'FAILED'} ({meta_report.checked_cohorts_count} cohorts checked)")

    has_errors = not meta_report.valid
    for issue in meta_report.issues:
        tag = f"[{issue.level.upper()}]"
        print(f"  {tag:<9} Cohort: '{issue.cohort_id}' | Rule: {issue.rule} -> {issue.message}")

    # 2. Database verification if environment requested or reachable
    target_env = args.env
    if target_env:
        print("-" * 80)
        print(f"Database Verification Target: [{target_env.upper()}]")
        try:
            conn = get_verified_connection(target_env)
            cohorts_to_verify = [
                c for c in catalog.cohorts
                if target_env in c.environment and (not args.cohort or c.id == args.cohort)
            ]
            for cohort in cohorts_to_verify:
                db_report = validate_cohort_in_database(cohort, conn, base_dir=PROJECT_ROOT)
                res_str = "PASSED" if db_report.valid else "FAILED"
                print(f"  Cohort '{cohort.id}': {res_str}")
                if not db_report.valid:
                    has_errors = True
                    for issue in db_report.issues:
                        print(f"    - [{issue.level.upper()}] Rule: {issue.rule} -> {issue.message}")
            conn.close()
        except Exception as e:
            print(f"  ERROR: Could not verify against '{target_env}' database: {e}")
            has_errors = True

    print("=" * 80)
    return 1 if has_errors else 0


# ==============================================================================
# COMMAND: PLAN
# ==============================================================================
def generate_seed_plan(cohort: Cohort, target_env: str) -> Dict[str, Any]:
    """Computes a deterministic, non-destructive plan for a proposed seed operation."""
    if cohort.id in PROTECTED_COHORT_IDS:
        raise ValueError(
            f"SAFETY VIOLATION: Cohort '{cohort.id}' is protected/immutable and CANNOT be planned or seeded!"
        )

    if cohort.status != CohortStatus.ACTIVE:
        raise ValueError(
            f"LIFECYCLE ERROR: Cohort '{cohort.id}' has status '{cohort.status.value}'. Only 'active' cohorts can be seeded."
        )

    if target_env not in cohort.environment:
        raise ValueError(
            f"ENVIRONMENT MISMATCH: Cohort '{cohort.id}' is configured for {cohort.environment}, not '{target_env}'."
        )

    if not cohort.source.endswith(".json"):
        raise ValueError(
            f"UNSUPPORTED COHORT SOURCE: Cohort '{cohort.id}' has source '{cohort.source}' which is not a JSON seed specification."
        )

    conn = get_verified_connection(target_env)
    sources = load_cohort_source(cohort, base_dir=PROJECT_ROOT)

    emails = [r["email"] for r in sources]
    expected_ids = {r["email"]: r.get("id") for r in sources}

    with conn.cursor() as cur:
        cur.execute("SELECT id::text, email FROM auth.users WHERE email = ANY(%s);", (emails,))
        found_users = {row["email"]: row["id"] for row in cur.fetchall()}

    conn.close()

    records_present = []
    records_to_create = []
    conflicts = []

    for rec in sources:
        email = rec["email"]
        expected_id = rec.get("id")
        if email in found_users:
            actual_id = found_users[email]
            if expected_id and str(expected_id) != str(actual_id):
                conflicts.append({
                    "email": email,
                    "expected_id": expected_id,
                    "actual_db_id": actual_id,
                    "conflict_type": "id_mismatch",
                    "detail": "Email already exists in database under a different UUID.",
                })
            else:
                records_present.append({"email": email, "id": actual_id, "name": rec.get("display_name")})
        else:
            records_to_create.append({
                "email": email,
                "id": expected_id,
                "first_name": rec.get("first_name"),
                "last_name": rec.get("last_name"),
                "display_name": rec.get("display_name"),
                "birth_date": rec.get("birth_date"),
                "birth_city": rec.get("birth_city"),
            })

    plan = {
        "cohort_id": cohort.id,
        "cohort_version": cohort.version,
        "target_environment": target_env,
        "total_source_records": len(sources),
        "records_already_present_count": len(records_present),
        "records_already_present": records_present,
        "records_to_create_count": len(records_to_create),
        "records_to_create": records_to_create,
        "conflicts_count": len(conflicts),
        "conflicts": conflicts,
        "dependencies": cohort.dependencies,
        "is_executable": len(conflicts) == 0,
    }

    # Deterministic plan fingerprint (TOCTOU guard)
    fingerprint_raw = json.dumps({
        "cohort_id": plan["cohort_id"],
        "cohort_version": plan["cohort_version"],
        "target_environment": plan["target_environment"],
        "total_source_records": plan["total_source_records"],
        "records_already_present_count": plan["records_already_present_count"],
        "records_to_create_count": plan["records_to_create_count"],
        "to_create_emails": sorted(r["email"] for r in plan["records_to_create"]),
    }, sort_keys=True).encode("utf-8")
    plan["plan_fingerprint"] = hashlib.sha256(fingerprint_raw).hexdigest()[:16]

    return plan


def cmd_plan(args: argparse.Namespace) -> int:
    """CLI handler for plan command."""
    if not args.cohort:
        print("ERROR: --cohort is required for plan command.")
        return 1

    target_env = args.env or "test"
    try:
        cohort = get_cohort(args.cohort)
        plan = generate_seed_plan(cohort, target_env)
    except Exception as e:
        print(f"PLAN FAILED: {e}")
        return 1

    if args.json:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return 0

    print("=" * 80)
    print(f"JESTER PROVISIONING PLAN: Cohort '{plan['cohort_id']}' -> [{target_env.upper()}]")
    print("=" * 80)
    print(f"Plan Fingerprint:    {plan['plan_fingerprint']}")
    print(f"Cohort Version:      {plan['cohort_version']}")
    print(f"Total Source Specs:  {plan['total_source_records']}")
    print(f"Records In DB:       {plan['records_already_present_count']} (Will be preserved)")
    print(f"Records To Create:   {plan['records_to_create_count']} (Creation-only)")
    print(f"Conflicts Detected:  {plan['conflicts_count']}")
    print("-" * 80)

    if plan["conflicts_count"] > 0:
        print("CRITICAL CONFLICTS (Provisioning BLOCKED):")
        for conf in plan["conflicts"]:
            print(f"  - {conf['email']}: {conf['conflict_type']} -> {conf['detail']}")
        print("=" * 80)
        return 1

    if plan["records_to_create_count"] == 0:
        print("[IDEMPOTENT] All records in cohort are already fully provisioned. No actions needed.")
    else:
        print("Records scheduled for creation:")
        for r in plan["records_to_create"][:10]:
            print(f"  + {r['email']:<24} ({r['display_name']}) | Birth: {r['birth_date']}")
        if len(plan["records_to_create"]) > 10:
            print(f"  ... and {len(plan['records_to_create']) - 10} more.")

    print("=" * 80)
    print("Plan is valid and non-destructive.")
    print(f"To execute safely: seed {plan['cohort_id']} --env {target_env} --apply-plan --fingerprint {plan['plan_fingerprint']}")
    return 0


# ==============================================================================
# COMMAND: SEED
# ==============================================================================
def execute_seed_provisioning(plan: Dict[str, Any], cohort: Cohort, target_env: str) -> Dict[str, Any]:
    """
    Executes safe, creation-only provisioning strictly applying a validated plan.
    Never overwrites, never deletes, never resets passwords or wallets.
    """
    if not plan["is_executable"]:
        raise RuntimeError("Refusing to seed: Plan has unresolved conflicts!")

    if plan["records_to_create_count"] == 0:
        return {"status": "idempotent_no_op", "created_count": 0, "preserved_count": plan["records_already_present_count"]}

    conn = get_verified_connection(target_env)
    sources = load_cohort_source(cohort, base_dir=PROJECT_ROOT)
    sources_to_create = [
        s for s in sources if any(r["email"] == s["email"] for r in plan["records_to_create"])
    ]

    with conn.cursor() as cur:
        # Pre-load interests map
        cur.execute("SELECT id, slug FROM public.interests;")
        interest_slug_to_id = {row["slug"]: row["id"] for row in cur.fetchall()}
        # Pre-load cities map
        cur.execute("SELECT id, name, latitude, longitude, timezone FROM public.cities;")
        cities_map = {row["name"].lower(): row for row in cur.fetchall()}

    created_records = []
    failed_record = None

    default_password = os.getenv("JESTER_DEMO_PASSWORD", "LocalDemoPass2026!")

    for spec in sources_to_create:
        email = spec["email"]
        fn = spec.get("first_name", "Demo")
        ln = spec.get("last_name", "User")
        display_name = spec.get("display_name") or f"{fn} {ln[0]}."
        user_uuid = uuid.UUID(spec["id"]) if spec.get("id") else uuid.uuid4()

        b_city_name = spec.get("birth_city", "tbilisi").lower()
        c_city_name = spec.get("current_city", "tbilisi").lower()

        b_city = cities_map.get(b_city_name) or next(iter(cities_map.values()))
        c_city = cities_map.get(c_city_name) or b_city

        try:
            with conn.cursor() as cur:
                # 1. Insert into auth.users (creation-only)
                cur.execute("""
                    INSERT INTO auth.users (
                        id, email, raw_user_meta_data, role, aud, email_confirmed_at, created_at, updated_at
                    )
                    VALUES (
                        %s, %s, %s, 'authenticated', 'authenticated', now(), now(), now()
                    )
                    ON CONFLICT (id) DO NOTHING;
                """, (user_uuid, email, '{"name": "%s"}' % display_name))

                # 2. Insert public.profiles (creation-only)
                cur.execute("""
                    INSERT INTO public.profiles (
                        id, display_name, first_name, last_name, bio,
                        city, city_id, current_city_id, occupation,
                        timezone, is_discoverable, onboarding_completed, onboarding_step
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, true, 4)
                    ON CONFLICT (id) DO NOTHING;
                """, (
                    user_uuid, display_name, fn, ln, spec.get("bio", ""),
                    c_city["name"], c_city["id"], c_city["id"], spec.get("occupation", ""),
                    c_city["timezone"],
                ))

                # 3. Insert public.birth_data (creation-only)
                b_date = spec.get("birth_date", "1995-01-01")
                b_time = spec.get("birth_time", "12:00:00")
                cur.execute("""
                    INSERT INTO public.birth_data (
                        user_id, birth_date, birth_time, birth_time_precision,
                        birth_timezone, latitude, longitude, place_label, birth_city_id
                    )
                    VALUES (%s, %s, %s, 'exact', %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING;
                """, (
                    user_uuid, b_date, b_time,
                    b_city["timezone"], b_city["latitude"], b_city["longitude"],
                    f"{b_city['name']}, Georgia", b_city["id"],
                ))

                # 4. Insert user interests
                for slug in spec.get("interest_slugs", []):
                    if slug in interest_slug_to_id:
                        cur.execute("""
                            INSERT INTO public.user_interests (user_id, interest_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING;
                        """, (user_uuid, interest_slug_to_id[slug]))

            # 5. Swiss Ephemeris calculation using canonical engine
            recalculate_user_astrology(user_uuid, conn)

            # 6. Initialize Stars Wallet using canonical wallet service
            get_or_create_wallet(user_uuid, conn)

            created_records.append({"email": email, "id": str(user_uuid)})

        except Exception as e:
            failed_record = {"email": email, "error": str(e)}
            # Stop immediately without deleting created users as rollback
            break

    conn.close()

    return {
        "status": "success" if not failed_record else "partial_failure",
        "created_count": len(created_records),
        "created_records": created_records,
        "failed_record": failed_record,
    }


def cmd_seed(args: argparse.Namespace) -> int:
    """CLI handler for seed command."""
    if not args.cohort:
        print("ERROR: --cohort is required for seed command.")
        return 1

    target_env = args.env or "test"

    try:
        cohort = get_cohort(args.cohort)
        plan = generate_seed_plan(cohort, target_env)
    except Exception as e:
        print(f"PROVISIONING REJECTED: {e}")
        return 1

    if not plan["is_executable"]:
        print("ERROR: Cannot execute seed. Plan contains conflicts:")
        for conf in plan["conflicts"]:
            print(f"  - {conf['email']}: {conf['detail']}")
        return 1

    if getattr(args, "fingerprint", None):
        if plan["plan_fingerprint"] != args.fingerprint:
            print("=" * 80)
            print("CRITICAL TOCTOU SAFETY VIOLATION: Execution aborted!")
            print("Database or cohort state changed between review and application.")
            print(f"Expected plan fingerprint: {args.fingerprint}")
            print(f"Current computed fingerprint: {plan['plan_fingerprint']}")
            print("=" * 80)
            return 1

    if plan["records_to_create_count"] == 0:
        print("=" * 80)
        print(f"[IDEMPOTENT] Cohort '{cohort.id}' is already 100% provisioned in '{target_env}'.")
        print("Zero modifications executed. Safe idempotency invariant preserved.")
        print("=" * 80)
        return 0

    if not args.apply_plan:
        print("=" * 80)
        print(f"SAFETY CHECK: {plan['records_to_create_count']} records scheduled for creation in [{target_env.upper()}].")
        print(f"Plan Fingerprint: {plan['plan_fingerprint']}")
        print(f"To apply this plan and execute safe provisioning, re-run with:")
        print(f"  seed {cohort.id} --env {target_env} --apply-plan --fingerprint {plan['plan_fingerprint']}")
        print("=" * 80)
        return 0

    print("=" * 80)
    print(f"EXECUTING SAFE PROVISIONING: Cohort '{cohort.id}' -> [{target_env.upper()}]")
    print(f"Plan Fingerprint: {plan['plan_fingerprint']}")
    print("=" * 80)
    result = execute_seed_provisioning(plan, cohort, target_env)

    if result["status"] == "success":
        print(f"SUCCESS: Provisioned {result['created_count']} new accounts cleanly.")
        print(f"All Swiss Ephemeris natal charts and Stars wallets successfully initialized.")
        print("=" * 80)
        return 0
    else:
        print(f"PARTIAL PROVISIONING FAILURE: Successfully created {result['created_count']} accounts.")
        print(f"Failed at: {result['failed_record']['email']} -> Error: {result['failed_record']['error']}")
        print("Per Founder policy, existing created accounts are PRESERVED and not deleted.")
        print("Fix the underlying error and resume.")
        print("=" * 80)
        return 1


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================
def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m backend.app.tools.data_manager",
        description="JESTER Canonical Data Management CLI: Declarative Cohort Registry & Provisioning",
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available subcommands")

    # list
    p_list = subparsers.add_parser("list", help="List registered cohorts and categories (Read-only)")
    p_list.add_argument("--category", help="Filter by cohort category")
    p_list.add_argument("--status", help="Filter by cohort lifecycle status (active, disabled, retired)")
    p_list.add_argument("--env", help="Filter by target environment (development, test)")
    p_list.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    p_list.add_argument("--json", action="store_true", help="Output in JSON format")

    # status
    p_status = subparsers.add_parser("status", help="Report catalog status and actual database state (Read-only)")
    p_status.add_argument("--env", choices=["development", "test"], default="development", help="Target database environment")
    p_status.add_argument("--cohort", help="Filter by specific cohort ID")
    p_status.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    p_status.add_argument("--json", action="store_true", help="Output in JSON format")

    # verify
    p_verify = subparsers.add_parser("verify", help="Validate catalog metadata and database integrity (Read-only)")
    p_verify.add_argument("--cohort", help="Specific cohort ID to verify")
    p_verify.add_argument("--env", choices=["development", "test"], help="Target database environment for DB verification")
    p_verify.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    p_verify.add_argument("--json", action="store_true", help="Output in JSON format")

    # plan
    p_plan = subparsers.add_parser("plan", help="Generate deterministic preview of a seed operation (Read-only)")
    p_plan.add_argument("cohort", help="Cohort ID to plan")
    p_plan.add_argument("--env", choices=["development", "test"], required=True, help="Target environment")
    p_plan.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    p_plan.add_argument("--json", action="store_true", help="Output in JSON format")

    # seed
    p_seed = subparsers.add_parser("seed", help="Execute safe, creation-only provisioning")
    p_seed.add_argument("cohort", help="Cohort ID to seed")
    p_seed.add_argument("--env", choices=["development", "test"], required=True, help="Target environment")
    p_seed.add_argument("--apply-plan", action="store_true", help="Confirm and apply the reviewed plan")
    p_seed.add_argument("--fingerprint", help="Require execution to match a previously reviewed plan fingerprint (TOCTOU guard)")

    return parser


def main() -> int:
    parser = build_cli_parser()
    args = parser.parse_args()

    if getattr(args, "format", None) == "json":
        args.json = True

    if args.command == "list":
        return cmd_list(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "verify":
        return cmd_verify(args)
    elif args.command == "plan":
        return cmd_plan(args)
    elif args.command == "seed":
        return cmd_seed(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
