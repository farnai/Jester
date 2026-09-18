"""
Unit and Integration Tests for Persistent Execution History (TASK-0008).

Verifies:
1. Create execution record
2. Retrieve execution record
3. Execution ID uniqueness enforcement
4. Multiple executions associated with the same task ID (task_id != execution_id)
5. Append execution events
6. Retrieve chronological events
7. Event ordering guarantees
8. Duplicate event handling (idempotency)
9. Update execution status
10. Finalize execution record
11. Failure state persistence
12. Blocked state persistence
13. Rework state persistence
14. Token usage persistence (input, output, total)
15. Role, agent, provider, and model metadata persistence
16. Verification result persistence
17. Review result persistence
18. Human signoff persistence
19. Git commit result persistence
20. Git push result persistence
21. Bounded metadata enforcement
22. Bounded summaries enforcement
23. Secret and credential exclusion
24. Persistence failure handling
25. Isolated test database verification
26. Multiple executions for same task retrieval
27. Recent executions retrieval
28. Complete execution history audit reconstruction
29. End-to-end controlled workflow integration with execution history
"""
from datetime import datetime, timezone
from pathlib import Path
import pytest

from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig
from jester_bridge.contracts import InvocationResult, InvocationStatus, UsageMetrics
from jester_bridge.core import BridgeCore
from jester_bridge.execution_history import (
    ExecutionEvent,
    ExecutionHistoryError,
    ExecutionHistoryStore,
    ExecutionRecord,
    sanitize_bounded_text,
    sanitize_metadata,
)
from jester_bridge.git_controller import CommitAuthorization, GitController
from jester_bridge.orchestration import (
    BridgeOrchestrator,
    OrchestrationStage,
    ReviewResult,
    ReviewVerdict,
)
from jester_bridge.preflight import PreflightValidator
from jester_bridge.protocol import Task
from jester_bridge.runtime import BoundedWorkspaceRuntime
from jester_bridge.testing import MockProviderA, MockProviderB
from jester_bridge.workflow import ControlledWorkflowRunner


@pytest.fixture
def history_store(tmp_path: Path) -> ExecutionHistoryStore:
    """Provides an isolated, temporary SQLite execution history store."""
    db_file = tmp_path / "test_history.db"
    return ExecutionHistoryStore(db_path=db_file)


# -------------------------------------------------------------------
# TEST 1 — Create execution record
# -------------------------------------------------------------------
def test_01_create_execution(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(
        execution_id="exec-001",
        task_id="TASK-TEST-01",
        task_title="Test Task Title",
        overall_status="running",
        current_stage="preflight",
    )
    assert history_store.create_execution(rec) is True


# -------------------------------------------------------------------
# TEST 2 — Retrieve execution record
# -------------------------------------------------------------------
def test_02_retrieve_execution(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(
        execution_id="exec-002",
        task_id="TASK-TEST-02",
        task_title="Retrieve Me",
        overall_status="running",
    )
    history_store.create_execution(rec)
    fetched = history_store.get_execution("exec-002")
    assert fetched is not None
    assert fetched.execution_id == "exec-002"
    assert fetched.task_id == "TASK-TEST-02"
    assert fetched.task_title == "Retrieve Me"
    assert fetched.overall_status == "running"


# -------------------------------------------------------------------
# TEST 3 — Execution ID uniqueness enforcement
# -------------------------------------------------------------------
def test_03_execution_id_uniqueness(history_store: ExecutionHistoryStore):
    rec1 = ExecutionRecord(execution_id="exec-unique", task_id="TASK-01", overall_status="running")
    rec2 = ExecutionRecord(execution_id="exec-unique", task_id="TASK-02", overall_status="running")
    history_store.create_execution(rec1)
    with pytest.raises(ExecutionHistoryError, match="already exists"):
        history_store.create_execution(rec2)


# -------------------------------------------------------------------
# TEST 4 — Multiple executions for same task (task_id != execution_id)
# -------------------------------------------------------------------
def test_04_multiple_executions_per_task(history_store: ExecutionHistoryStore):
    task_id = "TASK-MULTI-EXEC"
    rec_a = ExecutionRecord(execution_id="exec-run-1", task_id=task_id, overall_status="failed")
    rec_b = ExecutionRecord(execution_id="exec-run-2", task_id=task_id, overall_status="completed")
    history_store.create_execution(rec_a)
    history_store.create_execution(rec_b)

    task_executions = history_store.get_executions_for_task(task_id)
    assert len(task_executions) == 2
    ids = {e.execution_id for e in task_executions}
    assert ids == {"exec-run-1", "exec-run-2"}


# -------------------------------------------------------------------
# TEST 5 — Append execution event
# -------------------------------------------------------------------
def test_05_append_event(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-evt-test", task_id="TASK-05", overall_status="running")
    history_store.create_execution(rec)

    evt = ExecutionEvent(
        event_id="evt-101",
        execution_id="exec-evt-test",
        event_type="architect_started",
        stage="architect",
        status="running",
        summary="Architect stage invoked",
    )
    assert history_store.record_event(evt) is True


# -------------------------------------------------------------------
# TEST 6 & 7 — Retrieve chronological events and ordering
# -------------------------------------------------------------------
def test_06_07_chronological_events_and_ordering(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-ordered", task_id="TASK-ORDER", overall_status="running")
    history_store.create_execution(rec)

    evt1 = ExecutionEvent(
        event_id="evt-1",
        execution_id="exec-ordered",
        event_type="execution_created",
        timestamp="2026-09-18T10:00:00Z",
        summary="First event",
    )
    evt2 = ExecutionEvent(
        event_id="evt-2",
        execution_id="exec-ordered",
        event_type="architect_started",
        timestamp="2026-09-18T10:01:00Z",
        summary="Second event",
    )
    evt3 = ExecutionEvent(
        event_id="evt-3",
        execution_id="exec-ordered",
        event_type="executor_completed",
        timestamp="2026-09-18T10:02:00Z",
        summary="Third event",
    )

    history_store.record_event(evt1)
    history_store.record_event(evt2)
    history_store.record_event(evt3)

    events = history_store.get_events_for_execution("exec-ordered")
    assert len(events) == 3
    assert [e.event_id for e in events] == ["evt-1", "evt-2", "evt-3"]
    assert [e.event_type for e in events] == ["execution_created", "architect_started", "executor_completed"]


# -------------------------------------------------------------------
# TEST 8 — Duplicate event handling (idempotency)
# -------------------------------------------------------------------
def test_08_duplicate_event_handling(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-dup", task_id="TASK-DUP", overall_status="running")
    history_store.create_execution(rec)

    evt = ExecutionEvent(
        event_id="evt-same",
        execution_id="exec-dup",
        event_type="ping",
        summary="Ping",
    )
    assert history_store.record_event(evt) is True
    # Re-recording identical event_id is safely ignored without raising or duplicating
    assert history_store.record_event(evt) is True

    events = history_store.get_events_for_execution("exec-dup")
    assert len(events) == 1


# -------------------------------------------------------------------
# TEST 9 — Update execution status
# -------------------------------------------------------------------
def test_09_update_execution_status(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-update", task_id="TASK-UP", overall_status="running")
    history_store.create_execution(rec)

    rec.overall_status = "awaiting_human_signoff"
    rec.current_stage = "awaiting_human_signoff"
    rec.final_summary = "Ready for human review"
    assert history_store.update_execution(rec) is True

    fetched = history_store.get_execution("exec-update")
    assert fetched.overall_status == "awaiting_human_signoff"
    assert fetched.current_stage == "awaiting_human_signoff"
    assert fetched.final_summary == "Ready for human review"


# -------------------------------------------------------------------
# TEST 10 — Finalize execution
# -------------------------------------------------------------------
def test_10_finalize_execution(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-fin", task_id="TASK-FIN", overall_status="running")
    history_store.create_execution(rec)

    rec.overall_status = "completed"
    rec.current_stage = "completed"
    rec.completed_at = datetime.now(timezone.utc).isoformat()
    rec.final_summary = "Task completed successfully."
    history_store.update_execution(rec)

    fetched = history_store.get_execution("exec-fin")
    assert fetched.overall_status == "completed"
    assert fetched.completed_at is not None


# -------------------------------------------------------------------
# TEST 11 — Failure state persistence
# -------------------------------------------------------------------
def test_11_failure_state_persistence(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-fail", task_id="TASK-FAIL", overall_status="running")
    history_store.create_execution(rec)

    rec.overall_status = "failed"
    rec.current_stage = "executor"
    rec.error_message = "Syntax error in generated code."
    history_store.update_execution(rec)

    fetched = history_store.get_execution("exec-fail")
    assert fetched.overall_status == "failed"
    assert "Syntax error" in (fetched.error_message or "")


# -------------------------------------------------------------------
# TEST 12 — Blocked state persistence
# -------------------------------------------------------------------
def test_12_blocked_state_persistence(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-block", task_id="TASK-BLOCK", overall_status="running")
    history_store.create_execution(rec)

    rec.overall_status = "blocked"
    rec.current_stage = "verification"
    rec.error_message = "Verification tests failed; changes rolled back."
    history_store.update_execution(rec)

    fetched = history_store.get_execution("exec-block")
    assert fetched.overall_status == "blocked"
    assert "Verification tests failed" in (fetched.error_message or "")


# -------------------------------------------------------------------
# TEST 13 — Rework state persistence
# -------------------------------------------------------------------
def test_13_rework_state_persistence(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-rework", task_id="TASK-REWORK", overall_status="running")
    history_store.create_execution(rec)

    rec.overall_status = "rework_required"
    rec.current_stage = "reviewer"
    rec.reviewer_verdict = "REWORK_REQUIRED"
    rec.reviewer_summary = "Please fix docstring formatting."
    history_store.update_execution(rec)

    fetched = history_store.get_execution("exec-rework")
    assert fetched.overall_status == "rework_required"
    assert fetched.reviewer_verdict == "REWORK_REQUIRED"
    assert fetched.reviewer_summary == "Please fix docstring formatting."


# -------------------------------------------------------------------
# TEST 14 — Token usage persistence
# -------------------------------------------------------------------
def test_14_token_usage_persistence(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(
        execution_id="exec-tokens",
        task_id="TASK-TOKENS",
        overall_status="running",
        total_input_tokens=450,
        total_output_tokens=150,
        total_tokens=600,
    )
    history_store.create_execution(rec)

    evt = ExecutionEvent(
        execution_id="exec-tokens",
        event_type="executor_completed",
        stage="executor",
        input_tokens=300,
        output_tokens=100,
        total_tokens=400,
    )
    history_store.record_event(evt)

    fetched = history_store.get_execution("exec-tokens")
    assert fetched.total_input_tokens == 450
    assert fetched.total_output_tokens == 150
    assert fetched.total_tokens == 600

    events = history_store.get_events_for_execution("exec-tokens")
    assert events[0].input_tokens == 300
    assert events[0].output_tokens == 100
    assert events[0].total_tokens == 400


# -------------------------------------------------------------------
# TEST 15 — Provider/model metadata persistence
# -------------------------------------------------------------------
def test_15_provider_model_metadata_persistence(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-meta", task_id="TASK-META", overall_status="running")
    history_store.create_execution(rec)

    evt = ExecutionEvent(
        execution_id="exec-meta",
        event_type="executor_completed",
        stage="executor",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        model="gemini-2.0-flash",
    )
    history_store.record_event(evt)

    events = history_store.get_events_for_execution("exec-meta")
    assert events[0].role == "executor"
    assert events[0].agent_id == "gemini-dev"
    assert events[0].provider == "google"
    assert events[0].model == "gemini-2.0-flash"


# -------------------------------------------------------------------
# TEST 16 — Verification result persistence
# -------------------------------------------------------------------
def test_16_verification_result_persistence(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(
        execution_id="exec-verif",
        task_id="TASK-VERIF",
        overall_status="running",
        verification_passed=True,
        verification_summary="All 10 tests passed in 0.45s",
    )
    history_store.create_execution(rec)

    fetched = history_store.get_execution("exec-verif")
    assert fetched.verification_passed is True
    assert fetched.verification_summary == "All 10 tests passed in 0.45s"


# -------------------------------------------------------------------
# TEST 17 — Review result persistence
# -------------------------------------------------------------------
def test_17_review_result_persistence(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(
        execution_id="exec-rev",
        task_id="TASK-REV",
        overall_status="running",
        reviewer_verdict="PASS",
        reviewer_summary="Independent diff review verified against acceptance criteria.",
    )
    history_store.create_execution(rec)

    fetched = history_store.get_execution("exec-rev")
    assert fetched.reviewer_verdict == "PASS"
    assert "Independent diff review" in (fetched.reviewer_summary or "")


# -------------------------------------------------------------------
# TEST 18 — Human signoff persistence
# -------------------------------------------------------------------
def test_18_human_signoff_persistence(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-signoff", task_id="TASK-SIGN", overall_status="running")
    history_store.create_execution(rec)

    rec.human_signoff_by = "founder-operator"
    rec.human_signoff_notes = "Explicitly approved after unified diff verification."
    history_store.update_execution(rec)

    fetched = history_store.get_execution("exec-signoff")
    assert fetched.human_signoff_by == "founder-operator"
    assert "Explicitly approved" in (fetched.human_signoff_notes or "")


# -------------------------------------------------------------------
# TEST 19 — Git commit result persistence
# -------------------------------------------------------------------
def test_19_git_commit_result_persistence(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-commit", task_id="TASK-GIT", overall_status="running")
    history_store.create_execution(rec)

    rec.git_commit_hash = "a1b2c3d4e5f6"
    rec.git_branch = "feature/history"
    rec.git_delivery_summary = "Committed 2 approved files."
    history_store.update_execution(rec)

    fetched = history_store.get_execution("exec-commit")
    assert fetched.git_commit_hash == "a1b2c3d4e5f6"
    assert fetched.git_branch == "feature/history"


# -------------------------------------------------------------------
# TEST 20 — Git push result persistence
# -------------------------------------------------------------------
def test_20_git_push_result_persistence(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(execution_id="exec-push", task_id="TASK-PUSH", overall_status="running")
    history_store.create_execution(rec)

    rec.git_pushed = True
    history_store.update_execution(rec)

    fetched = history_store.get_execution("exec-push")
    assert fetched.git_pushed is True


# -------------------------------------------------------------------
# TEST 21 & 22 — Bounded metadata and summaries
# -------------------------------------------------------------------
def test_21_22_bounded_metadata_and_summaries(history_store: ExecutionHistoryStore):
    huge_summary = "A" * 5000
    huge_error = "E" * 5000

    rec = ExecutionRecord(
        execution_id="exec-bounded",
        task_id="TASK-BOUND",
        overall_status="running",
        final_summary=huge_summary,
        error_message=huge_error,
        metadata={"key": "V" * 5000},
    )
    history_store.create_execution(rec)

    fetched = history_store.get_execution("exec-bounded")
    assert len(fetched.final_summary) < 1100
    assert "[TRUNCATED]" in fetched.final_summary
    assert len(fetched.error_message) < 1100
    assert "[TRUNCATED]" in fetched.error_message


# -------------------------------------------------------------------
# TEST 23 — Secret and credential exclusion
# -------------------------------------------------------------------
def test_23_secret_exclusion(history_store: ExecutionHistoryStore):
    meta_with_secrets = {
        "api_key": "sk-secret-key-12345",
        "authorization": "Bearer eyJhbGciOi...",
        "db_password": "supersecretpassword",
        "safe_key": "ordinary_value",
    }
    cleaned = sanitize_metadata(meta_with_secrets)
    assert cleaned["api_key"] == "[REDACTED_SECRET]"
    assert cleaned["authorization"] == "[REDACTED_SECRET]"
    assert cleaned["db_password"] == "[REDACTED_SECRET]"
    assert cleaned["safe_key"] == "ordinary_value"

    rec = ExecutionRecord(
        execution_id="exec-secret-test",
        task_id="TASK-SEC",
        overall_status="running",
        metadata=meta_with_secrets,
    )
    history_store.create_execution(rec)

    fetched = history_store.get_execution("exec-secret-test")
    assert fetched.metadata["api_key"] == "[REDACTED_SECRET]"
    assert fetched.metadata["authorization"] == "[REDACTED_SECRET]"
    assert fetched.metadata["db_password"] == "[REDACTED_SECRET]"


# -------------------------------------------------------------------
# TEST 24 — Persistence failure handling
# -------------------------------------------------------------------
def test_24_persistence_failure_handling(tmp_path: Path):
    # Case A: Store raises ExecutionHistoryError when database path is invalid
    invalid_dir = tmp_path / "as_dir"
    invalid_dir.mkdir()
    with pytest.raises(ExecutionHistoryError, match="Failed to connect"):
        ExecutionHistoryStore(db_path=invalid_dir)

    # Case B: ControlledWorkflowRunner catches persistence error without aborting business workflow
    valid_db = tmp_path / "good.db"
    store = ExecutionHistoryStore(db_path=valid_db)
    # Simulate a failing history store
    def raise_err(*args, **kwargs):
        raise RuntimeError("Disk full")

    store.create_execution = raise_err

    config = BridgeConfig(
        role_bindings={"architect": "lead"},
        agents={"lead": AgentProfile(id="lead", role="architect", provider="mock", capabilities={"planning"})},
    )
    core = BridgeCore(config=config, providers={"mock": MockProviderA(provider_id="mock")})
    runner = ControlledWorkflowRunner(core=core, repo_root=tmp_path, history_store=store)

    rec = ExecutionRecord(execution_id="exec-err", task_id="T1", overall_status="running")
    assert runner._create_execution_safe(rec) is False
    assert "Disk full" in (runner.last_persistence_error or "")



# -------------------------------------------------------------------
# TEST 25 — Isolated test database verification
# -------------------------------------------------------------------
def test_25_isolated_test_database(tmp_path: Path):
    db_a = tmp_path / "db_a.db"
    db_b = tmp_path / "db_b.db"

    store_a = ExecutionHistoryStore(db_path=db_a)
    store_b = ExecutionHistoryStore(db_path=db_b)

    rec_a = ExecutionRecord(execution_id="exec-in-a", task_id="TASK-A", overall_status="running")
    store_a.create_execution(rec_a)

    assert store_a.get_execution("exec-in-a") is not None
    assert store_b.get_execution("exec-in-a") is None


# -------------------------------------------------------------------
# TEST 26 — Multiple executions for same task retrieval
# -------------------------------------------------------------------
def test_26_multiple_executions_retrieval(history_store: ExecutionHistoryStore):
    task_id = "TASK-MULTI"
    history_store.create_execution(ExecutionRecord(execution_id="exec-1", task_id=task_id, overall_status="failed"))
    history_store.create_execution(ExecutionRecord(execution_id="exec-2", task_id=task_id, overall_status="rework_required"))
    history_store.create_execution(ExecutionRecord(execution_id="exec-3", task_id=task_id, overall_status="completed"))

    execs = history_store.get_executions_for_task(task_id)
    assert len(execs) == 3
    statuses = [e.overall_status for e in execs]
    assert "failed" in statuses
    assert "rework_required" in statuses
    assert "completed" in statuses


# -------------------------------------------------------------------
# TEST 27 — Recent executions retrieval
# -------------------------------------------------------------------
def test_27_recent_executions_retrieval(history_store: ExecutionHistoryStore):
    for i in range(10):
        history_store.create_execution(
            ExecutionRecord(execution_id=f"exec-recent-{i}", task_id=f"TASK-{i}", overall_status="running")
        )

    recent_5 = history_store.list_recent_executions(limit=5)
    assert len(recent_5) == 5


# -------------------------------------------------------------------
# TEST 28 — Complete execution history reconstruction
# -------------------------------------------------------------------
def test_28_execution_history_reconstruction(history_store: ExecutionHistoryStore):
    rec = ExecutionRecord(
        execution_id="exec-recon",
        task_id="TASK-RECON",
        task_title="Reconstruction Proof",
        overall_status="completed",
        total_input_tokens=500,
        total_output_tokens=200,
        total_tokens=700,
        verification_passed=True,
        verification_summary="Tests passing",
        reviewer_verdict="PASS",
        reviewer_summary="Approved",
        human_signoff_by="founder",
        human_signoff_notes="Good to ship",
        git_commit_hash="c0ffee1234",
        git_branch="main",
        git_pushed=False,
    )
    history_store.create_execution(rec)

    for stage_name in ["architect", "executor", "verification", "reviewer", "human_signoff"]:
        history_store.record_event(
            ExecutionEvent(
                execution_id="exec-recon",
                event_type=f"{stage_name}_completed",
                stage=stage_name,
                status="success",
            )
        )

    summary = history_store.get_execution_summary("exec-recon")
    assert summary is not None
    assert summary["execution_id"] == "exec-recon"
    assert summary["task_id"] == "TASK-RECON"
    assert summary["overall_status"] == "completed"
    assert summary["token_usage"]["total_tokens"] == 700
    assert summary["verification"]["passed"] is True
    assert summary["review"]["verdict"] == "PASS"
    assert summary["human_signoff"]["approver"] == "founder"
    assert summary["git_delivery"]["commit_hash"] == "c0ffee1234"
    assert summary["event_count"] == 5
    assert len(summary["stages_executed"]) == 5


# -------------------------------------------------------------------
# TEST 29 — End-to-end workflow integration with history store
# -------------------------------------------------------------------
def test_29_workflow_integration_with_history(tmp_path: Path):
    db_file = tmp_path / "workflow_history.db"
    store = ExecutionHistoryStore(db_path=db_file)

    mock_arch_resp = "Title: History Utility\nScope: src/util.py\n"
    mock_exec_resp = "```python:src/util.py\ndef ping(): return 'pong'\n```\n"
    mock_rev_resp = "Review verdict: PASS. Verified."

    prov_arch = MockProviderA(provider_id="openai", default_summary=mock_arch_resp)
    prov_exec = MockProviderB(provider_id="google", default_summary=mock_exec_resp)

    config = BridgeConfig(
        role_bindings={"architect": "chatgpt-lead", "executor": "gemini-dev", "reviewer": "chatgpt-critic"},
        agents={
            "chatgpt-lead": AgentProfile(id="chatgpt-lead", role="architect", provider="openai", capabilities={"planning", "reasoning", "repository_read"}),
            "gemini-dev": AgentProfile(id="gemini-dev", role="executor", provider="google", capabilities={"planning", "reasoning", "code_generation", "repository_read"}),
            "chatgpt-critic": AgentProfile(id="chatgpt-critic", role="reviewer", provider="openai", capabilities={"reasoning", "repository_read", "review"}),
        },
    )
    core = BridgeCore(config=config, providers={"openai": prov_arch, "google": prov_exec})
    runtime = BoundedWorkspaceRuntime(repo_root=tmp_path)
    git_controller = GitController(repo_root=tmp_path)

    runner = ControlledWorkflowRunner(
        core=core,
        repo_root=tmp_path,
        runtime=runtime,
        git_controller=git_controller,
        history_store=store,
    )

    # 1. Run workflow -> stops at AWAITING_HUMAN_SIGNOFF
    outcome = runner.run_e2e_workflow(
        intent="Create ping utility",
        target_task_id="TASK-HIST-E2E",
        scope=["src/util.py"],
        verification=["python -c \"import sys; sys.exit(0)\""],
        auto_apply=True,
        check_credentials=False,
    )
    assert outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert outcome.execution_id is not None
    assert outcome.persistence_error is None

    # 2. Assert execution record was persisted in database
    persisted_rec = store.get_execution(outcome.execution_id)
    assert persisted_rec is not None
    assert persisted_rec.task_id == "TASK-HIST-E2E"
    assert persisted_rec.overall_status == OrchestrationStage.AWAITING_HUMAN_SIGNOFF.value
    assert persisted_rec.reviewer_verdict == "PASS"
    assert persisted_rec.total_tokens is not None
    assert persisted_rec.total_tokens > 0

    # 3. Assert events were recorded chronologically
    events = store.get_events_for_execution(outcome.execution_id)
    assert len(events) >= 6
    event_types = [e.event_type for e in events]
    assert "execution_created" in event_types
    assert "preflight_completed" in event_types
    assert "architect_completed" in event_types
    assert "task_activated" in event_types
    assert "executor_completed" in event_types
    assert "verification_completed" in event_types
    assert "review_completed" in event_types
    assert "awaiting_human_signoff" in event_types

    # 4. Execute human signoff
    completed_task_path = runner.complete_human_approval(
        session=outcome.session,
        approver="lead-founder",
        notes="Approved for merge.",
    )
    assert completed_task_path.exists()

    # 5. Assert final status updated in history store
    final_rec = store.get_execution(outcome.execution_id)
    assert final_rec.overall_status == OrchestrationStage.COMPLETED.value
    assert final_rec.current_stage == OrchestrationStage.COMPLETED.value
    assert final_rec.human_signoff_by == "lead-founder"
    assert final_rec.human_signoff_notes == "Approved for merge."


    # Assert human_approved and execution_completed events recorded
    updated_events = store.get_events_for_execution(outcome.execution_id)
    updated_types = [e.event_type for e in updated_events]
    assert "human_approved" in updated_types
    assert "execution_completed" in updated_types
