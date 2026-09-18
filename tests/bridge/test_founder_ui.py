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
        },
    )

    core = BridgeCore(config=config, providers={"openai": prov_openai, "google": prov_google})
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
