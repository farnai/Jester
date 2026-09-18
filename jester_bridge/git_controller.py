"""
Controlled Git Delivery Engine for the JESTER Provider-Agnostic AI Bridge (TASK-0007).

Provides bounded, auditable, and non-autonomous Git delivery operations:
- Enforces mandatory human sign-off before commit.
- Requires separate, explicit push authorization (no automatic push, no force push).
- Stages ONLY explicitly approved files (NEVER git add . or git add -A).
- Validates staged diff against the approved delivery set before committing.
- Rejects writes to protected paths (.git, .env, AGENTS.md, migrations).
- Rejects destructive working tree operations (reset --hard, clean -fd).
- Uses safe, bounded subprocess execution with timeouts.
- Completely decoupled from AI providers.
"""
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from .core import BridgeError
from .orchestration import OrchestrationSession, OrchestrationStage, ReviewVerdict
from .protocol import Task
from .runtime import PROTECTED_PATHS, is_path_in_scope


DEFAULT_GIT_TIMEOUT = 30.0


class GitControllerError(BridgeError):
    """Base exception for Git delivery errors."""
    pass


class GitSecurityError(GitControllerError):
    """Raised when an operation violates Git security or protected path rules."""
    pass


class GitAuthorizationError(GitControllerError):
    """Raised when an operation lacks explicit human approval or push authorization."""
    pass


class GitDiffMismatchError(GitControllerError):
    """Raised when staged diff content does not match the approved delivery set."""
    pass


class GitStatusResult(BaseModel):
    """Structured representation of repository git status."""
    branch: str
    is_clean: bool
    modified_files: List[str] = Field(default_factory=list)
    untracked_files: List[str] = Field(default_factory=list)
    staged_files: List[str] = Field(default_factory=list)
    raw_status: str = ""


class GitOperationResult(BaseModel):
    """Normalized structured result of a Git operation."""
    operation: str  # "inspect", "stage", "commit", "push"
    success: bool
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    files_affected: List[str] = Field(default_factory=list)
    commit_hash: Optional[str] = None
    branch: Optional[str] = None
    remote: Optional[str] = None
    pushed: bool = False
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CommitAuthorization(BaseModel):
    """
    Explicit human authorization token required to execute a Git commit.
    Reuses the existing human sign-off boundary.
    """
    task_id: str
    approver: str
    approved_files: List[str]
    commit_message: str
    notes: Optional[str] = None


class PushAuthorization(BaseModel):
    """
    Separate, explicit authorization required to push commits to an upstream remote.
    Human commit approval does NOT automatically authorize push.
    """
    task_id: str
    approver: str
    remote: str = "origin"
    branch: Optional[str] = None


class GitController:
    """
    Controlled, provider-neutral Git delivery controller.
    Executes explicit, bounded Git operations following verified human sign-off.
    """

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        timeout: float = DEFAULT_GIT_TIMEOUT,
    ):
        self.repo_root = (repo_root or Path.cwd()).resolve()
        self.timeout = timeout

    def _run_git(self, args: List[str]) -> Tuple[int, str, str]:
        """
        Executes a git command safely via subprocess with parameterized arguments and timeout.
        Does NOT use shell=True.
        """
        # Block dangerous or destructive git commands unconditionally
        forbidden_commands = {
            "clean", "reset", "restore", "rebase", "checkout", "stash",
        }
        if args and args[0] in forbidden_commands:
            raise GitSecurityError(f"Destructive git command '{args[0]}' is strictly prohibited.")

        for arg in args:
            if arg in ("--force", "-f", "--force-with-lease"):
                raise GitSecurityError("Force operations ('--force', '-f') are strictly prohibited.")

        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            return res.returncode, res.stdout, res.stderr
        except subprocess.TimeoutExpired:
            return 124, "", f"Git command 'git {' '.join(args)}' timed out after {self.timeout}s."
        except Exception as e:
            return 1, "", f"Git execution error: {str(e)}"

    def inspect_status(self) -> GitStatusResult:
        """Inspects current working tree status without modifying anything."""
        # 1. Get current branch
        _, branch_out, _ = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        branch = branch_out.strip() or "unknown"

        # 2. Get status --porcelain
        code, stdout, _ = self._run_git(["status", "--porcelain"])
        modified: List[str] = []
        untracked: List[str] = []
        staged: List[str] = []

        if code == 0 and stdout:
            for line in stdout.splitlines():
                if len(line) < 3:
                    continue
                index_status = line[0]
                worktree_status = line[1]
                path = line[3:].strip().replace("\\", "/")

                if index_status in ("M", "A", "D", "R"):
                    staged.append(path)
                if worktree_status == "M":
                    modified.append(path)
                elif worktree_status == "?" and index_status == "?":
                    untracked.append(path)

        is_clean = len(modified) == 0 and len(untracked) == 0 and len(staged) == 0
        return GitStatusResult(
            branch=branch,
            is_clean=is_clean,
            modified_files=sorted(list(set(modified))),
            untracked_files=sorted(list(set(untracked))),
            staged_files=sorted(list(set(staged))),
            raw_status=stdout,
        )

    def inspect_diff(self, staged: bool = False, files: Optional[List[str]] = None) -> str:
        """Returns the current working tree or staged diff, optionally filtered by file list."""
        cmd = ["diff", "--cached"] if staged else ["diff"]
        if files:
            cmd.append("--")
            cmd.extend(files)
        code, stdout, _ = self._run_git(cmd)
        return stdout if code == 0 else ""

    def validate_delivery(
        self,
        task: Task,
        session: OrchestrationSession,
        approved_files: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Validates delivery prerequisites:
        1. Reviewer verdict must be PASS.
        2. Session must be in AWAITING_HUMAN_SIGNOFF or COMPLETED.
        3. Human sign-off must be present.
        4. Approved files must be non-empty.
        5. No protected paths may be in approved_files.
        6. Approved files must adhere to task.scope.
        """
        errors: List[str] = []

        if not session.review_result or session.review_result.verdict != ReviewVerdict.PASS:
            errors.append("Reviewer verdict is not PASS. Delivery requires independent reviewer pass.")

        valid_stages = (OrchestrationStage.AWAITING_HUMAN_SIGNOFF, OrchestrationStage.COMPLETED)
        if session.current_stage not in valid_stages:
            errors.append(
                f"Invalid session stage '{session.current_stage.value}'. "
                "Delivery is only authorized at human sign-off gate or completed stage."
            )

        if not session.human_signoff_by:
            errors.append("Human sign-off has not been granted. Delivery requires explicit human approval.")

        if not approved_files:
            errors.append("Approved delivery file list is empty. Explicit file list is required.")

        for f in approved_files:
            norm_f = f.replace("\\", "/").strip().lstrip("/")
            for protected in PROTECTED_PATHS:
                if norm_f == protected or norm_f.startswith(f"{protected}/"):
                    errors.append(f"Approved file '{f}' attempts to deliver protected path '{protected}'.")
            if task.scope and not is_path_in_scope(norm_f, task.scope):
                errors.append(f"Approved file '{f}' falls outside authorized task.scope {task.scope}.")

        return len(errors) == 0, errors

    def stage_approved_files(self, approved_files: List[str]) -> GitOperationResult:
        """
        Stages ONLY the explicitly approved files.
        Never runs 'git add .' or 'git add -A'.
        """
        if not approved_files:
            return GitOperationResult(
                operation="stage",
                success=False,
                error="No files specified for staging.",
            )

        # Validate that no protected paths are being staged
        for f in approved_files:
            norm_f = f.replace("\\", "/").strip().lstrip("/")
            for protected in PROTECTED_PATHS:
                if norm_f == protected or norm_f.startswith(f"{protected}/"):
                    return GitOperationResult(
                        operation="stage",
                        success=False,
                        error=f"Cannot stage protected path: '{protected}'",
                    )

        cmd = ["add", "--"] + [f.replace("\\", "/") for f in approved_files]
        code, stdout, stderr = self._run_git(cmd)

        if code != 0:
            return GitOperationResult(
                operation="stage",
                success=False,
                exit_code=code,
                stdout=stdout,
                stderr=stderr,
                error=f"Failed to stage approved files: {stderr}",
            )

        return GitOperationResult(
            operation="stage",
            success=True,
            exit_code=0,
            stdout=stdout,
            files_affected=approved_files,
        )

    def validate_staged_diff(self, approved_files: List[str]) -> Tuple[bool, str]:
        """
        Verifies that ONLY approved files are staged.
        Compares `git diff --cached --name-only` against approved_files.
        """
        code, stdout, stderr = self._run_git(["diff", "--cached", "--name-only"])
        if code != 0:
            return False, f"Failed to inspect staged files: {stderr}"

        staged_files = [line.strip().replace("\\", "/") for line in stdout.splitlines() if line.strip()]
        norm_approved = {f.replace("\\", "/").strip().lstrip("/") for f in approved_files}

        unauthorized_staged = set(staged_files) - norm_approved
        if unauthorized_staged:
            return False, f"Staged diff contains unauthorized files: {sorted(list(unauthorized_staged))}"

        if not staged_files:
            return False, "No changes are staged for delivery."

        return True, "Staged diff valid"

    def commit(
        self,
        authorization: CommitAuthorization,
        session: Optional[OrchestrationSession] = None,
        task: Optional[Task] = None,
    ) -> GitOperationResult:
        """
        Creates a Git commit only after explicit human approval and staged diff validation.
        """
        # 1. Authorization check
        if not authorization or not authorization.approver:
            raise GitAuthorizationError("Commit refused: Missing explicit human approval authorization.")

        if not authorization.commit_message or not authorization.commit_message.strip():
            raise GitAuthorizationError("Commit refused: Commit message cannot be empty.")

        # 2. Lifecycle & Session verification if session is provided
        if session:
            t = task or session.task
            valid, errors = self.validate_delivery(t, session, authorization.approved_files)
            if not valid:
                return GitOperationResult(
                    operation="commit",
                    success=False,
                    error="Delivery validation failed: " + "; ".join(errors),
                )

        # 3. Stage ONLY approved files
        stage_res = self.stage_approved_files(authorization.approved_files)
        if not stage_res.success:
            return GitOperationResult(
                operation="commit",
                success=False,
                error=stage_res.error,
            )

        # 4. Verify that the staged diff matches the approved delivery set
        staged_ok, staged_msg = self.validate_staged_diff(authorization.approved_files)
        if not staged_ok:
            return GitOperationResult(
                operation="commit",
                success=False,
                error=f"Staged diff mismatch: {staged_msg}",
            )

        # 5. Execute commit
        commit_cmd = ["commit", "-m", authorization.commit_message.strip()]
        code, stdout, stderr = self._run_git(commit_cmd)

        if code != 0:
            return GitOperationResult(
                operation="commit",
                success=False,
                exit_code=code,
                stdout=stdout,
                stderr=stderr,
                error=f"Git commit command failed: {stderr}",
            )

        # 6. Extract commit hash
        _, hash_out, _ = self._run_git(["rev-parse", "HEAD"])
        commit_hash = hash_out.strip()

        # 7. Extract current branch
        _, branch_out, _ = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        branch = branch_out.strip()

        return GitOperationResult(
            operation="commit",
            success=True,
            exit_code=0,
            stdout=stdout,
            files_affected=authorization.approved_files,
            commit_hash=commit_hash,
            branch=branch,
        )

    def push(self, authorization: PushAuthorization) -> GitOperationResult:
        """
        Pushes committed changes to the configured upstream remote.
        Requires separate, explicit PushAuthorization.
        Never executes force push.
        """
        if not authorization or not authorization.approver:
            raise GitAuthorizationError("Push refused: Missing explicit push authorization.")

        remote = authorization.remote or "origin"
        _, branch_out, _ = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        branch = authorization.branch or branch_out.strip()

        if not branch or branch == "HEAD":
            return GitOperationResult(
                operation="push",
                success=False,
                error="Cannot push detached HEAD.",
            )

        # Execute safe push with explicit remote and branch
        cmd = ["push", remote, branch]
        code, stdout, stderr = self._run_git(cmd)

        if code != 0:
            return GitOperationResult(
                operation="push",
                success=False,
                exit_code=code,
                stdout=stdout,
                stderr=stderr,
                remote=remote,
                branch=branch,
                error=f"Git push failed: {stderr or stdout}",
            )

        return GitOperationResult(
            operation="push",
            success=True,
            exit_code=0,
            stdout=stdout,
            remote=remote,
            branch=branch,
            pushed=True,
        )
