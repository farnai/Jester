"""
Unit and Integration Tests for ControlledWorkflowRunner and PreflightValidator.

Verifies:
- Preflight validation of tasks, scopes, and provider readiness
- Clean abort upon preflight failure
- Full end-to-end controlled workflow execution
- Disk state transitions (.jester/tasks/inbox -> active -> review -> completed)
- Mandatory human signoff before completion
"""
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig
from jester_bridge.core import BridgeCore
from jester_bridge.orchestration import OrchestrationStage, ReviewVerdict
from jester_bridge.preflight import PreflightValidator
from jester_bridge.protocol import Task
from jester_bridge.runtime import BoundedWorkspaceRuntime
from jester_bridge.testing import MockProviderA, MockProviderB
from jester_bridge.workflow import ControlledWorkflowRunner, sanitize_portable_paths


def _setup_workflow_test_env(tmp_path: Path):
    """Sets up an isolated mock environment for workflow testing."""
    mock_arch_resp = (
        "Task specification analyzed.\n\n"
        "Title: Mini Diagnostic Utility\n"
        "Scope: sandbox/diagnostics.py\n"
    )
    mock_exec_resp = (
        "Implementation complete.\n\n"
        "```python:sandbox/diagnostics.py\n"
        "def get_status():\n"
        "    return 'ONLINE'\n"
        "```\n"
    )
    mock_rev_resp = "Review verdict: PASS. Implementation verified against acceptance criteria."

    prov_arch = MockProviderA(provider_id="openai", default_summary=mock_arch_resp)
    prov_exec = MockProviderB(provider_id="google", default_summary=mock_exec_resp)
    prov_rev = MockProviderA(provider_id="openai", default_summary=mock_rev_resp)

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
    runner = ControlledWorkflowRunner(core=core, repo_root=tmp_path, runtime=runtime)

    return runner, tmp_path


def test_preflight_validation_dangerous_scope():
    config = BridgeConfig(
        role_bindings={"executor": "agent-1"},
        agents={"agent-1": AgentProfile(id="agent-1", role="executor", provider="mock", capabilities={"code_generation"})},
    )
    core = BridgeCore(config=config, providers={"mock": MockProviderA(provider_id="mock")})
    validator = PreflightValidator(core=core)

    # Dangerously broad scope: "."
    task_broad = Task(id="TASK-PRE-01", title="Broad Scope", role="executor", goal="Do something", scope=["."])
    report = validator.validate(task_broad, check_credentials=False)
    assert not report.is_valid
    assert any("dangerously broad" in err for err in report.errors)

    # Protected scope: "AGENTS.md"
    task_protected = Task(id="TASK-PRE-02", title="Protected Scope", role="executor", goal="Do something", scope=["AGENTS.md"])
    report_p = validator.validate(task_protected, check_credentials=False)
    assert not report_p.is_valid
    assert any("protected path" in err for err in report_p.errors)


def test_workflow_runner_end_to_end_lifecycle(tmp_path):
    runner, repo_root = _setup_workflow_test_env(tmp_path)

    intent = "Create a mini diagnostic utility returning status ONLINE"
    target_task_id = "TASK-TEST-E2E"
    scope = ["sandbox/diagnostics.py"]
    verification = ["python -c \"import sys; sys.exit(0)\""]  # Passing verification

    outcome = runner.run_e2e_workflow(
        intent=intent,
        target_task_id=target_task_id,
        scope=scope,
        verification=verification,
        auto_apply=True,
        check_credentials=False,
    )

    # 1. Assert workflow progressed to AWAITING_HUMAN_SIGNOFF
    assert outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert outcome.preflight.is_valid is True

    # 2. Assert files were actually written to disk in the authorized sandbox scope
    created_file = repo_root / "sandbox" / "diagnostics.py"
    assert created_file.exists()
    assert "return 'ONLINE'" in created_file.read_text(encoding="utf-8")

    # 3. Assert task file is currently in .jester/tasks/review/
    review_task_path = repo_root / ".jester" / "tasks" / "review" / f"{target_task_id}.json"
    assert review_task_path.exists()
    inbox_task_path = repo_root / ".jester" / "tasks" / "inbox" / f"{target_task_id}.json"
    active_task_path = repo_root / ".jester" / "tasks" / "active" / f"{target_task_id}.json"
    assert not inbox_task_path.exists()
    assert not active_task_path.exists()

    # 4. Assert implementation and review reports exist
    impl_report = repo_root / ".jester" / "reports" / "implementations" / f"{target_task_id}.md"
    rev_report = repo_root / ".jester" / "reports" / "reviews" / f"{target_task_id}.md"
    assert impl_report.exists()
    assert rev_report.exists()

    # 5. Execute human signoff approval
    completed_task_path = runner.complete_human_approval(
        session=outcome.session,
        approver="lead-reviewer",
        notes="All sandbox checks passed.",
    )
    assert completed_task_path.exists()
    assert not review_task_path.exists()
    assert outcome.session.current_stage == OrchestrationStage.COMPLETED
    assert outcome.session.task.status == "completed"


def test_workflow_runner_human_rejection(tmp_path):
    runner, repo_root = _setup_workflow_test_env(tmp_path)

    outcome = runner.run_e2e_workflow(
        intent="Create a feature for rejection test",
        target_task_id="TASK-TEST-REJECT",
        scope=["sandbox/diagnostics.py"],
        verification=["python -c \"import sys; sys.exit(0)\""],
        auto_apply=True,
        check_credentials=False,
    )

    assert outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    # 1st rejection: rework cycles remain (rework_count=1 <= max=2), moves back to active
    rework_file = runner.reject_human_signoff(
        session=outcome.session,
        rejector="human-operator",
        reason="Please refine the docstring.",
    )
    assert rework_file.exists()
    assert "active" in str(rework_file)
    assert outcome.session.current_stage == OrchestrationStage.REWORK_REQUIRED

    # Simulate reaching review and rejecting past max_rework_cycles
    outcome.session.current_stage = OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    runner.reject_human_signoff(
        session=outcome.session,
        rejector="human-operator",
        reason="Still needs work.",
    )
    outcome.session.current_stage = OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    blocked_file = runner.reject_human_signoff(
        session=outcome.session,
        rejector="human-operator",
        reason="Exceeded tolerance.",
    )
    assert blocked_file.exists()
    assert "blocked" in str(blocked_file)
    assert outcome.session.current_stage == OrchestrationStage.BLOCKED


def test_workflow_runner_verification_failure_rollback(tmp_path):
    runner, repo_root = _setup_workflow_test_env(tmp_path)

    target_task_id = "TASK-TEST-FAIL-VERIFY"
    scope = ["sandbox/diagnostics.py"]
    # Failing verification command (exits with code 1)
    verification = ["python -c \"import sys; sys.exit(1)\""]

    outcome = runner.run_e2e_workflow(
        intent="Create a failing feature",
        target_task_id=target_task_id,
        scope=scope,
        verification=verification,
        auto_apply=True,
        check_credentials=False,
    )

    # Workflow must stop in BLOCKED stage
    assert outcome.stage == OrchestrationStage.BLOCKED
    assert outcome.runtime_result is not None
    assert outcome.runtime_result.reverted is True

    # Applied file should be rolled back (deleted because it was newly created)
    target_file = repo_root / "sandbox" / "diagnostics.py"
    assert not target_file.exists()

    # Task file must be in .jester/tasks/blocked/
    blocked_task_path = repo_root / ".jester" / "tasks" / "blocked" / f"{target_task_id}.json"
    assert blocked_task_path.exists()


def test_preflight_validation_placeholder_and_traversal(tmp_path):
    config = BridgeConfig(
        role_bindings={"executor": "agent-1"},
        agents={"agent-1": AgentProfile(id="agent-1", role="executor", provider="mock", capabilities={"code_generation"})},
    )
    core = BridgeCore(config=config, providers={"mock": MockProviderA(provider_id="mock")})
    validator = PreflightValidator(core=core, repo_root=tmp_path)

    # Path traversal scope
    task_traversal = Task(id="TASK-PRE-03", title="Traversal", role="executor", goal="Do something", scope=["../outside"])
    report = validator.validate(task_traversal, check_credentials=False)
    assert not report.is_valid
    assert any("path traversal" in err for err in report.errors)


def test_workflow_runner_portability_and_observability(tmp_path):
    runner, repo_root = _setup_workflow_test_env(tmp_path)

    intent = "Create diagnostic utility"
    target_task_id = "TASK-PORT-OBS"
    scope = ["sandbox/diagnostics.py"]
    verification = ["python -c \"import sys; sys.exit(0)\""]

    outcome = runner.run_e2e_workflow(
        intent=intent,
        target_task_id=target_task_id,
        scope=scope,
        verification=verification,
        auto_apply=True,
        check_credentials=False,
    )

    # 1. Observability: outcome contains total usage and stage usage
    assert outcome.usage is not None
    assert outcome.usage.total_tokens is not None
    assert outcome.usage.total_tokens > 0
    assert outcome.stage_usage is not None
    assert "architect" in outcome.stage_usage
    assert "executor" in outcome.stage_usage
    assert "reviewer" in outcome.stage_usage

    # 2. Portability: all paths in outcome must be relative, not absolute
    for path_str in [outcome.task_file_path, outcome.implementation_report_path, outcome.review_report_path]:
        assert path_str is not None
        assert not path_str.startswith("C:")
        assert not path_str.startswith("c:")
        assert not path_str.startswith("file:///")
        assert not path_str.startswith("/")
        assert "\\" not in path_str

    # 3. Portability: generated implementation and review reports must contain Token Observability
    # and MUST NOT contain any machine-specific paths
    impl_report = repo_root / outcome.implementation_report_path
    rev_report = repo_root / outcome.review_report_path
    impl_content = impl_report.read_text(encoding="utf-8")
    rev_content = rev_report.read_text(encoding="utf-8")

    for content in [impl_content, rev_content]:
        assert "## Token Observability" in content
        assert "- **Input Tokens:**" in content
        assert "- **Output Tokens:**" in content
        assert "- **Total Tokens:**" in content
        # Assert prohibited machine-specific strings
        assert "file:///" not in content
        assert "OneDrive" not in content
        assert "Desktop" not in content
        assert "C:\\Users" not in content
        assert "C:/Users" not in content
        assert "c:/users" not in content
        assert "c:\\users" not in content


def test_sanitize_portable_paths_comprehensive(tmp_path):
    repo_root = tmp_path / "Desktop" / "Jester"
    repo_root.mkdir(parents=True)

    test_str = (
        f"See file at file:///{repo_root.as_posix()}/jester_bridge/foo.py\n"
        f"Windows path: C:\\Users\\johndoe\\OneDrive\\Desktop\\Jester\\jester_bridge\\bar.py\n"
        f"Posix path: /Users/johndoe/Desktop/Jester/jester_bridge/baz.py\n"
        f"Lowercase file URL: file:///c:/users/johndoe/onedrive/desktop/jester/tests/bridge/test_foo.py\n"
        f"Direct repo ref: {repo_root.as_posix()}/tests/bridge/test_bar.py\n"
    )

    sanitized = sanitize_portable_paths(test_str, repo_root)

    assert "file:///" not in sanitized
    assert "OneDrive" not in sanitized
    assert "Desktop" not in sanitized
    assert "johndoe" not in sanitized
    assert "C:\\Users" not in sanitized
    assert "C:/Users" not in sanitized
    assert "c:/users" not in sanitized
    assert "jester_bridge/foo.py" in sanitized
    assert "jester_bridge/bar.py" in sanitized
    assert "jester_bridge/baz.py" in sanitized
    assert "tests/bridge/test_foo.py" in sanitized
    assert "tests/bridge/test_bar.py" in sanitized
