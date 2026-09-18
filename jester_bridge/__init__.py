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
    BaseHandoff,
    ArchitectHandoff,
    ExecutorHandoff,
    ReviewerHandoff,
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
    task_expects_code_changes,
)
from .preflight import PreflightValidator, PreflightReport
from .workflow import (
    ControlledWorkflowRunner,
    WorkflowOutcome,
    extract_safe_target_paths,
)
from .context import (
    ContextEngine,
    ContextBundle,
    FileContext,
    ContextPackage,
    ContextSnapshot,
    ContextPriority,
    SourceType,
    ContextItemProvenance,
)
from .git_controller import (
    GitController,
    CommitAuthorization,
    PushAuthorization,
    GitOperationResult,
    GitStatusResult,
    GitControllerError,
    GitSecurityError,
    GitAuthorizationError,
    GitDiffMismatchError,
)
from .execution_history import (
    ExecutionRecord,
    ExecutionEvent,
    ExecutionHistoryStore,
    ExecutionHistoryError,
)
from .server import create_bridge_app
from .runtimes import (
    RuntimeType,
    RuntimeStatus,
    AuthType,
    AuthReference,
    AccountIdentity,
    RuntimeReadiness,
    RuntimeEntry,
    FallbackEvent,
    RoutingDecision,
    RuntimeRegistry,
    RuntimeRouter,
    create_antigravity_runtime,
)
from .adapters import CLIRuntimeAdapter, LocalRuntimeAdapter

__all__ = [
    "create_bridge_app",
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
    "task_expects_code_changes",
    "PreflightValidator",
    "PreflightReport",
    "ControlledWorkflowRunner",
    "WorkflowOutcome",
    "extract_safe_target_paths",
    "ContextEngine",
    "ContextBundle",
    "FileContext",
    "ContextPackage",
    "ContextSnapshot",
    "ContextPriority",
    "SourceType",
    "ContextItemProvenance",
    "BaseHandoff",
    "ArchitectHandoff",
    "ExecutorHandoff",
    "ReviewerHandoff",
    "GitController",
    "CommitAuthorization",
    "PushAuthorization",
    "GitOperationResult",
    "GitStatusResult",
    "GitControllerError",
    "GitSecurityError",
    "GitAuthorizationError",
    "GitDiffMismatchError",
    "ExecutionRecord",
    "ExecutionEvent",
    "ExecutionHistoryStore",
    "ExecutionHistoryError",
    "RuntimeType",
    "RuntimeStatus",
    "AuthType",
    "AuthReference",
    "AccountIdentity",
    "RuntimeReadiness",
    "RuntimeEntry",
    "FallbackEvent",
    "RoutingDecision",
    "RuntimeRegistry",
    "RuntimeRouter",
    "create_antigravity_runtime",
    "CLIRuntimeAdapter",
    "LocalRuntimeAdapter",
]
