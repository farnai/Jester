"""
Bounded Workspace Runtime for the JESTER Provider-Agnostic AI Bridge.

Provides safe, bounded, and auditable repository execution capabilities:
- Enforces strict scope boundaries (only paths within task.scope may be modified).
- Rejects writes to protected paths (.git, .env, AGENTS.md, migrations).
- Applies structured code modifications or patches.
- Executes declared verification commands (e.g. pytest).
- Supports automatic rollback upon test failure or abort.
- Contains zero provider-specific or vendor SDK logic.
"""
import difflib
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from .contracts import InvocationStatus
from .core import BridgeError
from .protocol import Task


# Sensitive files/directories that may NEVER be modified by an automated runtime
PROTECTED_PATHS: Set[str] = {
    ".git",
    ".env",
    "AGENTS.md",
    "supabase/migrations",
    "migrations",
}


class RuntimeError(BridgeError):
    """Base exception for runtime execution errors."""
    pass


class ScopeViolationError(RuntimeError):
    """Raised when an operation attempts to touch files outside authorized task.scope."""
    pass


class RuntimeExecutionResult(BaseModel):
    """Normalized output produced by the BoundedWorkspaceRuntime."""
    status: InvocationStatus
    files_modified: List[str] = Field(default_factory=list)
    diff: str = ""
    verification_passed: bool = False
    verification_output: str = ""
    error_message: Optional[str] = None
    reverted: bool = False


class FileChange(BaseModel):
    """Represents an individual file modification or creation."""
    relative_path: str
    content: str
    action: str = "write"  # "write" or "delete"


def is_path_in_scope(target_path: str, allowed_scopes: List[str]) -> bool:
    """
    Checks whether target_path matches at least one prefix or exact pattern in allowed_scopes.
    Normalizes path separators to forward slashes.
    """
    normalized_target = target_path.replace("\\", "/").lstrip("/")

    # Check protected paths first
    for protected in PROTECTED_PATHS:
        if normalized_target == protected or normalized_target.startswith(f"{protected}/"):
            return False

    # Check allowed scopes
    for scope in allowed_scopes:
        normalized_scope = scope.replace("\\", "/").lstrip("/")
        if normalized_scope.endswith("/"):
            if normalized_target.startswith(normalized_scope):
                return True
        else:
            if normalized_target == normalized_scope or normalized_target.startswith(f"{normalized_scope}/"):
                return True
    return False


def task_expects_code_changes(task: Task) -> bool:
    """
    Determines whether a task semantically expects repository code/file modifications.
    Tasks requiring code_generation or refactoring capabilities, or tasks of type
    feature, bugfix, refactor, or implementation are expected to produce changes.
    """
    if "code_generation" in task.required_capabilities or "refactoring" in task.required_capabilities:
        return True
    if task.type.lower() in ("feature", "bugfix", "refactor", "implementation"):
        return True
    return False


def extract_file_changes_from_text(text: str) -> List[FileChange]:
    """
    Extracts structured file modifications from LLM output.
    Looks for standard markdown code blocks with file path markers, e.g.:
    ```python:relative/path/to/file.py
    code
    ```
    or
    <!-- FILE: relative/path/to/file.py -->
    ```python
    code
    ```
    """
    changes: List[FileChange] = []

    # Pattern A: ```language:filepath
    pattern_a = re.compile(r"```[a-zA-Z0-9_\-\.]*:([a-zA-Z0-9_\-\./\\]+)\r?\n(.*?)```", re.DOTALL)
    for match in pattern_a.finditer(text):
        file_path = match.group(1).strip()
        content = match.group(2)
        changes.append(FileChange(relative_path=file_path, content=content))

    # Pattern B: <!-- FILE: filepath --> ... ```code```
    pattern_b = re.compile(
        r"(?:<!--|#|\/\/)\s*FILE:\s*([a-zA-Z0-9_\-\./\\]+)\s*(?:-->)?\r?\n```[a-zA-Z0-9_\-\.]*\r?\n(.*?)```",
        re.DOTALL,
    )
    for match in pattern_b.finditer(text):
        file_path = match.group(1).strip()
        content = match.group(2)
        # Avoid duplicate if matched pattern_a
        if not any(c.relative_path == file_path for c in changes):
            changes.append(FileChange(relative_path=file_path, content=content))

    # Pattern C: (File:|### File:|**File:**) `?filepath`? \n ```...```
    pattern_c = re.compile(
        r"(?:###\s*|\*\*|#)?\s*[Ff]ile:\s*[`'\"]?([a-zA-Z0-9_\-\./\\]+)[`'\"]?\s*(?:\*\*)?\r?\n\s*```[a-zA-Z0-9_\-\.]*\r?\n(.*?)```",
        re.DOTALL,
    )
    for match in pattern_c.finditer(text):
        file_path = match.group(1).strip()
        content = match.group(2)
        if not any(c.relative_path == file_path for c in changes):
            changes.append(FileChange(relative_path=file_path, content=content))

    return changes


class BoundedWorkspaceRuntime:
    """
    Executes and verifies changes in the local repository under strict guardrails.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = (repo_root or Path.cwd()).resolve()

    def validate_scope(self, target_relative_path: str, task: Task) -> None:
        """Enforces that target path is allowed by task.scope and not protected."""
        if not is_path_in_scope(target_relative_path, task.scope):
            raise ScopeViolationError(
                f"Path '{target_relative_path}' violates authorized scope {task.scope} "
                "or is a protected repository path."
            )

    def apply_changes(
        self, changes: List[FileChange], task: Task
    ) -> Tuple[List[str], Dict[str, Optional[str]]]:
        """
        Applies a list of FileChange operations to disk, recording original backups.
        Returns (modified_paths, backup_store).
        """
        backups: Dict[str, Optional[str]] = {}
        modified: List[str] = []

        try:
            for change in changes:
                self.validate_scope(change.relative_path, task)
                abs_path = (self.repo_root / change.relative_path).resolve()

                # Ensure path does not escape repo root
                if not abs_path.is_relative_to(self.repo_root):
                    raise ScopeViolationError(f"Path traversal detected: '{change.relative_path}'")

                # Backup existing content (or None if creating new file)
                if abs_path.exists():
                    backups[change.relative_path] = abs_path.read_text(encoding="utf-8")
                else:
                    backups[change.relative_path] = None

                abs_path.parent.mkdir(parents=True, exist_ok=True)
                abs_path.write_text(change.content, encoding="utf-8")
                modified.append(change.relative_path)

            return modified, backups
        except Exception:
            # Revert immediately if any file application fails
            self.rollback(backups)
            raise

    def rollback(self, backups: Dict[str, Optional[str]]) -> None:
        """Restores original file contents from backup_store."""
        for rel_path, original_content in backups.items():
            abs_path = self.repo_root / rel_path
            if original_content is None:
                # File was newly created; delete it
                if abs_path.exists():
                    abs_path.unlink()
            else:
                # File existed; restore content
                abs_path.write_text(original_content, encoding="utf-8")

    def run_verification(
        self, task: Task, timeout: float = 60.0
    ) -> Tuple[bool, str]:
        """
        Executes the verification commands declared in task.verification.
        Returns (all_passed: bool, combined_output: str).
        """
        if not task.verification:
            return True, "No verification commands declared."

        combined_output: List[str] = []
        all_passed = True

        env = os.environ.copy()
        venv_scripts = Path(sys.executable).parent
        if venv_scripts.exists():
            env["PATH"] = f"{venv_scripts}{os.pathsep}{env.get('PATH', '')}"

        for cmd in task.verification:
            exec_cmd = cmd
            if exec_cmd.strip().startswith("pytest "):
                exec_cmd = f'"{sys.executable}" -m pytest ' + exec_cmd.strip()[7:]
            elif exec_cmd.strip() == "pytest":
                exec_cmd = f'"{sys.executable}" -m pytest'
            elif exec_cmd.strip().startswith("python "):
                exec_cmd = f'"{sys.executable}" ' + exec_cmd.strip()[7:]

            try:
                result = subprocess.run(
                    exec_cmd,
                    shell=True,
                    cwd=str(self.repo_root),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                output = f"Command: {cmd}\nExit Code: {result.returncode}\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}\n"
                combined_output.append(output)
                if result.returncode != 0:
                    all_passed = False
                    break
            except Exception as e:
                combined_output.append(f"Command '{cmd}' failed with exception: {str(e)}")
                all_passed = False
                break

        return all_passed, "\n---\n".join(combined_output)

    def generate_unified_diff(
        self, backups: Dict[str, Optional[str]], modified_paths: List[str]
    ) -> str:
        """
        Generates a standard unified diff comparing original file states (from backups)
        against the current modified states on disk.
        """
        diff_chunks: List[str] = []
        for rel_path in modified_paths:
            orig_content = backups.get(rel_path)
            abs_path = self.repo_root / rel_path
            try:
                curr_content = abs_path.read_text(encoding="utf-8") if abs_path.exists() else ""
            except Exception:
                curr_content = ""

            orig_lines = orig_content.splitlines(keepends=True) if orig_content is not None else []
            curr_lines = curr_content.splitlines(keepends=True)

            fromfile = f"a/{rel_path}" if orig_content is not None else "/dev/null"
            tofile = f"b/{rel_path}"

            chunk = list(
                difflib.unified_diff(
                    orig_lines,
                    curr_lines,
                    fromfile=fromfile,
                    tofile=tofile,
                )
            )
            if chunk:
                diff_chunks.append("".join(chunk))

        if not diff_chunks:
            return "No file changes detected."
        return "\n".join(diff_chunks)

    def execute_and_verify(
        self,
        changes: List[FileChange],
        task: Task,
        auto_rollback_on_failure: bool = True,
    ) -> RuntimeExecutionResult:
        """
        Full atomic execution cycle:
        1. Validates scope
        2. Applies changes to disk
        3. Generates unified diff of changes
        4. Runs task.verification commands
        5. Rolls back if verification fails (if auto_rollback_on_failure=True)
        6. Returns structured RuntimeExecutionResult
        """
        if not changes:
            if task_expects_code_changes(task):
                return RuntimeExecutionResult(
                    status=InvocationStatus.FAILED,
                    files_modified=[],
                    diff="No file changes detected.",
                    verification_passed=False,
                    verification_output="No code changes were produced for a task requiring code modifications.",
                    error_message="Execution produced zero file changes for an implementation task.",
                    reverted=False,
                )
            # Legitimate no-change task (e.g. audit, investigation, docs without edits)
            if task.verification:
                passed, verification_output = self.run_verification(task)
                return RuntimeExecutionResult(
                    status=InvocationStatus.SUCCESS if passed else InvocationStatus.FAILED,
                    files_modified=[],
                    diff="No file changes detected.",
                    verification_passed=passed,
                    verification_output=verification_output,
                    error_message=None if passed else "Verification failed.",
                    reverted=False,
                )
            return RuntimeExecutionResult(
                status=InvocationStatus.SUCCESS,
                files_modified=[],
                diff="No file changes detected.",
                verification_passed=True,
                verification_output="No file changes to apply; task does not require code modifications.",
                reverted=False,
            )

        try:
            modified_paths, backups = self.apply_changes(changes, task)
        except Exception as e:
            return RuntimeExecutionResult(
                status=InvocationStatus.FAILED,
                files_modified=[],
                diff="",
                verification_passed=False,
                error_message=f"Failed to apply changes: {str(e)}",
            )

        # Capture unified diff of applied changes before verification/potential rollback
        diff = self.generate_unified_diff(backups, modified_paths)

        passed, verification_output = self.run_verification(task)

        if not passed and auto_rollback_on_failure:
            self.rollback(backups)
            return RuntimeExecutionResult(
                status=InvocationStatus.FAILED,
                files_modified=[],
                diff=diff,
                verification_passed=False,
                verification_output=verification_output,
                error_message="Verification commands failed. Changes rolled back.",
                reverted=True,
            )

        return RuntimeExecutionResult(
            status=InvocationStatus.SUCCESS if passed else InvocationStatus.FAILED,
            files_modified=modified_paths,
            diff=diff,
            verification_passed=passed,
            verification_output=verification_output,
            error_message=None if passed else "Verification failed.",
            reverted=False,
        )
