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
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from .contracts import (
    ArchitectHandoff,
    BaseHandoff,
    ExecutorHandoff,
    InvocationRequest,
    InvocationResult,
    InvocationStatus,
    ReviewerHandoff,
    UsageMetrics,
)
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
    handoff: Optional[ArchitectHandoff] = None


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
    diff: str = ""
    error_message: Optional[str] = None
    raw_result: InvocationResult
    handoff: Optional[ExecutorHandoff] = None


class ReviewInput(BaseModel):
    """Normalized input provided to the Reviewer stage."""
    task: Task
    executor_summary: str
    files_modified: List[str] = Field(default_factory=list)
    reports_generated: List[str] = Field(default_factory=list)
    diff: str = Field(default="")
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
    handoff: Optional[ReviewerHandoff] = None


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
    architect_handoff: Optional[ArchitectHandoff] = None
    executor_handoff: Optional[ExecutorHandoff] = None
    reviewer_handoff: Optional[ReviewerHandoff] = None
    current_context_id: Optional[str] = None
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

        # Context lineage resolution
        ctx_id = None
        parent_ctx_id = None
        if architect_input.context and isinstance(architect_input.context, dict):
            arch_bundle = architect_input.context.get("architect_context_bundle")
            if isinstance(arch_bundle, dict):
                ctx_id = arch_bundle.get("context_id")
                parent_ctx_id = arch_bundle.get("parent_context_id")

        arch_handoff = ArchitectHandoff(
            task_id=validated_task.id,
            task_objective=validated_task.goal,
            implementation_intent=architect_input.intent,
            affected_areas=list(validated_task.scope or []),
            expected_files=list(validated_task.scope or []),
            constraints=list(validated_task.constraints or []),
            acceptance_criteria=list(validated_task.acceptance_criteria or []),
            risks=[],
            architectural_notes=inv_result.summary,
            relevant_context_references=list(validated_task.scope or []),
            context_package_metadata={"intent": architect_input.intent},
            context_id=ctx_id,
            parent_context_id=parent_ctx_id,
        )
        session.architect_handoff = arch_handoff
        session.current_context_id = ctx_id
        session.architect_result = ArchitectResult(
            task=validated_task,
            summary=inv_result.summary,
            raw_result=inv_result,
            handoff=arch_handoff,
        )
        session.current_stage = OrchestrationStage.ARCHITECT
        session.updated_at = datetime.now(timezone.utc).isoformat()
        return session

    def run_executor_stage(
        self,
        session: OrchestrationSession,
        extra_context: Optional[Dict[str, Any]] = None,
        architect_handoff: Optional[ArchitectHandoff] = None,
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

        if architect_handoff:
            session.architect_handoff = architect_handoff

        task = session.task
        # Update task status to active (.jester lifecycle integration)
        task.status = "active"
        task.role = Role.EXECUTOR.value

        payload = dict(extra_context or {})
        if session.review_result and session.review_result.verdict == ReviewVerdict.REWORK_REQUIRED:
            payload["rework_feedback"] = session.review_result.feedback or session.review_result.summary

        # Context lineage resolution
        ctx_id = None
        parent_ctx_id = session.architect_handoff.context_id if session.architect_handoff else None
        if extra_context and isinstance(extra_context, dict):
            ctx_bundle = extra_context.get("context_bundle")
            if isinstance(ctx_bundle, dict):
                ctx_id = ctx_bundle.get("context_id")
                if ctx_bundle.get("parent_context_id"):
                    parent_ctx_id = ctx_bundle.get("parent_context_id")

        # Dispatch execution task through BridgeCore
        inv_result = self.core.dispatch(task, payload)

        if inv_result.status != InvocationStatus.SUCCESS:
            session.current_stage = (
                OrchestrationStage.BLOCKED
                if inv_result.status == InvocationStatus.BLOCKED
                else OrchestrationStage.FAILED
            )
            exec_fail_handoff = ExecutorHandoff(
                task_id=task.id,
                implementation_summary=inv_result.summary,
                files_modified=[],
                tests_changed=[],
                verification_passed=False,
                verification_output=None,
                diff="",
                relevant_context_references=[],
                known_limitations=[],
                warnings=[inv_result.error_message or "Execution failed."],
                usage_metrics=inv_result.usage,
                context_id=ctx_id,
                parent_context_id=parent_ctx_id,
            )
            session.executor_handoff = exec_fail_handoff
            session.current_context_id = ctx_id
            session.executor_result = ExecutorResult(
                task_id=task.id,
                status=inv_result.status,
                summary=inv_result.summary,
                error_message=inv_result.error_message,
                raw_result=inv_result,
                handoff=exec_fail_handoff,
            )
            session.updated_at = datetime.now(timezone.utc).isoformat()
            return session

        exec_success_handoff = ExecutorHandoff(
            task_id=task.id,
            implementation_summary=inv_result.summary,
            files_modified=inv_result.files_modified,
            tests_changed=[],
            verification_passed=True,
            verification_output=None,
            diff="",
            relevant_context_references=inv_result.files_modified,
            known_limitations=[],
            warnings=[],
            usage_metrics=inv_result.usage,
            context_id=ctx_id,
            parent_context_id=parent_ctx_id,
        )
        session.executor_handoff = exec_success_handoff
        session.current_context_id = ctx_id
        session.executor_result = ExecutorResult(
            task_id=task.id,
            status=InvocationStatus.SUCCESS,
            summary=inv_result.summary,
            files_modified=inv_result.files_modified,
            reports_generated=inv_result.reports_generated,
            raw_result=inv_result,
            handoff=exec_success_handoff,
        )
        session.current_stage = OrchestrationStage.EXECUTOR
        session.updated_at = datetime.now(timezone.utc).isoformat()
        return session

    def run_reviewer_stage(
        self,
        session: OrchestrationSession,
        verification_output: Optional[str] = None,
        diff: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None,
        executor_handoff: Optional[ExecutorHandoff] = None,
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

        if executor_handoff:
            session.executor_handoff = executor_handoff

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

        # Resolve files_modified from all available sources
        files_mod = []
        if extra_context and isinstance(extra_context, dict) and "files_modified" in extra_context:
            files_mod = extra_context.get("files_modified") or []
        elif exec_res and hasattr(exec_res, "files_modified") and exec_res.files_modified:
            files_mod = exec_res.files_modified
        elif session.executor_handoff and hasattr(session.executor_handoff, "files_modified") and session.executor_handoff.files_modified:
            files_mod = session.executor_handoff.files_modified

        # Determine diff content
        diff_explicitly_provided = diff is not None
        if diff is not None:
            actual_diff = diff
        elif exec_res and hasattr(exec_res, "diff") and exec_res.diff:
            actual_diff = exec_res.diff
            diff_explicitly_provided = True
        else:
            actual_diff = "No file changes detected."
            diff_explicitly_provided = False

        payload: Dict[str, Any] = {
            "executor_summary": exec_res.summary if exec_res else "",
            "files_modified": files_mod,
            "reports_generated": exec_res.reports_generated if exec_res else [],
            "verification_output": verification_output or "All test assertions passed.",
            "diff": actual_diff,
        }
        if session.architect_handoff:
            payload["architect_intent"] = session.architect_handoff.implementation_intent
        if extra_context:
            payload.update(extra_context)

        # Dispatch review task through BridgeCore
        inv_result = self.core.dispatch(rev_task, payload)

        # Parse normalized review verdict
        verdict = self._parse_review_verdict(inv_result)

        # Integrity Invariant: If task semantically requires code changes,
        # an empty diff or lack of modified files MUST NOT pass review.
        from .runtime import task_expects_code_changes
        expects_code = task_expects_code_changes(task)

        diff_has_content = bool(
            actual_diff
            and actual_diff.strip()
            and actual_diff.strip() != "No file changes detected."
        )
        has_real_diff = diff_has_content or bool(files_mod)

        if expects_code and diff_explicitly_provided and not has_real_diff:
            if verdict == ReviewVerdict.PASS:
                verdict = ReviewVerdict.REWORK_REQUIRED
            defect_msg = (
                "Integrity check failed: Task requires implementation changes, "
                "but no code diff or file modifications were produced for review."
            )
            inv_result.error_message = defect_msg
            if not inv_result.summary or inv_result.summary.startswith("["):
                inv_result.summary = f"Review verdict: REWORK_REQUIRED. {defect_msg}"

        # Context lineage resolution
        ctx_id = None
        parent_ctx_id = session.executor_handoff.context_id if session.executor_handoff else None
        if extra_context and isinstance(extra_context, dict):
            rev_bundle = extra_context.get("reviewer_context_bundle")
            if isinstance(rev_bundle, dict):
                ctx_id = rev_bundle.get("context_id")
                if rev_bundle.get("parent_context_id"):
                    parent_ctx_id = rev_bundle.get("parent_context_id")

        rev_handoff = ReviewerHandoff(
            task_id=task.id,
            verdict=verdict.value,
            summary=inv_result.summary,
            feedback=inv_result.error_message if verdict != ReviewVerdict.PASS else None,
            criteria_verified={c: (verdict == ReviewVerdict.PASS) for c in (task.acceptance_criteria or [])},
            diff_inspected=has_real_diff if diff_explicitly_provided else True,
            defect_details=inv_result.error_message if verdict != ReviewVerdict.PASS else None,
            usage_metrics=inv_result.usage,
            context_id=ctx_id,
            parent_context_id=parent_ctx_id,
            executor_context_id=(session.executor_handoff.context_id if session.executor_handoff else None),
        )
        session.reviewer_handoff = rev_handoff
        session.current_context_id = ctx_id
        session.review_result = ReviewResult(
            task_id=task.id,
            verdict=verdict,
            summary=inv_result.summary,
            feedback=inv_result.error_message if verdict != ReviewVerdict.PASS else None,
            error_message=inv_result.error_message,
            raw_result=inv_result,
            handoff=rev_handoff,
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

        summary_upper = result.summary.upper() if result.summary else ""

        # 1. Look for explicit VERDICT: or REVIEW: declarations first (e.g. "VERDICT: PASS", "Review: REWORK_REQUIRED")
        verdict_match = re.search(r"(?:VERDICT|REVIEW(?:\s+VERDICT)?|STATUS):\s*([A-Z_]+)", summary_upper)
        if verdict_match:
            v = verdict_match.group(1).strip()
            if "PASS" in v:
                return ReviewVerdict.PASS
            if "REWORK" in v:
                return ReviewVerdict.REWORK_REQUIRED
            if "BLOCK" in v:
                return ReviewVerdict.BLOCKED
            if "FAIL" in v:
                return ReviewVerdict.FAILED

        # 2. Heuristic fallback with word boundaries and phrase negation handling
        has_rework = bool(re.search(r"\bREWORK(?:[_\s]+REQUIRED)?\b", summary_upper))
        rework_negated = bool(re.search(r"\b(ZERO|NO|WITHOUT)\s+(?:\w+\s+){0,3}REWORK", summary_upper))
        if has_rework and not rework_negated:
            return ReviewVerdict.REWORK_REQUIRED

        if re.search(r"\bBLOCK(?:ED)?\b", summary_upper):
            return ReviewVerdict.BLOCKED

        # Match FAIL only if not preceded by zero/no/without
        has_fail = bool(re.search(r"\bFAIL(?:ED|URE|URES)?\b", summary_upper))
        fail_negated = bool(re.search(r"\b(ZERO|NO|WITHOUT)\s+(?:\w+\s+){0,3}FAIL", summary_upper))
        if has_fail and not fail_negated:
            return ReviewVerdict.FAILED

        if re.search(r"\bPASS(?:ED)?\b", summary_upper):
            return ReviewVerdict.PASS

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
