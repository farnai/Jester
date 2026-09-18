"""
Comprehensive test suite for Context Lifecycle, Snapshots, Lineage, Rework, and Multi-Turn Continuity (TASK-0010).

Covers:
1. Context snapshot creation & identity
2. Context ID uniqueness
3. Execution ID association
4. task_id vs execution_id distinction
5. Stage association
6. parent_context_id lineage tracking
7. Deterministic context lineage
8. Static vs dynamic context formatting
9. Current vs historical context distinction
10. Freshness metadata (SHA-256 hash, mtime)
11. Stale context detection via check_context_freshness
12. Context reassembly producing independent new snapshots
13. Immutability of previous snapshots
14. Rework context assembly
15. Previous reviewer feedback inclusion
16. Previous diff inclusion
17. Current diff inclusion
18. Current repository state precedence over historical
19. Current verification precedence over historical
20. Bounded historical context
21. Historical context budget enforcement
22. Overall context budget enforcement
23. Provenance preservation for historical and current items
24. Protected path handling
25. Secret exclusion & sanitization in historical context
26. Execution history metadata persistence (no raw code dumps)
27. History retrieval for rework
28. Multiple executions for same task
29. Context lineage serialization
30. Handoff -> Context reference integrity

Integration Cases:
- CASE A: Normal execution (Architect Context -> Handoff -> Executor Context -> Handoff -> Reviewer Context)
- CASE B: Rework cycle (Executor -> Diff -> Reviewer REWORK -> Rework Context -> Executor -> New Diff -> Reviewer)
- CASE C: Fresh repository context (File updated on disk, subsequent stage receives updated disk content)
- CASE D: Historical context explicitly classified as non-authoritative explanation
- CASE E: Current evidence precedence (Previous verification PASS vs Current verification FAIL)
- CASE F: Context budget bounding on large historical diff / feedback
- CASE G: Secret sanitization in historical context payloads
- CASE H: Write isolation (Read context != write authority)
- CASE I: Execution isolation (Multiple executions for same task maintain independent lineage)
"""
from pathlib import Path
import pytest

from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig
from jester_bridge.context import (
    ContextEngine,
    ContextPackage,
    ContextPriority,
    ContextSnapshot,
    FileContext,
    SourceType,
    sanitize_context_text,
)
from jester_bridge.contracts import (
    ArchitectHandoff,
    ExecutorHandoff,
    InvocationResult,
    InvocationStatus,
    ReviewerHandoff,
    UsageMetrics,
)
from jester_bridge.core import BridgeCore
from jester_bridge.execution_history import ExecutionHistoryStore, ExecutionRecord
from jester_bridge.orchestration import (
    ArchitectInput,
    BridgeOrchestrator,
    ExecutorResult,
    OrchestrationSession,
    OrchestrationStage,
    ReviewVerdict,
)
from jester_bridge.protocol import Task
from jester_bridge.roles import Role
from jester_bridge.runtime import BoundedWorkspaceRuntime, FileChange, ScopeViolationError
from jester_bridge.testing import MockProviderA, MockProviderB
from jester_bridge.workflow import ControlledWorkflowRunner


# ---------------------------------------------------------------------------
# Unit Tests (1 - 30)
# ---------------------------------------------------------------------------

def test_01_context_snapshot_creation(tmp_path: Path):
    """1. Context snapshot creation captures metadata and identity."""
    f = tmp_path / "sample.py"
    f.write_text("print('hello')", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-01", title="Task 01", goal="Test snapshot", scope=["sample.py"])

    pkg = engine.assemble_context(
        task=task,
        role="executor",
        stage="active",
        execution_id="exec-101",
        parent_context_id="ctx-000",
    )
    snapshot = pkg.to_snapshot()

    assert isinstance(snapshot, ContextSnapshot)
    assert snapshot.context_id == pkg.context_id
    assert snapshot.parent_context_id == "ctx-000"
    assert snapshot.execution_id == "exec-101"
    assert snapshot.task_id == "TASK-01"
    assert snapshot.role == "executor"
    assert snapshot.stage == "active"
    assert snapshot.selected_file_count == 1
    assert "sample.py" in snapshot.file_freshness_hashes


def test_02_context_id_uniqueness(tmp_path: Path):
    """2. Multiple context assemblies generate distinct, unique context_ids."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-02", title="Task 02", goal="Unique IDs", scope=[])

    pkg1 = engine.assemble_context(task, role="architect", stage="architect")
    pkg2 = engine.assemble_context(task, role="executor", stage="executor")
    pkg3 = engine.assemble_context(task, role="reviewer", stage="reviewer")

    ids = {pkg1.context_id, pkg2.context_id, pkg3.context_id}
    assert len(ids) == 3
    for cid in ids:
        assert cid.startswith("ctx-")


def test_03_execution_id_association(tmp_path: Path):
    """3. Context packages explicitly record and associate execution_id."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-03", title="Task 03", goal="Exec association", scope=[])

    pkg = engine.assemble_context(task, execution_id="exec-custom-99")
    assert pkg.execution_id == "exec-custom-99"
    assert pkg.to_snapshot().execution_id == "exec-custom-99"


def test_04_task_id_vs_execution_id_distinction(tmp_path: Path):
    """4. task_id and execution_id are strictly distinct."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-BIZ-42", title="Biz Task", goal="Distinct IDs", scope=[])

    pkg = engine.assemble_context(task, execution_id="exec-run-007")
    assert pkg.task_id == "TASK-BIZ-42"
    assert pkg.execution_id == "exec-run-007"
    assert pkg.task_id != pkg.execution_id


def test_05_stage_association(tmp_path: Path):
    """5. Context identifies the exact stage for which it was assembled."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-05", title="Task 05", goal="Stage test", scope=[])

    pkg_arch = engine.assemble_context(task, role="architect", stage="architect")
    pkg_rework = engine.assemble_context(task, role="executor", stage="rework_executor")

    assert pkg_arch.stage == "architect"
    assert pkg_rework.stage == "rework_executor"


def test_06_parent_context_id_lineage(tmp_path: Path):
    """6. parent_context_id links context snapshots into a lineage chain."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-06", title="Task 06", goal="Lineage test", scope=[])

    pkg1 = engine.assemble_context(task, role="architect", stage="architect")
    pkg2 = engine.assemble_context(
        task,
        role="executor",
        stage="active",
        parent_context_id=pkg1.context_id,
    )

    assert pkg2.parent_context_id == pkg1.context_id
    assert pkg2.to_snapshot().parent_context_id == pkg1.context_id


def test_07_deterministic_context_lineage(tmp_path: Path):
    """7. Deterministic context lineage across multiple transitions."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-07", title="Task 07", goal="Chain test", scope=[])

    c1 = engine.assemble_context(task, role="architect", stage="architect")
    c2 = engine.assemble_context(task, role="executor", stage="active", parent_context_id=c1.context_id)
    c3 = engine.assemble_context(task, role="reviewer", stage="review", parent_context_id=c2.context_id)
    c4 = engine.assemble_context(task, role="executor", stage="rework_executor", parent_context_id=c3.context_id)

    assert c2.parent_context_id == c1.context_id
    assert c3.parent_context_id == c2.context_id
    assert c4.parent_context_id == c3.context_id


def test_08_static_vs_dynamic_context_distinction(tmp_path: Path):
    """8. Static task context and dynamic workspace files are separated in prompt format."""
    f = tmp_path / "code.py"
    f.write_text("x = 10\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="TASK-08",
        title="Sum Calculator",
        goal="Calculate sum",
        scope=["code.py"],
        constraints=["No imports"],
        acceptance_criteria=["x equals 10"],
    )

    pkg = engine.assemble_context(
        task,
        architect_intent="Use functional decomposition",
        rework_objective="Ensure clean formatting",
    )
    formatted = pkg.format_for_prompt()

    assert "## Architect Intent:" in formatted
    assert "Use functional decomposition" in formatted
    assert "### Rework Objective:" in formatted
    assert "## In-Scope Repository Files Context" in formatted
    assert "code.py" in formatted


def test_09_current_vs_historical_context_distinction(tmp_path: Path):
    """9. Historical explanation is explicitly labeled and separated from current diff."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-09", title="Diff Separation", goal="Diff separation", scope=[])

    pkg = engine.assemble_context(
        task,
        diff="--- current diff\n+++ current diff\n+new_val = True\n",
        previous_diff="--- old diff\n+++ old diff\n+old_bug = False\n",
        reviewer_feedback="Bug in old_val",
    )
    formatted = pkg.format_for_prompt()

    assert "Historical Rework Context" in formatted
    assert "Previous Code Diff (Rejected Iteration)" in formatted
    assert "old_bug = False" in formatted
    assert "## Code Diff Evidence" in formatted
    assert "new_val = True" in formatted


def test_10_freshness_metadata(tmp_path: Path):
    """10. FileContext captures SHA-256 freshness_hash and file_mtime."""
    f = tmp_path / "module.py"
    f.write_text("def ping(): return 'pong'\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-10", title="Freshness Task", goal="Freshness test", scope=["module.py"])

    pkg = engine.assemble_context(task)
    fc = pkg.files[0]

    assert fc.freshness_hash is not None
    assert len(fc.freshness_hash) == 64  # SHA-256 hex string
    assert fc.file_mtime is not None
    assert fc.file_mtime > 0


def test_11_stale_context_detection(tmp_path: Path):
    """11. check_context_freshness detects when repository files change after context assembly."""
    f = tmp_path / "module.py"
    f.write_text("version 1", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-11", title="Stale Task", goal="Stale test", scope=["module.py"])

    pkg = engine.assemble_context(task)
    is_fresh, stale = engine.check_context_freshness(pkg)
    assert is_fresh is True
    assert len(stale) == 0

    # Modify file on disk
    f.write_text("version 2 (modified)", encoding="utf-8")

    is_fresh_after, stale_after = engine.check_context_freshness(pkg)
    assert is_fresh_after is False
    assert "module.py" in stale_after


def test_12_context_reassembly(tmp_path: Path):
    """12. Context reassembly creates a new independent package rather than mutating the old one."""
    f = tmp_path / "state.py"
    f.write_text("initial", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-12", title="Reassembly Task", goal="Reassembly", scope=["state.py"])

    pkg_v1 = engine.assemble_context(task, role="executor", stage="executor")
    f.write_text("updated", encoding="utf-8")

    pkg_v2 = engine.assemble_context(
        task,
        role="reviewer",
        stage="reviewer",
        parent_context_id=pkg_v1.context_id,
    )

    # v1 remains unchanged
    assert pkg_v1.files[0].content == "initial"
    assert pkg_v1.stage == "executor"

    # v2 reflects new state
    assert pkg_v2.files[0].content == "updated"
    assert pkg_v2.stage == "reviewer"
    assert pkg_v2.parent_context_id == pkg_v1.context_id
    assert pkg_v2.context_id != pkg_v1.context_id


def test_13_immutability_of_previous_snapshot(tmp_path: Path):
    """13. ContextSnapshot is an immutable record that cannot accidentally mutate."""
    f = tmp_path / "file.py"
    f.write_text("content", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-13", title="Immutable Task", goal="Immutable test", scope=["file.py"])

    pkg = engine.assemble_context(task)
    snap = pkg.to_snapshot()

    # Modifying pkg files does not affect the snapshot
    pkg.included_paths.append("another.py")
    assert "another.py" not in snap.included_paths
    assert snap.selected_file_count == 1


def test_14_rework_context_assembly(tmp_path: Path):
    """14. assemble_rework_context packages all 10 required rework context components."""
    src = tmp_path / "app.py"
    src.write_text("def execute(): return False\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="TASK-14",
        title="App Execution",
        goal="Make execute return True",
        scope=["app.py"],
        acceptance_criteria=["Must return True"],
    )

    pkg = engine.assemble_rework_context(
        task=task,
        execution_id="exec-rework-14",
        parent_context_id="ctx-rev-99",
        reviewer_feedback="Returned False instead of True",
        reviewer_defect_details="AssertionError on line 2",
        previous_diff="--- a\n+++ b\n-False\n+False\n",
        previous_verification_output="1 failed in 0.05s",
        architect_intent="Ensure boolean return type",
        previous_implementation_summary="Tried returning False",
        rework_objective="Fix return statement to return True",
    )

    assert pkg.role == "executor"
    assert pkg.stage == "rework_executor"
    assert pkg.execution_id == "exec-rework-14"
    assert pkg.parent_context_id == "ctx-rev-99"
    assert pkg.reviewer_feedback == "Returned False instead of True"
    assert pkg.reviewer_defect_details == "AssertionError on line 2"
    assert pkg.previous_diff is not None
    assert pkg.previous_verification_output == "1 failed in 0.05s"
    assert pkg.architect_intent == "Ensure boolean return type"
    assert pkg.previous_implementation_summary == "Tried returning False"
    assert pkg.rework_objective == "Fix return statement to return True"
    assert len(pkg.files) == 1
    assert "def execute(): return False" in pkg.files[0].content


def test_15_previous_reviewer_feedback_inclusion(tmp_path: Path):
    """15. Reviewer feedback is recorded in provenance with SourceType.REVIEWER_FEEDBACK."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-15", title="Feedback Prov", goal="Feedback provenance", scope=[])

    pkg = engine.assemble_context(task, reviewer_feedback="Syntax error in line 10")
    prov = [p for p in pkg.provenance_items if p.source_type == SourceType.REVIEWER_FEEDBACK]

    assert len(prov) >= 1
    assert prov[0].source_path == "reviewer_feedback"
    assert prov[0].priority == ContextPriority.CRITICAL


def test_16_previous_diff_inclusion(tmp_path: Path):
    """16. Previous diff is classified with SourceType.HISTORICAL_EXECUTION."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-16", title="Prev Diff", goal="Previous diff test", scope=[])

    diff_text = "--- a/foo.py\n+++ b/foo.py\n@@ -1 +1 @@\n-1\n+2\n"
    pkg = engine.assemble_context(task, previous_diff=diff_text)
    prov = [p for p in pkg.provenance_items if p.source_type == SourceType.HISTORICAL_EXECUTION and p.source_path == "previous_diff"]

    assert len(prov) == 1
    assert pkg.previous_diff == diff_text


def test_17_current_diff_inclusion(tmp_path: Path):
    """17. Current diff is classified with SourceType.DIFF as CRITICAL priority."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-17", title="Current Diff", goal="Current diff test", scope=[])

    diff_text = "--- a/bar.py\n+++ b/bar.py\n@@ -1 +1 @@\n-a\n+b\n"
    pkg = engine.assemble_context(task, diff=diff_text)
    prov = [p for p in pkg.provenance_items if p.source_type == SourceType.DIFF]

    assert len(prov) == 1
    assert prov[0].priority == ContextPriority.CRITICAL
    assert pkg.diff == diff_text


def test_18_current_repository_state_precedence(tmp_path: Path):
    """18. Rework context assembles the CURRENT disk state, never reconstructing from old diff."""
    f = tmp_path / "live_code.py"
    f.write_text("version = 2 # Updated by runtime\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-18", title="Precedence Task", goal="Disk precedence", scope=["live_code.py"])

    pkg = engine.assemble_rework_context(
        task=task,
        execution_id="exec-18",
        parent_context_id="ctx-17",
        reviewer_feedback="Need version 3",
        previous_diff="--- a\n+++ b\n-version = 1\n+version = 2\n",
    )

    # Current disk content is version = 2
    assert "version = 2 # Updated by runtime" in pkg.files[0].content
    # Historical diff describes the change from version 1
    assert "version = 1" in pkg.previous_diff


def test_19_current_verification_precedence(tmp_path: Path):
    """19. Current verification output is current evidence, previous verification is historical."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-19", title="Verification Precedence", goal="Verif precedence", scope=[])

    pkg = engine.assemble_context(
        task,
        verification_output="CURRENT: 5 passed in 0.2s",
        previous_verification_output="HISTORICAL: 1 failed in 0.1s",
    )

    assert pkg.verification_output == "CURRENT: 5 passed in 0.2s"
    assert pkg.previous_verification_output == "HISTORICAL: 1 failed in 0.1s"
    assert "CURRENT: 5 passed in 0.2s" in pkg.format_for_prompt()
    assert "HISTORICAL: 1 failed in 0.1s" in pkg.format_for_prompt()


def test_20_bounded_historical_context(tmp_path: Path):
    """20. Historical items are bounded and recorded in historical_items metadata."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-20", title="Bounding Task", goal="Bounding test", scope=[])

    pkg = engine.assemble_context(
        task,
        reviewer_feedback="Short feedback",
        previous_diff="--- diff\n",
    )

    assert len(pkg.historical_items) == 2
    labels = {item["label"] for item in pkg.historical_items}
    assert "reviewer_feedback" in labels
    assert "previous_diff" in labels


def test_21_historical_context_budget_enforcement(tmp_path: Path):
    """21. Oversized historical diff is truncated to respect configured character budget."""
    engine = ContextEngine(repo_root=tmp_path, max_characters=500)
    task = Task(id="TASK-21", title="Budget Task", goal="Budget test", scope=[])

    huge_diff = "diff --git\n" + ("+line of code added\n" * 50)  # ~1000 chars
    pkg = engine.assemble_context(task, previous_diff=huge_diff)

    assert pkg.total_characters <= 500
    assert pkg.previous_diff_truncated is True
    assert pkg.truncated is True
    assert "[... previous_diff truncated" in pkg.previous_diff


def test_22_context_budget_enforcement(tmp_path: Path):
    """22. Total characters strictly never exceed max_characters across all items."""
    f1 = tmp_path / "file1.txt"
    f2 = tmp_path / "file2.txt"
    f1.write_text("A" * 600, encoding="utf-8")
    f2.write_text("B" * 600, encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path, max_characters=800, max_file_characters=500)
    task = Task(id="TASK-22", title="Total Budget Task", goal="Total budget", scope=["file1.txt", "file2.txt"])

    pkg = engine.assemble_context(
        task,
        reviewer_feedback="Reviewer note " * 10,
    )

    assert pkg.total_characters <= 800
    assert pkg.truncated is True


def test_23_provenance_preservation(tmp_path: Path):
    """23. Every item added to ContextPackage has an exact provenance record."""
    f = tmp_path / "service.py"
    f.write_text("def run(): pass\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-23", title="Prov Audit", goal="Provenance audit", scope=["service.py"])

    pkg = engine.assemble_context(
        task,
        diff="--- diff\n",
        reviewer_feedback="Fix indentation",
    )

    sources = {p.source_type for p in pkg.provenance_items}
    assert SourceType.EXPLICIT_SCOPE in sources
    assert SourceType.DIFF in sources
    assert SourceType.REVIEWER_FEEDBACK in sources


def test_24_protected_path_handling(tmp_path: Path):
    """24. Protected repository paths remain strictly excluded in context assembly."""
    (tmp_path / ".env").write_text("DB_PASSWORD=secret", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("Governance", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-24", title="Protected Test", goal="Security test", scope=[".env", "AGENTS.md"])

    pkg = engine.assemble_context(task)
    assert len(pkg.files) == 0
    assert ".env" in pkg.excluded_paths
    assert "AGENTS.md" in pkg.excluded_paths


def test_25_secret_exclusion_in_historical_context(tmp_path: Path):
    """25. Sensitive tokens in historical context inputs are sanitized before insertion."""
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-25", title="Secret Test", goal="Secret sanitization", scope=[])

    raw_feedback = "The auth header Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 was leaked."
    pkg = engine.assemble_context(task, reviewer_feedback=raw_feedback)

    assert "[REDACTED_SECRET]" in pkg.reviewer_feedback
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in pkg.reviewer_feedback


def test_26_execution_history_metadata_persistence(tmp_path: Path):
    """26. to_summary_dict() provides bounded context metadata for SQLite persistence."""
    f = tmp_path / "code.py"
    f.write_text("x = 1\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-26", title="Persistence Test", goal="Persistence test", scope=["code.py"])

    pkg = engine.assemble_context(
        task,
        execution_id="exec-26",
        parent_context_id="ctx-parent",
        reviewer_feedback="Good progress",
    )
    summary = pkg.to_summary_dict()

    assert summary["context_id"] == pkg.context_id
    assert summary["parent_context_id"] == "ctx-parent"
    assert summary["execution_id"] == "exec-26"
    assert summary["has_rework_context"] is True
    # Invariant: No code bodies in summary
    assert "content" not in summary
    assert "code" not in summary


def test_27_history_retrieval_for_rework(tmp_path: Path):
    """27. ExecutionHistoryStore retrieves rework history accurately."""
    test_db = tmp_path / "test_hist.db"
    store = ExecutionHistoryStore(db_path=test_db)

    rec = ExecutionRecord(
        execution_id="exec-hist-27",
        task_id="TASK-27",
        task_title="Calc Defect",
        overall_status="review_required",
        reviewer_verdict="REWORK_REQUIRED",
        reviewer_summary="Defect in calculator logic",
        verification_passed=False,
        verification_summary="1 failed in 0.1s",
    )
    store.create_execution(rec)

    rework_data = store.get_rework_history("exec-hist-27")
    assert rework_data["execution_id"] == "exec-hist-27"
    assert rework_data["reviewer_verdict"] == "REWORK_REQUIRED"
    assert rework_data["reviewer_feedback"] == "Defect in calculator logic"
    assert rework_data["verification_summary"] == "1 failed in 0.1s"


def test_28_multiple_executions_for_same_task(tmp_path: Path):
    """28. Multiple executions for the same task have distinct IDs and records."""
    test_db = tmp_path / "test_hist2.db"
    store = ExecutionHistoryStore(db_path=test_db)

    rec1 = ExecutionRecord(execution_id="exec-1", task_id="TASK-MULTI", task_title="Multi 1", overall_status="failed")
    rec2 = ExecutionRecord(execution_id="exec-2", task_id="TASK-MULTI", task_title="Multi 2", overall_status="completed")
    store.create_execution(rec1)
    store.create_execution(rec2)

    task_execs = store.get_executions_for_task("TASK-MULTI")
    assert len(task_execs) == 2
    latest = store.get_latest_execution_for_task("TASK-MULTI")
    assert latest is not None
    assert latest.execution_id in ("exec-1", "exec-2")


def test_29_context_lineage_serialization(tmp_path: Path):
    """29. ContextSnapshot models serialize to JSON and reconstruct faithfully."""
    snap = ContextSnapshot(
        context_id="ctx-abc-123",
        parent_context_id="ctx-root-000",
        execution_id="exec-99",
        task_id="TASK-SERIAL",
        role="reviewer",
        stage="review",
        created_at="2026-09-18T00:00:00Z",
        selected_file_count=3,
        excluded_file_count=1,
        total_budget=50000,
        used_budget=1250,
        has_diff=True,
        file_freshness_hashes={"main.py": "abc123hash"},
    )

    dumped = snap.model_dump()
    reconstructed = ContextSnapshot.model_validate(dumped)

    assert reconstructed.context_id == "ctx-abc-123"
    assert reconstructed.parent_context_id == "ctx-root-000"
    assert reconstructed.file_freshness_hashes["main.py"] == "abc123hash"


def test_30_handoff_context_reference_integrity(tmp_path: Path):
    """30. Handoff contracts carry valid context_id and parent_context_id references."""
    arch = ArchitectHandoff(
        task_id="T-30",
        task_objective="Obj",
        implementation_intent="Intent",
        context_id="ctx-arch",
        parent_context_id=None,
    )
    exec_h = ExecutorHandoff(
        task_id="T-30",
        implementation_summary="Summary",
        context_id="ctx-exec",
        parent_context_id="ctx-arch",
    )
    rev = ReviewerHandoff(
        task_id="T-30",
        verdict="PASS",
        summary="Clean",
        context_id="ctx-rev",
        parent_context_id="ctx-exec",
        executor_context_id="ctx-exec",
    )

    assert arch.context_id == "ctx-arch"
    assert exec_h.parent_context_id == "ctx-arch"
    assert rev.executor_context_id == "ctx-exec"
    assert rev.parent_context_id == "ctx-exec"


# ---------------------------------------------------------------------------
# Integration Tests: Cases A - I
# ---------------------------------------------------------------------------

def test_integration_case_a_normal_execution_chain(tmp_path: Path):
    """
    CASE A: Normal Execution
    Task -> Architect Context -> Architect Handoff -> Executor Context -> Executor Handoff -> Reviewer Context
    Verifies that context IDs chain deterministically throughout the workflow.
    """
    f = tmp_path / "components" / "feature.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("def run(): return 42\n", encoding="utf-8")

    mock_arch = "Architect specification complete."
    mock_exec = "Implementation finished.\n\n```python:components/feature.py\ndef run(): return 42\n```\n"
    mock_rev = "Review verdict: PASS. Implementation is clean."

    core = BridgeCore(
        config=BridgeConfig(
            role_bindings={"architect": "arch", "executor": "exec", "reviewer": "rev"},
            agents={
                "arch": AgentProfile(id="arch", role="architect", provider="mock-a", capabilities={"planning", "reasoning"}),
                "exec": AgentProfile(id="exec", role="executor", provider="mock-b", capabilities={"code_generation", "reasoning"}),
                "rev": AgentProfile(id="rev", role="reviewer", provider="mock-a", capabilities={"review", "reasoning"}),
            },
        ),
        providers={
            "mock-a": MockProviderA("mock-a", default_summary=mock_arch),
            "mock-b": MockProviderB("mock-b", default_summary=mock_exec),
        },
    )

    runner = ControlledWorkflowRunner(core=core, repo_root=tmp_path)
    outcome = runner.run_e2e_workflow(
        intent="Deploy feature",
        target_task_id="CASE-A",
        scope=["components/feature.py"],
        verification=["python -c \"exit(0)\""],
        auto_apply=True,
        check_credentials=False,
    )

    assert outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert outcome.architect_context is not None
    assert outcome.context_bundle is not None
    assert outcome.reviewer_context is not None

    # Lineage chain verification
    arch_id = outcome.architect_context.context_id
    exec_id = outcome.context_bundle.context_id
    rev_id = outcome.reviewer_context.context_id

    assert outcome.context_bundle.parent_context_id == arch_id
    assert outcome.reviewer_context.parent_context_id == exec_id


def test_integration_case_b_rework_cycle(tmp_path: Path):
    """
    CASE B: Rework Cycle
    Executor -> Diff -> Reviewer -> REWORK_REQUIRED -> Rework Context -> Executor -> New Diff -> Reviewer
    """
    src = tmp_path / "components" / "calc.py"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("def add(a, b): return a - b # Bug\n", encoding="utf-8")

    # Mock reviewer: first returns REWORK, second returns PASS
    class StatefulReviewer(MockProviderA):
        def __init__(self):
            super().__init__("mock-rev")
            self.calls = 0

        def invoke(self, request):
            self.calls += 1
            if self.calls == 1:
                return InvocationResult(
                    request_id=request.request_id,
                    task_id=request.task_id,
                    status=InvocationStatus.REWORK_REQUIRED,
                    agent_id=request.agent_id,
                    provider=self.provider_id,
                    summary="Review verdict: REWORK_REQUIRED. add() subtracted instead of adding.",
                    error_message="Defect: subtraction operator used",
                    completed_at="2026-09-18T00:00:00Z",
                )
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.SUCCESS,
                agent_id=request.agent_id,
                provider=self.provider_id,
                summary="Review verdict: PASS. Correct addition implemented.",
                completed_at="2026-09-18T00:00:00Z",
            )

    core = BridgeCore(
        config=BridgeConfig(
            role_bindings={"architect": "arch", "executor": "exec", "reviewer": "rev"},
            agents={
                "arch": AgentProfile(id="arch", role="architect", provider="mock-a", capabilities={"planning", "reasoning"}),
                "exec": AgentProfile(id="exec", role="executor", provider="mock-b", capabilities={"code_generation", "reasoning"}),
                "rev": AgentProfile(id="rev", role="reviewer", provider="mock-rev", capabilities={"review", "reasoning"}),
            },
        ),
        providers={
            "mock-a": MockProviderA("mock-a", default_summary="Specification complete."),
            "mock-b": MockProviderB("mock-b", default_summary="Fixed add.\n\n```python:components/calc.py\ndef add(a, b): return a + b\n```\n"),
            "mock-rev": StatefulReviewer(),
        },
    )

    runner = ControlledWorkflowRunner(core=core, repo_root=tmp_path)
    outcome_initial = runner.run_e2e_workflow(
        intent="Fix addition",
        target_task_id="CASE-B-REWORK",
        scope=["components/calc.py"],
        verification=["python -c \"exit(0)\""],
        auto_apply=True,
        check_credentials=False,
    )

    assert outcome_initial.stage == OrchestrationStage.REWORK_REQUIRED
    session = outcome_initial.session
    assert session.rework_count == 1

    # Execute controlled rework cycle
    outcome_rework = runner.run_rework_cycle(
        session=session,
        rework_objective="Ensure add() correctly computes a + b",
        auto_apply=True,
    )

    assert outcome_rework.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert outcome_rework.rework_context is not None
    assert outcome_rework.rework_context.reviewer_feedback is not None
    assert "add() subtracted" in outcome_rework.rework_context.reviewer_feedback


def test_integration_case_c_fresh_repository_context(tmp_path: Path):
    """
    CASE C: Fresh Repository Context
    Initial context contains version 1. Runtime updates file to version 2.
    Reviewer context MUST contain version 2 on disk (never reuses version 1).
    """
    f = tmp_path / "components" / "state.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("v = 1\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="CASE-C", title="State Update", goal="Update state", scope=["components/state.py"])

    # Stage 1: Executor context sees v = 1
    pkg_exec = engine.assemble_context(task, role="executor", stage="executor")
    assert "v = 1" in pkg_exec.files[0].content

    # Runtime changes file to v = 2
    f.write_text("v = 2 # Modified by runtime\n", encoding="utf-8")

    # Stage 2: Reviewer context newly assembled
    pkg_rev = engine.assemble_context(
        task,
        role="reviewer",
        stage="reviewer",
        parent_context_id=pkg_exec.context_id,
    )
    assert "v = 2 # Modified by runtime" in pkg_rev.files[0].content
    assert "v = 1" not in pkg_rev.files[0].content


def test_integration_case_d_historical_context_classification(tmp_path: Path):
    """
    CASE D: Historical Context
    Reviewer feedback is marked as historical explanation, not current workspace source code.
    """
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="CASE-D", title="Auth History", goal="History classification", scope=[])

    pkg = engine.assemble_context(
        task,
        reviewer_feedback="Defect in auth signature",
        previous_diff="--- auth.py\n+++ auth.py\n",
    )

    formatted = pkg.format_for_prompt()
    assert "Historical Rework Context (Context from previous iteration; for reference only)" in formatted
    assert "Defect in auth signature" in formatted


def test_integration_case_e_current_evidence_precedence(tmp_path: Path):
    """
    CASE E: Current Evidence Precedence
    Previous verification = PASS, Current verification = FAIL.
    Reviewer context receives current verification as authoritative.
    """
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="CASE-E", title="Verification Precedence", goal="Verification precedence", scope=[])

    pkg = engine.assemble_context(
        task,
        role="reviewer",
        verification_output="FAILED: 2 tests failed",
        previous_verification_output="PASSED: 10 tests passed",
    )

    assert pkg.verification_output == "FAILED: 2 tests failed"
    assert pkg.previous_verification_output == "PASSED: 10 tests passed"


def test_integration_case_f_context_budget_bound(tmp_path: Path):
    """
    CASE F: Context Budget
    Large historical diff and feedback cannot exceed configured budget.
    """
    engine = ContextEngine(repo_root=tmp_path, max_characters=1000)
    task = Task(id="CASE-F", title="Budget Bound", goal="Budget bound test", scope=[])

    huge_feedback = "CRITICAL DEFECT DETECTED: " + ("explanation " * 200)  # ~2400 chars
    pkg = engine.assemble_context(task, reviewer_feedback=huge_feedback)

    assert pkg.total_characters <= 1000
    assert pkg.truncated is True
    assert "[... reviewer_feedback truncated" in pkg.reviewer_feedback


def test_integration_case_g_security_sanitization(tmp_path: Path):
    """
    CASE G: Security
    Secrets in historical metadata are sanitized before entering context.
    """
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="CASE-G", title="Security Sanitization", goal="Security test", scope=[])

    secret_feedback = "Found token Bearer eyJhbGciOiJIUzI1NiJ9.test and api_key sk-proj-123456"
    pkg = engine.assemble_context(task, reviewer_feedback=secret_feedback)

    assert "Bearer" not in pkg.reviewer_feedback
    assert "sk-proj-123456" not in pkg.reviewer_feedback
    assert "[REDACTED_SECRET]" in pkg.reviewer_feedback


def test_integration_case_h_write_isolation(tmp_path: Path):
    """
    CASE H: Write Isolation
    A file included in read context outside Task.scope cannot be modified by the Executor.
    READ CONTEXT != WRITE AUTHORITY.
    """
    f_read = tmp_path / "readonly_config.py"
    f_read.write_text("READONLY = True\n", encoding="utf-8")

    runtime = BoundedWorkspaceRuntime(repo_root=tmp_path)
    # Task scope allows only components/worker.py
    task = Task(id="CASE-H", title="Write Scope Isolation", goal="Scope isolation", scope=["components/worker.py"])

    # Attempt to write to readonly_config.py (which is readable but out of write scope)
    with pytest.raises(ScopeViolationError):
        runtime.validate_scope("readonly_config.py", task)


def test_integration_case_i_execution_isolation(tmp_path: Path):
    """
    CASE I: Execution Isolation
    Two separate executions for the same task have independent context lineage.
    """
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(id="TASK-SHARED", title="Shared Task", goal="Isolation test", scope=[])

    # Execution 1
    pkg1_a = engine.assemble_context(task, execution_id="exec-run-1", role="architect")
    pkg1_b = engine.assemble_context(task, execution_id="exec-run-1", role="executor", parent_context_id=pkg1_a.context_id)

    # Execution 2
    pkg2_a = engine.assemble_context(task, execution_id="exec-run-2", role="architect")
    pkg2_b = engine.assemble_context(task, execution_id="exec-run-2", role="executor", parent_context_id=pkg2_a.context_id)

    assert pkg1_a.execution_id == "exec-run-1"
    assert pkg2_a.execution_id == "exec-run-2"
    assert pkg1_b.parent_context_id == pkg1_a.context_id
    assert pkg2_b.parent_context_id == pkg2_a.context_id
    assert pkg1_b.parent_context_id != pkg2_b.parent_context_id
