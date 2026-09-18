"""
Preflight Validation Engine for the JESTER Provider-Agnostic AI Bridge.

Performs deterministic validation before live execution:
- Provider configuration and registration
- Required environment variable presence
- Provider health status
- Task scope boundaries and protection rules
- Capability satisfaction
"""
from pathlib import Path
from typing import List, Optional, Set
from pydantic import BaseModel, Field

from .core import BridgeCore
from .protocol import Task
from .roles import Role
from .runtime import PROTECTED_PATHS


class PreflightReport(BaseModel):
    """Detailed summary of preflight check outcomes."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    checks_passed: List[str] = Field(default_factory=list)


class PreflightValidator:
    """Validates tasks, provider configurations, and workspace safety before execution."""

    def __init__(self, core: BridgeCore, repo_root: Optional[Path] = None):
        self.core = core
        self.repo_root = (repo_root or Path.cwd()).resolve()

    def validate(
        self,
        task: Task,
        check_credentials: bool = True,
        check_all_roles: bool = False,
        target_runtime_id: Optional[str] = None,
    ) -> PreflightReport:
        """
        Runs comprehensive preflight checks against task, workspace, and registered providers.
        """
        errors: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        # 1. Task Definition Integrity
        if not task.id:
            errors.append("Task ID is missing.")
        elif not task.id.startswith("TASK-"):
            warnings.append(f"Task ID '{task.id}' does not match standard TASK-XXXX format.")
        else:
            passed.append(f"Task ID valid: {task.id}")

        if not task.goal:
            errors.append("Task goal is missing.")
        else:
            passed.append("Task goal present")

        # 2. Workspace State & Scope Safety Checks
        if not self.repo_root.exists() or not self.repo_root.is_dir():
            errors.append(f"Workspace repository root does not exist or is not a directory: {self.repo_root}")
        else:
            passed.append(f"Workspace root verified: {self.repo_root.name}")

        if not task.scope:
            errors.append("Task has an empty scope. Authorized execution requires at least one bounded path.")
        else:
            has_dangerous_scope = False
            for s in task.scope:
                norm = s.replace("\\", "/").strip().lstrip("/")
                if norm in ("", ".", "*", "/", "./"):
                    errors.append(f"Task scope '{s}' is dangerously broad. Global repository scopes are prohibited.")
                    has_dangerous_scope = True
                if ".." in norm:
                    errors.append(f"Task scope '{s}' contains path traversal ('..'), which is prohibited.")
                    has_dangerous_scope = True
                for protected in PROTECTED_PATHS:
                    if norm == protected or norm.startswith(f"{protected}/"):
                        errors.append(f"Task scope '{s}' attempts to grant access to protected path '{protected}'.")
                        has_dangerous_scope = True
            if not has_dangerous_scope:
                passed.append(f"Task scope bounded and safe: {task.scope}")

        # 3. Agent & Provider Resolution for Task
        try:
            agent = self.core.resolve_agent(task)
            passed.append(f"Agent resolved: {agent.id} (role={agent.role}, provider={agent.provider})")

            provider = self.core.resolve_provider(agent)
            passed.append(f"Provider resolved: {provider.provider_id}")

            # 4. Capability Preflight
            try:
                self.core.validate_task_capabilities(task, agent, provider)
                passed.append(f"Capabilities verified: {sorted(list(task.required_capabilities))}")
            except Exception as e:
                errors.append(f"Capability check failed: {str(e)}")

            # 5. Runtime Router / Provider Readiness
            if check_credentials:
                routing = self.core.runtime_router.route(
                    task=task,
                    target_role=task.role,
                    target_provider=agent.provider,
                    target_runtime_id=target_runtime_id,
                )
                if routing.status == "SUCCESS" and routing.selected_runtime:
                    passed.append(
                        f"Runtime '{routing.selected_runtime.runtime_id}' "
                        f"(account='{routing.selected_runtime.account.account_id}') readiness verified"
                    )
                elif routing.candidates_evaluated:
                    errors.append(
                        f"PROVIDER_UNAVAILABLE: Provider '{provider.provider_id}' for role '{task.role}' "
                        f"failed readiness check ({routing.reason})."
                    )
                elif not provider.health_check():
                    errors.append(
                        f"PROVIDER_UNAVAILABLE: Provider '{provider.provider_id}' for role '{task.role}' "
                        f"failed readiness check (credentials not configured)."
                    )
                else:
                    passed.append(f"Provider '{provider.provider_id}' readiness verified")

        except Exception as e:
            errors.append(f"Resolution error: {str(e)}")

        # 6. Optional: All Workflow Roles Preflight (Architect, Executor, Reviewer)
        if check_all_roles:
            workflow_roles = [Role.ARCHITECT.value, Role.EXECUTOR.value, Role.REVIEWER.value]
            for role_name in workflow_roles:
                try:
                    role_agent = self.core.config.get_agent_for_role(role_name)
                    if not role_agent:
                        errors.append(f"No configured agent found for required workflow role '{role_name}'.")
                        continue
                    role_provider = self.core.resolve_provider(role_agent)
                    if check_credentials:
                        role_routing = self.core.runtime_router.route(
                            task=task,
                            target_role=role_name,
                            target_provider=role_agent.provider,
                            target_runtime_id=target_runtime_id,
                        )
                        if role_routing.status == "SUCCESS":
                            passed.append(f"Role '{role_name}' runtime readiness verified")
                        elif not role_provider.health_check():
                            errors.append(
                                f"PROVIDER_UNAVAILABLE: Provider '{role_provider.provider_id}' for role '{role_name}' "
                                f"failed readiness check (credentials not configured)."
                            )
                except Exception as e:
                    errors.append(f"Workflow role check failed for '{role_name}': {str(e)}")

        is_valid = len(errors) == 0
        return PreflightReport(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            checks_passed=passed,
        )
