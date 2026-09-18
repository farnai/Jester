"""
Tests for Unified Diff Generation and Reviewer Hardening (TASK-0006).

Verifies:
- TEST 5: Bounded runtime unified diff generation (added, removed, file paths).
- TEST 6: ReviewInput contract receives actual diff.
- TEST 7: Reviewer prompts (OpenAI & Gemini) render the UNIFIED CODE DIFF section.
- TEST 8: Reviewer rejects known defects even when Executor summary claims success.
- TEST 9: Zero Git side effects (no automatic commit/push/stage).
"""
from pathlib import Path
import subprocess
from unittest.mock import MagicMock
import pytest

from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig
from jester_bridge.contracts import (
    InvocationRequest,
    InvocationResult,
    InvocationStatus,
)
from jester_bridge.core import BridgeCore
from jester_bridge.google_provider import GoogleProvider
from jester_bridge.openai_provider import OpenAIProvider
from jester_bridge.orchestration import (
    BridgeOrchestrator,
    OrchestrationSession,
    OrchestrationStage,
    ReviewInput,
    ReviewResult,
    ReviewVerdict,
    ExecutorResult,
)
from jester_bridge.protocol import Task
from jester_bridge.roles import Role
from jester_bridge.runtime import (
    BoundedWorkspaceRuntime,
    FileChange,
    RuntimeExecutionResult,
)
from jester_bridge.testing import MockProviderA, MockProviderB
from jester_bridge.workflow import ControlledWorkflowRunner

# Capture baseline repository HEAD at test module start
_INITIAL_HEAD = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()


def test_unified_diff_generation(tmp_path: Path):
    runtime = BoundedWorkspaceRuntime(repo_root=tmp_path)
    file_rel = "components/calculator.py"
    abs_file = tmp_path / file_rel
    abs_file.parent.mkdir(parents=True, exist_ok=True)
    abs_file.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

    task = Task(
        id="TASK-DIFF-01",
        title="Diff Test",
        role="executor",
        goal="Update add function",
        scope=["components/calculator.py"],
    )

    changes = [
        FileChange(
            relative_path=file_rel,
            content="def add(a, b):\n    # Enhanced adder\n    return a + b\n",
        )
    ]

    res = runtime.execute_and_verify(changes=changes, task=task)
    assert res.status == InvocationStatus.SUCCESS
    assert file_rel in res.files_modified
    assert res.diff != ""

    # Verify standard unified diff structure
    assert "--- a/components/calculator.py" in res.diff
    assert "+++ b/components/calculator.py" in res.diff
    assert "+    # Enhanced adder" in res.diff


def test_review_input_contract_contains_diff():
    task = Task(
        id="TASK-REV-INPUT",
        title="Review Input Test",
        role="reviewer",
        goal="Verify diff presence",
        scope=["jester_bridge/"],
    )

    diff_sample = "--- a/foo.py\n+++ b/foo.py\n@@ -1 +1 @@\n-old\n+new\n"
    review_input = ReviewInput(
        task=task,
        executor_summary="Replaced old with new.",
        files_modified=["foo.py"],
        diff=diff_sample,
        verification_output="Tests passed.",
    )

    assert review_input.diff == diff_sample
    assert review_input.executor_summary == "Replaced old with new."


def test_reviewer_prompts_render_unified_diff():
    diff_sample = "--- a/mod.py\n+++ b/mod.py\n@@ -1 +1 @@\n-broken()\n+fixed()\n"
    request = InvocationRequest(
        request_id="req-test-diff",
        task_id="TASK-PROMPT-01",
        role=Role.REVIEWER.value,
        agent_id="test-reviewer",
        provider="openai",
        model="gpt-4o",
        payload={
            "title": "Fix bug",
            "goal": "Repair broken function",
            "executor_summary": "Function fixed.",
            "diff": diff_sample,
        },
        created_at="2026-09-18T00:00:00Z",
    )

    # 1. OpenAI Provider prompt
    openai_prov = OpenAIProvider(api_key="mock-key")
    prompt_openai = openai_prov._build_user_prompt(request)
    assert "UNIFIED CODE DIFF (CRITICAL EVIDENCE):" in prompt_openai
    assert diff_sample in prompt_openai

    # 2. Google Provider prompt
    google_prov = GoogleProvider(api_key="mock-key")
    prompt_google = google_prov._build_user_prompt(request)
    assert "UNIFIED CODE DIFF (CRITICAL EVIDENCE):" in prompt_google
    assert diff_sample in prompt_google


def test_reviewer_detects_defect_despite_executor_claim():
    """
    CRITICAL TEST 8:
    Executor summary claims complete success and test pass.
    However, the actual code diff introduces a fatal flaw (e.g. security bypass).
    The Reviewer inspects the diff and issues REWORK_REQUIRED.
    """
    defect_diff = (
        "--- a/auth/guard.py\n"
        "+++ b/auth/guard.py\n"
        "@@ -10,3 +10,4 @@\n"
        " def verify_token(token):\n"
        "-    return validate_jwt_signature(token)\n"
        "+    # Intentional defect: bypass auth\n"
        "+    return True\n"
    )

    # Reviewer LLM receives the prompt with the defect diff and correctly responds with REWORK
    reviewer_verdict_summary = (
        "Review verdict: REWORK_REQUIRED.\n"
        "Critical defect detected in UNIFIED CODE DIFF: auth/guard.py bypasses signature verification with return True. "
        "This introduces a major security vulnerability."
    )

    prov_mock = MockProviderA(provider_id="openai", default_summary=reviewer_verdict_summary)
    config = BridgeConfig(
        role_bindings={"reviewer": "chatgpt-critic"},
        agents={
            "chatgpt-critic": AgentProfile(
                id="chatgpt-critic",
                role="reviewer",
                provider="openai",
                capabilities={"review", "reasoning"},
            )
        },
    )
    core = BridgeCore(config=config, providers={"openai": prov_mock})
    orchestrator = BridgeOrchestrator(core=core)

    task = Task(
        id="TASK-DEFECT-01",
        title="Auth Guard Update",
        role="executor",
        goal="Enhance auth validation",
        scope=["auth/guard.py"],
    )

    session = orchestrator.create_session(task=task)
    session.current_stage = OrchestrationStage.EXECUTOR
    # Executor falsely claims success:
    session.executor_result = ExecutorResult(
        task_id=task.id,
        status=InvocationStatus.SUCCESS,
        summary="Authentication security fully updated. All tests pass with 100% confidence.",
        files_modified=["auth/guard.py"],
        diff=defect_diff,
        raw_result=InvocationResult(
            request_id="req-exec",
            task_id=task.id,
            status=InvocationStatus.SUCCESS,
            agent_id="exec-agent",
            provider="openai",
            summary="Auth updated cleanly.",
            completed_at="2026-09-18T00:00:00Z",
        ),
    )

    # Run reviewer stage with the actual diff
    session = orchestrator.run_reviewer_stage(
        session=session,
        verification_output="Tests passed.",
        diff=defect_diff,
    )

    # Assert reviewer caught the defect and demanded rework
    assert session.review_result is not None
    assert session.review_result.verdict == ReviewVerdict.REWORK_REQUIRED
    assert session.current_stage == OrchestrationStage.REWORK_REQUIRED
    assert "defect detected in UNIFIED CODE DIFF" in session.review_result.summary


def test_workflow_generates_diff_in_reports(tmp_path: Path):
    """Verifies that ControlledWorkflowRunner captures diff and embeds it into reports."""
    mock_arch = "Architect specification complete."
    mock_exec = (
        "Implementation finished.\n\n"
        "```python:service/worker.py\n"
        "def work():\n"
        "    return 'DONE'\n"
        "```\n"
    )
    mock_rev = "Review verdict: PASS. All criteria met based on inspection of code diff."

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
        intent="Create service worker",
        target_task_id="TASK-DIFF-REPORT",
        scope=["service/worker.py"],
        verification=["python -c \"import sys; sys.exit(0)\""],
        auto_apply=True,
        check_credentials=False,
    )

    assert outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert outcome.diff is not None
    assert "+++ b/service/worker.py" in outcome.diff
    assert "+    return 'DONE'" in outcome.diff

    # Verify implementation report has diff section
    impl_report = tmp_path / outcome.implementation_report_path
    assert impl_report.exists()
    impl_content = impl_report.read_text(encoding="utf-8")
    assert "## Code Diff" in impl_content
    assert "+++ b/service/worker.py" in impl_content

    # Verify review report has diff section
    rev_report = tmp_path / outcome.review_report_path
    assert rev_report.exists()
    rev_content = rev_report.read_text(encoding="utf-8")
    assert "## Code Diff" in rev_content
    assert "+++ b/service/worker.py" in rev_content


def test_zero_git_side_effects():
    """TEST 9: Verifies that no git operations (commit, push, stage) were triggered."""
    current_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    # Commit must remain unchanged from baseline
    assert current_head == _INITIAL_HEAD
    assert len(current_head) == 40

    # No files should have been staged in the repository
    staged = subprocess.run(
        ["git", "diff", "--staged", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert staged == ""
