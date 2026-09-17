"""
Bridge Core: The Provider-Agnostic AI Orchestration Engine.

Coordinates task loading, role resolution, agent resolution, provider resolution,
capability preflight validation, and normalized invocation dispatch.
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union
import uuid

from .agent import AgentProfile
from .capabilities import validate_capabilities
from .config import BridgeConfig
from .contracts import InvocationRequest, InvocationResult, InvocationStatus
from .protocol import Task, load_task_from_dict, load_task_from_file
from .provider import AgentProvider
from .roles import is_valid_role


class BridgeError(Exception):
    """Base exception for Bridge Core operations."""
    pass


class ConfigurationError(BridgeError):
    """Raised when an agent, role, or provider cannot be resolved from configuration."""
    pass


class CapabilityMismatchError(BridgeError):
    """Raised when an agent or provider cannot satisfy the capabilities required by a task."""
    def __init__(self, message: str, missing_capabilities: Set[str]):
        super().__init__(message)
        self.missing_capabilities = missing_capabilities


class BridgeCore:
    """
    Provider-Agnostic Bridge Core.

    Operates strictly against abstractions (Task, Role, Agent, Provider, Capability, Result).
    Zero vendor-specific imports or SDK assumptions.
    """

    def __init__(
        self,
        config: BridgeConfig,
        providers: Optional[Dict[str, AgentProvider]] = None,
    ):
        self.config = config
        self._providers: Dict[str, AgentProvider] = dict(providers or {})

    def register_provider(self, provider: AgentProvider) -> None:
        """Registers an active provider adapter."""
        self._providers[provider.provider_id] = provider

    def get_provider(self, provider_id: str) -> Optional[AgentProvider]:
        """Returns the registered provider instance for the given ID."""
        return self._providers.get(provider_id)

    def load_task(self, source: Union[str, Path, Dict[str, Any], Task]) -> Task:
        """Loads and normalizes a task from a file, dict, or Task instance."""
        if isinstance(source, Task):
            return source
        elif isinstance(source, dict):
            return load_task_from_dict(source)
        elif isinstance(source, (str, Path)):
            return load_task_from_file(source)
        raise ValueError(f"Unsupported task source: {type(source)}")

    def resolve_role(self, task: Task) -> str:
        """Resolves and validates the operational role for a task."""
        role = task.role
        if not is_valid_role(role):
            raise ConfigurationError(f"Task {task.id} specifies unknown role: '{role}'")
        return role

    def resolve_agent(self, task: Task) -> AgentProfile:
        """
        Resolves the AgentProfile for a task.
        Priority:
        1. Task's explicitly assigned_agent (or legacy agent field)
        2. Configured role binding for task.role
        """
        role = self.resolve_role(task)

        # 1. Direct assignment
        agent_id = task.assigned_agent or task.agent
        if agent_id:
            agent = self.config.get_agent(agent_id)
            if agent:
                return agent

        # 2. Role binding fallback
        agent = self.config.get_agent_for_role(role)
        if agent:
            return agent

        raise ConfigurationError(
            f"Unable to resolve an agent for task '{task.id}' (role='{role}', assigned_agent='{agent_id}')"
        )

    def resolve_provider(self, agent: AgentProfile) -> AgentProvider:
        """Resolves the AgentProvider registered for an agent's provider identifier."""
        provider = self._providers.get(agent.provider)
        if not provider:
            raise ConfigurationError(
                f"Provider '{agent.provider}' required by agent '{agent.id}' is not registered."
            )
        return provider

    def validate_task_capabilities(
        self, task: Task, agent: AgentProfile, provider: AgentProvider
    ) -> None:
        """
        Enforces that both the Agent and the Provider satisfy task.required_capabilities.
        Raises CapabilityMismatchError if required capabilities are missing.
        """
        required = task.required_capabilities

        # Validate agent capabilities
        agent_ok, agent_missing = validate_capabilities(required, agent.capabilities)
        if not agent_ok:
            raise CapabilityMismatchError(
                f"Agent '{agent.id}' lacks required capabilities for task '{task.id}': {sorted(agent_missing)}",
                missing_capabilities=agent_missing,
            )

        # Validate provider technical capabilities
        provider_caps = provider.get_supported_capabilities()
        provider_ok, provider_missing = validate_capabilities(required, provider_caps)
        if not provider_ok:
            raise CapabilityMismatchError(
                f"Provider '{provider.provider_id}' lacks technical capabilities for task '{task.id}': {sorted(provider_missing)}",
                missing_capabilities=provider_missing,
            )

    def prepare_invocation(
        self, task: Task, payload: Optional[Dict[str, Any]] = None
    ) -> tuple[InvocationRequest, AgentProvider]:
        """
        Resolves role, agent, provider, validates capabilities, and returns
        a normalized InvocationRequest ready for dispatch.
        """
        role = self.resolve_role(task)
        agent = self.resolve_agent(task)
        provider = self.resolve_provider(agent)

        # Enforce capability requirements
        self.validate_task_capabilities(task, agent, provider)

        context_payload = {
            "title": task.title,
            "goal": task.goal,
            "scope": task.scope,
            "constraints": task.constraints,
            "acceptance_criteria": task.acceptance_criteria,
            "verification": task.verification,
            "dependencies": task.dependencies,
        }
        if payload:
            context_payload.update(payload)

        request = InvocationRequest(
            request_id=f"req-{uuid.uuid4().hex[:8]}",
            task_id=task.id,
            role=role,
            agent_id=agent.id,
            provider=agent.provider,
            model=agent.model,
            required_capabilities=task.required_capabilities,
            payload=context_payload,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return request, provider

    def dispatch(
        self, task: Union[str, Path, Dict[str, Any], Task], payload: Optional[Dict[str, Any]] = None
    ) -> InvocationResult:
        """
        Loads the task, validates the pipeline, and invokes the provider.
        Returns a normalized InvocationResult.
        """
        loaded_task = self.load_task(task)
        request, provider = self.prepare_invocation(loaded_task, payload)
        return provider.invoke(request)
