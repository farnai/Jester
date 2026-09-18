"""
Unit and Integration Tests for GitController and Post-Approval Controlled Delivery (TASK-0007).

Verifies:
1. Inspect status
2. Inspect diff
3. Refuse commit without human approval
4. Refuse commit when reviewer not passed
5. Explicit human approval allows commit
6. Only approved files staged
7. Unexpected modified file handling
8. Protected file (.env) rejection
9. Protected directory rejection
10. Staged diff mismatch rejection
11. Commit success & commit hash capture
12. Push not authorized
13. Push explicitly authorized with safe local remote
14. Force push strictly forbidden
15. Destructive commands strictly forbidden
16. Timeout bounded execution
17. Structured result contract verification
18. Controlled workflow integration
19. Zero provider coupling
20. Zero automatic Git execution
"""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from typing import List, Optional
import pytest

from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig
from jester_bridge.contracts import InvocationResult, InvocationStatus, UsageMetrics
from jester_bridge.core import BridgeCore
from jester_bridge.git_controller import (
    CommitAuthorization,
    GitAuthorizationError,
    GitController,
    GitOperationResult,
    GitSecurityError,
    GitStatusResult,
    PushAuthorization,
)
from jester_bridge.orchestration import (
    BridgeOrchestrator,
    OrchestrationSession,
    OrchestrationStage,
    ReviewResult,
    ReviewVerdict,
)
from jester_bridge.preflight import PreflightValidator
from jester_bridge.protocol import Task
from jester_bridge.runtime import BoundedWorkspaceRuntime
from jester_bridge.testing import MockProviderA, MockProviderB
from jester_bridge.workflow import ControlledWorkflowRunner


def _init_isolated_git_repo(path: Path) -> GitController:
    """Initializes a self-contained local Git repository for testing."""
    subprocess.run(["git", "init"], cwd=str(path), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test Deliverer"], cwd=str(path), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "deliverer@jester.local"], cwd=str(path), check=True, capture_output=True)

    # Base initial commit so HEAD exists and default branch is formed
    readme = path / "README.md"
    readme.write_text("# Jester Isolated Test Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=str(path), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial baseline commit"], cwd=str(path), check=True, capture_output=True)

    return GitController(repo_root=path)


def _create_mock_session(
    task_id: str,
    scope: List[str],
    verdict: ReviewVerdict = ReviewVerdict.PASS,
    human_signoff: Optional[str] = "lead-founder",
    stage: OrchestrationStage = OrchestrationStage.AWAITING_HUMAN_SIGNOFF,
) -> OrchestrationSession:
    task = Task(
        id=task_id,
        title=f"Task: {task_id}",
        type="feature",
        status="review",
        goal="Test Git Delivery",
        scope=scope,
        constraints=["Preserve invariants"],
        acceptance_criteria=["Pass review"],
        verification=["pytest"],
        required_capabilities={"code_generation"},
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    raw = InvocationResult(
        request_id="req-mock",
        task_id=task_id,
        status=InvocationStatus.SUCCESS,
        agent_id="critic",
        role="reviewer",
        provider="mock",
        model="mock-v1",
        summary="Review completed",
        completed_at=datetime.now(timezone.utc).isoformat(),
        usage=UsageMetrics(input_tokens=10, output_tokens=10, total_tokens=20),
    )
    rev_res = ReviewResult(
        task_id=task_id,
        verdict=verdict,
        summary="Review completed with verdict.",
        raw_result=raw,
    )
    return OrchestrationSession(
        session_id=f"session-{task_id}",
        task=task,
        current_stage=stage,
        review_result=rev_res,
        human_signoff_by=human_signoff,
    )


# -------------------------------------------------------------------
# TEST 1 — Inspect status
# -------------------------------------------------------------------
def test_01_inspect_status(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    status_initial = controller.inspect_status()
    assert isinstance(status_initial, GitStatusResult)
    assert status_initial.is_clean is True
    assert len(status_initial.modified_files) == 0
    assert len(status_initial.untracked_files) == 0
    assert status_initial.branch in ("master", "main")

    # Introduce modified file and untracked file
    readme = tmp_path / "README.md"
    readme.write_text("# Updated README\n", encoding="utf-8")
    new_file = tmp_path / "new_feature.py"
    new_file.write_text("x = 1\n", encoding="utf-8")

    status_dirty = controller.inspect_status()
    assert status_dirty.is_clean is False
    assert "README.md" in status_dirty.modified_files
    assert "new_feature.py" in status_dirty.untracked_files


# -------------------------------------------------------------------
# TEST 2 — Inspect diff
# -------------------------------------------------------------------
def test_02_inspect_diff(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text("# Line 1\n# Line 2 Added\n", encoding="utf-8")

    diff_unstaged = controller.inspect_diff(staged=False)
    assert "Line 2 Added" in diff_unstaged

    # Stage changes
    controller.stage_approved_files(["README.md"])
    diff_staged = controller.inspect_diff(staged=True)
    assert "Line 2 Added" in diff_staged


# -------------------------------------------------------------------
# TEST 3 — No human approval
# -------------------------------------------------------------------
def test_03_refuse_commit_without_human_approval(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    src = tmp_path / "app.py"
    src.write_text("print('hello')\n", encoding="utf-8")

    # Case A: Missing approver in CommitAuthorization raises GitAuthorizationError
    with pytest.raises(GitAuthorizationError, match="Missing explicit human approval"):
        invalid_auth = CommitAuthorization(
            task_id="TASK-01",
            approver="",
            approved_files=["app.py"],
            commit_message="Feat: app",
        )
        controller.commit(invalid_auth)

    # Case B: Session has no human signoff
    session_no_signoff = _create_mock_session(
        task_id="TASK-01",
        scope=["app.py"],
        human_signoff=None,
    )
    auth = CommitAuthorization(
        task_id="TASK-01",
        approver="founder",
        approved_files=["app.py"],
        commit_message="Feat: app",
    )
    res = controller.commit(auth, session=session_no_signoff)
    assert res.success is False
    assert "Human sign-off has not been granted" in (res.error or "")


# -------------------------------------------------------------------
# TEST 4 — Reviewer not passed
# -------------------------------------------------------------------
def test_04_refuse_commit_when_reviewer_not_passed(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    src = tmp_path / "app.py"
    src.write_text("print('unreviewed')\n", encoding="utf-8")

    session_rework = _create_mock_session(
        task_id="TASK-02",
        scope=["app.py"],
        verdict=ReviewVerdict.REWORK_REQUIRED,
        human_signoff="lead-founder",
    )
    auth = CommitAuthorization(
        task_id="TASK-02",
        approver="lead-founder",
        approved_files=["app.py"],
        commit_message="Feat: unreviewed app",
    )
    res = controller.commit(auth, session=session_rework)
    assert res.success is False
    assert "Reviewer verdict is not PASS" in (res.error or "")


# -------------------------------------------------------------------
# TEST 5 — Explicit human approval
# -------------------------------------------------------------------
def test_05_explicit_human_approval_allows_commit(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    src = tmp_path / "app.py"
    src.write_text("print('verified and approved')\n", encoding="utf-8")

    session = _create_mock_session(
        task_id="TASK-03",
        scope=["app.py"],
        verdict=ReviewVerdict.PASS,
        human_signoff="lead-founder",
    )
    auth = CommitAuthorization(
        task_id="TASK-03",
        approver="lead-founder",
        approved_files=["app.py"],
        commit_message="Feat: verified and approved app",
    )
    res = controller.commit(auth, session=session)
    assert res.success is True
    assert res.commit_hash is not None
    assert res.files_affected == ["app.py"]


# -------------------------------------------------------------------
# TEST 6 — Only approved files staged
# -------------------------------------------------------------------
def test_06_only_approved_files_staged(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    file_a = tmp_path / "file_a.py"
    file_b = tmp_path / "file_b.py"
    file_a.write_text("a = 1\n", encoding="utf-8")
    file_b.write_text("b = 2\n", encoding="utf-8")

    # Stage ONLY file_a.py
    res = controller.stage_approved_files(["file_a.py"])
    assert res.success is True

    status = controller.inspect_status()
    assert "file_a.py" in status.staged_files
    assert "file_b.py" not in status.staged_files
    assert "file_b.py" in status.untracked_files


# -------------------------------------------------------------------
# TEST 7 — Unexpected modified file handling
# -------------------------------------------------------------------
def test_07_unexpected_modified_file(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    file_a = tmp_path / "file_a.py"
    unrelated = tmp_path / "unrelated.py"
    file_a.write_text("a = 1\n", encoding="utf-8")
    unrelated.write_text("unrelated = True\n", encoding="utf-8")

    # If someone manually staged an unrelated file, validate_staged_diff must reject delivery
    subprocess.run(["git", "add", "unrelated.py"], cwd=str(tmp_path), check=True)

    session = _create_mock_session(task_id="TASK-04", scope=["file_a.py"])
    auth = CommitAuthorization(
        task_id="TASK-04",
        approver="founder",
        approved_files=["file_a.py"],
        commit_message="Feat: file a",
    )
    res = controller.commit(auth, session=session)
    assert res.success is False
    assert "Staged diff mismatch" in (res.error or "")
    assert "unauthorized files" in (res.error or "")


# -------------------------------------------------------------------
# TEST 8 — Protected file (.env) rejection
# -------------------------------------------------------------------
def test_08_protected_file_rejection(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET_KEY=12345\n", encoding="utf-8")

    # Attempt to stage .env directly
    res_stage = controller.stage_approved_files([".env"])
    assert res_stage.success is False
    assert "Cannot stage protected path" in (res_stage.error or "")

    # Attempt to validate delivery of .env
    session = _create_mock_session(task_id="TASK-ENV", scope=[".env"])
    valid, errors = controller.validate_delivery(session.task, session, [".env"])
    assert valid is False
    assert any("protected path" in err for err in errors)


# -------------------------------------------------------------------
# TEST 9 — Protected directory rejection
# -------------------------------------------------------------------
def test_09_protected_directory_rejection(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    mig_dir = tmp_path / "supabase" / "migrations"
    mig_dir.mkdir(parents=True, exist_ok=True)
    mig_file = mig_dir / "999_injected.sql"
    mig_file.write_text("SELECT 1;", encoding="utf-8")

    res_stage = controller.stage_approved_files(["supabase/migrations/999_injected.sql"])
    assert res_stage.success is False
    assert "Cannot stage protected path" in (res_stage.error or "")


# -------------------------------------------------------------------
# TEST 10 — Staged diff mismatch
# -------------------------------------------------------------------
def test_10_staged_diff_mismatch(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    # Staging nothing, then validating
    valid, msg = controller.validate_staged_diff(["non_existent.py"])
    assert valid is False
    assert "No changes are staged" in msg


# -------------------------------------------------------------------
# TEST 11 — Commit success
# -------------------------------------------------------------------
def test_11_commit_success(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    code = tmp_path / "module.py"
    code.write_text("def run(): return 42\n", encoding="utf-8")

    session = _create_mock_session(task_id="TASK-SUCCESS", scope=["module.py"])
    auth = CommitAuthorization(
        task_id="TASK-SUCCESS",
        approver="founder-approver",
        approved_files=["module.py"],
        commit_message="Feat: add run method",
        notes="Ship it",
    )
    res = controller.commit(auth, session=session)
    assert res.success is True
    assert res.commit_hash is not None
    assert len(res.commit_hash) >= 7
    assert res.files_affected == ["module.py"]

    # Verify git log
    log_out = subprocess.run(
        ["git", "show", "--stat", res.commit_hash],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "module.py" in log_out
    assert "README.md" not in log_out


# -------------------------------------------------------------------
# TEST 12 — Push not authorized
# -------------------------------------------------------------------
def test_12_push_not_authorized(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)

    # Calling push without valid PushAuthorization raises GitAuthorizationError
    with pytest.raises(GitAuthorizationError, match="Missing explicit push authorization"):
        invalid_push_auth = PushAuthorization(
            task_id="TASK-PUSH",
            approver="",
        )
        controller.push(invalid_push_auth)


# -------------------------------------------------------------------
# TEST 13 — Push explicitly authorized with safe local remote
# -------------------------------------------------------------------
def test_13_push_explicitly_authorized(tmp_path: Path):
    # Set up remote bare repository
    remote_bare = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote_bare)], check=True, capture_output=True)

    # Set up working repository
    work_repo = tmp_path / "work"
    work_repo.mkdir()
    controller = _init_isolated_git_repo(work_repo)

    # Attach remote
    subprocess.run(
        ["git", "remote", "add", "origin", str(remote_bare.resolve())],
        cwd=str(work_repo),
        check=True,
        capture_output=True,
    )

    # Commit a feature
    feat = work_repo / "feat.py"
    feat.write_text("x = 100\n", encoding="utf-8")
    session = _create_mock_session(task_id="TASK-PUSH", scope=["feat.py"])
    commit_auth = CommitAuthorization(
        task_id="TASK-PUSH",
        approver="founder",
        approved_files=["feat.py"],
        commit_message="Feat: feat 100",
    )
    commit_res = controller.commit(commit_auth, session=session)
    assert commit_res.success is True

    # Push with explicit authorization
    push_auth = PushAuthorization(
        task_id="TASK-PUSH",
        approver="founder",
        remote="origin",
    )
    push_res = controller.push(push_auth)
    assert push_res.success is True
    assert push_res.pushed is True
    assert push_res.remote == "origin"

    # Verify bare remote received the commit
    rev_bare = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(remote_bare),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert rev_bare == commit_res.commit_hash


# -------------------------------------------------------------------
# TEST 14 — Force push strictly forbidden
# -------------------------------------------------------------------
def test_14_force_push_forbidden(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    with pytest.raises(GitSecurityError, match="Force operations .* strictly prohibited"):
        controller._run_git(["push", "--force", "origin", "main"])

    with pytest.raises(GitSecurityError, match="Force operations .* strictly prohibited"):
        controller._run_git(["push", "-f", "origin", "main"])

    with pytest.raises(GitSecurityError, match="Force operations .* strictly prohibited"):
        controller._run_git(["push", "--force-with-lease", "origin", "main"])


# -------------------------------------------------------------------
# TEST 15 — Destructive commands strictly forbidden
# -------------------------------------------------------------------
def test_15_destructive_commands_forbidden(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)

    destructive = [
        ["reset", "--hard"],
        ["clean", "-fd"],
        ["checkout", "--", "."],
        ["restore", "."],
        ["rebase", "main"],
        ["stash", "drop"],
    ]
    for cmd in destructive:
        with pytest.raises(GitSecurityError, match="Destructive git command .* strictly prohibited"):
            controller._run_git(cmd)


# -------------------------------------------------------------------
# TEST 16 — Timeout bounded execution
# -------------------------------------------------------------------
def test_16_timeout(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    # Configure an impractically small timeout to trigger timeout handling safely
    controller.timeout = 0.000001
    code, stdout, stderr = controller._run_git(["status"])
    assert code == 124
    assert "timed out after" in stderr


# -------------------------------------------------------------------
# TEST 17 — Structured result contract verification
# -------------------------------------------------------------------
def test_17_structured_result(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)
    status = controller.inspect_status()
    assert isinstance(status, GitStatusResult)
    assert hasattr(status, "branch")
    assert hasattr(status, "is_clean")
    assert hasattr(status, "modified_files")
    assert hasattr(status, "untracked_files")
    assert hasattr(status, "staged_files")

    file_test = tmp_path / "test.py"
    file_test.write_text("pass\n", encoding="utf-8")
    stage_res = controller.stage_approved_files(["test.py"])
    assert isinstance(stage_res, GitOperationResult)
    assert stage_res.operation == "stage"
    assert stage_res.success is True
    assert stage_res.files_affected == ["test.py"]
    assert stage_res.timestamp is not None


# -------------------------------------------------------------------
# TEST 18 — Controlled workflow integration
# -------------------------------------------------------------------
def test_18_workflow_integration(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)

    mock_arch_resp = "Title: Delivery Task\nScope: src/core.py\n"
    mock_exec_resp = "```python:src/core.py\ndef version(): return '1.0'\n```\n"
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
    runner = ControlledWorkflowRunner(
        core=core,
        repo_root=tmp_path,
        runtime=runtime,
        git_controller=controller,
    )

    # 1. Run workflow -> stops at AWAITING_HUMAN_SIGNOFF
    outcome = runner.run_e2e_workflow(
        intent="Create core version function",
        target_task_id="TASK-DELIVERY",
        scope=["src/core.py"],
        verification=["python -c \"import sys; sys.exit(0)\""],
        auto_apply=True,
        check_credentials=False,
    )
    assert outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert outcome.git_delivery is None

    # 2. Complete human approval with commit authorization
    commit_auth = CommitAuthorization(
        task_id="TASK-DELIVERY",
        approver="founder",
        approved_files=["src/core.py"],
        commit_message="Feat: add version function",
    )
    completed_path = runner.complete_human_approval(
        session=outcome.session,
        approver="founder",
        notes="LGTM",
        commit_auth=commit_auth,
    )
    assert completed_path.exists()
    assert runner.last_delivery_result is not None
    assert runner.last_delivery_result.success is True
    assert runner.last_delivery_result.commit_hash is not None


# -------------------------------------------------------------------
# TEST 19 — Zero provider coupling
# -------------------------------------------------------------------
def test_19_no_provider_coupling():
    import inspect
    import jester_bridge.git_controller as gc_mod

    source = inspect.getsource(gc_mod)
    # Ensure no direct provider imports
    assert "import openai" not in source
    assert "import google.generativeai" not in source
    assert "from .openai_provider" not in source
    assert "from .google_provider" not in source

    # Instantiating GitController does not require BridgeCore or any AI Provider
    gc = GitController()
    assert gc is not None


# -------------------------------------------------------------------
# TEST 20 — Zero automatic Git execution
# -------------------------------------------------------------------
def test_20_no_automatic_git(tmp_path: Path):
    controller = _init_isolated_git_repo(tmp_path)

    mock_arch_resp = "Title: Auto Task\nScope: src/demo.py\n"
    mock_exec_resp = "```python:src/demo.py\nx = 1\n```\n"

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
    runner = ControlledWorkflowRunner(
        core=core,
        repo_root=tmp_path,
        runtime=runtime,
        git_controller=controller,
    )

    # Initial commit count
    rev_count_before = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    outcome = runner.run_e2e_workflow(
        intent="Create demo file",
        target_task_id="TASK-NO-AUTO",
        scope=["src/demo.py"],
        verification=["python -c \"import sys; sys.exit(0)\""],
        auto_apply=True,
        check_credentials=False,
    )

    # Outcome halts at AWAITING_HUMAN_SIGNOFF
    assert outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert outcome.git_delivery is None

    # Verify no commit was made automatically
    rev_count_after = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert rev_count_before == rev_count_after
