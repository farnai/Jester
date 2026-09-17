"""
Unit and Integration Tests for BoundedWorkspaceRuntime.

Verifies:
- Scope checking logic
- Protection of sensitive files (.git, .env, AGENTS.md, migrations)
- Code block extraction
- Atomic file application and rollback
- Verification command execution and rollback on failure
"""
from pathlib import Path
import pytest

from jester_bridge.protocol import Task
from jester_bridge.runtime import (
    BoundedWorkspaceRuntime,
    FileChange,
    ScopeViolationError,
    extract_file_changes_from_text,
    is_path_in_scope,
)


def test_is_path_in_scope_allowed():
    allowed_scopes = ["jester_bridge/diagnostics.py", "tests/bridge/"]
    assert is_path_in_scope("jester_bridge/diagnostics.py", allowed_scopes)
    assert is_path_in_scope("tests/bridge/test_diagnostics.py", allowed_scopes)
    assert not is_path_in_scope("backend/app/main.py", allowed_scopes)


def test_is_path_in_scope_protected_rejected():
    allowed_scopes = ["."]  # Even if broad
    assert not is_path_in_scope(".git/config", allowed_scopes)
    assert not is_path_in_scope(".env", allowed_scopes)
    assert not is_path_in_scope("AGENTS.md", allowed_scopes)
    assert not is_path_in_scope("supabase/migrations/20260101_init.sql", allowed_scopes)


def test_extract_file_changes_from_markdown():
    sample_text = (
        "Here is the proposed implementation:\n\n"
        "```python:jester_bridge/sample.py\n"
        "def sample_fn():\n"
        "    return 42\n"
        "```\n\n"
        "And the test:\n"
        "<!-- FILE: tests/bridge/test_sample.py -->\n"
        "```python\n"
        "def test_sample():\n"
        "    assert True\n"
        "```\n"
    )
    changes = extract_file_changes_from_text(sample_text)
    assert len(changes) == 2
    assert changes[0].relative_path == "jester_bridge/sample.py"
    assert "return 42" in changes[0].content
    assert changes[1].relative_path == "tests/bridge/test_sample.py"
    assert "assert True" in changes[1].content


def test_runtime_scope_violation_raises(tmp_path):
    runtime = BoundedWorkspaceRuntime(repo_root=tmp_path)
    task = Task(
        id="TASK-SCOPE-01",
        title="Scope Test",
        scope=["allowed/dir/"],
    )

    changes = [FileChange(relative_path="forbidden/file.py", content="# bad")]
    with pytest.raises(ScopeViolationError, match="violates authorized scope"):
        runtime.apply_changes(changes, task)


def test_runtime_apply_and_rollback(tmp_path):
    runtime = BoundedWorkspaceRuntime(repo_root=tmp_path)
    task = Task(
        id="TASK-APPLY-01",
        title="Apply Test",
        scope=["sandbox/"],
    )

    # 1. Apply new file
    changes = [FileChange(relative_path="sandbox/test_file.txt", content="Hello Sandbox")]
    modified, backups = runtime.apply_changes(changes, task)

    target_file = tmp_path / "sandbox" / "test_file.txt"
    assert target_file.exists()
    assert target_file.read_text(encoding="utf-8") == "Hello Sandbox"
    assert modified == ["sandbox/test_file.txt"]

    # 2. Rollback
    runtime.rollback(backups)
    assert not target_file.exists(), "Newly created file should be unlinked on rollback"


def test_runtime_verification_failure_rolls_back(tmp_path):
    runtime = BoundedWorkspaceRuntime(repo_root=tmp_path)
    task = Task(
        id="TASK-VERIFY-01",
        title="Verify Failure Test",
        scope=["sandbox/"],
        verification=["python -c \"import sys; sys.exit(1)\""],  # Always fails
    )

    changes = [FileChange(relative_path="sandbox/failing.txt", content="Must rollback")]
    result = runtime.execute_and_verify(changes, task, auto_rollback_on_failure=True)

    target_file = tmp_path / "sandbox" / "failing.txt"
    assert not target_file.exists(), "File must be rolled back after verification failure"
    assert result.verification_passed is False
    assert result.reverted is True
    assert "Verification commands failed" in (result.error_message or "")
