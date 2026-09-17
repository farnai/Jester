"""
Canonical Roles for the JESTER Provider-Agnostic AI Bridge.

Roles define the operational responsibility within the development lifecycle,
independent of any specific agent, provider, or model.
"""
from enum import Enum
from typing import Set


class Role(str, Enum):
    """Canonical operational roles in JESTER task lifecycle."""
    ARCHITECT = "architect"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    AUDITOR = "auditor"


CANONICAL_ROLES: Set[str] = {role.value for role in Role}


def get_canonical_roles() -> Set[str]:
    """Returns the set of valid canonical role identifiers."""
    return set(CANONICAL_ROLES)


def is_valid_role(role: str) -> bool:
    """Checks whether a role string is a valid canonical role."""
    return role in CANONICAL_ROLES


def get_default_capabilities_for_role(role: str) -> Set[str]:
    """
    Returns the baseline capabilities required by a specific role.
    """
    if role == Role.ARCHITECT:
        return {"planning", "reasoning", "repository_read"}
    elif role == Role.EXECUTOR:
        return {"repository_read", "repository_write", "command_execution", "testing"}
    elif role == Role.REVIEWER:
        return {"reasoning", "repository_read", "testing", "review"}
    elif role == Role.AUDITOR:
        return {"reasoning", "repository_read", "review"}
    return set()
