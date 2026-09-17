"""
Task Protocol v2 implementation with transparent backward compatibility for v1 tasks.

Task Protocol v2 cleanly decouples task specification from specific AI vendors:
- Role expresses operational responsibility (e.g. 'executor', 'architect', 'reviewer', 'auditor')
- Assigned Agent expresses the logical worker identity
- Required Capabilities declare the competencies needed to execute the task
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from pydantic import BaseModel, Field

from .roles import Role, get_default_capabilities_for_role, is_valid_role


class Task(BaseModel):
    """
    Structured task model conforming to Task Protocol v2.
    """
    id: str
    title: str
    type: str = "feature"
    status: str = "inbox"
    priority: str = "normal"
    role: str = Role.EXECUTOR.value
    assigned_agent: Optional[str] = None
    required_capabilities: Set[str] = Field(default_factory=set)
    goal: str = ""
    scope: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    verification: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    blocked_reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Legacy v1 compatibility field (accessible if needed for backward-compatibility)
    agent: Optional[str] = None

    def to_dict(self, include_legacy_agent: bool = True) -> Dict[str, Any]:
        """Serializes task to dictionary, optionally including legacy 'agent' key."""
        data = {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "status": self.status,
            "priority": self.priority,
            "role": self.role,
            "assigned_agent": self.assigned_agent,
            "required_capabilities": sorted(list(self.required_capabilities)),
            "goal": self.goal,
            "scope": self.scope,
            "constraints": self.constraints,
            "acceptance_criteria": self.acceptance_criteria,
            "verification": self.verification,
            "dependencies": self.dependencies,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.blocked_reason is not None:
            data["blocked_reason"] = self.blocked_reason
        if include_legacy_agent and self.agent is not None:
            data["agent"] = self.agent
        return data


def normalize_task_dict(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a task dictionary to Task Protocol v2 standards.
    Handles legacy Task Protocol v1 transparently without altering historical files.
    """
    data = dict(raw)

    # Resolve ID
    task_id = data.get("id") or data.get("task_id", "")
    data["id"] = task_id

    # Resolve Role
    task_type = data.get("type", "feature")
    if "role" not in data or not data["role"]:
        if task_type == "audit":
            data["role"] = Role.AUDITOR.value
        elif task_type == "review":
            data["role"] = Role.REVIEWER.value
        else:
            data["role"] = Role.EXECUTOR.value
    elif not is_valid_role(data["role"]):
        # Fallback to executor if an unknown role was provided
        data["role"] = Role.EXECUTOR.value

    role = data["role"]

    # Resolve Assigned Agent (v2 assigned_agent or v1 agent fallback)
    if "assigned_agent" not in data or data["assigned_agent"] is None:
        data["assigned_agent"] = data.get("agent")
    if "agent" not in data or data["agent"] is None:
        data["agent"] = data.get("assigned_agent")

    # Resolve Required Capabilities
    if "required_capabilities" not in data or not data["required_capabilities"]:
        data["required_capabilities"] = get_default_capabilities_for_role(role)
    elif isinstance(data["required_capabilities"], list):
        data["required_capabilities"] = set(data["required_capabilities"])

    return data


def load_task_from_dict(data: Dict[str, Any]) -> Task:
    """Instantiates a validated Task model from a raw dictionary."""
    normalized = normalize_task_dict(data)
    return Task(**normalized)


def load_task_from_file(path: Union[str, Path]) -> Task:
    """Reads and parses a task file from disk (handles v1 and v2 formats)."""
    file_path = Path(path)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return load_task_from_dict(data)
