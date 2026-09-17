"""
End-to-End Controlled Workflow Engine for the JESTER Provider-Agnostic AI Bridge.

Connects:
Founder Request -> Architect -> Inbox Task -> Activation -> Executor ->
Workspace Runtime -> Verification -> Reviewer -> Human Sign-off Gate.

Adheres strictly to:
- .jester/tasks/ file lifecycle (inbox -> active -> review -> completed / blocked)
- Bounded workspace permissions (enforced by BoundedWorkspaceRuntime)
- Mandatory human sign-off before task completion
- Zero automatic git commit or push
"""
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from .contracts import InvocationStatus, UsageMetrics
from .core import BridgeCore
from .orchestration import (
    ArchitectInput,
    BridgeOrchestrator,
    OrchestrationSession,
    OrchestrationStage,
    ReviewVerdict,
)
from .preflight import PreflightReport, PreflightValidator
from .protocol import Task
from .runtime import (
    BoundedWorkspaceRuntime,
    extract_file_changes_from_text,
    RuntimeExecutionResult,
)
import re


def sanitize_portable_paths(text: str, repo_root: Path) -> str:
    """Replaces machine-specific absolute paths and URLs with portable representations."""
    sanitized = text

    root_str_win = str(repo_root)
    root_str_posix = repo_root.as_posix()

    # 1. Strip file:/// URLs referencing repository root explicitly
    pattern_file_root = re.compile(
        r"file:///(?:" + re.escape(root_str_posix) + r"|" + re.escape(root_str_win).replace(r"\\", r"[\\/]") + r")[\\/]?",
        re.IGNORECASE,
    )
    sanitized = pattern_file_root.sub("", sanitized)

    # 2. Strip any file:/// URLs leading into the repository root (e.g. file:///C:/.../Jester/)
    sanitized = re.sub(
        r"file:///(?:[A-Za-z]:[\\/]|/)?.*?[\\/](?:Jester|jester)[\\/]",
        "",
        sanitized,
        flags=re.IGNORECASE,
    )

    # 3. Strip any absolute filesystem paths leading into the repository (e.g. C:\Users\...\Jester\)
    sanitized = re.sub(
        r"(?:[A-Za-z]:[\\/]|/).*?[\\/](?:Jester|jester)[\\/]",
        "",
        sanitized,
        flags=re.IGNORECASE,
    )

    # 4. Replace exact repo_root references with "."
    pattern_repo_root = re.compile(
        re.escape(root_str_posix) + r"|" + re.escape(root_str_win).replace(r"\\", r"[\\/]"),
        re.IGNORECASE,
    )
    sanitized = pattern_repo_root.sub(".", sanitized)

    # 5. Replace any remaining user directory prefixes with "~/"
    sanitized = re.sub(
        r"(?:[A-Za-z]:[\\/]|/)(?:users|home)[\\/][^\\/\s\"']+[\\/]?",
        "~/",
        sanitized,
        flags=re.IGNORECASE,
    )

    # 6. Strip any residual file:/// protocol prefixes
    sanitized = re.sub(r"file:///", "", sanitized)

    # 7. Normalize backslashes in repository file paths
    sanitized = re.sub(
        r"\b(tests|jester_bridge|\.jester|backend|frontend|docs)\\([a-zA-Z0-9_\-\.\\]+)\b",
        lambda m: m.group(0).replace("\\", "/"),
        sanitized,
    )

    return sanitized


class WorkflowOutcome(BaseModel):
    """Normalized final status returned by the workflow runner."""
    task_id: str
    stage: OrchestrationStage
    session: OrchestrationSession
    preflight: PreflightReport
    runtime_result: Optional[RuntimeExecutionResult] = None
    task_file_path: Optional[str] = None
    implementation_report_path: Optional[str] = None
    review_report_path: Optional[str] = None
    error_message: Optional[str] = None
    usage: Optional[UsageMetrics] = None
    stage_usage: Optional[Dict[str, Dict[str, Any]]] = None


class ControlledWorkflowRunner:
    """
    Executes a bounded, multi-agent development workflow through standard JESTER lifecycle stages.
    """

    def __init__(
        self,
        core: BridgeCore,
        repo_root: Optional[Path] = None,
        orchestrator: Optional[BridgeOrchestrator] = None,
        runtime: Optional[BoundedWorkspaceRuntime] = None,
        preflight: Optional[PreflightValidator] = None,
    ):
        self.core = core
        self.repo_root = (repo_root or Path.cwd()).resolve()
        self.orchestrator = orchestrator or BridgeOrchestrator(core=core)
        self.runtime = runtime or BoundedWorkspaceRuntime(repo_root=self.repo_root)
        self.preflight = preflight or PreflightValidator(core=core)

    def _rel_path(self, path: Optional[Union[Path, str]]) -> Optional[str]:
        """Converts an absolute path to a portable repository-relative POSIX string."""
        if path is None:
            return None
        p = Path(path).resolve()
        try:
            return p.relative_to(self.repo_root).as_posix()
        except ValueError:
            return str(path).replace("\\", "/")

    def _task_path(self, folder: str, task_id: str) -> Path:
        """Helper to resolve .jester/tasks/{folder}/{task_id}.json."""
        return self.repo_root / ".jester" / "tasks" / folder / f"{task_id}.json"

    def _move_task_file(self, task: Task, from_folder: Optional[str], to_folder: str) -> Path:
        """Safely transitions a task file between .jester/tasks/ lifecycle folders."""
        dest_path = self._task_path(to_folder, task.id)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if from_folder:
            src_path = self._task_path(from_folder, task.id)
            if src_path.exists():
                src_path.unlink()

        task.status = to_folder
        task.updated_at = datetime.now(timezone.utc).isoformat()

        dest_path.write_text(json.dumps(task.to_dict(), indent=2), encoding="utf-8")
        return dest_path

    def run_e2e_workflow(
        self,
        intent: str,
        target_task_id: str,
        scope: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        acceptance_criteria: Optional[List[str]] = None,
        verification: Optional[List[str]] = None,
        auto_apply: bool = True,
        check_credentials: bool = True,
    ) -> WorkflowOutcome:
        """
        Executes the full controlled workflow:
        1. Architect -> Task creation in inbox
        2. Preflight Check
        3. Activation -> Task in active
        4. Executor -> Code generation & Bounded Runtime Application
        5. Verification -> Test execution
        6. Reviewer -> Independent evaluation -> Task in review
        7. Halts at AWAITING_HUMAN_SIGNOFF
        """
        # Initial task stub
        task = Task(
            id=target_task_id,
            title=f"Task: {intent[:60]}",
            type="feature",
            status="inbox",
            goal=intent,
            scope=scope or [f"components/{target_task_id.lower()}/"],
            constraints=constraints or ["Preserve repository invariants", "Do not modify migrations"],
            acceptance_criteria=acceptance_criteria or ["Verification commands succeed"],
            verification=verification or ["pytest tests/bridge"],
            required_capabilities={"code_generation", "reasoning"},
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        session = self.orchestrator.create_session(task=task)

        # -------------------------------------------------------------
        # STAGE 1: PREFLIGHT VALIDATION (Before any live call)
        # -------------------------------------------------------------
        preflight_report = self.preflight.validate(
            task, check_credentials=check_credentials, check_all_roles=True
        )
        if not preflight_report.is_valid:
            session.current_stage = OrchestrationStage.BLOCKED
            session.task.blocked_reason = "; ".join(preflight_report.errors)
            blocked_file = self._move_task_file(session.task, from_folder=None, to_folder="blocked")
            return WorkflowOutcome(
                task_id=target_task_id,
                stage=OrchestrationStage.BLOCKED,
                session=session,
                preflight=preflight_report,
                task_file_path=self._rel_path(blocked_file),
                error_message="Preflight validation failed: " + "; ".join(preflight_report.errors),
            )

        # -------------------------------------------------------------
        # STAGE 2: ARCHITECT -> INBOX
        # -------------------------------------------------------------
        arch_input = ArchitectInput(intent=intent, target_task_id=target_task_id)
        session = self.orchestrator.run_architect_stage(session, arch_input)

        if session.current_stage == OrchestrationStage.FAILED:
            return WorkflowOutcome(
                task_id=target_task_id,
                stage=OrchestrationStage.FAILED,
                session=session,
                preflight=preflight_report,
                error_message="Architect stage failed during invocation.",
            )

        # Write Task Protocol v2 file into .jester/tasks/inbox/
        inbox_file = self._move_task_file(session.task, from_folder=None, to_folder="inbox")

        # -------------------------------------------------------------
        # STAGE 3: ACTIVATION -> ACTIVE
        # -------------------------------------------------------------
        active_file = self._move_task_file(session.task, from_folder="inbox", to_folder="active")

        # -------------------------------------------------------------
        # STAGE 4: EXECUTOR
        # -------------------------------------------------------------
        session = self.orchestrator.run_executor_stage(session)

        if session.current_stage in (OrchestrationStage.FAILED, OrchestrationStage.BLOCKED):
            blocked_file = self._move_task_file(session.task, from_folder="active", to_folder="blocked")
            return WorkflowOutcome(
                task_id=target_task_id,
                stage=session.current_stage,
                session=session,
                preflight=preflight_report,
                task_file_path=self._rel_path(blocked_file),
                error_message=session.executor_result.error_message if session.executor_result else "Execution failed.",
            )

        # -------------------------------------------------------------
        # STAGE 5: WORKSPACE RUNTIME & VERIFICATION
        # -------------------------------------------------------------
        runtime_res: Optional[RuntimeExecutionResult] = None
        verification_output = "No changes to verify."

        if auto_apply and session.executor_result:
            changes = extract_file_changes_from_text(session.executor_result.summary)
            # If the summary didn't have markdown blocks, check raw_result or payload
            if not changes and session.executor_result.raw_result:
                changes = extract_file_changes_from_text(session.executor_result.raw_result.summary)

            runtime_res = self.runtime.execute_and_verify(
                changes=changes,
                task=session.task,
                auto_rollback_on_failure=True,
            )
            verification_output = runtime_res.verification_output

            if not runtime_res.verification_passed and runtime_res.reverted:
                session.current_stage = OrchestrationStage.BLOCKED
                session.task.blocked_reason = f"Runtime execution / verification failed: {runtime_res.error_message}"
                blocked_file = self._move_task_file(session.task, from_folder="active", to_folder="blocked")
                return WorkflowOutcome(
                    task_id=target_task_id,
                    stage=OrchestrationStage.BLOCKED,
                    session=session,
                    preflight=preflight_report,
                    runtime_result=runtime_res,
                    task_file_path=self._rel_path(blocked_file),
                    error_message=runtime_res.error_message,
                )

        # Write implementation report to .jester/reports/implementations/
        impl_report_path = self.repo_root / ".jester" / "reports" / "implementations" / f"{target_task_id}.md"
        impl_report_path.parent.mkdir(parents=True, exist_ok=True)

        exec_raw = session.executor_result.raw_result if session.executor_result else None
        exec_usage = exec_raw.usage if exec_raw else None
        token_section_impl = (
            "## Token Observability\n"
            f"- **Provider:** {exec_raw.provider if exec_raw else 'unknown'}\n"
            f"- **Model:** {exec_raw.model or 'unknown' if exec_raw else 'unknown'}\n"
            f"- **Input Tokens:** {exec_usage.input_tokens if exec_usage and exec_usage.input_tokens is not None else 'N/A'}\n"
            f"- **Output Tokens:** {exec_usage.output_tokens if exec_usage and exec_usage.output_tokens is not None else 'N/A'}\n"
            f"- **Total Tokens:** {exec_usage.total_tokens if exec_usage and exec_usage.total_tokens is not None else 'N/A'}\n"
        )

        impl_report_raw = (
            f"# Implementation Report: {target_task_id}\n\n"
            f"**Status:** {session.executor_result.status.value}\n"
            f"**Summary:** {session.executor_result.summary}\n\n"
            f"## Files Modified\n"
            + "\n".join(f"- `{f}`" for f in (runtime_res.files_modified if runtime_res else []))
            + f"\n\n{token_section_impl}\n"
            + f"## Verification Output\n```text\n{verification_output}\n```\n"
        )
        impl_report_content = sanitize_portable_paths(impl_report_raw, self.repo_root)
        impl_report_path.write_text(impl_report_content, encoding="utf-8")

        # -------------------------------------------------------------
        # STAGE 6: REVIEWER
        # -------------------------------------------------------------
        review_file = self._move_task_file(session.task, from_folder="active", to_folder="review")

        session = self.orchestrator.run_reviewer_stage(
            session,
            verification_output=verification_output,
        )

        # Write review report to .jester/reports/reviews/
        rev_report_path = self.repo_root / ".jester" / "reports" / "reviews" / f"{target_task_id}.md"
        rev_report_path.parent.mkdir(parents=True, exist_ok=True)
        verdict_str = session.review_result.verdict.value if session.review_result else "UNKNOWN"

        rev_raw = session.review_result.raw_result if session.review_result else None
        rev_usage = rev_raw.usage if rev_raw else None
        total_usage = session.get_total_usage()
        token_section_rev = (
            "## Token Observability\n"
            f"- **Provider:** {rev_raw.provider if rev_raw else 'unknown'}\n"
            f"- **Model:** {rev_raw.model or 'unknown' if rev_raw else 'unknown'}\n"
            f"- **Input Tokens:** {rev_usage.input_tokens if rev_usage and rev_usage.input_tokens is not None else 'N/A'}\n"
            f"- **Output Tokens:** {rev_usage.output_tokens if rev_usage and rev_usage.output_tokens is not None else 'N/A'}\n"
            f"- **Total Tokens:** {rev_usage.total_tokens if rev_usage and rev_usage.total_tokens is not None else 'N/A'}\n\n"
            "### Workflow Aggregate Tokens\n"
            f"- **Total Input Tokens:** {total_usage.input_tokens if total_usage.input_tokens is not None else 'N/A'}\n"
            f"- **Total Output Tokens:** {total_usage.output_tokens if total_usage.output_tokens is not None else 'N/A'}\n"
            f"- **Total Tokens:** {total_usage.total_tokens if total_usage.total_tokens is not None else 'N/A'}\n"
        )

        rev_report_raw = (
            f"# Review Report: {target_task_id}\n\n"
            f"**Verdict:** {verdict_str}\n"
            f"**Summary:** {session.review_result.summary if session.review_result else ''}\n\n"
            f"**Feedback:** {session.review_result.feedback if session.review_result else 'None'}\n\n"
            f"{token_section_rev}"
        )
        rev_report_content = sanitize_portable_paths(rev_report_raw, self.repo_root)
        rev_report_path.write_text(rev_report_content, encoding="utf-8")

        # Session stops cleanly at AWAITING_HUMAN_SIGNOFF (or REWORK_REQUIRED / BLOCKED)
        return WorkflowOutcome(
            task_id=target_task_id,
            stage=session.current_stage,
            session=session,
            preflight=preflight_report,
            runtime_result=runtime_res,
            task_file_path=self._rel_path(review_file),
            implementation_report_path=self._rel_path(impl_report_path),
            review_report_path=self._rel_path(rev_report_path),
            usage=total_usage,
            stage_usage=session.get_stage_usage(),
        )

    def complete_human_approval(
        self, session: OrchestrationSession, approver: str, notes: str = "Approved."
    ) -> Path:
        """
        Finalizes human approval gate and transitions task to .jester/tasks/completed/.
        """
        session = self.orchestrator.approve_human_signoff(session, approver=approver, notes=notes)
        completed_file = self._move_task_file(session.task, from_folder="review", to_folder="completed")
        return completed_file

    def reject_human_signoff(
        self, session: OrchestrationSession, rejector: str, reason: str = "Rejected by human reviewer."
    ) -> Path:
        """
        Records human rejection at the approval gate and transitions task file.
        """
        session = self.orchestrator.reject_human_signoff(session, rejector=rejector, reason=reason)
        target_folder = "blocked" if session.current_stage == OrchestrationStage.BLOCKED else "active"
        target_file = self._move_task_file(session.task, from_folder="review", to_folder=target_folder)
        return target_file
