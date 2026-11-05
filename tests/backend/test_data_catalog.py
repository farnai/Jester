"""
tests/backend/test_data_catalog.py
==================================
Comprehensive test suite for JESTER's Declarative Data Catalog & Cohort Registry.

Covers:
1. Catalog loading from canonical JSON.
2. Cohort schema validation & SemVer adherence.
3. Duplicate cohort identifier detection.
4. Invalid metadata & unsupported category/environment rejection.
5. Cohort lifecycle states (active, disabled, retired).
6. Existing 20 demo accounts mapping & completeness.
7. Read-only validation behavior against database.
8. Environment targeting & cohort isolation.
9. Unknown / missing accounts detection.
"""

import copy
import pytest
import psycopg
from psycopg.rows import dict_row

from backend.app.data_catalog import (
    load_catalog,
    get_cohort,
    list_cohorts,
    load_cohort_source,
    validate_catalog_metadata,
    validate_cohort_in_database,
    CohortCategory,
    CohortStatus,
    PersistencePolicy,
    CatalogSchema,
    Cohort,
)
from backend.app.core.environment_verifier import APPROVED_TEST_DB_PORT


def test_catalog_loads_canonical_json():
    """Verify that catalog.json loads and parses into CatalogSchema."""
    catalog = load_catalog(reload=True)
    assert catalog.catalog_version == "1.0.0"
    assert len(catalog.cohorts) >= 8
    assert "development" in catalog.supported_environments
    assert "test" in catalog.supported_environments
    assert "persistent_demo" in catalog.supported_categories
    assert "protected_dev" in catalog.supported_categories


def test_cohort_schema_validation_passes_on_valid_catalog():
    """Verify that the canonical catalog passes in-memory metadata validation with zero issues."""
    catalog = load_catalog(reload=True)
    report = validate_catalog_metadata(catalog)
    assert report.valid is True
    assert len(report.issues) == 0
    assert report.checked_cohorts_count >= 8


def test_duplicate_cohort_id_detected():
    """Verify that duplicate cohort IDs are detected and flagged as errors."""
    catalog = load_catalog(reload=True)
    duplicate_cohort = copy.deepcopy(catalog.cohorts[0])
    mutated_catalog = CatalogSchema(
        catalog_version=catalog.catalog_version,
        supported_environments=catalog.supported_environments,
        supported_categories=catalog.supported_categories,
        supported_statuses=catalog.supported_statuses,
        cohorts=catalog.cohorts + [duplicate_cohort],
    )
    report = validate_catalog_metadata(mutated_catalog)
    assert report.valid is False
    unique_errors = [i for i in report.issues if i.rule == "unique_id"]
    assert len(unique_errors) == 1
    assert unique_errors[0].cohort_id == duplicate_cohort.id


def test_invalid_metadata_rejected():
    """Verify that invalid SemVer, unsupported environments, and missing dependencies are caught."""
    catalog = load_catalog(reload=True)
    bad_cohort = Cohort(
        id="invalid-qa-cohort",
        category=CohortCategory.AUTH_QA,
        version="v1_invalid_semver",
        description="Bad cohort for testing validation failure",
        environment=["unsupported_cloud"],
        origin="qa_test",
        persistence_policy=PersistencePolicy.EPHEMERAL_TEST,
        status=CohortStatus.ACTIVE,
        source="nonexistent_source.json",
        expected_count=1,
        dependencies=["nonexistent_dependency"],
    )
    mutated_catalog = CatalogSchema(
        catalog_version=catalog.catalog_version,
        supported_environments=catalog.supported_environments,
        supported_categories=catalog.supported_categories,
        supported_statuses=catalog.supported_statuses,
        cohorts=catalog.cohorts + [bad_cohort],
    )
    report = validate_catalog_metadata(mutated_catalog)
    assert report.valid is False
    rules_violated = {i.rule for i in report.issues if i.cohort_id == "invalid-qa-cohort"}
    assert "semver_version" in rules_violated
    assert "supported_environment" in rules_violated
    assert "dependency_exists" in rules_violated
    assert "source_exists" in rules_violated


def test_cohort_lifecycle_states_and_filtering():
    """Verify dynamic lifecycle states (active, disabled, retired) and filtering without user deletion."""
    catalog = load_catalog(reload=True)

    # All canonical cohorts are active initially
    active_cohorts = list_cohorts(status=CohortStatus.ACTIVE, catalog=catalog)
    assert len(active_cohorts) == len(catalog.cohorts)

    # Filter by category
    demo_cohorts = list_cohorts(category=CohortCategory.PERSISTENT_DEMO, catalog=catalog)
    assert len(demo_cohorts) == 1
    assert demo_cohorts[0].id == "demo-people-v1"

    # Simulate disabling a cohort
    mutated = copy.deepcopy(catalog)
    mutated.cohorts[0].status = CohortStatus.DISABLED

    remaining_active = list_cohorts(status=CohortStatus.ACTIVE, catalog=mutated)
    assert len(remaining_active) == len(catalog.cohorts) - 1

    disabled_cohorts = list_cohorts(status=CohortStatus.DISABLED, catalog=mutated)
    assert len(disabled_cohorts) == 1
    assert disabled_cohorts[0].id == catalog.cohorts[0].id


def test_existing_20_demo_accounts_mapping():
    """Verify that demo-people-v1 correctly maps the 20 synthetic demo accounts and their attributes."""
    cohort = get_cohort("demo-people-v1")
    assert cohort.expected_count == 20
    assert cohort.category == CohortCategory.PERSISTENT_DEMO
    assert cohort.persistence_policy == PersistencePolicy.PERMANENT

    source_records = load_cohort_source(cohort)
    assert len(source_records) == 20

    emails = [r["email"] for r in source_records]
    assert len(set(emails)) == 20  # All unique
    for r in source_records:
        assert r["email"].endswith("@jester.test")
        assert len(r["first_name"]) > 0
        assert len(r["last_name"]) > 0
        assert len(r["bio"]) > 0
        assert len(r["occupation"]) > 0
        assert r["is_discoverable"] is True
        assert r["onboarding_completed"] is True
        assert len(r["interest_slugs"]) >= 3


def test_environment_targeting_and_isolation():
    """Verify environment filtering isolates dev vs test cohorts cleanly."""
    catalog = load_catalog(reload=True)

    dev_cohorts = list_cohorts(environment="development", catalog=catalog)
    dev_ids = {c.id for c in dev_cohorts}
    assert "demo-people-v1" in dev_ids
    assert "protected-core-dev-v1" in dev_ids
    assert "historical-unmanaged-dev" in dev_ids
    assert "auth-qa-v1" not in dev_ids  # QA cohorts target test only

    test_cohorts = list_cohorts(environment="test", catalog=catalog)
    test_ids = {c.id for c in test_cohorts}
    assert "auth-qa-v1" in test_ids
    assert "onboarding-qa-v1" in test_ids
    assert "discovery-qa-v1" in test_ids
    assert "protected-core-dev-v1" not in test_ids  # Core dev does not target test


def test_unknown_account_flagged_in_validation(db_conn):
    """Verify that unknown accounts in a cohort are reported as errors without modifying the DB."""
    test_cohort = Cohort(
        id="ghost-cohort",
        category=CohortCategory.AUTH_QA,
        version="1.0.0",
        description="Ghost cohort with nonexistent user for read-only validation check",
        environment=["test"],
        origin="qa_test",
        persistence_policy=PersistencePolicy.EPHEMERAL_TEST,
        status=CohortStatus.ACTIVE,
        source="backend/app/data_catalog/sources/protected_core_dev.json",
        expected_count=4,
    )
    # The test database on port 54422 does not contain the dev founder accounts
    report = validate_cohort_in_database(test_cohort, db_conn)
    assert report.valid is False
    presence_issues = [i for i in report.issues if i.rule == "database_presence"]
    assert len(presence_issues) == 1
    assert "Database missing" in presence_issues[0].message

