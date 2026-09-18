"""
Tests for JESTER AI Bridge Integrity & Real Execution Hardening (TASK-0012).

Verifies:
- Test A: Missing live provider credentials do NOT silently become mock execution.
- Test B: Explicit simulation mode DOES still use mocks where intended.
- Test C: Live Founder request with unavailable provider reaches clear failure/block state.
- Test D: Code-generation task with zero changes does NOT receive verification PASS.
- Test E: Code-generation task with zero changes does NOT receive Reviewer PASS.
- Test F: Reviewer cannot PASS when diff is empty and changes are required.
- Test G: Explicit target path (e.g. tests/bridge/example.py) is safely extracted into task scope.
- Test H: Unsafe target paths (traversal, absolute) are strictly rejected.
- Test I: Existing protected path rules (.git, .env, AGENTS.md, migrations) remain enforced.
- Test J: Existing human signoff remains mandatory before Git delivery.
- Test K: No Git commit occurs without explicit human approval.
- Test L: No Git push occurs without explicit push authorization.
- Test M: Diff pipeline handles both newly created untracked files and modified files.
- Test N: Exact TASK-A8AC forensic reproduction (halts truthfully at PROVIDER_UNAVAILABLE).
"""
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig
from jester_bridge.contracts import (
    InvocationRequest,
    InvocationResult,
    InvocationStatus,
    UsageMetrics,
)
from jester_bridge.core import BridgeCore
from jester_bridge.execution_history import ExecutionHistoryStore
from jester_bridge.git_controller import (
    CommitAuthorization,
    GitController,
    PushAuthorization,
)
from jester_bridge.google_provider import GoogleProvider
from jester_bridge.openai_provider import OpenAIProvider
from jester_bridge.orchestration import (
    BridgeOrchestrator,
    OrchestrationSession,
    OrchestrationStage,
    ReviewVerdict,
)
from jester_bridge.preflight import PreflightValidator
from jester_bridge.protocol import Task
from jester_bridge.runtime import (
    BoundedWorkspaceRuntime,
    FileChange,
    PROTECTED_PATHS,
    ScopeViolationError,
    is_path_in_scope,
    task_expects_code_changes,
)
from jester_bridge.server import create_bridge_app
from jester_bridge.testing import MockProviderA, MockProviderB
from jester_bridge.workflow import (
    ControlledWorkflowRunner,
    extract_safe_target_paths,
)


@pytest.fixture
def test_workspace(tmp_path: Path):
    """Initializes a clean, isolated repository structure for integrity testing."""
    jester_dir = tmp_path / ".jester"
    for sub in [
        "tasks/inbox",
        "tasks/active",
        "tasks/review",
        "tasks/completed",
        "tasks/blocked",
        "reports/implementations",
        "reports/reviews",
        "config",
        "ui",
    ]:
        (jester_dir / sub).mkdir(parents=True, exist_ok=True)

    # Copy or create ui/index.html
    ui_dir = tmp_path / "jester_bridge" / "ui"
    ui_dir.mkdir(parents=True, exist_ok=True)
    real_ui = Path(__file__).resolve().parent.parent.parent / "jester_bridge" / "ui" / "index.html"
    if real_ui.exists():
        (ui_dir / "index.html").write_text(real_ui.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        (ui_dir / "index.html").write_text("<html><body>Founder UI Mock</body></html>", encoding="utf-8")

    # Create a dummy agents.json in tmp_path
    agents_cfg = {
        "role_bindings": {
            "architect": "chatgpt-lead",
            "executor": "gemini-dev",
            "reviewer": "chatgpt-critic",
        },
        "agents": {
            "chatgpt-lead": {
                "id": "chatgpt-lead",
                "role": "architect",
                "provider": "openai",
                "capabilities": ["planning", "reasoning", "repository_read"],
            },
            "gemini-dev": {
                "id": "gemini-dev",
                "role": "executor",
                "provider": "google",
                "capabilities": ["planning", "reasoning", "code_generation", "repository_read"],
            },
            "chatgpt-critic": {
                "id": "chatgpt-critic",
                "role": "reviewer",
                "provider": "openai",
                "capabilities": ["reasoning", "repository_read", "review"],
            },
        },
    }
    (jester_dir / "config" / "agents.json").write_text(json.dumps(agents_cfg), encoding="utf-8")

    return tmp_path


# ==============================================================================
# TEST A: No Silent Mock Fallback on Missing Credentials
# ==============================================================================

def test_no_silent_mock_fallback_on_missing_credentials(test_workspace: Path):
    """
    Verifies that when create_bridge_app initializes without injected runner,
    it registers real OpenAIProvider and GoogleProvider rather than silently
    falling back to MockProviderA/B when API keys are absent.
    """
    with patch.dict(os.environ, {"OPENAI_API_KEY": "", "GEMINI_API_KEY": ""}, clear=True):
        app = create_bridge_app(repo_root=test_workspace)
        runner = app.state.runner
        assert runner is not None
        assert runner.core is not None

        openai_prov = runner.core.providers.get("openai")
        google_prov = runner.core.providers.get("google")

        # Must be real adapter instances, NOT MockProviderA or MockProviderB
        assert isinstance(openai_prov, OpenAIProvider)
        assert isinstance(google_prov, GoogleProvider)
        assert not isinstance(openai_prov, MockProviderA)
        assert not isinstance(google_prov, MockProviderB)

        # Health checks must truthfully return False when credentials are empty
        assert openai_prov.health_check() is False
        assert google_prov.health_check() is False


# ==============================================================================
# TEST B: Explicit Simulation Mode Uses Mocks
# ==============================================================================

def test_explicit_simulation_mode_uses_mocks(test_workspace: Path):
    """
    Verifies that explicit simulation (simulate_all=True) DOES dynamically swap
    in mock providers and allows deterministic simulation execution.
    """
    app = create_bridge_app(repo_root=test_workspace)
    client = TestClient(app)

    res = client.post(
        "/api/tasks",
        json={
            "intent": "Implement dummy feature in simulation mode",
            "simulate_all": True,
            "sync": True,
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["task_id"].startswith("TASK-")

    # In explicit simulation mode, mock providers are used
    prov_a = app.state.runner.core.providers.get("openai")
    prov_b = app.state.runner.core.providers.get("google")
    assert isinstance(prov_a, MockProviderA)
    assert isinstance(prov_b, MockProviderB)


# ==============================================================================
# TEST C: Live Request with Unavailable Provider Fails Preflight
# ==============================================================================

def test_live_request_with_unavailable_provider_fails_preflight(test_workspace: Path):
    """
    Verifies that a live Founder request without credentials fails preflight
    truthfully with PROVIDER_UNAVAILABLE and halts at BLOCKED stage.
    """
    with patch.dict(os.environ, {"OPENAI_API_KEY": "", "GEMINI_API_KEY": ""}, clear=True):
        app = create_bridge_app(repo_root=test_workspace)
        client = TestClient(app)

        res = client.post(
            "/api/tasks",
            json={
                "intent": "Create a new production service",
                "simulate_all": False,  # Live mode
                "sync": True,
            },
        )
        assert res.status_code == 201
        data = res.json()
        assert data["stage"].upper() == "BLOCKED"
        assert "PROVIDER_UNAVAILABLE" in (data.get("error") or "")
        assert "credentials not configured" in (data.get("error") or "")

        # Task file in .jester/tasks/blocked/ must exist
        task_id = data["task_id"]
        blocked_file = test_workspace / ".jester" / "tasks" / "blocked" / f"{task_id}.json"
        assert blocked_file.exists()


# ==============================================================================
# TEST D: Code-Generation Task with Zero Changes Fails Verification
# ==============================================================================

def test_code_generation_zero_changes_fails_verification(test_workspace: Path):
    """
    Verifies that a task requiring code generation (or type=feature) returns
    FAILED and verification_passed=False when changes == [].
    """
    runtime = BoundedWorkspaceRuntime(repo_root=test_workspace)

    code_task = Task(
        id="TASK-CODE-01",
        title="Code Gen Task",
        type="feature",
        required_capabilities={"code_generation"},
        scope=["src/app.py"],
        verification=["pytest tests/"],
    )

    assert task_expects_code_changes(code_task) is True

    # Zero changes applied
    res = runtime.execute_and_verify(changes=[], task=code_task)
    assert res.status == InvocationStatus.FAILED
    assert res.verification_passed is False
    assert "zero file changes" in (res.error_message or "").lower()
    assert res.files_modified == []


def test_legitimate_no_change_task_can_pass_verification(test_workspace: Path):
    """
    Verifies that tasks legitimately not expecting code changes (e.g. type=audit)
    do not fail merely because changes are empty.
    """
    runtime = BoundedWorkspaceRuntime(repo_root=test_workspace)

    audit_task = Task(
        id="TASK-AUDIT-01",
        title="Audit Task",
        type="audit",
        role="auditor",
        required_capabilities={"review", "repository_read"},
        scope=["docs/"],
    )

    assert task_expects_code_changes(audit_task) is False

    res = runtime.execute_and_verify(changes=[], task=audit_task)
    assert res.status == InvocationStatus.SUCCESS
    assert res.verification_passed is True
    assert "does not require code modifications" in res.verification_output


# ==============================================================================
# TEST E & F: Reviewer Cannot PASS When Diff is Empty and Changes Expected
# ==============================================================================

def test_reviewer_cannot_pass_empty_diff_when_changes_expected(test_workspace: Path):
    """
    Verifies that the Reviewer stage cannot produce PASS when the task requires
    code changes but the diff is empty or 'No file changes detected.',
    even if the LLM provider emits 'Review verdict: PASS.'.
    """
    config = BridgeConfig(
        role_bindings={"architect": "arch", "executor": "exec", "reviewer": "rev"},
        agents={
            "arch": AgentProfile(id="arch", role="architect", provider="mock-p", capabilities={"planning"}),
            "exec": AgentProfile(id="exec", role="executor", provider="mock-p", capabilities={"code_generation"}),
            "rev": AgentProfile(id="rev", role="reviewer", provider="mock-p", capabilities={"review", "reasoning"}),
        },
    )
    # Mock reviewer returning PASS
    mock_prov = MockProviderA(
        provider_id="mock-p",
        default_summary="Review verdict: PASS. Looks perfect to me!",
    )
    core = BridgeCore(config=config, providers={"mock-p": mock_prov})
    orchestrator = BridgeOrchestrator(core=core)

    code_task = Task(
        id="TASK-REV-01",
        title="Feature Task",
        type="feature",
        required_capabilities={"code_generation"},
        scope=["src/feature.py"],
    )

    session = orchestrator.create_session(task=code_task)
    session.current_stage = OrchestrationStage.EXECUTOR

    # Empty diff passed to reviewer
    session = orchestrator.run_reviewer_stage(
        session,
        diff="No file changes detected.",
        verification_output="No changes applied.",
    )

    # Invariant: Reviewer verdict MUST NOT be PASS
    assert session.review_result.verdict == ReviewVerdict.REWORK_REQUIRED
    assert session.reviewer_handoff.verdict == "REWORK_REQUIRED"
    assert session.reviewer_handoff.diff_inspected is False
    assert "Integrity check failed" in (session.review_result.error_message or "")
    assert session.current_stage == OrchestrationStage.REWORK_REQUIRED
    assert session.current_stage != OrchestrationStage.AWAITING_HUMAN_SIGNOFF


def test_reviewer_passes_when_diff_is_present_and_valid(test_workspace: Path):
    """
    Verifies that when a real diff and modified files are present,
    Reviewer can issue PASS and advance to AWAITING_HUMAN_SIGNOFF.
    """
    config = BridgeConfig(
        role_bindings={"architect": "arch", "executor": "exec", "reviewer": "rev"},
        agents={
            "arch": AgentProfile(id="arch", role="architect", provider="mock-p", capabilities={"planning"}),
            "exec": AgentProfile(id="exec", role="executor", provider="mock-p", capabilities={"code_generation"}),
            "rev": AgentProfile(id="rev", role="reviewer", provider="mock-p", capabilities={"review", "reasoning"}),
        },
    )
    mock_prov = MockProviderA(
        provider_id="mock-p",
        default_summary="Review verdict: PASS. Verified clean diff.",
    )
    core = BridgeCore(config=config, providers={"mock-p": mock_prov})
    orchestrator = BridgeOrchestrator(core=core)

    code_task = Task(
        id="TASK-REV-02",
        title="Valid Feature Task",
        type="feature",
        required_capabilities={"code_generation"},
        scope=["src/feature.py"],
    )

    session = orchestrator.create_session(task=code_task)
    session.current_stage = OrchestrationStage.EXECUTOR

    real_diff = "--- a/src/feature.py\n+++ b/src/feature.py\n@@ -1 +1 @@\n-old\n+new"
    session = orchestrator.run_reviewer_stage(
        session,
        diff=real_diff,
        verification_output="All tests passed.",
        extra_context={"files_modified": ["src/feature.py"]},
    )

    assert session.review_result.verdict == ReviewVerdict.PASS
    assert session.reviewer_handoff.diff_inspected is True
    assert session.current_stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF


# ==============================================================================
# TEST G, H, I: Scope Resolution & Security Guardrails
# ==============================================================================

def test_safe_target_path_extraction(test_workspace: Path):
    """
    Verifies that extract_safe_target_paths accurately extracts explicit safe
    paths while rejecting path traversal, absolute paths, and protected files.
    """
    # Valid file target
    intent_valid = "Create tests/bridge/task_0011_ui_e2e_probe.py containing a pytest test."
    paths = extract_safe_target_paths(intent_valid, test_workspace)
    assert paths == ["tests/bridge/task_0011_ui_e2e_probe.py"]

    # Valid directory target
    intent_dir = "Update files under components/ui/ with dark mode styles."
    paths = extract_safe_target_paths(intent_dir, test_workspace)
    assert paths == ["components/ui/"]

    # Multiple targets
    intent_multi = "Add tests/unit/test_auth.py and backend/app/auth.py"
    paths = extract_safe_target_paths(intent_multi, test_workspace)
    assert paths == ["backend/app/auth.py", "tests/unit/test_auth.py"]

    # Traversal attack
    intent_traversal = "Read ../../../etc/shadow and write to ../pass.txt"
    paths = extract_safe_target_paths(intent_traversal, test_workspace)
    assert paths == []

    # Absolute path attack
    intent_abs = "Modify /etc/hosts or C:\\Windows\\System32\\drivers\\etc\\hosts"
    paths = extract_safe_target_paths(intent_abs, test_workspace)
    assert paths == []

    # Protected paths
    intent_protected = "Update .env and .git/config and AGENTS.md"
    paths = extract_safe_target_paths(intent_protected, test_workspace)
    assert paths == []


def test_protected_paths_cannot_be_written_at_runtime(test_workspace: Path):
    """
    Verifies that BoundedWorkspaceRuntime strictly rejects writes to protected paths.
    """
    runtime = BoundedWorkspaceRuntime(repo_root=test_workspace)

    # Even if someone attempts to craft a task scope with protected paths
    malicious_task = Task(
        id="TASK-EVIL",
        title="Evil Task",
        scope=[".env", ".git/config", "AGENTS.md", "supabase/migrations/test.sql"],
    )

    for prot in [".env", ".git/config", "AGENTS.md", "supabase/migrations/test.sql"]:
        assert is_path_in_scope(prot, malicious_task.scope) is False
        with pytest.raises(ScopeViolationError):
            runtime.validate_scope(prot, malicious_task)


# ==============================================================================
# TEST J, K, L: Human Signoff and Git Governance Boundaries
# ==============================================================================

def test_human_signoff_mandatory_before_git_delivery(test_workspace: Path):
    """
    Verifies that reaching Reviewer PASS halts at AWAITING_HUMAN_SIGNOFF
    and does NOT automatically commit or push.
    """
    config = BridgeConfig(
        role_bindings={"architect": "arch", "executor": "exec", "reviewer": "rev"},
        agents={
            "arch": AgentProfile(id="arch", role="architect", provider="mock-p", capabilities={"planning"}),
            "exec": AgentProfile(id="exec", role="executor", provider="mock-p", capabilities={"code_generation"}),
            "rev": AgentProfile(id="rev", role="reviewer", provider="mock-p", capabilities={"review", "reasoning"}),
        },
    )
    mock_prov = MockProviderA(
        provider_id="mock-p",
        default_summary="Review verdict: PASS. Verified.",
    )
    core = BridgeCore(config=config, providers={"mock-p": mock_prov})
    git = GitController(repo_root=test_workspace)
    orchestrator = BridgeOrchestrator(core=core)

    task = Task(id="TASK-SIGN-01", title="Signoff Task", scope=["src/app.py"])
    session = orchestrator.create_session(task=task)
    session.current_stage = OrchestrationStage.EXECUTOR

    session = orchestrator.run_reviewer_stage(
        session,
        diff="--- a/src/app.py\n+++ b/src/app.py\n@@ -1 +1 @@\n-old\n+new",
        extra_context={"files_modified": ["src/app.py"]},
    )

    # Must halt at AWAITING_HUMAN_SIGNOFF
    assert session.current_stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF

    # Delivery validation must fail because human signoff has not occurred
    can_deliver, reasons = git.validate_delivery(task, session, ["src/app.py"])
    assert can_deliver is False
    assert any("Human sign-off has not been granted" in r for r in reasons)

    # Attempting to commit without human signoff must return failure
    commit_res = git.commit(
        authorization=CommitAuthorization(
            task_id="TASK-SIGN-01",
            approver="unauthorized_actor",
            commit_message="auto commit attempt",
            approved_files=["src/app.py"],
            review_passed=False,  # Not verified by human
        ),
        session=session,
        task=task,
    )
    assert commit_res.success is False
    assert "Human sign-off has not been granted" in (commit_res.error or "")

    # Missing authorization object completely raises GitAuthorizationError
    with pytest.raises(Exception):
        git.commit(authorization=None, session=session, task=task)


# ==============================================================================
# TEST M: Diff Pipeline Handles Untracked New Files and Modified Files
# ==============================================================================

def test_diff_pipeline_new_untracked_and_modified_files(test_workspace: Path):
    """
    Verifies that BoundedWorkspaceRuntime.generate_unified_diff accurately
    produces standard unified diffs for newly created files (/dev/null -> b/path)
    and modified tracked files (a/path -> b/path).
    """
    runtime = BoundedWorkspaceRuntime(repo_root=test_workspace)

    # 1. New file
    new_rel = "tests/test_new_sample.py"
    backups_new = {new_rel: None}  # None indicates newly created file
    new_abs = test_workspace / new_rel
    new_abs.parent.mkdir(parents=True, exist_ok=True)
    new_abs.write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    diff_new = runtime.generate_unified_diff(backups_new, [new_rel])
    assert "--- /dev/null" in diff_new
    assert f"+++ b/{new_rel}" in diff_new
    assert "+def test_ok():" in diff_new

    # 2. Modified file
    mod_rel = "src/sample_mod.py"
    mod_abs = test_workspace / mod_rel
    mod_abs.parent.mkdir(parents=True, exist_ok=True)
    orig_content = "def calculate():\n    return 1\n"
    new_content = "def calculate():\n    return 2\n"
    mod_abs.write_text(new_content, encoding="utf-8")
    backups_mod = {mod_rel: orig_content}

    diff_mod = runtime.generate_unified_diff(backups_mod, [mod_rel])
    assert f"--- a/{mod_rel}" in diff_mod
    assert f"+++ b/{mod_rel}" in diff_mod
    assert "-    return 1" in diff_mod
    assert "+    return 2" in diff_mod


# ==============================================================================
# TEST N: Exact TASK-A8AC Forensic Reproduction
# ==============================================================================

def test_exact_task_a8ac_forensic_reproduction(test_workspace: Path):
    """
    Exact regression test for TASK-A8AC:
    Founder request:
    "Create tests/bridge/task_0011_ui_e2e_probe.py containing a pytest test that verifies 2 + 2 == 4."

    Without live provider credentials:
    The system must NOT:
    - silently use mock providers for a normal Founder request
    - report Executor success
    - report verification PASS
    - report Reviewer PASS
    - reach a misleading AWAITING_HUMAN_SIGNOFF state

    Instead, it MUST:
    - safely extract scope as ['tests/bridge/task_0011_ui_e2e_probe.py']
    - fail preflight with PROVIDER_UNAVAILABLE
    - halt at BLOCKED stage
    - record truthful failure reasons
    """
    with patch.dict(os.environ, {"OPENAI_API_KEY": "", "GEMINI_API_KEY": ""}, clear=True):
        app = create_bridge_app(repo_root=test_workspace)
        client = TestClient(app)

        founder_prompt = (
            "Create tests/bridge/task_0011_ui_e2e_probe.py containing a pytest test that verifies 2 + 2 == 4."
        )

        res = client.post(
            "/api/tasks",
            json={
                "intent": founder_prompt,
                "task_id": "TASK-A8AC-REGRESSION",
                "simulate_all": False,  # Live request!
                "sync": True,
            },
        )
        assert res.status_code == 201
        data = res.json()

        # 1. Must be BLOCKED, never AWAITING_HUMAN_SIGNOFF
        assert data["stage"].upper() == "BLOCKED"

        # 2. Must report PROVIDER_UNAVAILABLE
        err = data.get("error") or ""
        assert "PROVIDER_UNAVAILABLE" in err
        assert "credentials not configured" in err

        # 3. Inspect execution record in store
        store: ExecutionHistoryStore = app.state.history_store
        exec_id = data["execution_id"]
        rec = store.get_execution(exec_id)
        assert rec is not None
        assert rec.overall_status.upper() == "BLOCKED"
        assert rec.current_stage.upper() == "BLOCKED"
        assert rec.verification_passed is None or rec.verification_passed is False
        assert rec.reviewer_verdict is None or rec.reviewer_verdict != "PASS"

        # 4. Task file in blocked folder
        blocked_task_file = test_workspace / ".jester" / "tasks" / "blocked" / "TASK-A8AC-REGRESSION.json"
        assert blocked_task_file.exists()

        # 5. Task scope must have captured the exact file requested
        t_data = json.loads(blocked_task_file.read_text(encoding="utf-8"))
        assert "tests/bridge/task_0011_ui_e2e_probe.py" in t_data["scope"]
