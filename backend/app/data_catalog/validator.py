"""
backend.app.data_catalog.validator
==================================
Lightweight, read-only validation layer for JESTER's Data Catalog & Cohorts.
Guaranteed 100% read-only: never performs INSERT, UPDATE, DELETE, TRUNCATE, or ALTER.
"""

from pathlib import Path
import re
from typing import Optional, List, Dict, Any
import psycopg
from psycopg.rows import dict_row

from backend.app.data_catalog.models import (
    CatalogSchema,
    Cohort,
    ValidationReport,
    ValidationIssue,
)
from backend.app.data_catalog.loader import load_cohort_source


SEMVER_REGEX = re.compile(r"^\d+\.\d+\.\d+$")


def validate_catalog_metadata(catalog: CatalogSchema, base_dir: Optional[Path] = None) -> ValidationReport:
    """
    Validates in-memory catalog structure, schemas, dependencies, and file integrity.
    Never connects to or mutates the database.
    """
    issues: List[ValidationIssue] = []
    seen_ids: set[str] = set()
    cohort_map: Dict[str, Cohort] = {}

    root = base_dir or Path(__file__).resolve().parents[3]

    for cohort in catalog.cohorts:
        # 1. Duplicate detection
        if cohort.id in seen_ids:
            issues.append(
                ValidationIssue(
                    cohort_id=cohort.id,
                    rule="unique_id",
                    message=f"Duplicate cohort identifier detected: '{cohort.id}'.",
                )
            )
        seen_ids.add(cohort.id)
        cohort_map[cohort.id] = cohort

        # 2. Version validation
        if not SEMVER_REGEX.match(cohort.version):
            issues.append(
                ValidationIssue(
                    cohort_id=cohort.id,
                    rule="semver_version",
                    message=f"Cohort '{cohort.id}' has invalid version format: '{cohort.version}'. Expected SemVer (X.Y.Z).",
                )
            )

        # 3. Environment validation
        for env in cohort.environment:
            if env not in catalog.supported_environments:
                issues.append(
                    ValidationIssue(
                        cohort_id=cohort.id,
                        rule="supported_environment",
                        message=f"Cohort '{cohort.id}' targets unsupported environment '{env}'. Supported: {catalog.supported_environments}",
                    )
                )

        # 4. Category validation
        if cohort.category.value not in catalog.supported_categories:
            issues.append(
                ValidationIssue(
                    cohort_id=cohort.id,
                    rule="supported_category",
                    message=f"Cohort '{cohort.id}' has invalid category '{cohort.category.value}'.",
                )
            )

        # 5. Source definition check
        if cohort.source.endswith(".json"):
            source_file = root / cohort.source
            if not source_file.exists():
                issues.append(
                    ValidationIssue(
                        cohort_id=cohort.id,
                        rule="source_exists",
                        message=f"Cohort '{cohort.id}' source JSON file does not exist: {cohort.source}",
                    )
                )
            else:
                # Check expected count vs source count
                try:
                    records = load_cohort_source(cohort, base_dir=root)
                    if len(records) != cohort.expected_count:
                        issues.append(
                            ValidationIssue(
                                cohort_id=cohort.id,
                                rule="source_count_match",
                                message=(
                                    f"Cohort '{cohort.id}' source defines {len(records)} records, "
                                    f"but expected_count is {cohort.expected_count}."
                                ),
                            )
                        )
                except Exception as e:
                    issues.append(
                        ValidationIssue(
                            cohort_id=cohort.id,
                            rule="source_parse",
                            message=f"Could not load source file for cohort '{cohort.id}': {e}",
                        )
                    )

    # 6. Dependency validation
    for cohort in catalog.cohorts:
        for dep in cohort.dependencies:
            if dep not in cohort_map:
                issues.append(
                    ValidationIssue(
                        cohort_id=cohort.id,
                        rule="dependency_exists",
                        message=f"Cohort '{cohort.id}' specifies missing dependency '{dep}'.",
                    )
                )
            elif dep == cohort.id:
                issues.append(
                    ValidationIssue(
                        cohort_id=cohort.id,
                        rule="no_self_dependency",
                        message=f"Cohort '{cohort.id}' cannot depend on itself.",
                    )
                )

    return ValidationReport(
        valid=len([i for i in issues if i.level == "error"]) == 0,
        checked_cohorts_count=len(catalog.cohorts),
        issues=issues,
    )


def validate_cohort_in_database(
    cohort: Cohort,
    conn: psycopg.Connection,
    base_dir: Optional[Path] = None,
) -> ValidationReport:
    """
    Performs READ-ONLY verification of a cohort against an active database connection.
    Guaranteed zero mutations: only runs SELECT queries.
    """
    issues: List[ValidationIssue] = []
    root = base_dir or Path(__file__).resolve().parents[3]

    # Only validate database state if cohort source is a JSON data list
    if not cohort.source.endswith(".json"):
        return ValidationReport(valid=True, checked_cohorts_count=1, issues=[])

    try:
        source_records = load_cohort_source(cohort, base_dir=root)
    except Exception as e:
        return ValidationReport(
            valid=False,
            checked_cohorts_count=1,
            issues=[
                ValidationIssue(
                    cohort_id=cohort.id,
                    rule="source_readable",
                    message=f"Cannot load cohort source for DB validation: {e}",
                )
            ],
        )

    emails = [r["email"] for r in source_records if "email" in r]
    expected_ids = {r["id"]: r for r in source_records if "id" in r and r["id"]}

    with conn.cursor(row_factory=dict_row) as cur:
        # 1. Check matching auth.users
        cur.execute(
            "SELECT id::text, email FROM auth.users WHERE email = ANY(%s);",
            (emails,),
        )
        found_users = {row["email"]: row["id"] for row in cur.fetchall()}

        if len(found_users) != len(emails):
            missing_emails = set(emails) - set(found_users.keys())
            issues.append(
                ValidationIssue(
                    cohort_id=cohort.id,
                    rule="database_presence",
                    message=(
                        f"Database missing {len(missing_emails)}/{len(emails)} users for cohort '{cohort.id}'. "
                        f"Missing: {sorted(list(missing_emails))[:5]}"
                    ),
                )
            )

        # 2. Check stable ID consistency if IDs are defined in source
        for email, db_id in found_users.items():
            expected_rec = next(
                (r for r in source_records if r.get("email") == email and r.get("id")),
                None,
            )
            if expected_rec and str(expected_rec["id"]) != str(db_id):
                issues.append(
                    ValidationIssue(
                        cohort_id=cohort.id,
                        rule="stable_id_match",
                        message=f"User '{email}' has DB id {db_id}, expected source id {expected_rec['id']}.",
                    )
                )

        user_ids = list(found_users.values())
        if not user_ids:
            return ValidationReport(
                valid=len(issues) == 0,
                checked_cohorts_count=1,
                issues=issues,
            )

        # 3. Check profiles
        rules = cohort.validation_rules
        if rules.get("require_profiles"):
            cur.execute(
                "SELECT id::text, first_name, last_name, onboarding_completed, is_discoverable FROM public.profiles WHERE id = ANY(%s::uuid[]);",
                (user_ids,),
            )
            profiles = {row["id"]: row for row in cur.fetchall()}
            if len(profiles) != len(user_ids):
                missing_p = set(user_ids) - set(profiles.keys())
                issues.append(
                    ValidationIssue(
                        cohort_id=cohort.id,
                        rule="profiles_present",
                        message=f"Missing {len(missing_p)} profiles in public.profiles for cohort '{cohort.id}'.",
                    )
                )

            if rules.get("onboarding_completed_required"):
                incomplete = [
                    uid for uid, p in profiles.items() if not p.get("onboarding_completed")
                ]
                if incomplete:
                    issues.append(
                        ValidationIssue(
                            cohort_id=cohort.id,
                            rule="onboarding_completed",
                            message=f"{len(incomplete)} users in cohort '{cohort.id}' have not completed onboarding.",
                        )
                    )

        # 4. Check birth data & 18+ requirement
        if rules.get("require_birth_data"):
            cur.execute(
                "SELECT user_id::text, birth_date, extract(year from age(current_date, birth_date)) as age FROM public.birth_data WHERE user_id = ANY(%s::uuid[]);",
                (user_ids,),
            )
            births = {row["user_id"]: row for row in cur.fetchall()}
            if len(births) != len(user_ids):
                missing_b = set(user_ids) - set(births.keys())
                issues.append(
                    ValidationIssue(
                        cohort_id=cohort.id,
                        rule="birth_data_present",
                        message=f"Missing {len(missing_b)} birth_data rows for cohort '{cohort.id}'.",
                    )
                )

            if rules.get("require_adult_age"):
                minors = [
                    uid for uid, b in births.items() if (b.get("age") or 0) < 18
                ]
                if minors:
                    issues.append(
                        ValidationIssue(
                            cohort_id=cohort.id,
                            rule="adult_age_18_plus",
                            message=f"{len(minors)} users in cohort '{cohort.id}' violate 18+ requirement (underage).",
                        )
                    )

        # 5. Check astrology calculation
        if rules.get("require_astrology_calculated"):
            cur.execute(
                "SELECT user_id::text FROM public.astro_safe_profile WHERE user_id = ANY(%s::uuid[]);",
                (user_ids,),
            )
            safe_ids = {row["user_id"] for row in cur.fetchall()}
            if len(safe_ids) != len(user_ids):
                issues.append(
                    ValidationIssue(
                        cohort_id=cohort.id,
                        rule="astro_safe_profile_present",
                        message=f"Missing {len(user_ids) - len(safe_ids)} astro_safe_profile records for cohort '{cohort.id}'.",
                    )
                )

    return ValidationReport(
        valid=len([i for i in issues if i.level == "error"]) == 0,
        checked_cohorts_count=1,
        issues=issues,
    )
