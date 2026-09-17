"""
Tests for Task Protocol v2 and Backward Compatibility with v1 Historical Tasks.
"""
from pathlib import Path
import pytest

from jester_bridge.protocol import (
    Task,
    load_task_from_dict,
    load_task_from_file,
    normalize_task_dict,
)
from jester_bridge.roles import Role


def test_task_protocol_v2_instantiation():
    task = Task(
        id="TASK-0004",
        title="Implement AI Bridge Foundation",
        type="feature",
        status="active",
        priority="high",
        role=Role.EXECUTOR.value,
        assigned_agent="gemini-dev",
        required_capabilities={"repository_read", "repository_write", "testing"},
        goal="Provide provider-agnostic bridge foundation",
    )
    assert task.id == "TASK-0004"
    assert task.role == "executor"
    assert task.assigned_agent == "gemini-dev"
    assert "testing" in task.required_capabilities

    task_dict = task.to_dict()
    assert task_dict["role"] == "executor"
    assert task_dict["assigned_agent"] == "gemini-dev"
    assert "repository_write" in task_dict["required_capabilities"]


def test_task_protocol_v1_backward_compatibility_dict():
    # Legacy v1 dictionary format without 'role', 'assigned_agent', or 'required_capabilities'
    legacy_raw = {
        "id": "TASK-0099",
        "title": "Legacy Task",
        "type": "audit",
        "status": "inbox",
        "priority": "normal",
        "agent": "gemini",
        "goal": "Legacy audit goal",
    }
    normalized = normalize_task_dict(legacy_raw)
    assert normalized["id"] == "TASK-0099"
    assert normalized["role"] == Role.AUDITOR.value  # Inferred from type="audit"
    assert normalized["assigned_agent"] == "gemini"   # Mapped from agent
    assert "repository_read" in normalized["required_capabilities"]

    task = load_task_from_dict(legacy_raw)
    assert task.role == Role.AUDITOR.value
    assert task.assigned_agent == "gemini"
    assert task.agent == "gemini"


def test_historical_task_0001_backward_compatibility():
    path = Path(".jester/tasks/review/TASK-0001.json")
    assert path.exists(), "Historical TASK-0001 must exist on disk"

    task = load_task_from_file(path)
    assert task.id == "TASK-0001"
    assert task.status == "review"
    assert task.role == Role.AUDITOR.value  # type='audit' mapped to role='auditor'
    assert task.assigned_agent == "gemini"
    assert task.agent == "gemini"
    assert "repository_read" in task.required_capabilities


def test_historical_task_0002_backward_compatibility():
    path = Path(".jester/tasks/blocked/TASK-0002.json")
    assert path.exists(), "Historical TASK-0002 must exist on disk"

    task = load_task_from_file(path)
    assert task.id == "TASK-0002"
    assert task.status == "blocked"
    assert task.role == Role.EXECUTOR.value
    assert task.assigned_agent == "gemini"
    assert task.blocked_reason is not None


def test_historical_task_0003_backward_compatibility():
    path = Path(".jester/tasks/completed/TASK-0003.json")
    assert path.exists(), "Historical TASK-0003 must exist on disk"

    task = load_task_from_file(path)
    assert task.id == "TASK-0003"
    assert task.status == "completed"
    assert task.role == Role.EXECUTOR.value
    assert task.assigned_agent == "gemini"
