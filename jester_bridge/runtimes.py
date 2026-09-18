"""
Generic Multi-Runtime and Multi-Account Architecture for the JESTER AI Bridge (TASK-0013).

Provides a vendor-neutral, runtime-neutral orchestration layer:
ROLE -> AGENT -> PROVIDER -> RUNTIME -> ACCOUNT / CREDENTIAL -> MODEL

Enables:
- Dynamic account registration (e.g. Gemini Account A + Account B without orchestration code changes)
- Multiple runtime execution types (API, CLI, Local)
- Deterministic, explainable capability-aware and readiness-aware routing
- Rich runtime availability states (READY, UNAVAILABLE, AUTH_REQUIRED, RATE_LIMITED, QUOTA_EXHAUSTED, OFFLINE)
- Safe fallback chains between accounts and runtimes
- Strict credential reference isolation (zero raw secret leakage)
"""
from datetime import datetime, timezone
from enum import Enum
import os
import re
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .capabilities import validate_capabilities
from .protocol import Task
from .provider import AgentProvider


class RuntimeType(str, Enum):
    """Execution transport / runtime type."""
    API = "api"
    CLI = "cli"
    LOCAL = "local"


class RuntimeStatus(str, Enum):
    """Granular operational readiness status of a runtime."""
    READY = "READY"
    UNAVAILABLE = "UNAVAILABLE"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    RATE_LIMITED = "RATE_LIMITED"
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"
    OFFLINE = "OFFLINE"
    CAPABILITY_MISMATCH = "CAPABILITY_MISMATCH"
    ERROR = "ERROR"


class AuthType(str, Enum):
    """Mechanism used to authenticate the runtime."""
    API_KEY = "api_key"
    CLI_PROFILE = "cli_profile"
    SUBSCRIPTION = "subscription"
    LOCAL = "local"
    NONE = "none"


def _sanitize_secret_ref(text: Optional[str]) -> Optional[str]:
    """Ensures raw credentials are not accidentally passed into references."""
    if not text:
        return text
    lowered = text.lower()
    if any(pat in lowered for pat in ("sk-proj-", "sk-", "aiza", "bearer ")):
        return "[REDACTED_CREDENTIAL_REFERENCE]"
    return text


class AuthReference(BaseModel):
    """
    Non-sensitive reference to an authentication credential.
    Never stores raw API keys or session tokens; stores only configuration/env keys.
    """
    auth_type: AuthType = AuthType.NONE
    env_var: Optional[str] = None
    profile_name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("env_var", "profile_name", mode="before")
    @classmethod
    def sanitize_field(cls, v: Optional[str]) -> Optional[str]:
        return _sanitize_secret_ref(v)


class AccountIdentity(BaseModel):
    """
    Identity specification for an authenticated AI account.
    Decoupled from code: supports dynamic collections of accounts (e.g. Account A, B, C).
    """
    account_id: str
    label: Optional[str] = None
    provider: str
    auth_ref: AuthReference = Field(default_factory=AuthReference)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)


class RuntimeReadiness(BaseModel):
    """
    Status report for a runtime's operational readiness and quota state.
    """
    status: RuntimeStatus
    message: Optional[str] = None
    quota_info: Optional[Dict[str, Any]] = None
    checked_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RuntimeEntry(BaseModel):
    """
    Registered executable runtime instance.
    Binds provider, runtime type, account identity, model, and capabilities.
    """
    runtime_id: str
    provider_id: str
    runtime_type: RuntimeType
    account: AccountIdentity
    model: str
    capabilities: Set[str] = Field(default_factory=set)
    priority: int = 100
    endpoint: Optional[str] = None
    provider_adapter: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def check_readiness(self) -> RuntimeReadiness:
        """
        Evaluates the current readiness of this runtime instance.
        """
        # 1. Custom readiness method on adapter
        if self.provider_adapter and hasattr(self.provider_adapter, "check_readiness"):
            try:
                res = self.provider_adapter.check_readiness()
                if isinstance(res, RuntimeReadiness):
                    return res
            except Exception as e:
                return RuntimeReadiness(
                    status=RuntimeStatus.ERROR,
                    message=f"Runtime readiness check raised exception: {str(e)}",
                )

        # 2. Standard provider health_check
        if self.provider_adapter and hasattr(self.provider_adapter, "health_check"):
            try:
                is_healthy = self.provider_adapter.health_check()
                if is_healthy:
                    return RuntimeReadiness(status=RuntimeStatus.READY)
                else:
                    return RuntimeReadiness(
                        status=RuntimeStatus.AUTH_REQUIRED,
                        message=f"Provider adapter health check failed for runtime '{self.runtime_id}'.",
                    )
            except Exception as e:
                return RuntimeReadiness(
                    status=RuntimeStatus.ERROR,
                    message=f"Health check error: {str(e)}",
                )

        # 3. Environment-based auth check
        if self.account.auth_ref.auth_type == AuthType.API_KEY and self.account.auth_ref.env_var:
            val = os.getenv(self.account.auth_ref.env_var)
            if not val or not val.strip():
                return RuntimeReadiness(
                    status=RuntimeStatus.AUTH_REQUIRED,
                    message=f"Required environment variable '{self.account.auth_ref.env_var}' is not configured.",
                )
            return RuntimeReadiness(status=RuntimeStatus.READY)

        # 4. Local runtime check
        if self.runtime_type == RuntimeType.LOCAL:
            # If adapter not present or check passed, default to READY
            return RuntimeReadiness(status=RuntimeStatus.READY)

        # 5. CLI profile check
        if self.account.auth_ref.auth_type == AuthType.CLI_PROFILE:
            return RuntimeReadiness(status=RuntimeStatus.READY)

        return RuntimeReadiness(status=RuntimeStatus.READY)


class FallbackEvent(BaseModel):
    """Record of a runtime fallback event during routing."""
    from_runtime: str
    to_runtime: str
    reason: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RoutingDecision(BaseModel):
    """Deterministic routing outcome explaining runtime selection."""
    selected_runtime: Optional[RuntimeEntry] = None
    status: str
    reason: str
    fallback_events: List[FallbackEvent] = Field(default_factory=list)
    candidates_evaluated: List[str] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class RuntimeRegistry:
    """
    Central catalog of available AI runtimes and accounts.
    Allows dynamic registration without orchestration code modifications.
    """

    def __init__(self):
        self._runtimes: Dict[str, RuntimeEntry] = {}

    def register_runtime(self, entry: RuntimeEntry) -> None:
        """Registers a runtime entry."""
        self._runtimes[entry.runtime_id] = entry

    def get_runtime(self, runtime_id: str) -> Optional[RuntimeEntry]:
        """Retrieves a runtime by its unique ID."""
        return self._runtimes.get(runtime_id)

    def list_runtimes(self) -> List[RuntimeEntry]:
        """Returns all registered runtime entries."""
        return list(self._runtimes.values())

    def find_runtimes(
        self,
        provider_id: Optional[str] = None,
        runtime_type: Optional[RuntimeType] = None,
        account_id: Optional[str] = None,
        required_capabilities: Optional[Set[str]] = None,
        runtime_id: Optional[str] = None,
    ) -> List[RuntimeEntry]:
        """
        Queries runtimes matching filters and required capabilities.
        """
        results: List[RuntimeEntry] = []
        for r in self._runtimes.values():
            if runtime_id and r.runtime_id != runtime_id:
                continue
            if provider_id and r.provider_id != provider_id:
                continue
            if runtime_type and r.runtime_type != runtime_type:
                continue
            if account_id and r.account.account_id != account_id:
                continue
            if required_capabilities:
                ok, _ = validate_capabilities(required_capabilities, r.capabilities)
                if not ok:
                    continue
            results.append(r)

        # Sort deterministically by priority (ascending), then runtime_id
        results.sort(key=lambda x: (x.priority, x.runtime_id))
        return results


def create_antigravity_runtime(
    account_id: str = "google-ai-pro",
    account_label: str = "Google AI Pro (Antigravity CLI)",
    model: str = "gemini-3.8-flash-low",
    priority: int = 5,
    adapter: Optional[Any] = None,
    capabilities: Optional[Set[str]] = None,
) -> RuntimeEntry:
    """
    Constructs a RuntimeEntry for the Antigravity CLI runtime under Google Provider.
    """
    default_caps = {
        "planning",
        "reasoning",
        "repository_read",
        "repository_write",
        "code_generation",
        "code_editing",
        "command_execution",
        "testing",
        "review",
    }
    return RuntimeEntry(
        runtime_id="google-antigravity-cli",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=AccountIdentity(
            account_id=account_id,
            label=account_label,
            provider="google",
            auth_ref=AuthReference(
                auth_type=AuthType.SUBSCRIPTION,
                profile_name=account_id,
                metadata={"cli": "agy"},
            ),
        ),
        model=model,
        capabilities=set(capabilities or default_caps),
        priority=priority,
        provider_adapter=adapter,
        metadata={"executable": "agy", "transport": "cli"},
    )


class RuntimeRouter:
    """
    Deterministic, explainable runtime selector.
    Evaluates capabilities, priority, and real-time availability to choose a runtime
    and gracefully fall back across accounts/runtimes when quota or limits are reached.
    """

    def __init__(self, registry: RuntimeRegistry):
        self.registry = registry

    def route(
        self,
        task: Task,
        target_role: Optional[str] = None,
        target_provider: Optional[str] = None,
        target_account: Optional[str] = None,
        target_runtime_type: Optional[RuntimeType] = None,
        target_runtime_id: Optional[str] = None,
    ) -> RoutingDecision:
        """
        Selects a compatible, READY runtime for the given task and criteria.
        Evaluates candidate runtimes in priority order and records fallback events.
        """
        required_caps = set(task.required_capabilities or set())

        # 1. Gather all candidates matching provider/account/type/id filters
        candidates = self.registry.find_runtimes(
            provider_id=target_provider,
            runtime_type=target_runtime_type,
            account_id=target_account,
            runtime_id=target_runtime_id,
        )

        if not candidates:
            return RoutingDecision(
                selected_runtime=None,
                status="FAILED",
                reason=(
                    f"No registered runtimes found matching provider='{target_provider}', "
                    f"account='{target_account}', type='{target_runtime_type}', "
                    f"runtime_id='{target_runtime_id}'."
                ),
            )

        # 2. Filter by capability satisfaction
        capable_candidates: List[RuntimeEntry] = []
        for cand in candidates:
            ok, missing = validate_capabilities(required_caps, cand.capabilities)
            if ok:
                capable_candidates.append(cand)

        if not capable_candidates:
            all_missing = [
                f"{c.runtime_id} missing {sorted(list(set(required_caps) - set(c.capabilities)))}"
                for c in candidates
            ]
            return RoutingDecision(
                selected_runtime=None,
                status="FAILED",
                reason=(
                    f"No runtime can satisfy required capabilities {sorted(list(required_caps))}. "
                    f"Candidates: {'; '.join(all_missing)}."
                ),
                candidates_evaluated=[c.runtime_id for c in candidates],
            )

        # 3. Evaluate readiness and perform deterministic fallback
        fallback_events: List[FallbackEvent] = []
        evaluated: List[str] = []
        last_unready_runtime: Optional[RuntimeEntry] = None
        last_unready_reason: Optional[str] = None

        for cand in capable_candidates:
            evaluated.append(cand.runtime_id)
            readiness = cand.check_readiness()

            if readiness.status == RuntimeStatus.READY:
                if last_unready_runtime:
                    fallback_events.append(
                        FallbackEvent(
                            from_runtime=last_unready_runtime.runtime_id,
                            to_runtime=cand.runtime_id,
                            reason=last_unready_reason or "Fallback",
                        )
                    )

                # Explain selection
                if fallback_events:
                    reason = (
                        f"Selected '{cand.runtime_id}' (account='{cand.account.account_id}') after "
                        f"{len(fallback_events)} fallback(s). Required capabilities satisfied."
                    )
                else:
                    reason = (
                        f"Selected preferred runtime '{cand.runtime_id}' "
                        f"(account='{cand.account.account_id}'). Required capabilities satisfied."
                    )

                return RoutingDecision(
                    selected_runtime=cand,
                    status="SUCCESS",
                    reason=reason,
                    fallback_events=fallback_events,
                    candidates_evaluated=evaluated,
                )
            else:
                # Log unready candidate and continue fallback chain
                skip_reason = f"Status {readiness.status.value}: {readiness.message or 'Unavailable'}"
                if last_unready_runtime:
                    fallback_events.append(
                        FallbackEvent(
                            from_runtime=last_unready_runtime.runtime_id,
                            to_runtime=cand.runtime_id,
                            reason=last_unready_reason or "Fallback",
                        )
                    )
                last_unready_runtime = cand
                last_unready_reason = skip_reason

        # 4. If all candidates are unready, fail closed with explainable reason
        if last_unready_runtime:
            fallback_events.append(
                FallbackEvent(
                    from_runtime=last_unready_runtime.runtime_id,
                    to_runtime="NONE",
                    reason=last_unready_reason or "Exhausted all candidates",
                )
            )

        return RoutingDecision(
            selected_runtime=None,
            status="FAILED",
            reason=(
                f"All {len(capable_candidates)} capable runtime(s) are currently unavailable: "
                f"{'; '.join(evaluated)}."
            ),
            fallback_events=fallback_events,
            candidates_evaluated=evaluated,
        )
