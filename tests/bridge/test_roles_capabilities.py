"""
Tests for Canonical Roles and Capability Validation.
"""
import pytest

from jester_bridge.roles import (
    Role,
    get_canonical_roles,
    is_valid_role,
    get_default_capabilities_for_role,
)
from jester_bridge.capabilities import (
    Capability,
    validate_capabilities,
)


def test_canonical_roles():
    canonical = get_canonical_roles()
    assert "architect" in canonical
    assert "executor" in canonical
    assert "reviewer" in canonical
    assert "auditor" in canonical
    assert len(canonical) == 4

    assert is_valid_role("architect")
    assert is_valid_role("executor")
    assert not is_valid_role("ninja")
    assert not is_valid_role("gemini")  # Vendor name is not a role!


def test_role_default_capabilities():
    executor_caps = get_default_capabilities_for_role(Role.EXECUTOR)
    assert "repository_write" in executor_caps
    assert "command_execution" in executor_caps

    reviewer_caps = get_default_capabilities_for_role(Role.REVIEWER)
    assert "review" in reviewer_caps
    assert "repository_write" not in reviewer_caps  # Reviewer is read-only regarding code


def test_capability_validation_satisfied():
    required = {"repository_read", "testing"}
    supported = {"repository_read", "testing", "command_execution", "local_runtime"}

    satisfied, missing = validate_capabilities(required, supported)
    assert satisfied is True
    assert len(missing) == 0


def test_capability_validation_missing():
    required = {"repository_read", "command_execution", "local_runtime"}
    supported = {"repository_read"}

    satisfied, missing = validate_capabilities(required, supported)
    assert satisfied is False
    assert missing == {"command_execution", "local_runtime"}
