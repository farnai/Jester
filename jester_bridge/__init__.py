"""
JESTER Provider-Agnostic AI Bridge Foundation (Phase 1)
Decoupled multi-agent orchestration core for the JESTER Development Control Plane.
"""

from .roles import Role, get_canonical_roles, is_valid_role
from .capabilities import Capability, validate_capabilities
from .agent import AgentProfile
from .provider import AgentProvider
from .contracts import (
    InvocationRequest,
    InvocationResult,
    InvocationStatus,
    UsageMetrics,
)
from .protocol import Task, load_task_from_dict, load_task_from_file
from .config import BridgeConfig, load_bridge_config
from .core import BridgeCore, CapabilityMismatchError, ConfigurationError
from .openai_provider import OpenAIProvider
from .google_provider import GoogleProvider
from .orchestration import (
    BridgeOrchestrator,
    OrchestrationStage,
    ReviewVerdict,
    OrchestrationSession,
    ArchitectInput,
    ArchitectResult,
    ExecutorInput,
    ExecutorResult,
    ReviewInput,
    ReviewResult,
    InvalidTransitionError,
    MaxReworkExceededError,
)
from .runtime import (
    BoundedWorkspaceRuntime,
    RuntimeExecutionResult,
    FileChange,
    ScopeViolationError,
    is_path_in_scope,
    extract_file_changes_from_text,
)
from .preflight import PreflightValidator, PreflightReport
from .workflow import ControlledWorkflowRunner, WorkflowOutcome

__all__ = [
    "Role",
    "get_canonical_roles",
    "is_valid_role",
    "Capability",
    "validate_capabilities",
    "AgentProfile",
    "AgentProvider",
    "OpenAIProvider",
    "GoogleProvider",
    "InvocationRequest",
    "InvocationResult",
    "InvocationStatus",
    "UsageMetrics",
    "Task",
    "load_task_from_dict",
    "load_task_from_file",
    "BridgeConfig",
    "load_bridge_config",
    "BridgeCore",
    "CapabilityMismatchError",
    "ConfigurationError",
    "BridgeOrchestrator",
    "OrchestrationStage",
    "ReviewVerdict",
    "OrchestrationSession",
    "ArchitectInput",
    "ArchitectResult",
    "ExecutorInput",
    "ExecutorResult",
    "ReviewInput",
    "ReviewResult",
    "InvalidTransitionError",
    "MaxReworkExceededError",
    "BoundedWorkspaceRuntime",
    "RuntimeExecutionResult",
    "FileChange",
    "ScopeViolationError",
    "is_path_in_scope",
    "extract_file_changes_from_text",
    "PreflightValidator",
    "PreflightReport",
    "ControlledWorkflowRunner",
    "WorkflowOutcome",
]
