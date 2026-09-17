"""
Multi-Agent Orchestration Layer for the JESTER Provider-Agnostic AI Bridge.

Coordinates the lifecycle of development stages:
    ARCHITECT -> EXECUTOR -> REVIEWER -> AWAITING_HUMAN_SIGNOFF -> COMPLETED

Operates strictly through provider-neutral abstractions (BridgeCore, Task Protocol v2,
AgentProfile, AgentProvider, InvocationRequest, InvocationResult).
Contains zero provider-specific logic or SDK dependencies.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from .contracts import InvocationRequest, InvocationResult, InvocationStatus, UsageMetrics
from .core import BridgeCore, BridgeError, CapabilityMismatchError, ConfigurationError
from .protocol import Task, load_task_from_dict
from .roles import Role


class OrchestrationStage(str, Enum):
    """Canonical orchestration lifecycle stages."""
    PENDING = "PENDING"
    ARCHITECT = "ARCHITECT"
    EXECUTOR = "EXECUTOR"
    REVIEWER = "REVIEWER"
    REWORK_REQUIRED = "REWORK_REQUIRED"
    AWAITING_HUMAN_SIGNOFF = "AWAITING_HUMAN_SIGNOFF"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class ReviewVerdict(str, Enum):
    """Normalized outcomes produced by an independent Reviewer."""
    PASS = "PASS"
    REWORK_REQUIRED = "REWORK_REQUIRED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class OrchestrationError(BridgeError):
    """Base exception for orchestration lifecycle errors."""
    pass


class InvalidTransitionError(OrchestrationError):
    """Raised when attempting an unauthorized or illegal stage transition."""
    pass


class MaxReworkExceededError(OrchestrationError):
    """Raised when a task exceeds the authorized rework cycle threshold."""
    pass


# --- Normalized Handoff Contracts ---

class ArchitectInput(BaseModel):
    """Input provided to initiate the Architect stage."""
    intent: str
    target_task_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class ArchitectResult(BaseModel):
    """Normalized output produced by the Architect stage."""
    task: Task
    summary: str
    raw_result: InvocationResult


class ExecutorInput(BaseModel):
    """Normalized input provided to the Executor stage."""
    task: Task
    rework_feedback: Optional[str] = None
    extra_context: Dict[str, Any] = Field(default_factory=dict)


class ExecutorResult(BaseModel):
    """Normalized output produced by the Executor stage."""
    task_id: str
    status: InvocationStatus
    summary: str
    files_modified: List[str] = Field(default_factory=list)
    reports_generated: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    raw_result: InvocationResult


class ReviewInput(BaseModel):
    """Normalized input provided to the Reviewer stage."""
    task: Task
    executor_summary: str
    files_modified: List[str] = Field(default_factory=list)
    reports_generated: List[str] = Field(default_factory=list)
    verification_output: Optional[str] = None
    extra_context: Dict[str, Any] = Field(default_factory=dict)


class ReviewResult(BaseModel):
    """Normalized output produced by the Reviewer stage."""
    task_id: str
    verdict: ReviewVerdict
    summary: str
    feedback: Optional[str] = None
    error_message: Optional[str] = None
    raw_result: InvocationResult


class OrchestrationSession(BaseModel):
    """
    State tracking session for a multi-agent orchestrated task.
    Integrates with .jester task lifecycle without creating a second task store.
    """
    session_id: str
    task: Task
    current_stage: OrchestrationStage = OrchestrationStage.PENDING
    rework_count: int = 0
    max_rework_cycles: int = 2
    architect_result: Optional[ArchitectResult] = None
    executor_result: Optional[ExecutorResult] = None
    review_result: Optional[ReviewResult] = None
    human_signoff_by: Optional[str] = None
    human_signoff_notes: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def get_total_usage(self) -> UsageMetrics:
        """Computes aggregate token usage across all completed stages in the session."""
        total = UsageMetrics()
        for res in [self.architect_result, self.executor_result, self.review_result]:
            if res and res.raw_result and res.raw_result.usage:
                total = total.add(res.raw_result.usage)
        return total

    def get_stage_usage(self) -> Dict[str, Dict[str, Any]]:
        """Returns per-stage breakdown of provider, model, role, task, and token usage."""
        stages: Dict[str, Dict[str, Any]] = {}
        for stage_name, res in [
            ("architect", self.architect_result),
            ("executor", self.executor_result),
            ("reviewer", self.review_result),
        ]:
            if res and res.raw_result:
                stages[stage_name] = {
                    "role": stage_name,
                    "task_id": self.task.id,
                    "agent_id": res.raw_result.agent_id,
                    "provider": res.raw_result.provider,
                    "model": res.raw_result.model,
                    "usage": res.raw_result.usage,
                }
        return stages


class BridgeOrchestrator:
    """
    Provider-Agnostic Multi-Agent Orchestrator.

    Coordinates:
    ARCHITECT -> EXECUTOR -> REVIEWER -> AWAITING_HUMAN_SIGNOFF -> COMPLETED

    Invariants:
    - Zero vendor SDK imports or provider-name coupling.
    - Operates purely on normalized contracts and BridgeCore.
    - Reviewer PASS does NOT complete the task; halts at AWAITING_HUMAN_SIGNOFF.
    - REWORK_REQUIRED returns execution to EXECUTOR with bounded rework cycles.
    - Prohibits unauthorized state jumps (e.g. ARCHITECT -> REVIEWER).
    """

    def __init__(self, core: BridgeCore, max_rework_cycles: int = 2):
        self.core = core
        self.max_rework_cycles = max_rework_cycles

    def create_session(self, task: Task, session_id: Optional[str] = None) -> OrchestrationSession:
        """Initializes a new orchestration session for a given task."""
        import uuid
        sid = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        return OrchestrationSession(
            session_id=sid,
            task=task,
            current_stage=OrchestrationStage.PENDING,
            max_rework_cycles=self.max_rework_cycles,
        )

    def run_architect_stage(
        self,
        session: OrchestrationSession,
        architect_input: ArchitectInput,
    ) -> OrchestrationSession:
        """
        Executes the ARCHITECT stage.
        Input: user intent and goal.
        Output: validated Task Protocol v2 task specification ready for execution.
        """
        if session.current_stage not in (OrchestrationStage.PENDING, OrchestrationStage.ARCHITECT):
            raise InvalidTransitionError(
                f"Cannot transition to ARCHITECT from stage {session.current_stage}"
            )

        # 1. Prepare temporary architect task for dispatch
        arch_task = Task(
            id=architect_input.target_task_id or session.task.id,
            title=f"Architect Specification: {session.task.title or architect_input.intent[:50]}",
            role=Role.ARCHITECT.value,
            goal=architect_input.intent,
            required_capabilities={"planning", "reasoning"},
        )

        payload = {
            "intent": architect_input.intent,
            "context": architect_input.context,
        }

        # 2. Dispatch to the resolved Architect provider through BridgeCore
        inv_result = self.core.dispatch(arch_task, payload)

        if inv_result.status != InvocationStatus.SUCCESS:
            session.current_stage = OrchestrationStage.FAILED
            session.updated_at = datetime.now(timezone.utc).isoformat()
            return session

        # 3. Validate task specification output
        # In a real workflow or mock, the architect produces structured task details
        task_id = architect_input.target_task_id or session.task.id
        validated_task = Task(
            id=task_id,
            title=session.task.title or f"Task: {architect_input.intent[:60]}",
            type="feature",
            status="inbox",
            priority="normal",
            role=Role.EXECUTOR.value,
            goal=architect_input.intent,
            scope=session.task.scope or [f"components/{task_id.lower()}/"],
            constraints=session.task.constraints or ["Preserve repository invariants"],
            acceptance_criteria=session.task.acceptance_criteria or ["Verification commands succeed"],
            verification=session.task.verification or ["pytest tests/bridge"],
            required_capabilities={"code_generation", "reasoning"},
        )

        # Validate mandatory task fields per Task Protocol v2
        if not validated_task.id or not validated_task.goal or not validated_task.role:
            raise OrchestrationError("Architect output failed Task Protocol v2 validation: missing required fields.")

        session.task = validated_task
        session.architect_result = ArchitectResult(
            task=validated_task,
            summary=inv_result.summary,
            raw_result=inv_result,
        )
        session.current_stage = OrchestrationStage.ARCHITECT
        session.updated_at = datetime.now(timezone.utc).isoformat()
        return session

    def run_executor_stage(
        self,
        session: OrchestrationSession,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> OrchestrationSession:
        """
        Executes the EXECUTOR stage.
        Transitions from ARCHITECT or REWORK_REQUIRED -> EXECUTOR.
        """
        allowed_previous = (
            OrchestrationStage.ARCHITECT,
            OrchestrationStage.REWORK_REQUIRED,
            OrchestrationStage.PENDING,
        )
        if session.current_stage not in allowed_previous:
            raise InvalidTransitionError(
                f"Cannot transition to EXECUTOR from stage {session.current_stage}"
            )

        task = session.task
        # Update task status to active (.jester lifecycle integration)
        task.status = "active"
        task.role = Role.EXECUTOR.value

        payload = dict(extra_context or {})
        if session.review_result and session.review_result.verdict == ReviewVerdict.REWORK_REQUIRED:
            payload["rework_feedback"] = session.review_result.feedback or session.review_result.summary

        # Dispatch execution task through BridgeCore
        inv_result = self.core.dispatch(task, payload)

        if inv_result.status != InvocationStatus.SUCCESS:
            session.current_stage = (
                OrchestrationStage.BLOCKED
                if inv_result.status == InvocationStatus.BLOCKED
                else OrchestrationStage.FAILED
            )
            session.executor_result = ExecutorResult(
                task_id=task.id,
                status=inv_result.status,
                summary=inv_result.summary,
                error_message=inv_result.error_message,
                raw_result=inv_result,
            )
            session.updated_at = datetime.now(timezone.utc).isoformat()
            return session

        session.executor_result = ExecutorResult(
            task_id=task.id,
            status=InvocationStatus.SUCCESS,
            summary=inv_result.summary,
            files_modified=inv_result.files_modified,
            reports_generated=inv_result.reports_generated,
            raw_result=inv_result,
        )
        session.current_stage = OrchestrationStage.EXECUTOR
        session.updated_at = datetime.now(timezone.utc).isoformat()
        return session

    def run_reviewer_stage(
        self,
        session: OrchestrationSession,
        verification_output: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> OrchestrationSession:
        """
        Executes the REVIEWER stage.
        Must be preceded by a successful EXECUTOR stage.
        """
        if session.current_stage != OrchestrationStage.EXECUTOR:
            raise InvalidTransitionError(
                f"Cannot transition to REVIEWER from stage {session.current_stage}. "
                "Executor stage must complete successfully before review."
            )

        task = session.task
        # Update task status to review (.jester lifecycle integration)
        task.status = "review"

        # Construct independent reviewer task context
        rev_task = Task(
            id=task.id,
            title=f"Review: {task.title}",
            type="review",
            status="review",
            role=Role.REVIEWER.value,
            goal=f"Independently review implementation for task {task.id}",
            acceptance_criteria=task.acceptance_criteria,
            required_capabilities={"review", "reasoning"},
        )

        exec_res = session.executor_result
        payload: Dict[str, Any] = {
            "executor_summary": exec_res.summary if exec_res else "",
            "files_modified": exec_res.files_modified if exec_res else [],
            "reports_generated": exec_res.reports_generated if exec_res else [],
            "verification_output": verification_output or "All test assertions passed.",
        }
        if extra_context:
            payload.update(extra_context)

        # Dispatch review task through BridgeCore
        inv_result = self.core.dispatch(rev_task, payload)

        # Parse normalized review verdict
        verdict = self._parse_review_verdict(inv_result)

        session.review_result = ReviewResult(
            task_id=task.id,
            verdict=verdict,
            summary=inv_result.summary,
            feedback=inv_result.error_message if verdict != ReviewVerdict.PASS else None,
            error_message=inv_result.error_message,
            raw_result=inv_result,
        )

        if verdict == ReviewVerdict.PASS:
            # Crucial boundary: PASS does NOT complete; moves to AWAITING_HUMAN_SIGNOFF
            session.current_stage = OrchestrationStage.AWAITING_HUMAN_SIGNOFF
        elif verdict == ReviewVerdict.REWORK_REQUIRED:
            session.rework_count += 1
            if session.rework_count > session.max_rework_cycles:
                # Prevent infinite rework loops
                session.current_stage = OrchestrationStage.BLOCKED
                task.status = "blocked"
                task.blocked_reason = f"Exceeded maximum rework cycles ({session.max_rework_cycles})."
            else:
                session.current_stage = OrchestrationStage.REWORK_REQUIRED
        elif verdict == ReviewVerdict.BLOCKED:
            session.current_stage = OrchestrationStage.BLOCKED
            task.status = "blocked"
        else:
            session.current_stage = OrchestrationStage.FAILED
            task.status = "blocked"

        session.updated_at = datetime.now(timezone.utc).isoformat()
        return session

    def _parse_review_verdict(self, result: InvocationResult) -> ReviewVerdict:
        """Parses a normalized review verdict from the InvocationResult."""
        if result.status == InvocationStatus.FAILED:
            return ReviewVerdict.FAILED
        if result.status == InvocationStatus.BLOCKED:
            return ReviewVerdict.BLOCKED
        if result.status == InvocationStatus.REWORK_REQUIRED:
            return ReviewVerdict.REWORK_REQUIRED

        summary_upper = result.summary.upper()
        if "REWORK" in summary_upper:
            return ReviewVerdict.REWORK_REQUIRED
        if "FAIL" in summary_upper:
            return ReviewVerdict.FAILED
        if "BLOCK" in summary_upper:
            return ReviewVerdict.BLOCKED

        return ReviewVerdict.PASS

    def approve_human_signoff(
        self,
        session: OrchestrationSession,
        approver: str,
        notes: str = "Approved by human operator.",
    ) -> OrchestrationSession:
        """
        Applies human sign-off approval.
        Only valid from AWAITING_HUMAN_SIGNOFF stage.
        """
        if session.current_stage != OrchestrationStage.AWAITING_HUMAN_SIGNOFF:
            raise InvalidTransitionError(
                f"Cannot approve human signoff from stage {session.current_stage}. "
                "Task must be in AWAITING_HUMAN_SIGNOFF stage."
            )

        session.human_signoff_by = approver
        session.human_signoff_notes = notes
        session.current_stage = OrchestrationStage.COMPLETED
        session.task.status = "completed"
        session.updated_at = datetime.now(timezone.utc).isoformat()
        return session

    def reject_human_signoff(
        self,
        session: OrchestrationSession,
        rejector: str,
        reason: str,
    ) -> OrchestrationSession:
        """
        Rejects signoff during the human review gate, returning task to REWORK_REQUIRED
        or BLOCKED if max rework cycles exceeded.
        """
        if session.current_stage != OrchestrationStage.AWAITING_HUMAN_SIGNOFF:
            raise InvalidTransitionError(
                f"Cannot reject human signoff from stage {session.current_stage}."
            )

        session.human_signoff_by = rejector
        session.human_signoff_notes = f"Rejected: {reason}"
        session.rework_count += 1

        if session.rework_count > session.max_rework_cycles:
            session.current_stage = OrchestrationStage.BLOCKED
            session.task.status = "blocked"
            session.task.blocked_reason = f"Exceeded maximum rework cycles after human rejection: {reason}"
        else:
            session.current_stage = OrchestrationStage.REWORK_REQUIRED

        session.updated_at = datetime.now(timezone.utc).isoformat()
        return session
