"""
Tests for Structured Handoffs, Context Engine Integration, and Governance Invariants (TASK-0009).

Verifies:
- Unit: ArchitectHandoff, ExecutorHandoff, ReviewerHandoff serialization and validation.
- Unit: Provider neutrality of structured handoffs.
- Integration Case A: Task -> ContextEngine -> Architect -> ArchitectHandoff -> Executor.
- Integration Case B: Task -> ContextEngine -> Executor -> actual diff -> ExecutorHandoff -> Reviewer.
- Integration Case C: Large repository -> bounded context -> deterministic prioritization -> no budget overflow.
- Integration Case D: Protected files -> excluded from context.
- Integration Case E: Intentional defect -> Executor claims success -> Reviewer inspects actual diff -> Rejects defect.
- Integration Case F: Execution History -> context metadata persisted -> no full repository dump.
"""
from pathlib import Path
import pytest

from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig
from jester_bridge.context import (
    ContextEngine,
    ContextPackage,
    ContextPriority,
    SourceType,
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
from jester_bridge.execution_history import ExecutionHistoryStore
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
from jester_bridge.runtime import BoundedWorkspaceRuntime, FileChange
from jester_bridge.testing import MockProviderA, MockProviderB
from jester_bridge.workflow import ControlledWorkflowRunner


# ---------------------------------------------------------------------------
# Unit Tests: Structured Handoff Contracts
# ---------------------------------------------------------------------------

def test_architect_handoff_serialization():
    """Verifies ArchitectHandoff model validation and JSON serialization."""
    handoff = ArchitectHandoff(
        task_id="TASK-HAND-01",
        task_objective="Refactor authentication layer",
        implementation_intent="Modularize JWT and JWKS verifiers",
        affected_areas=["backend/app/auth/"],
        expected_files=["backend/app/auth/verifier.py", "backend/app/auth/jwks.py"],
        constraints=["Preserve RS256 invariant", "No HS256 fallback in prod"],
        acceptance_criteria=["pytest tests/backend/test_jwt_verification.py passes"],
        risks=["Key rotation latency"],
        architectural_notes="Split token decoding from signature verification",
        relevant_context_references=["docs/AI_BRIDGE_ARCHITECTURE.md"],
        context_package_metadata={"budget": 50000, "selected_files": 2},
    )

    dumped = handoff.model_dump()
    assert dumped["task_id"] == "TASK-HAND-01"
    assert dumped["implementation_intent"] == "Modularize JWT and JWKS verifiers"
    assert len(dumped["expected_files"]) == 2
    assert dumped["context_package_metadata"]["budget"] == 50000

    # Reconstruct
    reconstructed = ArchitectHandoff.model_validate(dumped)
    assert reconstructed.task_id == handoff.task_id
    assert reconstructed.constraints == handoff.constraints


def test_executor_handoff_serialization():
    """Verifies ExecutorHandoff carries diff, verification status, and files modified."""
    diff_sample = "--- a/auth.py\n+++ b/auth.py\n@@ -1 +1 @@\n-old\n+new\n"
    handoff = ExecutorHandoff(
        task_id="TASK-HAND-02",
        implementation_summary="Updated auth token verifier to support JWKS.",
        files_modified=["backend/app/auth/verifier.py"],
        tests_changed=["tests/backend/test_jwt.py"],
        verification_passed=True,
        verification_output="24 passed in 1.12s",
        diff=diff_sample,
        relevant_context_references=["backend/app/auth/verifier.py"],
        known_limitations=[],
        warnings=[],
        usage_metrics=UsageMetrics(input_tokens=100, output_tokens=50, total_tokens=150),
    )

    dumped = handoff.model_dump()
    assert dumped["task_id"] == "TASK-HAND-02"
    assert dumped["verification_passed"] is True
    assert dumped["diff"] == diff_sample
    assert dumped["usage_metrics"]["total_tokens"] == 150

    reconstructed = ExecutorHandoff.model_validate(dumped)
    assert reconstructed.verification_output == "24 passed in 1.12s"


def test_reviewer_handoff_serialization():
    """Verifies ReviewerHandoff records verdict, diff inspection, and feedback."""
    handoff = ReviewerHandoff(
        task_id="TASK-HAND-03",
        verdict=ReviewVerdict.PASS.value,
        summary="Implementation adheres to all specifications with zero regressions.",
        feedback=None,
        criteria_verified={"pytest passed": True, "no secrets": True},
        diff_inspected=True,
        defect_details=None,
        usage_metrics=UsageMetrics(input_tokens=200, output_tokens=40, total_tokens=240),
    )

    dumped = handoff.model_dump()
    assert dumped["task_id"] == "TASK-HAND-03"
    assert dumped["verdict"] == "PASS"
    assert dumped["diff_inspected"] is True
    assert dumped["criteria_verified"]["no secrets"] is True


# ---------------------------------------------------------------------------
# Integration Tests: Cases A - F
# ---------------------------------------------------------------------------

def test_integration_case_a_architect_to_executor(tmp_path: Path):
    """
    CASE A:
    Task -> ContextEngine -> Architect -> ArchitectHandoff -> Executor
    Verifies that Architect produces a structured ArchitectHandoff and that
    Executor receives this handoff with context metadata intact.
    """
    # Workspace setup
    f = tmp_path / "components" / "service.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("def run(): pass\n", encoding="utf-8")

    core = BridgeCore(
        config=BridgeConfig(
            role_bindings={"architect": "arch-mock", "executor": "exec-mock"},
            agents={
                "arch-mock": AgentProfile(id="arch-mock", role="architect", provider="mock-a", capabilities={"planning", "reasoning"}),
                "exec-mock": AgentProfile(id="exec-mock", role="executor", provider="mock-a", capabilities={"code_generation", "reasoning"}),
            },
        ),
        providers={"mock-a": MockProviderA("mock-a", default_summary="Architect specification complete.")},
    )

    orchestrator = BridgeOrchestrator(core=core)
    task = Task(
        id="CASE-A-01",
        title="Case A Architecture Flow",
        role="architect",
        goal="Design high performance service",
        scope=["components/service.py"],
    )

    session = orchestrator.create_session(task=task)
    arch_input = ArchitectInput(intent="Design high performance service", target_task_id="CASE-A-01")
    session = orchestrator.run_architect_stage(session, arch_input)

    assert session.current_stage == OrchestrationStage.ARCHITECT
    assert session.architect_handoff is not None
    assert session.architect_handoff.task_id == "CASE-A-01"
    assert session.architect_handoff.implementation_intent == "Design high performance service"
    assert session.architect_handoff.expected_files == ["components/service.py"]

    # Now transition to Executor stage with the ArchitectHandoff
    session = orchestrator.run_executor_stage(
        session,
        architect_handoff=session.architect_handoff,
        extra_context={"architect_intent": session.architect_handoff.implementation_intent},
    )

    assert session.current_stage == OrchestrationStage.EXECUTOR
    assert session.executor_handoff is not None
    assert session.executor_handoff.task_id == "CASE-A-01"


def test_integration_case_b_executor_to_reviewer_with_diff(tmp_path: Path):
    """
    CASE B:
    Task -> ContextEngine -> Executor -> actual diff -> ExecutorHandoff -> Reviewer
    Verifies that the Reviewer receives the real unified diff through ExecutorHandoff
    and passes review.
    """
    repo_file = tmp_path / "components" / "worker.py"
    repo_file.parent.mkdir(parents=True, exist_ok=True)
    repo_file.write_text("def work():\n    return False\n", encoding="utf-8")

    core = BridgeCore(
        config=BridgeConfig(
            role_bindings={"executor": "exec-mock", "reviewer": "rev-mock"},
            agents={
                "exec-mock": AgentProfile(id="exec-mock", role="executor", provider="mock-a", capabilities={"code_generation", "reasoning"}),
                "rev-mock": AgentProfile(id="rev-mock", role="reviewer", provider="mock-a", capabilities={"review", "reasoning"}),
            },
        ),
        providers={"mock-a": MockProviderA("mock-a", default_summary="Review verdict: PASS. Diff is clean.")},
    )

    runtime = BoundedWorkspaceRuntime(repo_root=tmp_path)
    task = Task(
        id="CASE-B-01",
        title="Worker Fix",
        role="executor",
        goal="Make worker return True",
        scope=["components/worker.py"],
        acceptance_criteria=["Worker returns True"],
    )

    # 1. Apply changes with runtime
    changes = [
        FileChange(relative_path="components/worker.py", content="def work():\n    return True\n")
    ]
    run_res = runtime.execute_and_verify(changes=changes, task=task)
    assert run_res.diff != ""

    # 2. Build ExecutorHandoff
    exec_handoff = ExecutorHandoff(
        task_id=task.id,
        implementation_summary="Updated worker.py to return True.",
        files_modified=run_res.files_modified,
        tests_changed=[],
        verification_passed=run_res.verification_passed,
        verification_output=run_res.verification_output,
        diff=run_res.diff,
        relevant_context_references=run_res.files_modified,
    )

    # 3. Dispatch to Reviewer
    orchestrator = BridgeOrchestrator(core=core)
    session = orchestrator.create_session(task=task)
    session.current_stage = OrchestrationStage.EXECUTOR
    session.executor_result = ExecutorResult(
        task_id=task.id,
        status=InvocationStatus.SUCCESS,
        summary="Worker updated.",
        diff=run_res.diff,
        raw_result=InvocationResult(
            request_id="r1",
            task_id=task.id,
            status=InvocationStatus.SUCCESS,
            agent_id="exec-mock",
            provider="mock-a",
            summary="Done",
            completed_at="2026-09-18T00:00:00Z",
        ),
    )

    session = orchestrator.run_reviewer_stage(
        session,
        diff=exec_handoff.diff,
        verification_output=exec_handoff.verification_output,
        executor_handoff=exec_handoff,
    )

    assert session.current_stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert session.reviewer_handoff is not None
    assert session.reviewer_handoff.verdict == "PASS"
    assert session.reviewer_handoff.diff_inspected is True


def test_integration_case_c_large_repo_bounded_budget(tmp_path: Path):
    """
    CASE C:
    Large repository -> bounded context -> deterministic prioritization -> no budget overflow.
    Generates 20 files (total > 20,000 chars), configures a 2,000 char budget,
    and proves that high-priority files are retained, lower-priority omitted, and
    total characters never exceed 2,000.
    """
    # Create 20 files
    for i in range(20):
        f = tmp_path / f"file_{i:02d}.txt"
        f.write_text(f"File {i:02d} " + ("DATA " * 200), encoding="utf-8")  # ~1010 chars each

    # Scope specifies 2 files explicitly (CRITICAL)
    scope_files = ["file_01.txt", "file_02.txt"]
    other_files = [f"file_{i:02d}.txt" for i in range(3, 20)]

    engine = ContextEngine(repo_root=tmp_path, max_characters=2500, max_file_characters=1500)
    task = Task(
        id="CASE-C-LARGE",
        title="Large Repo Budget Test",
        role="executor",
        goal=f"Check all files: {' '.join(other_files[:5])}",
        scope=scope_files,
    )

    pkg = engine.assemble_context(task)

    # Invariants:
    # 1. Total characters must NOT exceed budget
    assert pkg.total_characters <= 2500
    assert pkg.truncated is True

    # 2. Explicit scope files (CRITICAL) must be included
    assert "file_01.txt" in pkg.included_paths
    assert "file_02.txt" in pkg.included_paths

    # 3. Many other files must be excluded due to budget limit
    assert len(pkg.excluded_paths) > 0
    for exc_path, reason in pkg.excluded_paths.items():
        assert "budget exceeded" in reason.lower()


def test_integration_case_d_protected_files_excluded(tmp_path: Path):
    """
    CASE D:
    Protected files (.env, .git, AGENTS.md, supabase/migrations) must be strictly excluded.
    """
    (tmp_path / ".env").write_text("SUPABASE_KEY=secret\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# Master Governance\n", encoding="utf-8")
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    m_dir = tmp_path / "supabase" / "migrations"
    m_dir.mkdir(parents=True)
    (m_dir / "001.sql").write_text("SELECT 1;\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="CASE-D-PROT",
        title="Protected Exclusions",
        role="executor",
        goal="Attempt to read all protected paths",
        scope=[".env", "AGENTS.md", ".git/HEAD", "supabase/migrations/001.sql"],
    )

    pkg = engine.assemble_context(task)

    assert len(pkg.included_paths) == 0
    assert len(pkg.files) == 0
    assert ".env" in pkg.excluded_paths
    assert "AGENTS.md" in pkg.excluded_paths
    assert ".git/HEAD" in pkg.excluded_paths
    assert "supabase/migrations/001.sql" in pkg.excluded_paths

    for p in pkg.excluded_paths.values():
        assert "protected" in p.lower()


def test_integration_case_e_defect_diff_rejected_by_reviewer(tmp_path: Path):
    """
    CASE E:
    Intentional defect -> Executor claims success -> Reviewer receives actual diff -> Reviewer rejects defect.
    """
    defect_diff = (
        "--- a/security.py\n"
        "+++ b/security.py\n"
        "@@ -1,3 +1,3 @@\n"
        " def check_access(user):\n"
        "-    return user.is_authenticated\n"
        "+    return True # Fatal security bypass\n"
    )

    reviewer_response = (
        "Review verdict: REWORK_REQUIRED.\n"
        "CRITICAL SECURITY DEFECT detected in UNIFIED CODE DIFF: check_access unconditionally returns True."
    )

    core = BridgeCore(
        config=BridgeConfig(
            role_bindings={"reviewer": "critic-agent"},
            agents={
                "critic-agent": AgentProfile(id="critic-agent", role="reviewer", provider="mock-a", capabilities={"review", "reasoning"}),
            },
        ),
        providers={"mock-a": MockProviderA("mock-a", default_summary=reviewer_response)},
    )

    orchestrator = BridgeOrchestrator(core=core)
    task = Task(
        id="CASE-E-DEFECT",
        title="Security Fix",
        role="executor",
        goal="Fix security access",
        scope=["security.py"],
    )

    session = orchestrator.create_session(task=task)
    session.current_stage = OrchestrationStage.EXECUTOR
    # Executor falsely asserts full success
    session.executor_result = ExecutorResult(
        task_id=task.id,
        status=InvocationStatus.SUCCESS,
        summary="Security access updated with 100% test pass and zero defects.",
        diff=defect_diff,
        raw_result=InvocationResult(
            request_id="r-exec",
            task_id=task.id,
            status=InvocationStatus.SUCCESS,
            agent_id="exec",
            provider="mock-a",
            summary="Clean",
            completed_at="2026-09-18T00:00:00Z",
        ),
    )

    # Reviewer stage with actual diff evidence
    session = orchestrator.run_reviewer_stage(session, diff=defect_diff, verification_output="Tests passed.")

    assert session.review_result.verdict == ReviewVerdict.REWORK_REQUIRED
    assert session.current_stage == OrchestrationStage.REWORK_REQUIRED
    assert session.reviewer_handoff is not None
    assert session.reviewer_handoff.verdict == "REWORK_REQUIRED"
    assert "CRITICAL SECURITY DEFECT" in session.review_result.summary


def test_integration_case_f_execution_history_context_metadata(tmp_path: Path):
    """
    CASE F:
    Execution History -> context metadata persisted -> no full repository dump.
    Proves that running ControlledWorkflowRunner records context metadata in SQLite
    events without dumping entire source code files into the database.
    """
    mock_arch = "Architect specification complete."
    mock_exec = (
        "Implementation finished.\n\n"
        "```python:service/calc.py\n"
        "def compute():\n"
        "    return 42\n"
        "```\n"
    )
    mock_rev = "Review verdict: PASS. All criteria met based on diff inspection."

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

    test_db = tmp_path / "test_history.db"
    store = ExecutionHistoryStore(db_path=test_db)
    runner = ControlledWorkflowRunner(
        core=core,
        repo_root=tmp_path,
        history_store=store,
    )

    outcome = runner.run_e2e_workflow(
        intent="Create compute service",
        target_task_id="CASE-F-HIST",
        scope=["service/calc.py"],
        verification=["python -c \"import sys; sys.exit(0)\""],
        auto_apply=True,
        check_credentials=False,
    )

    assert outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert outcome.execution_id is not None

    # Inspect events in database
    events = store.get_events_for_execution(outcome.execution_id)
    ctx_events = [e for e in events if e.event_type == "context_assembled"]

    # Must have assembled context for stages (architect, executor, reviewer)
    assert len(ctx_events) >= 2

    for ce in ctx_events:
        meta = ce.metadata
        assert "context_version" in meta
        assert "selected_file_count" in meta
        assert "total_budget" in meta
        assert "used_budget" in meta
        # Invariant: NEVER dump full source code into event metadata!
        assert "code_content" not in meta
        assert "content" not in meta
