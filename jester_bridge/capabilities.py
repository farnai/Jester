"""
Capability system for the JESTER Provider-Agnostic AI Bridge.

Capabilities represent discrete technical and operational competencies.
Tasks declare required capabilities; agents and providers declare supported capabilities.
"""
from enum import Enum
from typing import Set, Tuple


class Capability(str, Enum):
    """Standardized capability identifiers for JESTER agents, providers, and runtimes."""
    PLANNING = "planning"
    REASONING = "reasoning"
    REPOSITORY_READ = "repository_read"
    REPOSITORY_WRITE = "repository_write"
    COMMAND_EXECUTION = "command_execution"
    TESTING = "testing"
    REVIEW = "review"
    LOCAL_RUNTIME = "local_runtime"
    CODE_GENERATION = "code_generation"
    CODE_EDITING = "code_editing"
    SHELL_EXECUTION = "shell_execution"
    LARGE_CONTEXT = "large_context"
    STRUCTURED_OUTPUT = "structured_output"
    TOOL_USE = "tool_use"
    STREAMING = "streaming"
    LOCAL_EXECUTION = "local_execution"
    REMOTE_EXECUTION = "remote_execution"


def validate_capabilities(
    required: Set[str], supported: Set[str]
) -> Tuple[bool, Set[str]]:
    """
    Validates whether supported capabilities satisfy all required capabilities.
    Enforces: required ⊆ supported.

    Returns:
        (is_satisfied: bool, missing_capabilities: Set[str])
    """
    missing = set(required) - set(supported)
    return (len(missing) == 0, missing)
