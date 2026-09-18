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

from .context import ContextBundle, ContextEngine, ContextPackage
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
    PROTECTED_PATHS,
    RuntimeExecutionResult,
)
from .git_controller import (
    GitController,
    CommitAuthorization,
    PushAuthorization,
    GitOperationResult,
    GitControllerError,
)
from .execution_history import (
    ExecutionHistoryStore,
    ExecutionRecord,
    ExecutionEvent,
    ExecutionHistoryError,
)
from .runtimes import RuntimeType
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


def extract_safe_target_paths(intent: str, repo_root: Path) -> List[str]:
    """
    Extracts explicit, safe repository-relative target paths declared in Founder intent.
    Strictly fail-closed:
    - Rejects path traversal ('..')
    - Rejects absolute paths (leading slash, backslash, Windows drive letter)
    - Rejects protected paths (.git, .env, AGENTS.md, migrations)
    - Rejects paths outside repo_root
    Returns a sorted, deduplicated list of safe relative paths.
    """
    if not intent:
        return []

    candidates: List[str] = []

    # Quoted path candidates (`path`, 'path', "path")
    quoted_pattern = re.compile(r"[`'\"]([a-zA-Z0-9_\-\./\\]+)[`'\"]")
    for match in quoted_pattern.finditer(intent):
        candidates.append(match.group(1))

    # Unquoted file paths with extension (e.g. tests/bridge/probe.py, backend/app/main.py)
    file_pattern = re.compile(r"(?:^|[\s(])([a-zA-Z0-9_\-]+[/\\][a-zA-Z0-9_\-/\\]+\.[a-zA-Z0-9_\-]+)")
    for match in file_pattern.finditer(intent):
        candidates.append(match.group(1))

    # Unquoted directory paths ending in /
    dir_pattern = re.compile(r"(?:^|[\s(])([a-zA-Z0-9_\-]+[/\\][a-zA-Z0-9_\-/\\]+/)(?:[\s)]|$)")
    for match in dir_pattern.finditer(intent):
        candidates.append(match.group(1))

    valid_paths: List[str] = []
    resolved_root = repo_root.resolve()

    for raw in candidates:
        cand = raw.strip().rstrip(".,;:!?)'\"`")
        if not cand:
            continue

        # Reject absolute paths
        if cand.startswith(("/", "\\")) or re.match(r"^[a-zA-Z]:", cand):
            continue

        norm = cand.replace("\\", "/").strip().lstrip("/")
        parts = [p for p in norm.split("/") if p]

        # Reject traversal
        if ".." in parts:
            continue

        # Reject protected paths
        is_protected = False
        for prot in PROTECTED_PATHS:
            if norm == prot or norm.startswith(f"{prot}/"):
                is_protected = True
                break
        if is_protected:
            continue

        # Ensure containment within repo_root
        try:
            target_abs = (repo_root / norm).resolve()
            if not target_abs.is_relative_to(resolved_root):
                continue
        except Exception:
            continue

        if norm and norm not in valid_paths:
            valid_paths.append(norm)

    return sorted(valid_paths)


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
    diff: Optional[str] = None
    context_bundle: Optional[Union[ContextPackage, ContextBundle]] = None
    architect_context: Optional[ContextPackage] = None
    reviewer_context: Optional[ContextPackage] = None
    rework_context: Optional[ContextPackage] = None
    git_delivery: Optional[GitOperationResult] = None
    execution_id: Optional[str] = None
    persistence_error: Optional[str] = None


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
        context_engine: Optional[ContextEngine] = None,
        git_controller: Optional[GitController] = None,
        history_store: Optional[ExecutionHistoryStore] = None,
    ):
        self.core = core
        self.repo_root = (repo_root or Path.cwd()).resolve()
        self.orchestrator = orchestrator or BridgeOrchestrator(core=core)
        self.runtime = runtime or BoundedWorkspaceRuntime(repo_root=self.repo_root)
        self.preflight = preflight or PreflightValidator(core=core)
        self.context_engine = context_engine or ContextEngine(repo_root=self.repo_root)
        self.git_controller = git_controller or GitController(repo_root=self.repo_root)
        self.history_store = history_store or ExecutionHistoryStore(repo_root=self.repo_root)
        self.last_delivery_result: Optional[GitOperationResult] = None
        self.last_persistence_error: Optional[str] = None

    def _create_execution_safe(self, record: ExecutionRecord) -> bool:
        if not self.history_store:
            return False
        try:
            return self.history_store.create_execution(record)
        except Exception as e:
            self.last_persistence_error = f"History persistence error: {str(e)}"
            return False

    def _update_execution_safe(self, record: ExecutionRecord) -> bool:
        if not self.history_store:
            return False
        try:
            return self.history_store.update_execution(record)
        except Exception as e:
            self.last_persistence_error = f"History persistence error: {str(e)}"
            return False

    def _record_event_safe(self, event: ExecutionEvent) -> bool:
        if not self.history_store:
            return False
        try:
            return self.history_store.record_event(event)
        except Exception as e:
            self.last_persistence_error = f"History persistence error: {str(e)}"
            return False



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
        target_runtime_id: Optional[str] = None,
        target_account: Optional[str] = None,
        target_runtime_type: Optional[RuntimeType] = None,
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
        # Resolve scope safely
        if scope:
            resolved_scope = []
            for s in scope:
                norm_s = s.replace("\\", "/").strip().lstrip("/")
                if not norm_s or ".." in norm_s or any(norm_s == p or norm_s.startswith(f"{p}/") for p in PROTECTED_PATHS):
                    continue
                try:
                    res_path = (self.repo_root / norm_s).resolve()
                    if res_path.is_relative_to(self.repo_root.resolve()):
                        resolved_scope.append(norm_s)
                except Exception:
                    continue
            if not resolved_scope:
                resolved_scope = [f"components/{target_task_id.lower()}/"]
        else:
            extracted = extract_safe_target_paths(intent, self.repo_root)
            resolved_scope = extracted if extracted else [f"components/{target_task_id.lower()}/"]

        # Tailor verification command to target test if applicable
        resolved_verification = verification
        if not resolved_verification:
            target_test = None
            for p in resolved_scope:
                if p.startswith("tests/") and p.endswith(".py"):
                    target_test = p
                    break
            if target_test:
                resolved_verification = [f"pytest {target_test}"]
            else:
                resolved_verification = ["pytest tests/bridge"]

        # Initial task stub
        task = Task(
            id=target_task_id,
            title=f"Task: {intent[:60]}",
            type="feature",
            status="inbox",
            goal=intent,
            scope=resolved_scope,
            constraints=constraints or ["Preserve repository invariants", "Do not modify migrations"],
            acceptance_criteria=acceptance_criteria or ["Verification commands succeed"],
            verification=resolved_verification,
            required_capabilities={"code_generation", "reasoning"},
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        session = self.orchestrator.create_session(task=task)
        execution_id = f"exec-{session.session_id}"
        self.last_persistence_error = None

        exec_record = ExecutionRecord(
            execution_id=execution_id,
            task_id=target_task_id,
            task_title=task.title,
            task_protocol_version="v2",
            overall_status=OrchestrationStage.PENDING.value,
            current_stage=OrchestrationStage.PENDING.value,

        )
        self._create_execution_safe(exec_record)
        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="execution_created",
                stage="pending",
                status="running",
                summary=f"Execution created for task {target_task_id}: {intent[:100]}",
            )
        )

        # -------------------------------------------------------------
        # STAGE 1: PREFLIGHT VALIDATION (Before any live call)
        # -------------------------------------------------------------
        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="preflight_started",
                stage="preflight",
                status="running",
            )
        )
        preflight_report = self.preflight.validate(
            task,
            check_credentials=check_credentials,
            check_all_roles=True,
            target_runtime_id=target_runtime_id,
        )
        if not preflight_report.is_valid:
            session.current_stage = OrchestrationStage.BLOCKED
            session.task.blocked_reason = "; ".join(preflight_report.errors)
            blocked_file = self._move_task_file(session.task, from_folder=None, to_folder="blocked")
            self._record_event_safe(
                ExecutionEvent(
                    execution_id=execution_id,
                    event_type="preflight_failed",
                    stage="preflight",
                    status="blocked",
                    error="; ".join(preflight_report.errors),
                )
            )
            exec_record.overall_status = "blocked"
            exec_record.current_stage = "blocked"
            exec_record.completed_at = datetime.now(timezone.utc).isoformat()
            exec_record.error_message = "; ".join(preflight_report.errors)
            self._update_execution_safe(exec_record)
            return WorkflowOutcome(
                task_id=target_task_id,
                stage=OrchestrationStage.BLOCKED,
                session=session,
                preflight=preflight_report,
                task_file_path=self._rel_path(blocked_file),
                error_message="Preflight validation failed: " + "; ".join(preflight_report.errors),
                execution_id=execution_id,
                persistence_error=self.last_persistence_error,
            )

        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="preflight_completed",
                stage="preflight",
                status="success",
                summary="Preflight validation passed.",
            )
        )

        # -------------------------------------------------------------
        # STAGE 2: ARCHITECT -> INBOX
        # -------------------------------------------------------------
        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="architect_started",
                stage="architect",
                role="architect",
            )
        )
        # Assemble role-aware context for Architect
        arch_context = self.context_engine.assemble_context(
            task=session.task,
            role="architect",
            stage="architect",
            execution_id=execution_id,
            parent_context_id=None,
            include_arch_docs=True,
        )
        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="context_assembled",
                stage="architect",
                status="success",
                role="architect",
                summary=f"Architect context assembled: {len(arch_context.files)} files, {arch_context.total_characters} chars",
                metadata=arch_context.to_summary_dict(),
            )
        )

        arch_context_payload = {
            "architecture_context": arch_context.format_for_prompt(),
            "architect_context_bundle": arch_context.model_dump(),
        }
        if target_runtime_id:
            arch_context_payload["target_runtime_id"] = target_runtime_id
        if target_account:
            arch_context_payload["target_account"] = target_account
        if target_runtime_type:
            arch_context_payload["target_runtime_type"] = target_runtime_type

        arch_input = ArchitectInput(
            intent=intent,
            target_task_id=target_task_id,
            context=arch_context_payload,
        )
        session = self.orchestrator.run_architect_stage(session, arch_input)

        if session.current_stage == OrchestrationStage.FAILED:
            self._record_event_safe(
                ExecutionEvent(
                    execution_id=execution_id,
                    event_type="architect_failed",
                    stage="architect",
                    status="failed",
                    error="Architect stage failed during invocation.",
                )
            )
            exec_record.overall_status = "failed"
            exec_record.current_stage = "failed"
            exec_record.completed_at = datetime.now(timezone.utc).isoformat()
            exec_record.error_message = "Architect stage failed during invocation."
            self._update_execution_safe(exec_record)
            return WorkflowOutcome(
                task_id=target_task_id,
                stage=OrchestrationStage.FAILED,
                session=session,
                preflight=preflight_report,
                error_message="Architect stage failed during invocation.",
                execution_id=execution_id,
                persistence_error=self.last_persistence_error,
            )

        arch_raw = session.architect_result.raw_result if session.architect_result else None
        arch_usage = arch_raw.usage if arch_raw else None
        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="architect_completed",
                stage="architect",
                status="success",
                role="architect",
                agent_id=arch_raw.agent_id if arch_raw else None,
                provider=arch_raw.provider if arch_raw else None,
                model=arch_raw.model if arch_raw else None,
                summary=session.architect_result.summary if session.architect_result else "Architect specification complete",
                input_tokens=arch_usage.input_tokens if arch_usage else None,
                output_tokens=arch_usage.output_tokens if arch_usage else None,
                total_tokens=arch_usage.total_tokens if arch_usage else None,
                metadata={k: v for k, v in {
                    "runtime_id": arch_raw.runtime_id if arch_raw else None,
                    "runtime_type": arch_raw.runtime_type if arch_raw else None,
                    "account_id": arch_raw.account_id if arch_raw else None,
                    "routing_reason": arch_raw.routing_reason if arch_raw else None,
                }.items() if v is not None},
            )
        )
        if arch_raw and arch_raw.runtime_id:
            if "runtimes" not in exec_record.metadata:
                exec_record.metadata["runtimes"] = {}
            exec_record.metadata["runtimes"]["architect"] = {
                "runtime_id": arch_raw.runtime_id,
                "runtime_type": arch_raw.runtime_type,
                "account_id": arch_raw.account_id,
                "model": arch_raw.model,
                "routing_reason": arch_raw.routing_reason,
            }

        # Write Task Protocol v2 file into .jester/tasks/inbox/
        inbox_file = self._move_task_file(session.task, from_folder=None, to_folder="inbox")

        # -------------------------------------------------------------
        # STAGE 3: ACTIVATION -> ACTIVE
        # -------------------------------------------------------------
        active_file = self._move_task_file(session.task, from_folder="inbox", to_folder="active")
        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="task_activated",
                stage="active",
                status="active",
                summary=f"Task moved from inbox to active: {target_task_id}",
            )
        )

        # -------------------------------------------------------------
        # STAGE 4: EXECUTOR (with deterministic repository context)
        # -------------------------------------------------------------
        context_bundle = self.context_engine.assemble_context(
            session.task,
            role="executor",
            stage="active",
            execution_id=execution_id,
            parent_context_id=arch_context.context_id,
            include_related_tests=True,
        )
        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="context_assembled",
                stage="active",
                status="success",
                role="executor",
                summary=f"Context assembled: {len(context_bundle.files)} files, {context_bundle.total_characters} chars",
                metadata=context_bundle.to_summary_dict(),
            )
        )
        executor_extra = {
            "code_context": context_bundle.format_for_prompt(),
            "context_bundle": context_bundle.model_dump(),
        }
        if target_runtime_id:
            executor_extra["target_runtime_id"] = target_runtime_id
        if target_account:
            executor_extra["target_account"] = target_account
        if target_runtime_type:
            executor_extra["target_runtime_type"] = target_runtime_type

        if session.architect_handoff:
            executor_extra["architect_intent"] = session.architect_handoff.implementation_intent
            if session.architect_handoff.architectural_notes:
                executor_extra["architect_notes"] = session.architect_handoff.architectural_notes
        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="executor_started",
                stage="executor",
                role="executor",
            )
        )
        session = self.orchestrator.run_executor_stage(
            session,
            extra_context=executor_extra,
            architect_handoff=session.architect_handoff,
        )

        if session.current_stage in (OrchestrationStage.FAILED, OrchestrationStage.BLOCKED):
            blocked_file = self._move_task_file(session.task, from_folder="active", to_folder="blocked")
            err_msg = session.executor_result.error_message if session.executor_result else "Execution failed."
            self._record_event_safe(
                ExecutionEvent(
                    execution_id=execution_id,
                    event_type="executor_failed",
                    stage="executor",
                    status=session.current_stage.value,
                    error=err_msg,
                )
            )
            exec_record.overall_status = session.current_stage.value
            exec_record.current_stage = session.current_stage.value
            exec_record.completed_at = datetime.now(timezone.utc).isoformat()
            exec_record.error_message = err_msg
            self._update_execution_safe(exec_record)
            return WorkflowOutcome(
                task_id=target_task_id,
                stage=session.current_stage,
                session=session,
                preflight=preflight_report,
                task_file_path=self._rel_path(blocked_file),
                error_message=err_msg,
                context_bundle=context_bundle,
                execution_id=execution_id,
                persistence_error=self.last_persistence_error,
            )

        exec_raw = session.executor_result.raw_result if session.executor_result else None
        exec_usage = exec_raw.usage if exec_raw else None
        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="executor_completed",
                stage="executor",
                status="success",
                role="executor",
                agent_id=exec_raw.agent_id if exec_raw else None,
                provider=exec_raw.provider if exec_raw else None,
                model=exec_raw.model if exec_raw else None,
                summary=session.executor_result.summary if session.executor_result else "Executor finished",
                input_tokens=exec_usage.input_tokens if exec_usage else None,
                output_tokens=exec_usage.output_tokens if exec_usage else None,
                total_tokens=exec_usage.total_tokens if exec_usage else None,
                metadata={k: v for k, v in {
                    "runtime_id": exec_raw.runtime_id if exec_raw else None,
                    "runtime_type": exec_raw.runtime_type if exec_raw else None,
                    "account_id": exec_raw.account_id if exec_raw else None,
                    "routing_reason": exec_raw.routing_reason if exec_raw else None,
                }.items() if v is not None},
            )
        )
        if exec_raw and exec_raw.runtime_id:
            if "runtimes" not in exec_record.metadata:
                exec_record.metadata["runtimes"] = {}
            exec_record.metadata["runtimes"]["executor"] = {
                "runtime_id": exec_raw.runtime_id,
                "runtime_type": exec_raw.runtime_type,
                "account_id": exec_raw.account_id,
                "model": exec_raw.model,
                "routing_reason": exec_raw.routing_reason,
            }

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

            self._record_event_safe(
                ExecutionEvent(
                    execution_id=execution_id,
                    event_type="verification_started",
                    stage="verification",
                )
            )

            runtime_res = self.runtime.execute_and_verify(
                changes=changes,
                task=session.task,
                auto_rollback_on_failure=True,
            )
            verification_output = runtime_res.verification_output
            session.executor_result.diff = runtime_res.diff
            session.executor_result.files_modified = runtime_res.files_modified
            if session.executor_handoff:
                session.executor_handoff.diff = runtime_res.diff
                session.executor_handoff.verification_output = verification_output
                session.executor_handoff.verification_passed = runtime_res.verification_passed
                session.executor_handoff.files_modified = runtime_res.files_modified
                session.executor_handoff.runtime_result = runtime_res.model_dump()

            if not runtime_res.verification_passed:
                session.current_stage = OrchestrationStage.BLOCKED
                session.task.blocked_reason = f"Runtime execution / verification failed: {runtime_res.error_message}"
                blocked_file = self._move_task_file(session.task, from_folder="active", to_folder="blocked")
                self._record_event_safe(
                    ExecutionEvent(
                        execution_id=execution_id,
                        event_type="verification_failed",
                        stage="verification",
                        status="blocked",
                        summary=verification_output,
                        error=runtime_res.error_message,
                    )
                )
                exec_record.overall_status = "blocked"
                exec_record.current_stage = "blocked"
                exec_record.completed_at = datetime.now(timezone.utc).isoformat()
                exec_record.verification_passed = False
                exec_record.verification_summary = verification_output
                exec_record.error_message = runtime_res.error_message
                self._update_execution_safe(exec_record)
                return WorkflowOutcome(
                    task_id=target_task_id,
                    stage=OrchestrationStage.BLOCKED,
                    session=session,
                    preflight=preflight_report,
                    runtime_result=runtime_res,
                    task_file_path=self._rel_path(blocked_file),
                    error_message=runtime_res.error_message,
                    diff=runtime_res.diff,
                    context_bundle=context_bundle,
                    execution_id=execution_id,
                    persistence_error=self.last_persistence_error,
                )

            self._record_event_safe(
                ExecutionEvent(
                    execution_id=execution_id,
                    event_type="verification_completed",
                    stage="verification",
                    status="success",
                    summary=verification_output,
                )
            )
            self._record_event_safe(
                ExecutionEvent(
                    execution_id=execution_id,
                    event_type="diff_generated",
                    stage="verification",
                    status="success",
                    summary=f"Unified diff generated for {len(runtime_res.files_modified)} files",
                    metadata={"files_modified": runtime_res.files_modified},
                )
            )

        diff_str = runtime_res.diff if runtime_res else "No file changes detected."

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
            + f"\n\n## Code Diff\n```diff\n{diff_str}\n```\n"
            + f"\n{token_section_impl}\n"
            + f"## Verification Output\n```text\n{verification_output}\n```\n"
        )
        impl_report_content = sanitize_portable_paths(impl_report_raw, self.repo_root)
        impl_report_path.write_text(impl_report_content, encoding="utf-8")

        # -------------------------------------------------------------
        # STAGE 6: REVIEWER (with actual unified diff evidence)
        # -------------------------------------------------------------
        review_file = self._move_task_file(session.task, from_folder="active", to_folder="review")

        # Assemble role-aware context for Reviewer
        reviewer_context = self.context_engine.assemble_context(
            task=session.task,
            role="reviewer",
            stage="review",
            execution_id=execution_id,
            parent_context_id=context_bundle.context_id,
            diff=diff_str,
            verification_output=verification_output,
            changed_files=runtime_res.files_modified if runtime_res else None,
            include_related_tests=True,
        )
        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="context_assembled",
                stage="review",
                status="success",
                role="reviewer",
                summary=f"Reviewer context assembled: {len(reviewer_context.files)} files, {reviewer_context.total_characters} chars",
                metadata=reviewer_context.to_summary_dict(),
            )
        )

        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="review_started",
                stage="reviewer",
                role="reviewer",
            )
        )

        rev_extra = {
            "reviewer_context": reviewer_context.format_for_prompt(),
            "reviewer_context_bundle": reviewer_context.model_dump(),
            "files_modified": runtime_res.files_modified if runtime_res else [],
        }
        if target_runtime_id:
            rev_extra["target_runtime_id"] = target_runtime_id
        if target_account:
            rev_extra["target_account"] = target_account
        if target_runtime_type:
            rev_extra["target_runtime_type"] = target_runtime_type

        session = self.orchestrator.run_reviewer_stage(
            session,
            verification_output=verification_output,
            diff=diff_str,
            extra_context=rev_extra,
            executor_handoff=session.executor_handoff,
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
            f"## Code Diff\n```diff\n{diff_str}\n```\n\n"
            f"{token_section_rev}"
        )
        rev_report_content = sanitize_portable_paths(rev_report_raw, self.repo_root)
        rev_report_path.write_text(rev_report_content, encoding="utf-8")

        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="review_completed",
                stage="reviewer",
                status=verdict_str,
                role="reviewer",
                agent_id=rev_raw.agent_id if rev_raw else None,
                provider=rev_raw.provider if rev_raw else None,
                model=rev_raw.model if rev_raw else None,
                summary=session.review_result.summary if session.review_result else verdict_str,
                input_tokens=rev_usage.input_tokens if rev_usage else None,
                output_tokens=rev_usage.output_tokens if rev_usage else None,
                total_tokens=rev_usage.total_tokens if rev_usage else None,
                metadata={k: v for k, v in {
                    "runtime_id": rev_raw.runtime_id if rev_raw else None,
                    "runtime_type": rev_raw.runtime_type if rev_raw else None,
                    "account_id": rev_raw.account_id if rev_raw else None,
                    "routing_reason": rev_raw.routing_reason if rev_raw else None,
                }.items() if v is not None},
            )
        )
        if rev_raw and rev_raw.runtime_id:
            if "runtimes" not in exec_record.metadata:
                exec_record.metadata["runtimes"] = {}
            exec_record.metadata["runtimes"]["reviewer"] = {
                "runtime_id": rev_raw.runtime_id,
                "runtime_type": rev_raw.runtime_type,
                "account_id": rev_raw.account_id,
                "model": rev_raw.model,
                "routing_reason": rev_raw.routing_reason,
            }

        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="awaiting_human_signoff",
                stage="awaiting_human_signoff",
                status="awaiting_human_signoff",
                summary="Review completed. Workflow halted awaiting explicit human sign-off.",
            )
        )

        exec_record.overall_status = session.current_stage.value
        exec_record.current_stage = session.current_stage.value
        exec_record.total_input_tokens = total_usage.input_tokens
        exec_record.total_output_tokens = total_usage.output_tokens
        exec_record.total_tokens = total_usage.total_tokens
        exec_record.verification_passed = True if (runtime_res and runtime_res.verification_passed) else None
        exec_record.verification_summary = verification_output
        exec_record.reviewer_verdict = verdict_str
        exec_record.reviewer_summary = session.review_result.summary if session.review_result else None
        exec_record.final_summary = f"Completed review with verdict {verdict_str}"
        self._update_execution_safe(exec_record)

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
            diff=diff_str,
            context_bundle=context_bundle,
            architect_context=arch_context,
            reviewer_context=reviewer_context,
            execution_id=execution_id,
            persistence_error=self.last_persistence_error,
        )

    def deliver_approved_work(
        self,
        session: OrchestrationSession,
        commit_auth: CommitAuthorization,
        push_auth: Optional[PushAuthorization] = None,
    ) -> GitOperationResult:
        """
        Executes controlled Git delivery for an approved session.
        Enforces that session has passed review and has human signoff.
        """
        execution_id = f"exec-{session.session_id}"
        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="git_delivery_started",
                stage="delivery",
                status="started",
                summary=f"Git delivery started for task {session.task.id}",
                metadata={"approved_files": commit_auth.approved_files},
            )
        )

        commit_res = self.git_controller.commit(
            authorization=commit_auth,
            session=session,
        )
        if not commit_res.success:
            self._record_event_safe(
                ExecutionEvent(
                    execution_id=execution_id,
                    event_type="git_commit_failed",
                    stage="delivery",
                    status="failed",
                    error=commit_res.error,
                )
            )
            self.last_delivery_result = commit_res
            return commit_res

        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="git_commit_completed",
                stage="delivery",
                status="success",
                summary=f"Commit created: {commit_res.commit_hash}",
                metadata={"commit_hash": commit_res.commit_hash, "branch": commit_res.branch},
            )
        )

        if push_auth:
            push_res = self.git_controller.push(authorization=push_auth)
            if push_res.success:
                self._record_event_safe(
                    ExecutionEvent(
                        execution_id=execution_id,
                        event_type="git_push_completed",
                        stage="delivery",
                        status="success",
                        summary=f"Pushed to {push_res.remote}/{push_res.branch}",
                        metadata={"remote": push_res.remote, "branch": push_res.branch},
                    )
                )
            else:
                self._record_event_safe(
                    ExecutionEvent(
                        execution_id=execution_id,
                        event_type="git_push_failed",
                        stage="delivery",
                        status="failed",
                        error=push_res.error,
                    )
                )
            self.last_delivery_result = push_res
            return push_res

        self.last_delivery_result = commit_res
        return commit_res

    def complete_human_approval(
        self,
        session: OrchestrationSession,
        approver: str,
        notes: str = "Approved.",
        commit_auth: Optional[CommitAuthorization] = None,
        push_auth: Optional[PushAuthorization] = None,
    ) -> Path:
        """
        Finalizes human approval gate and transitions task to .jester/tasks/completed/.
        If commit_auth is provided, executes controlled Git delivery post-approval.
        """
        execution_id = f"exec-{session.session_id}"
        session = self.orchestrator.approve_human_signoff(session, approver=approver, notes=notes)

        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="human_approved",
                stage="human_signoff",
                status="approved",
                summary=f"Human signoff approved by {approver}: {notes}",
                metadata={"approver": approver, "notes": notes},
            )
        )

        if commit_auth:
            delivery_res = self.deliver_approved_work(
                session=session,
                commit_auth=commit_auth,
                push_auth=push_auth,
            )
            if not delivery_res.success:
                raise GitControllerError(f"Git delivery failed: {delivery_res.error}")

        completed_file = self._move_task_file(session.task, from_folder="review", to_folder="completed")

        rec = self.history_store.get_execution(execution_id) if self.history_store else None
        if rec:
            rec.overall_status = OrchestrationStage.COMPLETED.value
            rec.current_stage = OrchestrationStage.COMPLETED.value

            rec.completed_at = datetime.now(timezone.utc).isoformat()
            rec.human_signoff_by = approver
            rec.human_signoff_notes = notes
            if self.last_delivery_result and self.last_delivery_result.success:
                rec.git_commit_hash = self.last_delivery_result.commit_hash
                rec.git_branch = self.last_delivery_result.branch
                rec.git_pushed = self.last_delivery_result.pushed
                rec.git_delivery_summary = f"Delivered via commit {self.last_delivery_result.commit_hash}"
            self._update_execution_safe(rec)

        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="execution_completed",
                stage="completed",
                status="completed",
                summary=f"Task {session.task.id} finalized and moved to completed.",
            )
        )
        return completed_file

    def reject_human_signoff(
        self, session: OrchestrationSession, rejector: str, reason: str = "Rejected by human reviewer."
    ) -> Path:
        """
        Records human rejection at the approval gate and transitions task file.
        """
        execution_id = f"exec-{session.session_id}"
        session = self.orchestrator.reject_human_signoff(session, rejector=rejector, reason=reason)

        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="human_rejected",
                stage="human_signoff",
                status="rejected",
                summary=f"Human signoff rejected by {rejector}: {reason}",
                metadata={"rejector": rejector, "reason": reason},
            )
        )

        target_folder = "blocked" if session.current_stage == OrchestrationStage.BLOCKED else "active"
        target_file = self._move_task_file(session.task, from_folder="review", to_folder=target_folder)

        rec = self.history_store.get_execution(execution_id) if self.history_store else None
        if rec:
            rec.overall_status = session.current_stage.value
            rec.current_stage = session.current_stage.value
            if session.current_stage == OrchestrationStage.BLOCKED:
                rec.completed_at = datetime.now(timezone.utc).isoformat()
                rec.error_message = reason
            self._update_execution_safe(rec)

        if session.current_stage == OrchestrationStage.REWORK_REQUIRED:
            self._record_event_safe(
                ExecutionEvent(
                    execution_id=execution_id,
                    event_type="rework_requested",
                    stage="active",
                    status="rework_required",
                    summary=f"Task {session.task.id} moved to rework: {reason}",
                )
            )
        elif session.current_stage == OrchestrationStage.BLOCKED:
            self._record_event_safe(
                ExecutionEvent(
                    execution_id=execution_id,
                    event_type="execution_blocked",
                    stage="blocked",
                    status="blocked",
                    error=reason,
                )
            )

        return target_file

    def run_rework_cycle(
        self,
        session: OrchestrationSession,
        rework_feedback: Optional[str] = None,
        rework_objective: Optional[str] = None,
        auto_apply: bool = True,
    ) -> WorkflowOutcome:
        """
        Executes a controlled rework cycle following Reviewer or human signoff rejection.
        Guarantees:
        - Fresh workspace state assembled from live disk (never reuses stale source code).
        - Previous diff and reviewer feedback bounded and categorized as historical explanation.
        - Chained context lineage (parent_context_id -> context_id).
        - Dispatches Executor, runs runtime execution & verification, and re-invokes Reviewer.
        """
        execution_id = f"exec-{session.session_id}"
        task = session.task
        task_id = task.id

        # 1. Resolve parent context from previous reviewer handoff or session
        parent_ctx_id = (
            session.reviewer_handoff.context_id
            if session.reviewer_handoff
            else session.current_context_id
        )

        review_text = None
        if session.review_result:
            if session.review_result.feedback and session.review_result.summary:
                review_text = f"{session.review_result.summary} — {session.review_result.feedback}"
            else:
                review_text = session.review_result.feedback or session.review_result.summary

        effective_feedback = (
            rework_feedback
            or review_text
            or "Address reviewer feedback"
        )
        effective_defects = (
            session.review_result.error_message
            if (session.review_result and session.review_result.error_message)
            else (session.reviewer_handoff.defect_details if session.reviewer_handoff else None)
        )
        prev_diff = (
            session.executor_result.diff
            if (session.executor_result and hasattr(session.executor_result, "diff"))
            else None
        )
        prev_verification = (
            session.executor_handoff.verification_output
            if session.executor_handoff
            else None
        )
        arch_intent = (
            session.architect_handoff.implementation_intent
            if session.architect_handoff
            else None
        )
        prev_summary = (
            session.executor_result.summary
            if session.executor_result
            else None
        )

        # 2. Assemble fresh rework context (guarantees live disk state precedence)
        rework_pkg = self.context_engine.assemble_rework_context(
            task=task,
            execution_id=execution_id,
            parent_context_id=parent_ctx_id or "ctx-initial",
            reviewer_feedback=effective_feedback,
            reviewer_defect_details=effective_defects,
            previous_diff=prev_diff,
            previous_verification_output=prev_verification,
            architect_intent=arch_intent,
            previous_implementation_summary=prev_summary,
            rework_objective=rework_objective,
            changed_files=session.executor_result.files_modified if session.executor_result else None,
            include_related_tests=True,
        )

        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="context_assembled",
                stage="rework_executor",
                status="success",
                role="executor",
                summary=f"Rework context assembled: {len(rework_pkg.files)} files, {rework_pkg.total_characters} chars",
                metadata=rework_pkg.to_summary_dict(),
            )
        )

        # 3. Transition to active in task files
        active_file = self._move_task_file(session.task, from_folder="review", to_folder="active")

        # 4. Run Executor stage with rework context
        executor_extra = {
            "code_context": rework_pkg.format_for_prompt(),
            "context_bundle": rework_pkg.model_dump(),
            "rework_feedback": effective_feedback,
        }
        if arch_intent:
            executor_extra["architect_intent"] = arch_intent

        session.current_stage = OrchestrationStage.REWORK_REQUIRED

        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="executor_started",
                stage="rework_executor",
                role="executor",
                summary=f"Executor re-invoked for rework on task {task_id}",
            )
        )
        session = self.orchestrator.run_executor_stage(
            session,
            extra_context=executor_extra,
            architect_handoff=session.architect_handoff,
        )

        if session.current_stage in (OrchestrationStage.FAILED, OrchestrationStage.BLOCKED):
            blocked_file = self._move_task_file(session.task, from_folder="active", to_folder="blocked")
            err_msg = session.executor_result.error_message if session.executor_result else "Rework execution failed."
            return WorkflowOutcome(
                task_id=task_id,
                stage=session.current_stage,
                session=session,
                preflight=PreflightReport(is_valid=True),
                task_file_path=self._rel_path(blocked_file),
                error_message=err_msg,
                context_bundle=rework_pkg,
                rework_context=rework_pkg,
                execution_id=execution_id,
                persistence_error=self.last_persistence_error,
            )

        # 5. Runtime execution & verification
        runtime_res = None
        verification_output = "No changes to verify."
        if auto_apply and session.executor_result:
            changes = extract_file_changes_from_text(session.executor_result.summary)
            if not changes and session.executor_result.raw_result:
                changes = extract_file_changes_from_text(session.executor_result.raw_result.summary)

            runtime_res = self.runtime.execute_and_verify(
                changes=changes,
                task=session.task,
                auto_rollback_on_failure=True,
            )
            verification_output = runtime_res.verification_output
            session.executor_result.diff = runtime_res.diff
            session.executor_result.files_modified = runtime_res.files_modified
            if session.executor_handoff:
                session.executor_handoff.diff = runtime_res.diff
                session.executor_handoff.verification_output = verification_output
                session.executor_handoff.verification_passed = runtime_res.verification_passed
                session.executor_handoff.files_modified = runtime_res.files_modified
                session.executor_handoff.runtime_result = runtime_res.model_dump()

        diff_str = runtime_res.diff if runtime_res else "No file changes detected."

        # 6. Re-assemble Reviewer context with new current diff and parent_context_id = rework_pkg.context_id
        review_file = self._move_task_file(session.task, from_folder="active", to_folder="review")
        reviewer_context = self.context_engine.assemble_context(
            task=session.task,
            role="reviewer",
            stage="rework_reviewer",
            execution_id=execution_id,
            parent_context_id=rework_pkg.context_id,
            diff=diff_str,
            verification_output=verification_output,
            previous_diff=prev_diff,
            previous_verification_output=prev_verification,
            reviewer_feedback=effective_feedback,
            changed_files=runtime_res.files_modified if runtime_res else None,
            include_related_tests=True,
        )

        self._record_event_safe(
            ExecutionEvent(
                execution_id=execution_id,
                event_type="context_assembled",
                stage="rework_reviewer",
                status="success",
                role="reviewer",
                summary=f"Rework Reviewer context assembled: {len(reviewer_context.files)} files, {reviewer_context.total_characters} chars",
                metadata=reviewer_context.to_summary_dict(),
            )
        )

        session = self.orchestrator.run_reviewer_stage(
            session,
            verification_output=verification_output,
            diff=diff_str,
            extra_context={
                "reviewer_context": reviewer_context.format_for_prompt(),
                "reviewer_context_bundle": reviewer_context.model_dump(),
                "files_modified": runtime_res.files_modified if runtime_res else [],
            },
            executor_handoff=session.executor_handoff,
        )

        total_usage = session.get_total_usage()
        return WorkflowOutcome(
            task_id=task_id,
            stage=session.current_stage,
            session=session,
            preflight=PreflightReport(is_valid=True),
            runtime_result=runtime_res,
            task_file_path=self._rel_path(review_file),
            usage=total_usage,
            stage_usage=session.get_stage_usage(),
            diff=diff_str,
            context_bundle=rework_pkg,
            reviewer_context=reviewer_context,
            rework_context=rework_pkg,
            execution_id=execution_id,
            persistence_error=self.last_persistence_error,
        )
