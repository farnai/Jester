"""
Normalized request and result contracts for the JESTER Provider-Agnostic AI Bridge.

These data structures ensure that the Bridge Core communicates using vendor-neutral
contracts, preventing provider-specific schemas or SDK objects from leaking into core logic.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class InvocationStatus(str, Enum):
    """Normalized outcome status of an agent invocation."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    REWORK_REQUIRED = "REWORK_REQUIRED"


class InvocationRequest(BaseModel):
    """
    Standardized payload delivered to a provider for execution.
    Contains full task context without vendor-specific formatting.
    """
    request_id: str
    task_id: str
    role: str
    agent_id: str
    provider: str
    model: Optional[str] = None
    runtime_id: Optional[str] = None
    runtime_type: Optional[str] = None
    account_id: Optional[str] = None
    required_capabilities: Set[str] = Field(default_factory=set)
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: str

    model_config = {"frozen": True}


class UsageMetrics(BaseModel):
    """
    Normalized token and context usage metrics.
    Provider-neutral representation capturing prompt, completion, and total tokens.
    """
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    def add(self, other: Optional["UsageMetrics"]) -> "UsageMetrics":
        """Returns a new UsageMetrics summing tokens across stages."""
        if not other:
            return UsageMetrics(
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
                total_tokens=self.total_tokens,
            )
        in_t = (self.input_tokens or 0) + (other.input_tokens or 0) if (self.input_tokens is not None or other.input_tokens is not None) else None
        out_t = (self.output_tokens or 0) + (other.output_tokens or 0) if (self.output_tokens is not None or other.output_tokens is not None) else None
        tot_t = (self.total_tokens or 0) + (other.total_tokens or 0) if (self.total_tokens is not None or other.total_tokens is not None) else None
        return UsageMetrics(input_tokens=in_t, output_tokens=out_t, total_tokens=tot_t)


class InvocationResult(BaseModel):
    """
    Standardized response returned by any provider adapter.
    Normalizes execution status, files touched, report paths, errors, and token usage.
    """
    request_id: str
    task_id: str
    status: InvocationStatus
    agent_id: str
    provider: str
    model: Optional[str] = None
    runtime_id: Optional[str] = None
    runtime_type: Optional[str] = None
    account_id: Optional[str] = None
    routing_reason: Optional[str] = None
    summary: str
    files_modified: List[str] = Field(default_factory=list)
    reports_generated: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    usage: Optional[UsageMetrics] = None
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)
    completed_at: str


# --- Structured Handoff Contracts (TASK-0009) ---

class BaseHandoff(BaseModel):
    """Base model for structured inter-role handoff packages."""
    task_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context_id: Optional[str] = None
    parent_context_id: Optional[str] = None


class ArchitectHandoff(BaseHandoff):
    """
    Structured handoff from Architect to Executor.
    Carries the decomposed intent, scope, architectural notes, and constraints.
    """
    task_objective: str
    implementation_intent: str
    affected_areas: List[str] = Field(default_factory=list)
    expected_files: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    architectural_notes: Optional[str] = None
    relevant_context_references: List[str] = Field(default_factory=list)
    context_package_metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutorHandoff(BaseHandoff):
    """
    Structured handoff from Executor to Reviewer.
    Carries actual execution output, modified files, verification output, and code diff.
    """
    implementation_summary: str
    files_modified: List[str] = Field(default_factory=list)
    tests_changed: List[str] = Field(default_factory=list)
    verification_passed: bool = False
    verification_output: Optional[str] = None
    diff: str = ""
    relevant_context_references: List[str] = Field(default_factory=list)
    known_limitations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    runtime_result: Optional[Dict[str, Any]] = None
    usage_metrics: Optional[UsageMetrics] = None


class ReviewerHandoff(BaseHandoff):
    """
    Structured handoff produced by the independent Reviewer.
    Carries verdict, verification criteria checks, diff inspection status, and feedback.
    """
    verdict: str
    summary: str
    feedback: Optional[str] = None
    criteria_verified: Dict[str, bool] = Field(default_factory=dict)
    diff_inspected: bool = False
    defect_details: Optional[str] = None
    executor_context_id: Optional[str] = None
    usage_metrics: Optional[UsageMetrics] = None
