"""
backend.app.data_catalog.models
================================
Pydantic models and Enums defining JESTER's Declarative Data Catalog schema.
"""

from enum import Enum
from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field


class CohortCategory(str, Enum):
    PERSISTENT_DEMO = "persistent_demo"
    PROTECTED_DEV = "protected_dev"
    AUTH_QA = "auth_qa"
    ONBOARDING_QA = "onboarding_qa"
    DISCOVERY_QA = "discovery_qa"
    WALLET_QA = "wallet_qa"
    PRIVACY_RLS_QA = "privacy_rls_qa"
    HISTORICAL_UNMANAGED = "historical_unmanaged"


class CohortStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    RETIRED = "retired"


class PersistencePolicy(str, Enum):
    PERMANENT = "permanent"
    EPHEMERAL_TEST = "ephemeral_test"
    PROTECTED_HISTORICAL = "protected_historical"


class Cohort(BaseModel):
    id: str
    category: CohortCategory
    version: str
    description: str
    environment: List[str]
    origin: str
    persistence_policy: PersistencePolicy
    status: CohortStatus
    source: str
    expected_count: int = Field(ge=0)
    dependencies: List[str] = Field(default_factory=list)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)


class CatalogSchema(BaseModel):
    catalog_version: str
    updated_at: Optional[str] = None
    description: Optional[str] = None
    supported_environments: List[str]
    supported_categories: List[str]
    supported_statuses: List[str]
    cohorts: List[Cohort]


class ValidationIssue(BaseModel):
    cohort_id: Optional[str] = None
    level: str = "error"  # "error", "warning"
    rule: str
    message: str


class ValidationReport(BaseModel):
    valid: bool
    checked_cohorts_count: int
    issues: List[ValidationIssue] = Field(default_factory=list)

