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
from .runtimes import (
    AccountIdentity,
    AuthReference,
    AuthType,
    RuntimeEntry,
    RuntimeRegistry,
    RuntimeRouter,
    RuntimeType,
)


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
    Provider-Agnostic, Runtime-Neutral Bridge Core.

    Operates strictly against abstractions:
    ROLE -> AGENT -> PROVIDER -> RUNTIME -> ACCOUNT -> MODEL.
    Zero vendor-specific imports or SDK assumptions.
    """

    def __init__(
        self,
        config: BridgeConfig,
        providers: Optional[Dict[str, AgentProvider]] = None,
        runtime_registry: Optional[RuntimeRegistry] = None,
        runtime_router: Optional[RuntimeRouter] = None,
    ):
        self.config = config
        self._providers: Dict[str, AgentProvider] = {}
        self._runtime_registry = runtime_registry or RuntimeRegistry()
        self._runtime_router = runtime_router or RuntimeRouter(self._runtime_registry)

        if providers:
            for pid, prov in providers.items():
                self.register_provider(prov)

    @property
    def providers(self) -> Dict[str, AgentProvider]:
        """Returns a copy of the registered providers dictionary."""
        return dict(self._providers)

    @property
    def runtime_registry(self) -> RuntimeRegistry:
        """Returns the active RuntimeRegistry."""
        return self._runtime_registry

    @property
    def runtime_router(self) -> RuntimeRouter:
        """Returns the active RuntimeRouter."""
        return self._runtime_router

    def register_runtime(self, entry: RuntimeEntry) -> None:
        """Registers a runtime entry into the registry."""
        self._runtime_registry.register_runtime(entry)
        if entry.provider_adapter and entry.provider_id not in self._providers:
            self._providers[entry.provider_id] = entry.provider_adapter

    def register_provider(self, provider: AgentProvider) -> None:
        """Registers an active provider adapter and creates a default runtime entry."""
        self._providers[provider.provider_id] = provider
        # Ensure provider is discoverable in runtime registry if not already registered
        default_rid = f"{provider.provider_id}-default"
        if not self._runtime_registry.get_runtime(default_rid):
            self._runtime_registry.register_runtime(
                RuntimeEntry(
                    runtime_id=default_rid,
                    provider_id=provider.provider_id,
                    runtime_type=RuntimeType.API,
                    account=AccountIdentity(
                        account_id="default",
                        provider=provider.provider_id,
                        auth_ref=AuthReference(auth_type=AuthType.API_KEY),
                    ),
                    model=getattr(provider, "default_model", "default"),
                    capabilities=provider.get_supported_capabilities(),
                    priority=100,
                    provider_adapter=provider,
                )
            )


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
        self,
        task: Task,
        payload: Optional[Dict[str, Any]] = None,
        target_account: Optional[str] = None,
        target_runtime_type: Optional[RuntimeType] = None,
        target_runtime_id: Optional[str] = None,
    ) -> tuple[InvocationRequest, AgentProvider]:
        """
        Resolves role, agent, runtime, account, validates capabilities, and returns
        a normalized InvocationRequest ready for dispatch.
        """
        role = self.resolve_role(task)
        agent = self.resolve_agent(task)

        if payload:
            for source_dict in [payload, payload.get("context"), payload.get("extra_context")]:
                if isinstance(source_dict, dict):
                    if target_runtime_id is None:
                        target_runtime_id = source_dict.get("target_runtime_id")
                    if target_account is None:
                        target_account = source_dict.get("target_account")
                    if target_runtime_type is None:
                        target_runtime_type = source_dict.get("target_runtime_type")

        # 1. Deterministic Runtime Routing
        routing = self.runtime_router.route(
            task=task,
            target_role=role,
            target_provider=agent.provider,
            target_account=target_account,
            target_runtime_type=target_runtime_type,
            target_runtime_id=target_runtime_id,
        )

        if routing.status == "SUCCESS" and routing.selected_runtime:
            runtime = routing.selected_runtime
            provider = runtime.provider_adapter or self.resolve_provider(agent)
            runtime_id = runtime.runtime_id
            runtime_type = runtime.runtime_type.value
            account_id = runtime.account.account_id
            routing_reason = routing.reason
            if runtime.runtime_type == RuntimeType.CLI and runtime.model and (not agent.model or agent.model in ("default", "gemini-2.5-pro", "gemini-1.5-pro")):
                model_name = runtime.model
            else:
                model_name = (
                    agent.model
                    if (agent.model and agent.model != "default")
                    else (runtime.model or agent.model or "default")
                )
        else:
            # Fallback if no matching runtimes were found in registry or direct provider
            provider = self.resolve_provider(agent)
            runtime_id = None
            runtime_type = None
            account_id = None
            routing_reason = routing.reason or "Direct provider fallback"
            model_name = agent.model

        # Enforce capability requirements on agent and provider
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
            provider=provider.provider_id,
            model=model_name,
            runtime_id=runtime_id,
            runtime_type=runtime_type,
            account_id=account_id,
            required_capabilities=task.required_capabilities,
            payload=context_payload,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return request, provider

    def dispatch(
        self,
        task: Union[str, Path, Dict[str, Any], Task],
        payload: Optional[Dict[str, Any]] = None,
        target_account: Optional[str] = None,
        target_runtime_type: Optional[RuntimeType] = None,
        target_runtime_id: Optional[str] = None,
    ) -> InvocationResult:
        """
        Loads the task, validates the pipeline, and invokes the routed provider/runtime.
        Returns a normalized InvocationResult with runtime and account metadata.
        """
        loaded_task = self.load_task(task)
        request, provider = self.prepare_invocation(
            loaded_task,
            payload=payload,
            target_account=target_account,
            target_runtime_type=target_runtime_type,
            target_runtime_id=target_runtime_id,
        )
        result = provider.invoke(request)

        # Attach runtime metadata if not already populated
        if not result.runtime_id and request.runtime_id:
            result.runtime_id = request.runtime_id
        if not result.runtime_type and request.runtime_type:
            result.runtime_type = request.runtime_type
        if not result.account_id and request.account_id:
            result.account_id = request.account_id

        return result
