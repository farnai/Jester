"""
JESTER Founder Local Interface Server (TASK-0011).

Provides the local-first HTTP and Web interface for the JESTER AI Bridge:
- Task intake and automated workflow dispatch.
- Live execution tracking and stage progression.
- Execution history retrieval and event timeline.
- Role-specific context snapshot and provenance inspection.
- Structured handoff inspection (Architect -> Executor -> Reviewer).
- Real runtime diff and verification output inspection.
- Reviewer verdict and feedback visualization.
- Mandatory Human Signoff gate (APPROVE / REJECT).
- Controlled Git delivery results via GitController.
- Zero autonomous commits or pushes.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import threading
from typing import Any, Dict, List, Optional
import uuid

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from .config import load_bridge_config
from .core import BridgeCore
from .execution_history import ExecutionHistoryStore, ExecutionRecord
from .git_controller import (
    CommitAuthorization,
    GitController,
    GitControllerError,
    PushAuthorization,
)
from .google_provider import GoogleProvider
from .openai_provider import OpenAIProvider
from .orchestration import OrchestrationSession, OrchestrationStage, ReviewVerdict
from .protocol import Task, load_task_from_file
from .testing import MockProviderA, MockProviderB
from .workflow import ControlledWorkflowRunner, WorkflowOutcome


# --- Pydantic Request & Response Models ---

class TaskCreateRequest(BaseModel):
    """Natural-language task creation request from the Founder."""
    intent: str
    task_id: Optional[str] = None
    scope: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None
    verification: Optional[List[str]] = None
    auto_apply: bool = True
    simulate_all: bool = False
    sync: bool = False


class HumanSignoffRequest(BaseModel):
    """Human approval or rejection payload for AWAITING_HUMAN_SIGNOFF gate."""
    decision: str  # "approve" or "reject"
    approver: str = "founder"
    notes: Optional[str] = "Approved by Founder via Local Interface."
    commit_message: Optional[str] = None
    approved_files: Optional[List[str]] = None
    push: bool = False
    remote: str = "origin"
    branch: Optional[str] = None
    reason: Optional[str] = None  # If rejecting


class PushAuthorizeRequest(BaseModel):
    """Explicit human push authorization payload."""
    task_id: str
    approver: str = "founder"
    remote: str = "origin"
    branch: Optional[str] = None


class ReworkRequest(BaseModel):
    """Payload to trigger a controlled rework cycle."""
    rework_feedback: Optional[str] = None
    rework_objective: Optional[str] = None
    auto_apply: bool = True
    sync: bool = False


# In-memory session tracking for active executions
_active_sessions: Dict[str, OrchestrationSession] = {}
_active_outcomes: Dict[str, WorkflowOutcome] = {}
_active_threads: Dict[str, threading.Thread] = {}
_session_lock = threading.Lock()


def _sanitize_sensitive_strings(text: Optional[str]) -> Optional[str]:
    """Redacts common credentials or API tokens from text."""
    if not text:
        return text
    # Mask common API keys and tokens
    text = re.sub(r"\b(sk-[a-zA-Z0-9_\-]{20,})\b", "[REDACTED_API_KEY]", text)
    text = re.sub(r"\b(AIza[a-zA-Z0-9_\-]{30,})\b", "[REDACTED_API_KEY]", text)
    text = re.sub(r"(Bearer\s+)[a-zA-Z0-9_\-\.]{20,}", r"\1[REDACTED_TOKEN]", text, flags=re.IGNORECASE)
    return text


def create_bridge_app(
    repo_root: Optional[Path] = None,
    runner: Optional[ControlledWorkflowRunner] = None,
    history_store: Optional[ExecutionHistoryStore] = None,
    git_controller: Optional[GitController] = None,
) -> FastAPI:
    """
    Factory creating the FastAPI Founder Local Interface application.
    Allows dependency injection for unit and integration tests.
    """
    root = (repo_root or Path.cwd()).resolve()

    # Initialize store and controllers if not injected
    store = history_store or ExecutionHistoryStore(repo_root=root)
    git = git_controller or GitController(repo_root=root)

    if runner is None:
        config_path = root / ".jester" / "config" / "agents.json"
        config = load_bridge_config(config_path) if config_path.exists() else None
        if config:
            # Register real providers by default (never silently fallback to mock)
            providers = {
                "openai": OpenAIProvider(),
                "google": GoogleProvider(),
            }
            core = BridgeCore(config=config, providers=providers)
            import shutil
            if shutil.which("agy"):
                from .adapters import CLIRuntimeAdapter
                from .runtimes import create_antigravity_runtime
                agy_adapter = CLIRuntimeAdapter(provider_id="google", executable_name="agy")
                core.register_runtime(create_antigravity_runtime(adapter=agy_adapter))
        else:
            core = None

        runner = ControlledWorkflowRunner(
            core=core,
            repo_root=root,
            history_store=store,
            git_controller=git,
        ) if core else None

    app = FastAPI(
        title="JESTER Founder Local Interface",
        version="1.0.0",
        description="Local-first operational control surface for the JESTER Provider-Agnostic AI Bridge.",
    )

    # CORS configuration for local browser access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store references on app state for route access
    app.state.repo_root = root
    app.state.runner = runner
    app.state.history_store = store
    app.state.git_controller = git

    # --- API Routes ---

    @app.get("/api/health")
    def get_health():
        """Health check returning bridge readiness status."""
        provider_status = {}
        if app.state.runner and app.state.runner.core:
            for pid, prov in app.state.runner.core.providers.items():
                is_mock = isinstance(prov, (MockProviderA, MockProviderB))
                provider_status[pid] = {
                    "healthy": prov.health_check(),
                    "provider_type": "mock" if is_mock else "live",
                }

        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repository": str(app.state.repo_root.name),
            "runner_ready": app.state.runner is not None,
            "git_ready": app.state.git_controller is not None,
            "history_ready": app.state.history_store is not None,
            "providers": provider_status,
        }

    @app.get("/api/runtimes")
    def list_runtimes():
        """Lists registered execution runtimes, account identities, and readiness status."""
        runtimes_data = []
        if app.state.runner and app.state.runner.core:
            for r in app.state.runner.core.runtime_registry.list_runtimes():
                readiness = r.check_readiness()
                runtimes_data.append({
                    "runtime_id": r.runtime_id,
                    "provider_id": r.provider_id,
                    "runtime_type": r.runtime_type.value,
                    "account_id": r.account.account_id,
                    "account_label": r.account.label,
                    "model": r.model,
                    "status": readiness.status.value,
                    "message": readiness.message,
                    "priority": r.priority,
                    "capabilities": sorted(list(r.capabilities)),
                })
        return {"runtimes": runtimes_data}

    @app.post("/api/tasks", status_code=status.HTTP_201_CREATED)
    def create_and_run_task(req: TaskCreateRequest):
        """
        Submits a natural-language Founder request into the task workflow.
        Dispatches through ControlledWorkflowRunner.
        """
        if not req.intent or not req.intent.strip():
            raise HTTPException(status_code=400, detail="Founder request intent cannot be empty.")

        r: ControlledWorkflowRunner = app.state.runner
        if not r:
            raise HTTPException(status_code=500, detail="ControlledWorkflowRunner is not initialized.")

        # Determine task ID
        task_id = req.task_id
        if not task_id:
            task_id = f"TASK-{uuid.uuid4().hex[:4].upper()}"

        # Setup simulation providers ONLY if explicitly requested
        if req.simulate_all and r.core:
            r.core.register_provider(MockProviderA("openai", default_summary=f"Architecture for {task_id}: {req.intent}"))
            sim_code = f"```python\n# Implementation for {task_id}\n# Intent: {req.intent}\n```"
            r.core.register_provider(MockProviderB("google", default_summary=sim_code))
            r.core._simulated = True
        elif r.core and getattr(r.core, "_simulated", False):
            # Restore real providers if a prior request explicitly enabled simulation
            r.core.register_provider(OpenAIProvider())
            r.core.register_provider(GoogleProvider())
            r.core._simulated = False

        def _execute():
            try:
                outcome = r.run_e2e_workflow(
                    intent=req.intent,
                    target_task_id=task_id,
                    scope=req.scope,
                    constraints=req.constraints,
                    acceptance_criteria=req.acceptance_criteria,
                    verification=req.verification,
                    auto_apply=req.auto_apply,
                    check_credentials=not req.simulate_all,
                )
                with _session_lock:
                    if outcome.execution_id:
                        _active_sessions[outcome.execution_id] = outcome.session
                        _active_outcomes[outcome.execution_id] = outcome
            except Exception:
                pass

        if req.sync:
            # Synchronous execution (useful for testing and deterministic inspection)
            outcome = r.run_e2e_workflow(
                intent=req.intent,
                target_task_id=task_id,
                scope=req.scope,
                constraints=req.constraints,
                acceptance_criteria=req.acceptance_criteria,
                verification=req.verification,
                auto_apply=req.auto_apply,
                check_credentials=not req.simulate_all,
            )
            with _session_lock:
                if outcome.execution_id:
                    _active_sessions[outcome.execution_id] = outcome.session
                    _active_outcomes[outcome.execution_id] = outcome
            return {
                "task_id": task_id,
                "execution_id": outcome.execution_id,
                "stage": outcome.stage.value if hasattr(outcome.stage, "value") else str(outcome.stage),
                "error": outcome.error_message,
            }
        else:
            # Asynchronous background thread execution
            worker_thread = threading.Thread(target=_execute, daemon=True)
            worker_thread.start()
            with _session_lock:
                _active_threads[task_id] = worker_thread

            return {
                "task_id": task_id,
                "execution_id": None,
                "status": "started",
                "message": f"Task {task_id} workflow started.",
            }

    @app.get("/api/tasks")
    def list_tasks():
        """Lists tasks from the .jester/tasks/ lifecycle folders."""
        tasks_root = app.state.repo_root / ".jester" / "tasks"
        folders = ["inbox", "active", "review", "completed", "blocked"]
        categorized: Dict[str, List[Dict[str, Any]]] = {f: [] for f in folders}

        if tasks_root.exists():
            for folder in folders:
                f_path = tasks_root / folder
                if f_path.exists():
                    for p in f_path.glob("*.json"):
                        try:
                            t = load_task_from_file(p)
                            categorized[folder].append({
                                "id": t.id,
                                "title": t.title,
                                "status": folder,
                                "priority": t.priority,
                                "role": t.role,
                                "created_at": t.created_at,
                                "goal": t.goal,
                                "path": f".jester/tasks/{folder}/{p.name}",
                            })
                        except Exception:
                            continue

        return {"tasks": categorized}

    @app.get("/api/tasks/{task_id}")
    def get_task(task_id: str):
        """Loads a specific task definition from .jester/tasks/."""
        tasks_root = app.state.repo_root / ".jester" / "tasks"
        for folder in ["inbox", "active", "review", "completed", "blocked"]:
            candidate = tasks_root / folder / f"{task_id}.json"
            if candidate.exists():
                try:
                    task = load_task_from_file(candidate)
                    return {
                        "task": task.to_dict(),
                        "folder": folder,
                        "file_path": f".jester/tasks/{folder}/{task_id}.json",
                    }
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to parse task: {str(e)}")

        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found in .jester/tasks/")

    @app.get("/api/executions")
    def list_executions(limit: int = Query(50, ge=1, le=200)):
        """Lists recent execution records from Persistent Execution History."""
        s: ExecutionHistoryStore = app.state.history_store
        records = s.list_recent_executions(limit=limit)
        return {
            "executions": [
                {
                    "execution_id": r.execution_id,
                    "task_id": r.task_id,
                    "task_title": r.task_title,
                    "overall_status": r.overall_status,
                    "current_stage": r.current_stage,
                    "created_at": r.created_at,
                    "completed_at": r.completed_at,
                    "verification_passed": r.verification_passed,
                    "reviewer_verdict": r.reviewer_verdict,
                    "human_signoff_by": r.human_signoff_by,
                    "git_commit_hash": r.git_commit_hash,
                    "total_tokens": r.total_tokens,
                }
                for r in records
            ]
        }

    @app.get("/api/executions/latest")
    def get_latest_execution():
        """Retrieves the most recent execution record."""
        s: ExecutionHistoryStore = app.state.history_store
        records = s.list_recent_executions(limit=1)
        if not records:
            return {"execution": None}
        return {"execution": records[0].model_dump()}

    @app.get("/api/executions/{execution_id}")
    def get_execution_details(execution_id: str):
        """
        Retrieves full execution details:
        record, timeline events, verification output, reviewer summary, and handoffs.
        """
        s: ExecutionHistoryStore = app.state.history_store
        record = s.get_execution(execution_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found.")

        events = s.get_events_for_execution(execution_id)
        summary = s.get_execution_summary(execution_id)

        # Check active session if available
        with _session_lock:
            session = _active_sessions.get(execution_id)
            outcome = _active_outcomes.get(execution_id)

        # Retrieve diff if present in outcome, session, or implementation report
        diff_content = None
        if outcome and outcome.diff:
            diff_content = outcome.diff
        elif session and session.executor_result and session.executor_result.diff:
            diff_content = session.executor_result.diff
        else:
            # Fallback to report file
            impl_path = app.state.repo_root / ".jester" / "reports" / "implementations" / f"{record.task_id}.md"
            if impl_path.exists():
                try:
                    text = impl_path.read_text(encoding="utf-8")
                    match = re.search(r"```diff\n([\s\S]*?)\n```", text)
                    if match:
                        diff_content = match.group(1)
                except Exception:
                    pass

        # Retrieve reviewer feedback
        reviewer_feedback = None
        if session and session.review_result and session.review_result.feedback:
            reviewer_feedback = session.review_result.feedback
        else:
            rev_path = app.state.repo_root / ".jester" / "reports" / "reviews" / f"{record.task_id}.md"
            if rev_path.exists():
                try:
                    text = rev_path.read_text(encoding="utf-8")
                    match = re.search(r"\*\*Feedback:\*\*\s*([\s\S]*?)\n\n", text)
                    if match:
                        reviewer_feedback = match.group(1).strip()
                except Exception:
                    pass

        # Retrieve handoffs
        handoffs = {}
        if session:
            if session.architect_handoff:
                handoffs["architect"] = session.architect_handoff.model_dump()
            if session.executor_handoff:
                handoffs["executor"] = session.executor_handoff.model_dump()
            if session.reviewer_handoff:
                handoffs["reviewer"] = session.reviewer_handoff.model_dump()

        return {
            "record": record.model_dump(),
            "summary": summary,
            "events": [e.model_dump() for e in events],
            "diff": diff_content,
            "reviewer_feedback": reviewer_feedback,
            "handoffs": handoffs,
            "is_awaiting_signoff": record.overall_status == OrchestrationStage.AWAITING_HUMAN_SIGNOFF.value,
        }

    @app.get("/api/executions/{execution_id}/diff")
    def get_execution_diff(execution_id: str):
        """Retrieves the unified diff generated during an execution."""
        s: ExecutionHistoryStore = app.state.history_store
        record = s.get_execution(execution_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found.")

        with _session_lock:
            outcome = _active_outcomes.get(execution_id)
            session = _active_sessions.get(execution_id)

        if outcome and outcome.diff:
            return {"diff": outcome.diff}
        if session and session.executor_result and session.executor_result.diff:
            return {"diff": session.executor_result.diff}

        impl_path = app.state.repo_root / ".jester" / "reports" / "implementations" / f"{record.task_id}.md"
        if impl_path.exists():
            try:
                text = impl_path.read_text(encoding="utf-8")
                match = re.search(r"```diff\n([\s\S]*?)\n```", text)
                if match:
                    return {"diff": match.group(1)}
            except Exception:
                pass

        return {"diff": "No diff recorded."}

    @app.get("/api/executions/{execution_id}/context")
    def get_execution_context(execution_id: str):
        """
        Retrieves context snapshot metadata and budget utilization.
        Strictly secret-redacted; never returns credentials or protected contents.
        """
        s: ExecutionHistoryStore = app.state.history_store
        record = s.get_execution(execution_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found.")

        events = s.get_events_for_execution(execution_id)
        context_events = [e for e in events if e.event_type == "context_assembled"]

        contexts = []
        for ce in context_events:
            meta = ce.metadata or {}
            contexts.append({
                "stage": ce.stage,
                "role": ce.role,
                "summary": ce.summary,
                "context_id": meta.get("context_id"),
                "parent_context_id": meta.get("parent_context_id"),
                "total_characters": meta.get("total_characters"),
                "max_characters": meta.get("max_characters"),
                "selected_file_count": meta.get("selected_file_count"),
                "excluded_file_count": meta.get("excluded_file_count"),
                "truncated": meta.get("truncated", False),
                "provenance": meta.get("provenance", []),
                "file_freshness_hashes": meta.get("file_freshness_hashes", {}),
            })

        return {
            "execution_id": execution_id,
            "task_id": record.task_id,
            "contexts": contexts,
        }

    @app.post("/api/executions/{execution_id}/signoff")
    def submit_human_signoff(execution_id: str, req: HumanSignoffRequest):
        """
        Human Signoff Gate.
        Enforces mandatory approval or rejection before task completion or delivery.
        """
        s: ExecutionHistoryStore = app.state.history_store
        record = s.get_execution(execution_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found.")

        if record.overall_status != OrchestrationStage.AWAITING_HUMAN_SIGNOFF.value:
            raise HTTPException(
                status_code=400,
                detail=f"Execution is in stage '{record.overall_status}', not 'AWAITING_HUMAN_SIGNOFF'.",
            )

        r: ControlledWorkflowRunner = app.state.runner
        if not r:
            raise HTTPException(status_code=500, detail="ControlledWorkflowRunner is not initialized.")

        # Resolve or reconstruct session
        with _session_lock:
            session = _active_sessions.get(execution_id)

        if not session:
            # Reconstruct session from .jester/tasks/review/{task_id}.json
            task_file = app.state.repo_root / ".jester" / "tasks" / "review" / f"{record.task_id}.json"
            if not task_file.exists():
                raise HTTPException(
                    status_code=400,
                    detail=f"Task file for '{record.task_id}' not found in review folder.",
                )
            loaded_task = load_task_from_file(task_file)
            session = r.orchestrator.create_session(task=loaded_task)
            session.current_stage = OrchestrationStage.AWAITING_HUMAN_SIGNOFF

        if req.decision.lower() == "approve":
            commit_auth = None
            if req.commit_message and req.approved_files:
                commit_auth = CommitAuthorization(
                    task_id=record.task_id,
                    approver=req.approver,
                    approved_files=req.approved_files,
                    commit_message=req.commit_message,
                    notes=req.notes,
                )

            push_auth = None
            if req.push and commit_auth:
                push_auth = PushAuthorization(
                    task_id=record.task_id,
                    approver=req.approver,
                    remote=req.remote,
                    branch=req.branch,
                )

            try:
                completed_file = r.complete_human_approval(
                    session=session,
                    approver=req.approver,
                    notes=req.notes or "Approved.",
                    commit_auth=commit_auth,
                    push_auth=push_auth,
                )
            except GitControllerError as e:
                raise HTTPException(status_code=400, detail=f"Git delivery error: {str(e)}")

            return {
                "decision": "approved",
                "task_id": record.task_id,
                "execution_id": execution_id,
                "completed_file": str(completed_file),
                "git_delivery": r.last_delivery_result.model_dump() if r.last_delivery_result else None,
            }

        elif req.decision.lower() == "reject":
            reason = req.reason or "Rejected by human reviewer."
            rejected_file = r.reject_human_signoff(
                session=session,
                rejector=req.approver,
                reason=reason,
            )
            return {
                "decision": "rejected",
                "task_id": record.task_id,
                "execution_id": execution_id,
                "target_file": str(rejected_file),
                "reason": reason,
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid decision. Must be 'approve' or 'reject'.")

    @app.post("/api/executions/{execution_id}/rework")
    def trigger_rework_cycle(execution_id: str, req: ReworkRequest):
        """
        Triggers a controlled rework cycle following review rejection.
        Uses fresh repository context and passes historical evidence.
        """
        s: ExecutionHistoryStore = app.state.history_store
        record = s.get_execution(execution_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found.")

        r: ControlledWorkflowRunner = app.state.runner
        if not r:
            raise HTTPException(status_code=500, detail="ControlledWorkflowRunner is not initialized.")

        with _session_lock:
            session = _active_sessions.get(execution_id)

        if not session:
            # Reconstruct session from task
            for folder in ["review", "active", "blocked"]:
                p = app.state.repo_root / ".jester" / "tasks" / folder / f"{record.task_id}.json"
                if p.exists():
                    t = load_task_from_file(p)
                    session = r.orchestrator.create_session(task=t)
                    session.current_stage = OrchestrationStage.REWORK_REQUIRED
                    break

        if not session:
            raise HTTPException(status_code=400, detail="Unable to resolve session for rework.")

        def _execute_rework():
            try:
                outcome = r.run_rework_cycle(
                    session=session,
                    rework_feedback=req.rework_feedback,
                    rework_objective=req.rework_objective,
                    auto_apply=req.auto_apply,
                )
                with _session_lock:
                    _active_sessions[execution_id] = outcome.session
                    _active_outcomes[execution_id] = outcome
            except Exception:
                pass

        if req.sync:
            outcome = r.run_rework_cycle(
                session=session,
                rework_feedback=req.rework_feedback,
                rework_objective=req.rework_objective,
                auto_apply=req.auto_apply,
            )
            with _session_lock:
                _active_sessions[execution_id] = outcome.session
                _active_outcomes[execution_id] = outcome
            return {
                "task_id": record.task_id,
                "execution_id": execution_id,
                "stage": outcome.stage.value if hasattr(outcome.stage, "value") else str(outcome.stage),
            }
        else:
            th = threading.Thread(target=_execute_rework, daemon=True)
            th.start()
            return {
                "task_id": record.task_id,
                "execution_id": execution_id,
                "status": "rework_started",
            }

    @app.get("/api/git/status")
    def get_git_status():
        """Inspects repository git status safely via GitController."""
        g: GitController = app.state.git_controller
        if not g:
            raise HTTPException(status_code=500, detail="GitController is not initialized.")
        res = g.inspect_status()
        return res.model_dump()

    @app.post("/api/git/push")
    def authorize_git_push(req: PushAuthorizeRequest):
        """
        Executes explicit, authorized Git push.
        Requires separate human authorization.
        """
        g: GitController = app.state.git_controller
        if not g:
            raise HTTPException(status_code=500, detail="GitController is not initialized.")

        push_auth = PushAuthorization(
            task_id=req.task_id,
            approver=req.approver,
            remote=req.remote,
            branch=req.branch,
        )
        res = g.push(push_auth)
        if not res.success:
            raise HTTPException(status_code=400, detail=f"Git push failed: {res.error}")
        return res.model_dump()

    # --- Web UI Route ---

    @app.get("/", response_class=HTMLResponse)
    def render_founder_interface():
        """Renders the local-first Founder Interface HTML control surface."""
        ui_path = app.state.repo_root / "jester_bridge" / "ui" / "index.html"
        if ui_path.exists():
            return ui_path.read_text(encoding="utf-8")
        return """<!DOCTYPE html><html><head><title>JESTER Founder Interface</title></head><body><h1>JESTER Founder Interface</h1><p>UI file not found.</p></body></html>"""

    return app


# Default singleton app for command-line runner (uvicorn jester_bridge.server:app)
app = create_bridge_app()
