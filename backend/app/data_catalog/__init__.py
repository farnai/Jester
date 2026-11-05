"""
backend.app.data_catalog
========================
Canonical Declarative Data Catalog & Cohort Registry for JESTER.
"""

from backend.app.data_catalog.models import (
    CohortCategory,
    CohortStatus,
    PersistencePolicy,
    Cohort,
    CatalogSchema,
    ValidationReport,
    ValidationIssue,
)
from backend.app.data_catalog.loader import (
    load_catalog,
    get_cohort,
    list_cohorts,
    load_cohort_source,
)
from backend.app.data_catalog.validator import (
    validate_catalog_metadata,
    validate_cohort_in_database,
)

__all__ = [
    "CohortCategory",
    "CohortStatus",
    "PersistencePolicy",
    "Cohort",
    "CatalogSchema",
    "ValidationReport",
    "ValidationIssue",
    "load_catalog",
    "get_cohort",
    "list_cohorts",
    "load_cohort_source",
    "validate_catalog_metadata",
    "validate_cohort_in_database",
]

