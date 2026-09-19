"""
Focused regression tests for JESTER AI Bridge runtime selection:
- Verifies that target_runtime_id="google-antigravity-cli" routes Architect, Executor,
  and Reviewer to Google runtime and Google agents (gemini-architect, gemini-dev, gemini-reviewer).
- Verifies that Preflight passes without requiring OPENAI_API_KEY.
- Verifies that invalid explicit runtimes fail clearly at intake and preflight.
- Verifies that an unavailable explicit runtime fails closed without silent fallback.
"""
from datetime import datetime, timezone
import os
from pathlib import Path
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig, load_bridge_config
from jester_bridge.contracts import (
    InvocationRequest,
    InvocationResult,
    InvocationStatus,
)
from jester_bridge.core import BridgeCore, ConfigurationError
from jester_bridge.execution_history import ExecutionHistoryStore
from jester_bridge.git_controller import GitController
from jester_bridge.orchestration import OrchestrationStage
from jester_bridge.preflight import PreflightValidator
from jester_bridge.protocol import Task
from jester_bridge.provider import AgentProvider
from jester_bridge.runtime import BoundedWorkspaceRuntime
from jester_bridge.runtimes import (
    AccountIdentity,
    AuthReference,
    AuthType,
    RuntimeEntry,
    RuntimeReadiness,
    RuntimeRegistry,
    RuntimeRouter,
    RuntimeStatus,
    RuntimeType,
    create_antigravity_runtime,
)
from jester_bridge.server import create_bridge_app
from jester_bridge.workflow import ControlledWorkflowRunner


class DummyAntigravityAdapter(AgentProvider):
    """Test double for Antigravity CLI adapter capturing invocations."""

    def __init__(self, provider_id: str = "google", status: RuntimeStatus = RuntimeStatus.READY):
        self._provider_id = provider_id
        self._status = status
        self.invocations = []

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def get_supported_capabilities(self):
        return {
            "planning",
            "reasoning",
            "repository_read",
            "repository_write",
            "code_generation",
            "command_execution",
            "testing",
            "review",
            "local_runtime",
        }

    def health_check(self) -> bool:
        return self._status == RuntimeStatus.READY

    def check_readiness(self) -> RuntimeReadiness:
        return RuntimeReadiness(
            status=self._status,
            message="Antigravity CLI is ready." if self._status == RuntimeStatus.READY else "Antigravity CLI unavailable.",
        )

    def invoke(self, request: InvocationRequest) -> InvocationResult:
        self.invocations.append(request)
        if request.role == "architect":
            summary = (
                "Task specification analyzed.\n\n"
                "Title: Test Antigravity Feature\n"
                "Scope: components/test_feature.py\n"
            )
        elif request.role == "executor":
            summary = (
                "Implementation complete.\n\n"
                "```python:components/test_feature.py\n"
                "def get_status():\n"
                "    return 'ANTIGRAVITY_ROUTED_OK'\n"
                "```\n"
            )
        elif request.role == "reviewer":
            summary = "Review verdict: PASS. Implementation strictly conforms to specifications."
        else:
            summary = "Execution succeeded."

        return InvocationResult(
            request_id=request.request_id,
            task_id=request.task_id,
            status=InvocationStatus.SUCCESS if self._status == RuntimeStatus.READY else InvocationStatus.FAILED,
            agent_id=request.agent_id,
            provider=self.provider_id,
            model=request.model or "gemini-3.8-flash-low",
            runtime_id=request.runtime_id or "google-antigravity-cli",
            runtime_type=request.runtime_type or "cli",
            account_id=request.account_id or "google-ai-pro",
            summary=summary,
            files_modified=["components/test_feature.py"] if request.role == "executor" else [],
            reports_generated=[],
            completed_at=datetime.now(timezone.utc).isoformat(),
        )


def _setup_test_bridge(tmp_path: Path, antigravity_status: RuntimeStatus = RuntimeStatus.READY):
    """Initializes a full bridge environment using canonical agents.json configuration."""
    for sub in [
        ".jester/tasks/inbox",
        ".jester/tasks/active",
        ".jester/tasks/review",
        ".jester/tasks/completed",
        ".jester/tasks/blocked",
        ".jester/reports/implementations",
        ".jester/reports/reviews",
        "components",
    ]:
        (tmp_path / sub).mkdir(parents=True, exist_ok=True)

    # Canonical config with default OpenAI bindings for architect/reviewer, but with Google agents defined
    config = BridgeConfig(
        role_bindings={
            "architect": "chatgpt-lead",
            "executor": "gemini-dev",
            "reviewer": "chatgpt-critic",
            "auditor": "jester-auditor",
        },
        agents={
            "chatgpt-lead": AgentProfile(id="chatgpt-lead", role="architect", provider="openai", capabilities={"planning", "reasoning", "repository_read"}),
            "chatgpt-critic": AgentProfile(id="chatgpt-critic", role="reviewer", provider="openai", capabilities={"reasoning", "repository_read", "review", "testing"}),
            "gemini-architect": AgentProfile(id="gemini-architect", role="architect", provider="google", model="gemini-3.8-flash-low", capabilities={"planning", "reasoning", "repository_read"}),
            "gemini-dev": AgentProfile(id="gemini-dev", role="executor", provider="google", model="gemini-2.5-pro", capabilities={"planning", "reasoning", "repository_read", "repository_write", "command_execution", "testing", "local_runtime", "code_generation"}),
            "gemini-reviewer": AgentProfile(id="gemini-reviewer", role="reviewer", provider="google", model="gemini-3.8-flash-low", capabilities={"reasoning", "repository_read", "review", "testing"}),
        },
    )

    # Mock unconfigured OpenAI provider (health_check=False)
    unconfigured_openai = MagicMock(spec=AgentProvider)
    unconfigured_openai.provider_id = "openai"
    unconfigured_openai.health_check.return_value = False
    unconfigured_openai.get_supported_capabilities.return_value = {"planning", "reasoning", "review", "repository_read", "testing"}

    # Antigravity adapter
    adapter = DummyAntigravityAdapter(provider_id="google", status=antigravity_status)

    core = BridgeCore(config=config, providers={"openai": unconfigured_openai, "google": adapter})

    # Register google-antigravity-cli runtime
    agy_runtime = create_antigravity_runtime(adapter=adapter)
    core.register_runtime(agy_runtime)

    runtime = BoundedWorkspaceRuntime(repo_root=tmp_path)
    store = ExecutionHistoryStore(repo_root=tmp_path)
    git = GitController(repo_root=tmp_path)

    runner = ControlledWorkflowRunner(
        core=core,
        repo_root=tmp_path,
        runtime=runtime,
        history_store=store,
        git_controller=git,
    )

    app = create_bridge_app(
        repo_root=tmp_path,
        runner=runner,
        history_store=store,
        git_controller=git,
    )
    client = TestClient(app)

    return client, runner, adapter, core, tmp_path


def test_google_antigravity_cli_selected_for_all_workflow_roles(tmp_path):
    """
    Verifies that target_runtime_id='google-antigravity-cli':
    - Passes Preflight without requiring OPENAI_API_KEY
    - Routes Architect to gemini-architect on google-antigravity-cli
    - Routes Executor to gemini-dev on google-antigravity-cli
    - Routes Reviewer to gemini-reviewer on google-antigravity-cli
    """
    client, runner, adapter, core, repo_root = _setup_test_bridge(tmp_path)

    outcome = runner.run_e2e_workflow(
        intent="Create an Antigravity feature at components/test_feature.py",
        target_task_id="TASK-AGY-01",
        scope=["components/test_feature.py"],
        verification=["python -c \"import sys; sys.exit(0)\""],
        auto_apply=True,
        check_credentials=True,
        target_runtime_id="google-antigravity-cli",
    )

    # 1. Preflight must pass without OpenAI credentials
    assert outcome.preflight.is_valid is True
    assert outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF

    # 2. Architect verification
    assert outcome.session.architect_result is not None
    arch_raw = outcome.session.architect_result.raw_result
    assert arch_raw.provider == "google"
    assert arch_raw.agent_id == "gemini-architect"
    assert arch_raw.runtime_id == "google-antigravity-cli"

    # 3. Executor verification
    assert outcome.session.executor_result is not None
    exec_raw = outcome.session.executor_result.raw_result
    assert exec_raw.provider == "google"
    assert exec_raw.agent_id == "gemini-dev"
    assert exec_raw.runtime_id == "google-antigravity-cli"

    # 4. Reviewer verification
    assert outcome.session.review_result is not None
    rev_raw = outcome.session.review_result.raw_result
    assert rev_raw.provider == "google"
    assert rev_raw.agent_id == "gemini-reviewer"
    assert rev_raw.runtime_id == "google-antigravity-cli"

    # 5. Exactly three invocations on the Antigravity adapter
    assert len(adapter.invocations) == 3
    assert adapter.invocations[0].role == "architect"
    assert adapter.invocations[0].agent_id == "gemini-architect"
    assert adapter.invocations[1].role == "executor"
    assert adapter.invocations[1].agent_id == "gemini-dev"
    assert adapter.invocations[2].role == "reviewer"
    assert adapter.invocations[2].agent_id == "gemini-reviewer"


def test_invalid_explicit_runtime_fails_clearly(tmp_path):
    """
    Verifies that an unrecognised target_runtime_id:
    - Fails clearly at HTTP intake with 400 Bad Request
    - Fails clearly in Preflight with TARGET_RUNTIME_NOT_FOUND
    """
    client, runner, adapter, core, repo_root = _setup_test_bridge(tmp_path)

    # 1. Intake API rejection
    res = client.post(
        "/api/tasks",
        json={
            "intent": "Task with invalid runtime",
            "task_id": "TASK-INV-01",
            "target_runtime_id": "nonexistent-runtime-9999",
            "sync": True,
        },
    )
    assert res.status_code == 400
    assert "not registered" in res.json()["detail"]

    # 2. Preflight direct validation rejection
    validator = PreflightValidator(core=core, repo_root=repo_root)
    task = Task(id="TASK-INV-02", title="Task", goal="Goal", scope=["components/test.py"])
    report = validator.validate(task, target_runtime_id="nonexistent-runtime-9999")
    assert report.is_valid is False
    assert any("TARGET_RUNTIME_NOT_FOUND" in e for e in report.errors)


def test_unavailable_explicit_runtime_fails_closed(tmp_path):
    """
    Verifies that if the explicitly selected runtime is unavailable:
    - Preflight marks task invalid with TARGET_RUNTIME_UNAVAILABLE
    - BridgeCore.prepare_invocation raises ConfigurationError instead of silently falling back
    """
    client, runner, adapter, core, repo_root = _setup_test_bridge(
        tmp_path, antigravity_status=RuntimeStatus.UNAVAILABLE
    )

    validator = PreflightValidator(core=core, repo_root=repo_root)
    task = Task(id="TASK-UNAVAIL-01", title="Task", goal="Goal", scope=["components/test.py"])

    # Preflight fails closed
    report = validator.validate(task, target_runtime_id="google-antigravity-cli", check_all_roles=True)
    assert report.is_valid is False
    assert any("TARGET_RUNTIME_UNAVAILABLE" in e for e in report.errors)

    # BridgeCore.prepare_invocation fails closed without silent provider fallback
    with pytest.raises(ConfigurationError) as exc_info:
        core.prepare_invocation(task, target_runtime_id="google-antigravity-cli")
    assert "Routing failed for explicit target_runtime_id" in str(exc_info.value)
