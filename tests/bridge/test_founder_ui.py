"""
Tests for JESTER Founder Local Interface & Server API (TASK-0011).

Verifies:
- Operational web interface rendering at GET /
- Natural language task intake & workflow execution via POST /api/tasks
- Real-time execution tracking, stages, and status
- Persistent Execution History retrieval (recent, latest, details)
- Context snapshot and budget observability without secret leakage
- Structured handoff inspection (Architect, Executor, Reviewer)
- Real runtime diff and verification output inspection
- Mandatory Human Signoff gate (APPROVE and REJECT)
- Controlled Git delivery results
- Zero autonomous commits or pushes
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig
from jester_bridge.contracts import InvocationResult, InvocationStatus, UsageMetrics
from jester_bridge.core import BridgeCore
from jester_bridge.execution_history import ExecutionHistoryStore, ExecutionRecord
from jester_bridge.git_controller import (
    CommitAuthorization,
    GitController,
    GitOperationResult,
    GitStatusResult,
    PushAuthorization,
)
from jester_bridge.orchestration import OrchestrationStage, ReviewVerdict
from jester_bridge.protocol import Task
from jester_bridge.runtime import BoundedWorkspaceRuntime
from jester_bridge.server import create_bridge_app
from jester_bridge.testing import MockProviderA, MockProviderB
from jester_bridge.runtimes import AccountIdentity, RuntimeEntry, RuntimeType
from jester_bridge.workflow import ControlledWorkflowRunner


def _setup_test_env(tmp_path: Path):
    """Sets up an isolated test environment with mock providers and git controller."""
    # Create required directory structure in tmp_path
    jester_dir = tmp_path / ".jester"
    for sub in ["tasks/inbox", "tasks/active", "tasks/review", "tasks/completed", "tasks/blocked",
                "reports/implementations", "reports/reviews", "config", "ui"]:
        (jester_dir / sub).mkdir(parents=True, exist_ok=True)

    # Copy or create ui/index.html in tmp_path/jester_bridge/ui/
    ui_dir = tmp_path / "jester_bridge" / "ui"
    ui_dir.mkdir(parents=True, exist_ok=True)
    real_ui = Path(__file__).resolve().parent.parent.parent / "jester_bridge" / "ui" / "index.html"
    if real_ui.exists():
        (ui_dir / "index.html").write_text(real_ui.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        (ui_dir / "index.html").write_text("<html><body>Founder UI Mock</body></html>", encoding="utf-8")

    mock_arch = (
        "Task specification analyzed.\n\n"
        "Title: Founder Test Feature\n"
        "Scope: src/founder_test.py\n"
    )
    mock_exec = (
        "Implementation complete.\n\n"
        "```python:src/founder_test.py\n"
        "def hello_founder():\n"
        "    return 'READY'\n"
        "```\n"
    )
    mock_rev = "Review verdict: PASS. Code conforms to specifications."

    prov_openai = MockProviderA(provider_id="openai", default_summary=mock_arch)
    prov_google = MockProviderB(provider_id="google", default_summary=mock_exec)

    config = BridgeConfig(
        role_bindings={"architect": "chatgpt-lead", "executor": "gemini-dev", "reviewer": "chatgpt-critic"},
        agents={
            "chatgpt-lead": AgentProfile(id="chatgpt-lead", role="architect", provider="openai", capabilities={"planning", "reasoning", "repository_read"}),
            "gemini-dev": AgentProfile(id="gemini-dev", role="executor", provider="google", capabilities={"planning", "reasoning", "code_generation", "repository_read"}),
            "chatgpt-critic": AgentProfile(id="chatgpt-critic", role="reviewer", provider="openai", capabilities={"reasoning", "repository_read", "review"}),
            "gemini-architect": AgentProfile(id="gemini-architect", role="architect", provider="google", capabilities={"planning", "reasoning", "repository_read"}),
            "gemini-reviewer": AgentProfile(id="gemini-reviewer", role="reviewer", provider="google", capabilities={"reasoning", "repository_read", "review"}),
        },
    )

    core = BridgeCore(config=config, providers={"openai": prov_openai, "google": prov_google})
    core.register_runtime(
        RuntimeEntry(
            runtime_id="test-runtime-id",
            provider_id="google",
            runtime_type=RuntimeType.CLI,
            account=AccountIdentity(account_id="test-account", provider="google"),
            model="gemini-2.5-pro",
            capabilities={"code_generation", "reasoning", "planning", "review"},
            priority=10,
            provider_adapter=prov_google,
        )
    )
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
    return client, runner, store, git, tmp_path


def test_server_health_check(tmp_path):
    """Verifies the health endpoint returns healthy status and bridge readiness."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["runner_ready"] is True
    assert data["git_ready"] is True
    assert data["history_ready"] is True


def test_render_founder_interface_html(tmp_path):
    """Verifies that GET / serves the Founder Local Interface single-page app."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    html = res.text
    assert "FOUNDER LOCAL INTERFACE" in html
    assert "Founder Task Intake" in html
    assert "Execution History" in html
    assert "HUMAN APPROVAL REQUIRED" in html
    assert "Unified Diff" in html


def test_task_create_empty_intent_rejected(tmp_path):
    """Verifies that submitting an empty task intent returns 400 Bad Request."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    res = client.post("/api/tasks", json={"intent": "   "})
    assert res.status_code == 400
    assert "cannot be empty" in res.json()["detail"]


def test_task_create_and_sync_execution(tmp_path):
    """Verifies full synchronous execution triggered by Founder request."""
    client, runner, store, _, _ = _setup_test_env(tmp_path)
    payload = {
        "intent": "Add founder health service helper",
        "task_id": "TASK-F001",
        "scope": ["src/founder_test.py"],
        "verification": ["python -c \"print('ok')\""],
        "sync": True,
        "auto_apply": True,
    }
    res = client.post("/api/tasks", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["task_id"] == "TASK-F001"
    assert data["execution_id"] is not None
    assert data["stage"] == OrchestrationStage.AWAITING_HUMAN_SIGNOFF.value

    # Verify task file moved to review
    review_task = tmp_path / ".jester" / "tasks" / "review" / "TASK-F001.json"
    assert review_task.exists()

    # Verify execution record persisted
    exec_rec = store.get_execution(data["execution_id"])
    assert exec_rec is not None
    assert exec_rec.task_id == "TASK-F001"
    assert exec_rec.overall_status == "AWAITING_HUMAN_SIGNOFF"


def test_task_create_async_execution(tmp_path):
    """Verifies async execution launch via background thread."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    payload = {
        "intent": "Async background task",
        "task_id": "TASK-ASYNC1",
        "scope": ["src/async.py"],
        "sync": False,
    }
    res = client.post("/api/tasks", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["task_id"] == "TASK-ASYNC1"
    assert data["status"] == "started"


def test_list_tasks_and_get_task(tmp_path):
    """Verifies listing tasks by lifecycle folder and getting specific task JSON."""
    client, _, _, _, _ = _setup_test_env(tmp_path)

    # Place sample task in inbox
    inbox_dir = tmp_path / ".jester" / "tasks" / "inbox"
    task_data = {
        "id": "TASK-INBOX-1",
        "title": "Inbox Task Title",
        "type": "feature",
        "status": "inbox",
        "role": "executor",
        "goal": "Test inbox task",
        "scope": ["test.py"],
    }
    (inbox_dir / "TASK-INBOX-1.json").write_text(json.dumps(task_data), encoding="utf-8")

    # List tasks
    res = client.get("/api/tasks")
    assert res.status_code == 200
    tasks_data = res.json()["tasks"]
    assert any(t["id"] == "TASK-INBOX-1" for t in tasks_data["inbox"])

    # Get specific task
    res_single = client.get("/api/tasks/TASK-INBOX-1")
    assert res_single.status_code == 200
    assert res_single.json()["task"]["id"] == "TASK-INBOX-1"
    assert res_single.json()["folder"] == "inbox"

    # Not found task
    res_404 = client.get("/api/tasks/TASK-NONEXISTENT")
    assert res_404.status_code == 404


def test_execution_details_timeline_and_diff(tmp_path):
    """Verifies comprehensive execution inspection: record, events, summary, diff, reviewer."""
    client, runner, store, _, _ = _setup_test_env(tmp_path)
    # Run a workflow
    create_res = client.post("/api/tasks", json={
        "intent": "Add founder helper utility",
        "task_id": "TASK-F002",
        "scope": ["src/founder_test.py"],
        "verification": ["python -c \"print('ok')\""],
        "sync": True,
    })
    exec_id = create_res.json()["execution_id"]

    # Get execution details
    res = client.get(f"/api/executions/{exec_id}")
    assert res.status_code == 200
    details = res.json()

    assert details["record"]["execution_id"] == exec_id
    assert details["record"]["task_id"] == "TASK-F002"
    assert details["is_awaiting_signoff"] is True
    assert len(details["events"]) > 0

    # Verify event timeline contains canonical stages
    event_types = [e["event_type"] for e in details["events"]]
    assert "execution_created" in event_types
    assert "preflight_started" in event_types
    assert "context_assembled" in event_types
    assert "executor_started" in event_types
    assert "review_completed" in event_types
    assert "awaiting_human_signoff" in event_types

    # Diff endpoint
    diff_res = client.get(f"/api/executions/{exec_id}/diff")
    assert diff_res.status_code == 200
    assert "diff" in diff_res.json()


def test_execution_context_inspection(tmp_path):
    """Verifies role-aware context inspection endpoint without exposing credentials."""
    client, runner, store, _, _ = _setup_test_env(tmp_path)
    create_res = client.post("/api/tasks", json={
        "intent": "Inspect context feature",
        "task_id": "TASK-F003",
        "scope": ["src/founder_test.py"],
        "verification": ["python -c \"print('ok')\""],
        "sync": True,
    })
    exec_id = create_res.json()["execution_id"]

    res = client.get(f"/api/executions/{exec_id}/context")
    assert res.status_code == 200
    data = res.json()
    assert data["execution_id"] == exec_id
    assert len(data["contexts"]) >= 2  # Architect and Executor/Reviewer contexts

    # Verify budget and provenance are recorded
    first_ctx = data["contexts"][0]
    assert "context_id" in first_ctx
    assert "total_characters" in first_ctx
    assert "provenance" in first_ctx


def test_human_signoff_approve_and_reconstruct_session(tmp_path):
    """Verifies that APPROVE invokes complete_human_approval and moves task to completed."""
    client, runner, store, _, _ = _setup_test_env(tmp_path)
    create_res = client.post("/api/tasks", json={
        "intent": "Signoff approval test",
        "task_id": "TASK-F004",
        "scope": ["src/founder_test.py"],
        "verification": ["python -c \"print('ok')\""],
        "sync": True,
    })
    exec_id = create_res.json()["execution_id"]

    # Submit APPROVE signoff
    signoff_payload = {
        "decision": "approve",
        "approver": "founder-alice",
        "notes": "Looks great, approved for release.",
    }
    res = client.post(f"/api/executions/{exec_id}/signoff", json=signoff_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "approved"
    assert data["task_id"] == "TASK-F004"

    # Verify task moved to completed/
    completed_file = tmp_path / ".jester" / "tasks" / "completed" / "TASK-F004.json"
    assert completed_file.exists()

    # Verify history record updated
    rec = store.get_execution(exec_id)
    assert rec.overall_status == OrchestrationStage.COMPLETED.value
    assert rec.human_signoff_by == "founder-alice"
    assert rec.human_signoff_notes == "Looks great, approved for release."


def test_human_signoff_reject(tmp_path):
    """Verifies that REJECT invokes reject_human_signoff and transitions task appropriately."""
    client, runner, store, _, _ = _setup_test_env(tmp_path)
    create_res = client.post("/api/tasks", json={
        "intent": "Signoff rejection test",
        "task_id": "TASK-F005",
        "scope": ["src/founder_test.py"],
        "verification": ["python -c \"print('ok')\""],
        "sync": True,
    })
    exec_id = create_res.json()["execution_id"]

    # Submit REJECT signoff
    signoff_payload = {
        "decision": "reject",
        "approver": "founder-bob",
        "reason": "Need different approach.",
    }
    res = client.post(f"/api/executions/{exec_id}/signoff", json=signoff_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "rejected"
    assert data["reason"] == "Need different approach."


def test_signoff_rejected_when_not_awaiting_signoff(tmp_path):
    """Verifies that attempting signoff on a non-awaiting execution returns 400."""
    client, _, store, _, _ = _setup_test_env(tmp_path)

    # Insert a dummy pending execution
    store.create_execution(ExecutionRecord(
        execution_id="exec-dummy-pending",
        task_id="TASK-DUMMY",
        overall_status="pending",
    ))

    res = client.post("/api/executions/exec-dummy-pending/signoff", json={
        "decision": "approve",
        "approver": "founder",
    })
    assert res.status_code == 400
    assert "not 'AWAITING_HUMAN_SIGNOFF'" in res.json()["detail"]


def test_git_status_inspection(tmp_path):
    """Verifies that GET /api/git/status calls GitController.inspect_status()."""
    client, _, _, git, _ = _setup_test_env(tmp_path)
    with patch.object(git, "inspect_status", return_value=GitStatusResult(
        branch="main",
        is_clean=True,
        modified_files=[],
        untracked_files=[],
        staged_files=[],
        raw_status="clean",
    )):
        res = client.get("/api/git/status")
        assert res.status_code == 200
        assert res.json()["branch"] == "main"
        assert res.json()["is_clean"] is True


def test_explicit_push_authorization(tmp_path):
    """Verifies that POST /api/git/push requires explicit human authorization and calls git.push()."""
    client, _, _, git, _ = _setup_test_env(tmp_path)
    with patch.object(git, "push", return_value=GitOperationResult(
        operation="push",
        success=True,
        remote="origin",
        branch="main",
        pushed=True,
    )):
        res = client.post("/api/git/push", json={
            "task_id": "TASK-F006",
            "approver": "founder-charlie",
            "remote": "origin",
            "branch": "main",
        })
        assert res.status_code == 200
        assert res.json()["pushed"] is True


def test_invalid_execution_id_returns_404(tmp_path):
    """Verifies 404 response for unknown execution IDs."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    res = client.get("/api/executions/exec-non-existent")
    assert res.status_code == 404


def test_rework_cycle_trigger(tmp_path):
    """Verifies triggering a rework cycle via POST /api/executions/{id}/rework."""
    client, runner, store, _, _ = _setup_test_env(tmp_path)
    create_res = client.post("/api/tasks", json={
        "intent": "Rework test feature",
        "task_id": "TASK-F007",
        "scope": ["src/founder_test.py"],
        "verification": ["python -c \"print('ok')\""],
        "sync": True,
    })
    exec_id = create_res.json()["execution_id"]

    rework_res = client.post(f"/api/executions/{exec_id}/rework", json={
        "rework_feedback": "Please improve docstrings",
        "sync": True,
    })
    assert rework_res.status_code == 200
    assert rework_res.json()["task_id"] == "TASK-F007"


def test_human_signoff_with_commit_authorization(tmp_path):
    """Verifies that human approval with commit details triggers controlled git commit."""
    client, runner, store, git, _ = _setup_test_env(tmp_path)
    create_res = client.post("/api/tasks", json={
        "intent": "Commit authorization test",
        "task_id": "TASK-F008",
        "scope": ["src/founder_test.py"],
        "verification": ["python -c \"print('ok')\""],
        "sync": True,
    })
    exec_id = create_res.json()["execution_id"]

    with patch.object(git, "commit", return_value=GitOperationResult(
        operation="commit",
        success=True,
        commit_hash="abc1234def",
        branch="main",
        files_affected=["src/founder_test.py"],
    )):
        signoff_payload = {
            "decision": "approve",
            "approver": "founder-dave",
            "notes": "Approved for commit.",
            "commit_message": "feat: founder approved feature",
            "approved_files": ["src/founder_test.py"],
        }
        res = client.post(f"/api/executions/{exec_id}/signoff", json=signoff_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["decision"] == "approved"
        assert data["git_delivery"] is not None
        assert data["git_delivery"]["commit_hash"] == "abc1234def"


def test_sensitive_credential_redaction(tmp_path):
    """Verifies that API keys and bearer tokens in text are redacted."""
    from jester_bridge.server import _sanitize_sensitive_strings
    dirty_text = "Here is my secret sk-proj-12345678901234567890 and Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz"
    clean = _sanitize_sensitive_strings(dirty_text)
    assert "sk-proj-" not in clean
    assert "[REDACTED_API_KEY]" in clean
    assert "[REDACTED_TOKEN]" in clean


def test_task_0017_ui_html_contains_runtime_and_rework_controls(tmp_path):
    """Verifies that GET / renders all TASK-0017 controls: runtime selector, rework timeline step, and metadata fields."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    # Task intake enhancements
    assert 'id="taskRuntime"' in html
    assert "What do you want JESTER to do?" in html
    # Active execution metadata items
    assert 'id="viewAgent"' in html
    assert 'id="viewProvider"' in html
    assert 'id="viewRuntime"' in html
    assert 'id="viewModel"' in html
    assert 'id="viewReworkCount"' in html
    assert 'id="viewFilesModified"' in html
    # Rework timeline and banner
    assert 'id="step-rework"' in html
    assert 'id="reworkBanner"' in html
    assert "Trigger Rework Cycle" in html


def test_task_0017_task_create_with_target_runtime_and_role_bindings(tmp_path):
    """Verifies that POST /api/tasks accepts target_runtime_id and role_bindings and applies them."""
    client, runner, _, _, _ = _setup_test_env(tmp_path)
    payload = {
        "intent": "Task intake with explicit runtime and role bindings",
        "task_id": "TASK-F017-1",
        "scope": ["src/founder_test.py"],
        "verification": ["python -c \"print('ok')\""],
        "sync": True,
        "target_runtime_id": "test-runtime-id",
        "role_bindings": {"executor": "gemini-dev"},
    }
    res = client.post("/api/tasks", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["task_id"] == "TASK-F017-1"
    assert data["execution_id"] is not None
    assert runner.core.config.role_bindings["executor"] == "gemini-dev"


def test_task_0017_execution_details_surfaces_active_runtime_and_files_modified(tmp_path):
    """Verifies that GET /api/executions/{id} returns enriched active_runtime and files_modified fields."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    create_res = client.post("/api/tasks", json={
        "intent": "Verify execution details enrichment",
        "task_id": "TASK-F017-2",
        "scope": ["src/founder_test.py"],
        "verification": ["python -c \"print('ok')\""],
        "sync": True,
    })
    exec_id = create_res.json()["execution_id"]

    res = client.get(f"/api/executions/{exec_id}")
    assert res.status_code == 200
    details = res.json()
    assert "active_runtime" in details
    assert "files_modified" in details
    assert "rework_count" in details
    assert isinstance(details["files_modified"], list)
    assert details["rework_count"] == 0
    assert details["active_runtime"]["provider"] in ["google", "openai", None]


def test_task_0017_reviewer_pass_strictly_halts_at_awaiting_human_signoff(tmp_path):
    """Verifies that Reviewer PASS strictly halts at AWAITING_HUMAN_SIGNOFF and does NOT complete."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    create_res = client.post("/api/tasks", json={
        "intent": "Test signoff gate integrity",
        "task_id": "TASK-F017-3",
        "scope": ["src/founder_test.py"],
        "verification": ["python -c \"print('ok')\""],
        "sync": True,
    })
    exec_id = create_res.json()["execution_id"]
    res = client.get(f"/api/executions/{exec_id}")
    details = res.json()
    assert details["record"]["overall_status"] == "AWAITING_HUMAN_SIGNOFF"
    assert details["is_awaiting_signoff"] is True
    assert details["record"]["git_commit_hash"] is None
    assert details["record"]["git_pushed"] is None

    # Verify task file is in review/, not completed/
    review_file = tmp_path / ".jester" / "tasks" / "review" / "TASK-F017-3.json"
    completed_file = tmp_path / ".jester" / "tasks" / "completed" / "TASK-F017-3.json"
    assert review_file.exists()
    assert not completed_file.exists()


def test_task_0017_runtimes_endpoint_returns_registered_runtimes(tmp_path):
    """Verifies that GET /api/runtimes returns registered runtimes list with status and metadata."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    res = client.get("/api/runtimes")
    assert res.status_code == 200
    data = res.json()
    assert "runtimes" in data
    assert isinstance(data["runtimes"], list)


# ---------------------------------------------------------------------------
# TASK-0018 Tests: Execution History & Runtime State UX
# ---------------------------------------------------------------------------

def test_task_0018_health_endpoint_distinguishes_provider_and_runtime_readiness(tmp_path):
    """Verifies that /api/health returns runtimes_summary and bridge_ready independently of direct provider health."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert "runtimes_summary" in data
    assert "bridge_ready" in data
    assert "providers" in data
    summary = data["runtimes_summary"]
    assert "total_runtimes" in summary
    assert "ready_runtimes_count" in summary
    assert "ready_runtimes" in summary
    assert "primary_ready_runtime" in summary


def test_task_0018_antigravity_runtime_readiness_truthful_when_provider_api_unconfigured(tmp_path):
    """Verifies that an authenticated Antigravity CLI runtime produces bridge_ready=True even if direct API keys are unconfigured."""
    from jester_bridge.runtimes import (
        AccountIdentity,
        AuthReference,
        AuthType,
        RuntimeEntry,
        RuntimeReadiness,
        RuntimeStatus,
        RuntimeType,
    )
    client, runner, _, _, _ = _setup_test_env(tmp_path)

    # Force direct provider API check to return unconfigured (healthy=False)
    for p in runner.core.providers.values():
        p.health_check = MagicMock(return_value=False)

    # Register Antigravity CLI runtime entry with Google AI Pro
    mock_adapter = MagicMock()
    mock_adapter.check_readiness.return_value = RuntimeReadiness(
        status=RuntimeStatus.READY,
        message="Antigravity CLI verified and authenticated (Google AI Pro).",
    )

    antigravity_entry = RuntimeEntry(
        runtime_id="google-antigravity-cli",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=AccountIdentity(
            account_id="google-ai-pro",
            label="Google AI Pro",
            provider="google",
            auth_ref=AuthReference(auth_type=AuthType.CLI_PROFILE),
        ),
        model="gemini-3.8-flash-low",
        capabilities={"code_generation", "planning", "reasoning", "repository_read"},
        priority=10,
        provider_adapter=mock_adapter,
    )

    runner.core.register_runtime(antigravity_entry)

    # Check /api/health
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    health_data = res_health.json()

    # Direct providers are unconfigured
    assert health_data["providers"]["openai"]["healthy"] is False
    assert health_data["providers"]["google"]["healthy"] is False

    # But bridge is READY because Antigravity CLI runtime is ready!
    assert health_data["bridge_ready"] is True
    summary = health_data["runtimes_summary"]
    assert summary["ready_runtimes_count"] >= 1
    assert "google-antigravity-cli" in summary["ready_runtimes"]
    primary = summary["primary_ready_runtime"]
    assert primary is not None
    assert primary["runtime_id"] == "google-antigravity-cli"
    assert primary["account_label"] == "Google AI Pro"
    assert primary["model"] == "gemini-3.8-flash-low"

    # Check /api/runtimes exposes it with status READY
    res_runtimes = client.get("/api/runtimes")
    assert res_runtimes.status_code == 200
    runtimes = res_runtimes.json()["runtimes"]
    cli_item = next(r for r in runtimes if r["runtime_id"] == "google-antigravity-cli")
    assert cli_item["status"] == "READY"
    assert cli_item["account_label"] == "Google AI Pro"
    assert cli_item["model"] == "gemini-3.8-flash-low"
    assert "provider" in cli_item


def test_task_0018_runtimes_endpoint_exposes_metadata_without_secrets(tmp_path):
    """Verifies /api/runtimes exposes registered runtime readiness and metadata with zero credential leakage."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    res = client.get("/api/runtimes")
    assert res.status_code == 200
    data = res.json()
    assert "runtimes" in data
    json_text = json.dumps(data).lower()
    for sensitive in ["api_key", "secret", "bearer", "password", "token="]:
        assert sensitive not in json_text


def test_task_0018_execution_history_filtering_and_counts(tmp_path):
    """Verifies /api/executions exposes counts, supports status filtering, and flags signoff priority."""
    client, _, store, _, _ = _setup_test_env(tmp_path)

    # Record 1: Awaiting signoff
    rec1 = ExecutionRecord(
        execution_id="exec-signoff-1",
        task_id="TASK-T18-1",
        overall_status="AWAITING_HUMAN_SIGNOFF",
        task_title="Signoff Needed Task",
        total_tokens=1500,
        metadata={"runtime_id": "google-antigravity-cli", "model": "gemini-3.8-flash-low"},
    )
    # Record 2: Completed
    rec2 = ExecutionRecord(
        execution_id="exec-comp-2",
        task_id="TASK-T18-2",
        overall_status="COMPLETED",
        task_title="Completed Task",
        total_tokens=2200,
        metadata={"runtime_id": "google-antigravity-cli", "model": "gemini-3.8-flash-low"},
    )
    # Record 3: Failed
    rec3 = ExecutionRecord(
        execution_id="exec-fail-3",
        task_id="TASK-T18-3",
        overall_status="FAILED",
        task_title="Failed Task",
        total_tokens=800,
        metadata={"runtime_id": "openai-mock", "model": "gpt-5-mock"},
        error_message="Verification check timed out",
    )
    # Record 4: Active
    rec4 = ExecutionRecord(
        execution_id="exec-act-4",
        task_id="TASK-T18-4",
        overall_status="ACTIVE",
        task_title="Active Task",
        total_tokens=300,
    )

    store.create_execution(rec1)
    store.create_execution(rec2)
    store.create_execution(rec3)
    store.create_execution(rec4)

    # 1. Query all
    res_all = client.get("/api/executions")
    assert res_all.status_code == 200
    data_all = res_all.json()
    assert "counts" in data_all
    assert data_all["counts"]["all"] >= 4
    assert data_all["counts"]["needs_signoff"] >= 1
    assert data_all["counts"]["completed"] >= 1
    assert data_all["counts"]["failed"] >= 1
    assert data_all["counts"]["active"] >= 1
    assert data_all["has_awaiting_signoff"] is True
    assert "exec-signoff-1" in data_all["awaiting_signoff_ids"]

    # 2. Filter: needs_signoff
    res_signoff = client.get("/api/executions?status=needs_signoff")
    assert res_signoff.status_code == 200
    items_signoff = res_signoff.json()["executions"]
    assert any(i["execution_id"] == "exec-signoff-1" for i in items_signoff)
    assert all(i["overall_status"] == "AWAITING_HUMAN_SIGNOFF" for i in items_signoff)

    # 3. Filter: completed
    res_comp = client.get("/api/executions?status=completed")
    assert res_comp.status_code == 200
    items_comp = res_comp.json()["executions"]
    assert any(i["execution_id"] == "exec-comp-2" for i in items_comp)
    assert all(i["overall_status"] == "COMPLETED" for i in items_comp)

    # 4. Filter: failed
    res_fail = client.get("/api/executions?status=failed")
    assert res_fail.status_code == 200
    items_fail = res_fail.json()["executions"]
    assert any(i["execution_id"] == "exec-fail-3" for i in items_fail)
    assert all(i["overall_status"] in ["FAILED", "BLOCKED"] for i in items_fail)
    # Check error message is enriched
    failed_item = next(i for i in items_fail if i["execution_id"] == "exec-fail-3")
    assert failed_item["error_message"] == "Verification check timed out"


def test_task_0018_multiple_executions_of_same_task_distinct_with_run_indices(tmp_path):
    """Verifies that multiple executions of the same task remain distinct records and receive run indices."""
    client, _, store, _, _ = _setup_test_env(tmp_path)

    # Two runs of the same task
    rec_run1 = ExecutionRecord(
        execution_id="exec-run-1",
        task_id="TASK-T18-MULTI",
        overall_status="FAILED",
        task_title="Multi-run Feature",
        error_message="First attempt failed",
    )
    rec_run2 = ExecutionRecord(
        execution_id="exec-run-2",
        task_id="TASK-T18-MULTI",
        overall_status="COMPLETED",
        task_title="Multi-run Feature",
    )
    store.create_execution(rec_run1)
    store.create_execution(rec_run2)

    res = client.get("/api/executions?task_id=TASK-T18-MULTI")
    assert res.status_code == 200
    data = res.json()
    items = data["executions"]
    assert len(items) == 2

    # Both executions remain distinct
    ids = {i["execution_id"] for i in items}
    assert ids == {"exec-run-1", "exec-run-2"}

    # Run indices computed accurately: run 1 has run_index=1, run 2 has run_index=2
    item1 = next(i for i in items if i["execution_id"] == "exec-run-1")
    item2 = next(i for i in items if i["execution_id"] == "exec-run-2")
    assert item1["total_runs"] == 2
    assert item2["total_runs"] == 2
    assert item1["run_index"] == 1
    assert item2["run_index"] == 2


def test_task_0018_ui_html_structure_and_controls(tmp_path):
    """Verifies that GET / renders HTML containing history filters, attention banner, and runtime modal."""
    client, _, _, _, _ = _setup_test_env(tmp_path)
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    assert 'id="statusIndicatorBox"' in html
    assert 'id="runtimeSelectedHint"' in html
    assert 'id="attentionBanner"' in html
    assert 'id="historyFilters"' in html
    assert 'data-filter="needs_signoff"' in html
    assert 'id="runtimeStateModal"' in html
    assert 'item-run-badge' in html
    assert 'signoff-pending' in html
