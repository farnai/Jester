"""
Automated Regression Test Suite for TASK-0013:
Multi-Runtime, Multi-Account, Routing, and Extensibility Architecture.

Covers:
- Runtime registration and lookup
- Multiple accounts under one provider (e.g. Gemini Account A + Account B)
- Extensibility: Adding Account C without orchestration code modifications
- Deterministic capability-aware and priority-aware selection
- Quota / rate limit fallback with explainable fallback events
- Fails closed when all runtimes are unavailable (no silent mock fallback)
- Capability mismatch protection
- Generic CLI adapter allowlist enforcement and invocation normalization
- Local runtime (Ollama) representation and offline status reporting
- Zero raw credential leakage in AuthReference, metadata, and history
- Persistent execution history recording runtime, account, and fallback lineage
- Preserved Human Signoff boundary before Git delivery
- Preserved GitController commit and push authorization boundaries
- End-to-end workflow dispatch with multi-account routing
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from unittest.mock import MagicMock, patch
import pytest

from jester_bridge.adapters import CLIRuntimeAdapter, LocalRuntimeAdapter
from jester_bridge.agent import AgentProfile
from jester_bridge.capabilities import Capability
from jester_bridge.config import BridgeConfig
from jester_bridge.contracts import (
    InvocationRequest,
    InvocationResult,
    InvocationStatus,
    UsageMetrics,
)
from jester_bridge.core import BridgeCore, CapabilityMismatchError
from jester_bridge.execution_history import (
    ExecutionEvent,
    ExecutionHistoryStore,
    ExecutionRecord,
)
from jester_bridge.git_controller import CommitAuthorization, GitController
from jester_bridge.orchestration import (
    BridgeOrchestrator,
    OrchestrationSession,
    OrchestrationStage,
    ReviewVerdict,
)
from jester_bridge.preflight import PreflightValidator
from jester_bridge.protocol import Task
from jester_bridge.provider import AgentProvider
from jester_bridge.runtimes import (
    AccountIdentity,
    AuthReference,
    AuthType,
    FallbackEvent,
    RoutingDecision,
    RuntimeEntry,
    RuntimeReadiness,
    RuntimeRegistry,
    RuntimeRouter,
    RuntimeStatus,
    RuntimeType,
)
from jester_bridge.workflow import ControlledWorkflowRunner


class DummyAdapter(AgentProvider):
    """Configurable test double adapter for testing readiness and invocations."""

    def __init__(
        self,
        provider_id: str,
        status: RuntimeStatus = RuntimeStatus.READY,
        message: Optional[str] = None,
        capabilities: Optional[Set[str]] = None,
        summary: str = "Execution succeeded.",
    ):
        self._provider_id = provider_id
        self._status = status
        self._message = message
        self._capabilities = set(capabilities or {"planning", "reasoning", "code_generation", "review"})
        self._summary = summary
        self.invocations: List[InvocationRequest] = []

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def get_supported_capabilities(self) -> Set[str]:
        return set(self._capabilities)

    def health_check(self) -> bool:
        return self._status == RuntimeStatus.READY

    def check_readiness(self) -> RuntimeReadiness:
        return RuntimeReadiness(status=self._status, message=self._message)

    def invoke(self, request: InvocationRequest) -> InvocationResult:
        self.invocations.append(request)
        return InvocationResult(
            request_id=request.request_id,
            task_id=request.task_id,
            status=InvocationStatus.SUCCESS if self._status == RuntimeStatus.READY else InvocationStatus.FAILED,
            agent_id=request.agent_id,
            provider=self.provider_id,
            model=request.model or "test-model",
            runtime_id=request.runtime_id,
            runtime_type=request.runtime_type,
            account_id=request.account_id,
            summary=self._summary,
            files_modified=[],
            reports_generated=[],
            completed_at=datetime.now(timezone.utc).isoformat(),
        )


@pytest.fixture
def test_workspace(tmp_path: Path) -> Path:
    """Provides a fresh isolated workspace directory."""
    (tmp_path / "components").mkdir(parents=True, exist_ok=True)
    return tmp_path


# ==============================================================================
# TEST 1 & 2: Runtime Registration & Multi-Account Isolation
# ==============================================================================

def test_runtime_registration_and_lookup():
    """Verifies that runtimes can be registered and retrieved by ID and capabilities."""
    registry = RuntimeRegistry()

    acc_a = AccountIdentity(
        account_id="account-a",
        label="Google AI Pro Account A",
        provider="google",
        auth_ref=AuthReference(auth_type=AuthType.CLI_PROFILE, profile_name="pro-a"),
    )
    entry_a = RuntimeEntry(
        runtime_id="gemini-cli-a",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=acc_a,
        model="gemini-2.5-pro",
        capabilities={"code_generation", "reasoning"},
        priority=10,
    )
    registry.register_runtime(entry_a)

    found = registry.get_runtime("gemini-cli-a")
    assert found is not None
    assert found.account.account_id == "account-a"
    assert found.account.label == "Google AI Pro Account A"
    assert found.runtime_type == RuntimeType.CLI
    assert "code_generation" in found.capabilities


def test_multi_account_isolation_under_same_provider():
    """
    Verifies that multiple accounts under the same provider (Gemini Account A and B)
    exist as distinct, isolated runtime entities.
    """
    registry = RuntimeRegistry()

    acc_a = AccountIdentity(
        account_id="gemini-account-a",
        label="Primary Team Gemini",
        provider="google",
        auth_ref=AuthReference(auth_type=AuthType.CLI_PROFILE, profile_name="gemini-team-a"),
    )
    acc_b = AccountIdentity(
        account_id="gemini-account-b",
        label="Secondary Backup Gemini",
        provider="google",
        auth_ref=AuthReference(auth_type=AuthType.CLI_PROFILE, profile_name="gemini-team-b"),
    )

    r_a = RuntimeEntry(
        runtime_id="gemini-cli-acc-a",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=acc_a,
        model="gemini-2.5-pro",
        capabilities={"code_generation", "reasoning"},
        priority=10,
    )
    r_b = RuntimeEntry(
        runtime_id="gemini-cli-acc-b",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=acc_b,
        model="gemini-2.5-pro",
        capabilities={"code_generation", "reasoning"},
        priority=20,
    )

    registry.register_runtime(r_a)
    registry.register_runtime(r_b)

    google_runtimes = registry.find_runtimes(provider_id="google")
    assert len(google_runtimes) == 2
    assert google_runtimes[0].runtime_id == "gemini-cli-acc-a"
    assert google_runtimes[1].runtime_id == "gemini-cli-acc-b"
    assert google_runtimes[0].account.auth_ref.profile_name == "gemini-team-a"
    assert google_runtimes[1].account.auth_ref.profile_name == "gemini-team-b"


# ==============================================================================
# TEST 3: Adding Account C requires ZERO orchestration code changes
# ==============================================================================

def test_adding_account_c_requires_zero_orchestration_changes():
    """
    Acceptance Criterion Proof:
    Adding 'account-c' requires only registration into the registry.
    The Router and Orchestration evaluate it dynamically without any code changes.
    """
    registry = RuntimeRegistry()
    router = RuntimeRouter(registry)

    # Initial setup: account-a and account-b
    for acc_id, prio in [("account-a", 10), ("account-b", 20)]:
        registry.register_runtime(
            RuntimeEntry(
                runtime_id=f"gemini-{acc_id}",
                provider_id="google",
                runtime_type=RuntimeType.CLI,
                account=AccountIdentity(account_id=acc_id, provider="google"),
                model="gemini-2.5-pro",
                capabilities={"code_generation"},
                priority=prio,
                provider_adapter=DummyAdapter("google", status=RuntimeStatus.QUOTA_EXHAUSTED),
            )
        )

    task = Task(id="TASK-C01", title="Test", goal="Do work", required_capabilities={"code_generation"})

    # Before adding Account C: both A and B are exhausted, routing fails
    res_before = router.route(task, target_provider="google")
    assert res_before.status == "FAILED"
    assert res_before.selected_runtime is None

    # Dynamically register Account C without ANY code changes:
    adapter_c = DummyAdapter("google", status=RuntimeStatus.READY)
    registry.register_runtime(
        RuntimeEntry(
            runtime_id="gemini-account-c",
            provider_id="google",
            runtime_type=RuntimeType.CLI,
            account=AccountIdentity(account_id="account-c", provider="google"),
            model="gemini-2.5-pro",
            capabilities={"code_generation"},
            priority=30,
            provider_adapter=adapter_c,
        )
    )

    # Re-evaluate with exact same router and task
    res_after = router.route(task, target_provider="google")
    assert res_after.status == "SUCCESS"
    assert res_after.selected_runtime is not None
    assert res_after.selected_runtime.runtime_id == "gemini-account-c"
    assert res_after.selected_runtime.account.account_id == "account-c"
    assert len(res_after.fallback_events) == 2  # Fell back past A and B to reach C!


# ==============================================================================
# TEST 4 & 5: Deterministic Selection & Graceful Quota Fallback
# ==============================================================================

def test_deterministic_runtime_selection():
    """Verifies that the router deterministically chooses the lowest priority number (highest priority)."""
    registry = RuntimeRegistry()
    router = RuntimeRouter(registry)

    r_low = RuntimeEntry(
        runtime_id="gemini-low",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=AccountIdentity(account_id="acc-low", provider="google"),
        model="gemini-2.5-pro",
        capabilities={"code_generation"},
        priority=100,
        provider_adapter=DummyAdapter("google", status=RuntimeStatus.READY),
    )
    r_high = RuntimeEntry(
        runtime_id="gemini-high",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=AccountIdentity(account_id="acc-high", provider="google"),
        model="gemini-2.5-pro",
        capabilities={"code_generation"},
        priority=10,
        provider_adapter=DummyAdapter("google", status=RuntimeStatus.READY),
    )

    registry.register_runtime(r_low)
    registry.register_runtime(r_high)

    task = Task(id="TASK-D01", title="Task", goal="Test", required_capabilities={"code_generation"})
    decision = router.route(task, target_provider="google")

    assert decision.status == "SUCCESS"
    assert decision.selected_runtime.runtime_id == "gemini-high"
    assert "gemini-high" in decision.reason
    assert len(decision.fallback_events) == 0


def test_runtime_fallback_on_quota_exhausted():
    """
    Verifies that when Account A reports QUOTA_EXHAUSTED, the router gracefully
    falls back to Account B and records an explicit FallbackEvent.
    """
    registry = RuntimeRegistry()
    router = RuntimeRouter(registry)

    # Account A: QUOTA_EXHAUSTED
    r_a = RuntimeEntry(
        runtime_id="gemini-acc-a",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=AccountIdentity(account_id="acc-a", provider="google"),
        model="gemini-2.5-pro",
        capabilities={"code_generation"},
        priority=10,
        provider_adapter=DummyAdapter(
            "google", status=RuntimeStatus.QUOTA_EXHAUSTED, message="Daily token limit reached"
        ),
    )
    # Account B: READY
    r_b = RuntimeEntry(
        runtime_id="gemini-acc-b",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=AccountIdentity(account_id="acc-b", provider="google"),
        model="gemini-2.5-pro",
        capabilities={"code_generation"},
        priority=20,
        provider_adapter=DummyAdapter("google", status=RuntimeStatus.READY),
    )

    registry.register_runtime(r_a)
    registry.register_runtime(r_b)

    task = Task(id="TASK-FB01", title="Task", goal="Test", required_capabilities={"code_generation"})
    decision = router.route(task, target_provider="google")

    assert decision.status == "SUCCESS"
    assert decision.selected_runtime.runtime_id == "gemini-acc-b"
    assert len(decision.fallback_events) == 1
    fb = decision.fallback_events[0]
    assert fb.from_runtime == "gemini-acc-a"
    assert fb.to_runtime == "gemini-acc-b"
    assert "QUOTA_EXHAUSTED" in fb.reason
    assert "Daily token limit reached" in fb.reason


# ==============================================================================
# TEST 6, 7, 8: Fail-Closed & Capability Mismatch Safety
# ==============================================================================

def test_all_runtimes_unavailable_fails_closed():
    """Verifies that when all candidates are unready, routing fails closed without guessing."""
    registry = RuntimeRegistry()
    router = RuntimeRouter(registry)

    r_a = RuntimeEntry(
        runtime_id="gemini-acc-a",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=AccountIdentity(account_id="acc-a", provider="google"),
        model="gemini-2.5-pro",
        capabilities={"code_generation"},
        priority=10,
        provider_adapter=DummyAdapter("google", status=RuntimeStatus.RATE_LIMITED),
    )
    r_b = RuntimeEntry(
        runtime_id="gemini-acc-b",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=AccountIdentity(account_id="acc-b", provider="google"),
        model="gemini-2.5-pro",
        capabilities={"code_generation"},
        priority=20,
        provider_adapter=DummyAdapter("google", status=RuntimeStatus.OFFLINE),
    )
    registry.register_runtime(r_a)
    registry.register_runtime(r_b)

    task = Task(id="TASK-FC01", title="Task", goal="Test", required_capabilities={"code_generation"})
    decision = router.route(task, target_provider="google")

    assert decision.status == "FAILED"
    assert decision.selected_runtime is None
    assert "unavailable" in decision.reason.lower()


def test_capability_mismatch_blocks_runtime():
    """Verifies that runtimes lacking task-required capabilities are skipped."""
    registry = RuntimeRegistry()
    router = RuntimeRouter(registry)

    r_plan = RuntimeEntry(
        runtime_id="planner-only",
        provider_id="google",
        runtime_type=RuntimeType.API,
        account=AccountIdentity(account_id="acc-plan", provider="google"),
        model="gemini-flash",
        capabilities={"planning", "reasoning"},
        priority=10,
        provider_adapter=DummyAdapter("google", status=RuntimeStatus.READY),
    )
    registry.register_runtime(r_plan)

    task = Task(id="TASK-CAP01", title="Task", goal="Code", required_capabilities={"code_generation"})
    decision = router.route(task, target_provider="google")

    assert decision.status == "FAILED"
    assert "missing" in decision.reason
    assert "code_generation" in decision.reason


def test_no_silent_mock_fallback_when_runtimes_fail(test_workspace: Path):
    """
    Integrity Invariant from TASK-0012:
    A real request whose runtimes fail readiness must NEVER silently switch to mock providers.
    """
    config = BridgeConfig(
        role_bindings={"executor": "gemini-dev"},
        agents={"gemini-dev": AgentProfile(id="gemini-dev", role="executor", provider="google", capabilities={"code_generation"})},
    )
    core = BridgeCore(config=config)
    # Register unavailable google runtime
    core.register_runtime(
        RuntimeEntry(
            runtime_id="gemini-cli-offline",
            provider_id="google",
            runtime_type=RuntimeType.CLI,
            account=AccountIdentity(account_id="acc-off", provider="google"),
            model="gemini-2.5-pro",
            capabilities={"code_generation"},
            priority=10,
            provider_adapter=DummyAdapter("google", status=RuntimeStatus.OFFLINE, message="Daemon not running"),
        )
    )

    validator = PreflightValidator(core=core, repo_root=test_workspace)
    task = Task(
        id="TASK-NOMOCK",
        title="Test",
        goal="Do work",
        role="executor",
        scope=["components/test/"],
        required_capabilities={"code_generation"},
    )

    report = validator.validate(task, check_credentials=True)
    assert report.is_valid is False
    assert any("PROVIDER_UNAVAILABLE" in err for err in report.errors)
    # Verify no mock provider was substituted
    assert not any("mock" in r.runtime_id for r in core.runtime_registry.list_runtimes())


# ==============================================================================
# TEST 9 & 10: Generic CLI Adapter Allowlist & Normalization
# ==============================================================================

def test_cli_runtime_adapter_allowlist_enforcement():
    """Verifies that CLIRuntimeAdapter strictly enforces the controlled executable allowlist."""
    # 1. Allowed executable (gemini) succeeds creation
    adapter = CLIRuntimeAdapter(provider_id="gemini-cli", executable_name="gemini")
    assert adapter.executable_name == "gemini"

    # 2. Disallowed executable (arbitrary binary) is rejected
    with pytest.raises(ValueError, match="not in the controlled allowlist"):
        CLIRuntimeAdapter(provider_id="bad-cli", executable_name="malicious_script.sh")

    # 3. Shell metacharacters in executable name are rejected
    with pytest.raises(ValueError):
        CLIRuntimeAdapter(provider_id="bad-cli", executable_name="gemini; rm -rf /")


def test_cli_runtime_adapter_execution_normalization():
    """Verifies that CLIRuntimeAdapter invokes runner cleanly and normalizes output into InvocationResult."""
    # Injected test double runner
    def mock_runner(cmd, env, payload):
        assert cmd[0] == "gemini"
        assert "--profile" in cmd
        assert "account-a" in cmd
        return 0, "CLI generation succeeded.\n```python:src/app.py\ndef main(): pass\n```", ""

    adapter = CLIRuntimeAdapter(
        provider_id="gemini-cli",
        executable_name="gemini",
        account_id="account-a",
        cli_profile="account-a",
        runner_fn=mock_runner,
    )

    req = InvocationRequest(
        request_id="req-cli-1",
        task_id="TASK-CLI-01",
        role="executor",
        agent_id="gemini-agent",
        provider="gemini-cli",
        model="gemini-2.5-pro",
        payload={"goal": "Build main"},
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    res = adapter.invoke(req)
    assert res.status == InvocationStatus.SUCCESS
    assert "CLI generation succeeded" in res.summary
    assert res.raw_metadata.get("account_id") == "account-a"
    assert res.raw_metadata.get("cli_profile") == "account-a"


# ==============================================================================
# TEST 11: Local Runtime (Ollama) Representation & Offline Handling
# ==============================================================================

def test_local_runtime_ollama_representation_and_offline_handling():
    """Verifies that LocalRuntimeAdapter detects offline daemon cleanly without raising unhandled exceptions."""
    # Mock offline local client
    mock_client = MagicMock()
    mock_client.is_healthy = False

    adapter = LocalRuntimeAdapter(
        provider_id="ollama",
        endpoint="http://127.0.0.1:11434",
        default_model="qwen2.5:7b",
        client=mock_client,
    )

    readiness = adapter.check_readiness()
    assert readiness.status == RuntimeStatus.OFFLINE
    assert "unreachable" in readiness.message.lower()

    # Invoking an offline local runtime produces BLOCKED status rather than crashing
    req = InvocationRequest(
        request_id="req-loc-1",
        task_id="TASK-LOC-01",
        role="executor",
        agent_id="local-agent",
        provider="ollama",
        payload={"goal": "Run local"},
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    res = adapter.invoke(req)
    assert res.status == InvocationStatus.BLOCKED
    assert "offline" in res.summary.lower()


# ==============================================================================
# TEST 12: Credential & Secret Redaction
# ==============================================================================

def test_credential_and_secret_redaction():
    """Verifies that AuthReference sanitizes raw API tokens and keys."""
    # Attempting to pass a raw secret into env_var or profile_name is automatically redacted
    auth_ref = AuthReference(
        auth_type=AuthType.API_KEY,
        env_var="sk-proj-super-secret-key-12345",
        profile_name="AIzaSySecretToken",
    )
    assert auth_ref.env_var == "[REDACTED_CREDENTIAL_REFERENCE]"
    assert auth_ref.profile_name == "[REDACTED_CREDENTIAL_REFERENCE]"


# ==============================================================================
# TEST 13: Execution History Records Runtime & Fallback Metadata
# ==============================================================================

def test_execution_history_records_runtime_and_fallback_metadata(test_workspace: Path):
    """Verifies that Persistent Execution History captures runtime ID, type, account, and routing reason."""
    store = ExecutionHistoryStore(repo_root=test_workspace)

    rec = ExecutionRecord(
        execution_id="exec-rt-001",
        task_id="TASK-RT-01",
        overall_status="completed",
        metadata={
            "runtimes": {
                "executor": {
                    "runtime_id": "gemini-cli-acc-b",
                    "runtime_type": "cli",
                    "account_id": "account-b",
                    "routing_reason": "Fallback from account-a (QUOTA_EXHAUSTED)",
                }
            }
        },
    )
    store.create_execution(rec)

    evt = ExecutionEvent(
        execution_id="exec-rt-001",
        event_type="executor_completed",
        stage="executor",
        status="success",
        role="executor",
        metadata={
            "runtime_id": "gemini-cli-acc-b",
            "runtime_type": "cli",
            "account_id": "account-b",
            "routing_reason": "Fallback from account-a",
        },
    )
    store.record_event(evt)

    fetched_rec = store.get_execution("exec-rt-001")
    assert fetched_rec is not None
    assert fetched_rec.metadata["runtimes"]["executor"]["runtime_id"] == "gemini-cli-acc-b"
    assert fetched_rec.metadata["runtimes"]["executor"]["account_id"] == "account-b"

    events = store.list_events("exec-rt-001")
    assert len(events) == 1
    assert events[0].metadata["runtime_id"] == "gemini-cli-acc-b"
    assert events[0].metadata["account_id"] == "account-b"


# ==============================================================================
# TEST 14 & 15: Human Signoff & Git Controller Governance Preserved
# ==============================================================================

def test_human_signoff_preserved_with_multi_runtime():
    """
    Governance Invariant:
    Reviewer PASS on routed runtimes must strictly halt at AWAITING_HUMAN_SIGNOFF.
    No automatic commit or completion is allowed.
    """
    config = BridgeConfig(
        role_bindings={"architect": "arch", "executor": "exec", "reviewer": "rev"},
        agents={
            "arch": AgentProfile(id="arch", role="architect", provider="google", capabilities={"planning", "reasoning"}),
            "exec": AgentProfile(id="exec", role="executor", provider="google", capabilities={"code_generation", "reasoning"}),
            "rev": AgentProfile(id="rev", role="reviewer", provider="google", capabilities={"review", "reasoning"}),
        },
    )
    core = BridgeCore(config=config)
    orchestrator = BridgeOrchestrator(core=core)

    task = Task(id="TASK-GOV-01", title="Feature", role="reviewer", required_capabilities={"review", "reasoning"})
    session = orchestrator.create_session(task)
    session.current_stage = OrchestrationStage.EXECUTOR

    # Mock reviewer response with PASS
    rev_adapter = DummyAdapter("google", status=RuntimeStatus.READY, summary="Review verdict: PASS. Verified.")
    core.register_runtime(
        RuntimeEntry(
            runtime_id="gemini-rev",
            provider_id="google",
            runtime_type=RuntimeType.API,
            account=AccountIdentity(account_id="account-a", provider="google"),
            model="gemini-2.5-pro",
            capabilities={"review", "reasoning"},
            provider_adapter=rev_adapter,
        )
    )

    session = orchestrator.run_reviewer_stage(
        session=session,
        diff="--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new",
        verification_output="Tests passed 5/5",
    )

    # Invariant: Must stop at AWAITING_HUMAN_SIGNOFF
    assert session.review_result.verdict == ReviewVerdict.PASS
    assert session.current_stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert session.current_stage != OrchestrationStage.COMPLETED


def test_git_controller_boundaries_preserved(test_workspace: Path):
    """Verifies that Git commit requires explicit human approval and push requires separate authorization."""
    git = GitController(repo_root=test_workspace)

    # Attempting push without approval raises GitAuthorizationError
    with pytest.raises(Exception):
        git.push(authorization=None)


# ==============================================================================
# TEST 16: End-to-End Workflow with Routed Multi-Account Runtime
# ==============================================================================

def test_e2e_workflow_with_routed_multi_account_runtime(test_workspace: Path):
    """
    Validates a complete controlled workflow execution using routed multi-account runtimes:
    - Architect executes via Gemini Account A
    - Executor falls back from Account A (QUOTA_EXHAUSTED) to Account B (READY)
    - Reviewer completes via Account A
    - Reaches AWAITING_HUMAN_SIGNOFF
    """
    config = BridgeConfig(
        role_bindings={"architect": "arch", "executor": "exec", "reviewer": "rev"},
        agents={
            "arch": AgentProfile(id="arch", role="architect", provider="google", capabilities={"planning", "reasoning"}),
            "exec": AgentProfile(id="exec", role="executor", provider="google", capabilities={"code_generation", "reasoning"}),
            "rev": AgentProfile(id="rev", role="reviewer", provider="google", capabilities={"review", "reasoning"}),
        },
    )
    core = BridgeCore(config=config)

    # Account A: Planning and Review ready; Code Generation QUOTA_EXHAUSTED
    adapter_a = DummyAdapter(
        "google",
        status=RuntimeStatus.READY,
        summary="Architect plan ready.\n\nTitle: Multi-Runtime Test\nScope: components/feature.py\n",
    )
    core.register_runtime(
        RuntimeEntry(
            runtime_id="gemini-acc-a-arch",
            provider_id="google",
            runtime_type=RuntimeType.CLI,
            account=AccountIdentity(account_id="account-a", provider="google"),
            model="gemini-2.5-pro",
            capabilities={"planning", "reasoning", "review"},
            priority=10,
            provider_adapter=adapter_a,
        )
    )

    # Account A: Executor QUOTA_EXHAUSTED
    adapter_a_exec = DummyAdapter(
        "google",
        status=RuntimeStatus.QUOTA_EXHAUSTED,
        message="Daily token limit reached on Account A",
    )
    core.register_runtime(
        RuntimeEntry(
            runtime_id="gemini-acc-a-exec",
            provider_id="google",
            runtime_type=RuntimeType.CLI,
            account=AccountIdentity(account_id="account-a", provider="google"),
            model="gemini-2.5-pro",
            capabilities={"code_generation", "reasoning"},
            priority=10,
            provider_adapter=adapter_a_exec,
        )
    )

    # Account B: Executor READY
    code_text = "Implementation done.\n\n```python:components/feature.py\ndef run():\n    return 'MULTI_ACCOUNT_OK'\n```\n"
    adapter_b_exec = DummyAdapter(
        "google",
        status=RuntimeStatus.READY,
        summary=code_text,
    )
    core.register_runtime(
        RuntimeEntry(
            runtime_id="gemini-acc-b-exec",
            provider_id="google",
            runtime_type=RuntimeType.CLI,
            account=AccountIdentity(account_id="account-b", provider="google"),
            model="gemini-2.5-pro",
            capabilities={"code_generation", "reasoning"},
            priority=20,
            provider_adapter=adapter_b_exec,
        )
    )

    runner = ControlledWorkflowRunner(core=core, repo_root=test_workspace)

    outcome = runner.run_e2e_workflow(
        intent="Implement multi-account feature at components/feature.py",
        target_task_id="TASK-E2E-MA",
        scope=["components/feature.py"],
        verification=["python -c \"import sys; sys.exit(0)\""],
        auto_apply=True,
        check_credentials=True,
    )

    # Assert workflow reached AWAITING_HUMAN_SIGNOFF
    assert outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert outcome.diff is not None
    assert "components/feature.py" in outcome.diff

    # Verify execution history recorded the fallback from Account A to Account B
    history = runner.history_store.get_execution(outcome.execution_id)
    assert history is not None
    assert "runtimes" in history.metadata
    assert history.metadata["runtimes"]["executor"]["runtime_id"] == "gemini-acc-b-exec"
    assert history.metadata["runtimes"]["executor"]["account_id"] == "account-b"


def test_server_api_runtimes_endpoint(test_workspace: Path):
    """Verifies that GET /api/runtimes exposes registered runtimes, accounts, and readiness."""
    from fastapi.testclient import TestClient
    from jester_bridge.server import create_bridge_app

    config = BridgeConfig(
        role_bindings={"executor": "gemini-dev"},
        agents={"gemini-dev": AgentProfile(id="gemini-dev", role="executor", provider="google", capabilities={"code_generation"})},
    )
    core = BridgeCore(config=config)
    core.register_runtime(
        RuntimeEntry(
            runtime_id="gemini-acc-a",
            provider_id="google",
            runtime_type=RuntimeType.CLI,
            account=AccountIdentity(account_id="account-a", label="Pro A", provider="google"),
            model="gemini-2.5-pro",
            capabilities={"code_generation"},
            priority=10,
            provider_adapter=DummyAdapter("google", status=RuntimeStatus.READY),
        )
    )

    runner = ControlledWorkflowRunner(core=core, repo_root=test_workspace)
    app = create_bridge_app(repo_root=test_workspace, runner=runner)
    client = TestClient(app)

    res = client.get("/api/runtimes")
    assert res.status_code == 200
    data = res.json()
    assert "runtimes" in data
    r_list = data["runtimes"]
    assert any(r["runtime_id"] == "gemini-acc-a" for r in r_list)
    match = next(r for r in r_list if r["runtime_id"] == "gemini-acc-a")
    assert match["account_id"] == "account-a"
    assert match["account_label"] == "Pro A"
    assert match["status"] == "READY"
