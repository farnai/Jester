"""
Persistent Execution History for the JESTER Provider-Agnostic AI Bridge (TASK-0008).

Provides durable, auditable, and bounded SQLite-based execution records:
- Records execution lifecycle, stage transitions, and chronological events.
- Captures role, agent, provider, model, and runtime metadata.
- Persists normalized token usage (input, output, total).
- Records verification, review, human signoff, and Git delivery results.
- Enforces strict secret exclusion and payload bounding.
- Fully decoupled from AI providers and task lifecycle state machine.
- Supports multiple executions per task ID (task_id != execution_id).
- Safe failure semantics: persistence errors do not corrupt business workflows.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field

from .core import BridgeError


DEFAULT_HISTORY_DB_REL = ".jester/history.db"
MAX_SUMMARY_LENGTH = 1000
MAX_ERROR_LENGTH = 1000
MAX_METADATA_JSON_LENGTH = 8192
SENSITIVE_KEY_PATTERNS = {
    "api_key",
    "secret",
    "token",
    "password",
    "authorization",
    "private_key",
    "bearer",
}


class ExecutionHistoryError(BridgeError):
    """Base exception for execution history errors."""
    pass


def sanitize_bounded_text(text: Optional[str], max_len: int = MAX_SUMMARY_LENGTH) -> Optional[str]:
    """Sanitizes sensitive values and enforces bounds on text fields."""
    if text is None:
        return None
    # Check for obvious credentials or secrets
    lowered = text.lower()
    if any(pat in lowered for pat in ("bearer ", "eyjhb", "sk-proj-", "ai-za-")):
        return "[REDACTED_SECRET]"
    if len(text) > max_len:
        return text[:max_len] + "... [TRUNCATED]"
    return text


def sanitize_metadata(meta: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Recursively redacts sensitive keys and bounds metadata payload size."""
    if not meta:
        return {}
    clean: Dict[str, Any] = {}
    for k, v in meta.items():
        k_lower = str(k).lower()
        if any(pat in k_lower for pat in SENSITIVE_KEY_PATTERNS):
            clean[str(k)] = "[REDACTED_SECRET]"
        elif isinstance(v, str):
            clean[str(k)] = sanitize_bounded_text(v, max_len=500)
        elif isinstance(v, (int, float, bool)):
            clean[str(k)] = v
        elif isinstance(v, list):
            clean[str(k)] = [
                sanitize_bounded_text(str(item), max_len=200) for item in v[:50]
            ]
        elif isinstance(v, dict):
            clean[str(k)] = sanitize_metadata(v)
        else:
            clean[str(k)] = sanitize_bounded_text(str(v), max_len=200)

    # Enforce total metadata serialization bound
    dumped = json.dumps(clean)
    if len(dumped) > MAX_METADATA_JSON_LENGTH:
        return {"_truncated": "[METADATA_EXCEEDED_BOUND]"}
    return clean


class ExecutionRecord(BaseModel):
    """
    Durable record of an individual workflow execution.
    A single task_id can have multiple execution records (task_id != execution_id).
    """
    execution_id: str
    task_id: str
    task_title: Optional[str] = None
    task_protocol_version: str = "v2"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    overall_status: str = "pending"
    current_stage: Optional[str] = None
    final_summary: Optional[str] = None
    error_message: Optional[str] = None
    total_input_tokens: Optional[int] = None
    total_output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    verification_passed: Optional[bool] = None
    verification_summary: Optional[str] = None
    reviewer_verdict: Optional[str] = None
    reviewer_summary: Optional[str] = None
    human_signoff_by: Optional[str] = None
    human_signoff_notes: Optional[str] = None
    git_commit_hash: Optional[str] = None
    git_branch: Optional[str] = None
    git_pushed: Optional[bool] = None
    git_delivery_summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionEvent(BaseModel):
    """
    Chronological, append-oriented event emitted during an execution.
    """
    event_id: str = Field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:12]}")
    execution_id: str
    event_type: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    stage: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None
    agent_id: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    summary: Optional[str] = None
    error: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionHistoryStore:
    """
    Durable, provider-neutral SQLite storage engine for execution history.
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        repo_root: Optional[Path] = None,
    ):
        if db_path:
            self.db_path = Path(db_path).resolve()
        else:
            root = (repo_root or Path.cwd()).resolve()
            self.db_path = (root / DEFAULT_HISTORY_DB_REL).resolve()

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.db_path), timeout=10.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except Exception as e:
            raise ExecutionHistoryError(f"Failed to connect to execution history database: {str(e)}")

    def _init_db(self) -> None:
        """Initializes tables and indexes idempotently."""
        create_executions_sql = """
        CREATE TABLE IF NOT EXISTS executions (
            execution_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            task_title TEXT,
            task_protocol_version TEXT DEFAULT 'v2',
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            overall_status TEXT NOT NULL,
            current_stage TEXT,
            final_summary TEXT,
            error_message TEXT,
            total_input_tokens INTEGER,
            total_output_tokens INTEGER,
            total_tokens INTEGER,
            verification_passed INTEGER,
            verification_summary TEXT,
            reviewer_verdict TEXT,
            reviewer_summary TEXT,
            human_signoff_by TEXT,
            human_signoff_notes TEXT,
            git_commit_hash TEXT,
            git_branch TEXT,
            git_pushed INTEGER,
            git_delivery_summary TEXT,
            metadata_json TEXT DEFAULT '{}'
        );
        """
        create_events_sql = """
        CREATE TABLE IF NOT EXISTS execution_events (
            event_id TEXT PRIMARY KEY,
            execution_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            stage TEXT,
            status TEXT,
            role TEXT,
            agent_id TEXT,
            provider TEXT,
            model TEXT,
            summary TEXT,
            error TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            total_tokens INTEGER,
            metadata_json TEXT DEFAULT '{}',
            FOREIGN KEY (execution_id) REFERENCES executions(execution_id)
        );
        """
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_exec_task_id ON executions(task_id);",
            "CREATE INDEX IF NOT EXISTS idx_exec_created_at ON executions(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_exec_status ON executions(overall_status);",
            "CREATE INDEX IF NOT EXISTS idx_evt_execution_id ON execution_events(execution_id);",
            "CREATE INDEX IF NOT EXISTS idx_evt_timestamp ON execution_events(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_evt_type ON execution_events(event_type);",
        ]

        with self._get_connection() as conn:
            conn.execute(create_executions_sql)
            conn.execute(create_events_sql)
            for idx in indexes_sql:
                conn.execute(idx)
            conn.commit()

    def create_execution(self, record: ExecutionRecord) -> bool:
        """Persists a new execution record. Fails if execution_id exists."""
        clean_meta = sanitize_metadata(record.metadata)
        sql = """
        INSERT INTO executions (
            execution_id, task_id, task_title, task_protocol_version,
            created_at, started_at, completed_at, overall_status, current_stage,
            final_summary, error_message,
            total_input_tokens, total_output_tokens, total_tokens,
            verification_passed, verification_summary,
            reviewer_verdict, reviewer_summary,
            human_signoff_by, human_signoff_notes,
            git_commit_hash, git_branch, git_pushed, git_delivery_summary,
            metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            record.execution_id,
            record.task_id,
            sanitize_bounded_text(record.task_title, 200),
            record.task_protocol_version,
            record.created_at,
            record.started_at,
            record.completed_at,
            record.overall_status,
            record.current_stage,
            sanitize_bounded_text(record.final_summary, MAX_SUMMARY_LENGTH),
            sanitize_bounded_text(record.error_message, MAX_ERROR_LENGTH),
            record.total_input_tokens,
            record.total_output_tokens,
            record.total_tokens,
            1 if record.verification_passed is True else (0 if record.verification_passed is False else None),
            sanitize_bounded_text(record.verification_summary, MAX_SUMMARY_LENGTH),
            record.reviewer_verdict,
            sanitize_bounded_text(record.reviewer_summary, MAX_SUMMARY_LENGTH),
            record.human_signoff_by,
            sanitize_bounded_text(record.human_signoff_notes, MAX_SUMMARY_LENGTH),
            record.git_commit_hash,
            record.git_branch,
            1 if record.git_pushed is True else (0 if record.git_pushed is False else None),
            sanitize_bounded_text(record.git_delivery_summary, MAX_SUMMARY_LENGTH),
            json.dumps(clean_meta),
        )

        try:
            with self._get_connection() as conn:
                conn.execute(sql, params)
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            raise ExecutionHistoryError(f"Execution record '{record.execution_id}' already exists.")
        except Exception as e:
            raise ExecutionHistoryError(f"Failed to create execution record: {str(e)}")

    def update_execution(self, record: ExecutionRecord) -> bool:
        """Updates an existing execution record."""
        clean_meta = sanitize_metadata(record.metadata)
        sql = """
        UPDATE executions SET
            task_title = ?,
            task_protocol_version = ?,
            started_at = ?,
            completed_at = ?,
            overall_status = ?,
            current_stage = ?,
            final_summary = ?,
            error_message = ?,
            total_input_tokens = ?,
            total_output_tokens = ?,
            total_tokens = ?,
            verification_passed = ?,
            verification_summary = ?,
            reviewer_verdict = ?,
            reviewer_summary = ?,
            human_signoff_by = ?,
            human_signoff_notes = ?,
            git_commit_hash = ?,
            git_branch = ?,
            git_pushed = ?,
            git_delivery_summary = ?,
            metadata_json = ?
        WHERE execution_id = ?;
        """
        params = (
            sanitize_bounded_text(record.task_title, 200),
            record.task_protocol_version,
            record.started_at,
            record.completed_at,
            record.overall_status,
            record.current_stage,
            sanitize_bounded_text(record.final_summary, MAX_SUMMARY_LENGTH),
            sanitize_bounded_text(record.error_message, MAX_ERROR_LENGTH),
            record.total_input_tokens,
            record.total_output_tokens,
            record.total_tokens,
            1 if record.verification_passed is True else (0 if record.verification_passed is False else None),
            sanitize_bounded_text(record.verification_summary, MAX_SUMMARY_LENGTH),
            record.reviewer_verdict,
            sanitize_bounded_text(record.reviewer_summary, MAX_SUMMARY_LENGTH),
            record.human_signoff_by,
            sanitize_bounded_text(record.human_signoff_notes, MAX_SUMMARY_LENGTH),
            record.git_commit_hash,
            record.git_branch,
            1 if record.git_pushed is True else (0 if record.git_pushed is False else None),
            sanitize_bounded_text(record.git_delivery_summary, MAX_SUMMARY_LENGTH),
            json.dumps(clean_meta),
            record.execution_id,
        )

        try:
            with self._get_connection() as conn:
                cursor = conn.execute(sql, params)
                conn.commit()
                if cursor.rowcount == 0:
                    raise ExecutionHistoryError(f"Execution record '{record.execution_id}' not found for update.")
                return True
        except ExecutionHistoryError:
            raise
        except Exception as e:
            raise ExecutionHistoryError(f"Failed to update execution record: {str(e)}")

    def record_event(self, event: ExecutionEvent) -> bool:
        """
        Appends an execution event.
        Duplicate event_ids are safely ignored to guarantee idempotency.
        """
        clean_meta = sanitize_metadata(event.metadata)
        sql = """
        INSERT OR IGNORE INTO execution_events (
            event_id, execution_id, event_type, timestamp, stage, status,
            role, agent_id, provider, model, summary, error,
            input_tokens, output_tokens, total_tokens, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            event.event_id,
            event.execution_id,
            event.event_type,
            event.timestamp,
            event.stage,
            event.status,
            event.role,
            event.agent_id,
            event.provider,
            event.model,
            sanitize_bounded_text(event.summary, MAX_SUMMARY_LENGTH),
            sanitize_bounded_text(event.error, MAX_ERROR_LENGTH),
            event.input_tokens,
            event.output_tokens,
            event.total_tokens,
            json.dumps(clean_meta),
        )

        try:
            with self._get_connection() as conn:
                conn.execute(sql, params)
                conn.commit()
                return True
        except Exception as e:
            raise ExecutionHistoryError(f"Failed to record execution event: {str(e)}")

    def _row_to_record(self, row: sqlite3.Row) -> ExecutionRecord:
        verif_passed = None
        if row["verification_passed"] is not None:
            verif_passed = bool(row["verification_passed"])

        pushed = None
        if row["git_pushed"] is not None:
            pushed = bool(row["git_pushed"])

        meta = {}
        if row["metadata_json"]:
            try:
                meta = json.loads(row["metadata_json"])
            except Exception:
                meta = {}

        return ExecutionRecord(
            execution_id=row["execution_id"],
            task_id=row["task_id"],
            task_title=row["task_title"],
            task_protocol_version=row["task_protocol_version"] or "v2",
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            overall_status=row["overall_status"],
            current_stage=row["current_stage"],
            final_summary=row["final_summary"],
            error_message=row["error_message"],
            total_input_tokens=row["total_input_tokens"],
            total_output_tokens=row["total_output_tokens"],
            total_tokens=row["total_tokens"],
            verification_passed=verif_passed,
            verification_summary=row["verification_summary"],
            reviewer_verdict=row["reviewer_verdict"],
            reviewer_summary=row["reviewer_summary"],
            human_signoff_by=row["human_signoff_by"],
            human_signoff_notes=row["human_signoff_notes"],
            git_commit_hash=row["git_commit_hash"],
            git_branch=row["git_branch"],
            git_pushed=pushed,
            git_delivery_summary=row["git_delivery_summary"],
            metadata=meta,
        )

    def _row_to_event(self, row: sqlite3.Row) -> ExecutionEvent:
        meta = {}
        if row["metadata_json"]:
            try:
                meta = json.loads(row["metadata_json"])
            except Exception:
                meta = {}

        return ExecutionEvent(
            event_id=row["event_id"],
            execution_id=row["execution_id"],
            event_type=row["event_type"],
            timestamp=row["timestamp"],
            stage=row["stage"],
            status=row["status"],
            role=row["role"],
            agent_id=row["agent_id"],
            provider=row["provider"],
            model=row["model"],
            summary=row["summary"],
            error=row["error"],
            input_tokens=row["input_tokens"],
            output_tokens=row["output_tokens"],
            total_tokens=row["total_tokens"],
            metadata=meta,
        )

    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Retrieves an execution record by its unique execution_id."""
        sql = "SELECT * FROM executions WHERE execution_id = ?;"
        with self._get_connection() as conn:
            cursor = conn.execute(sql, (execution_id,))
            row = cursor.fetchone()
            return self._row_to_record(row) if row else None

    def get_executions_for_task(self, task_id: str, limit: int = 50) -> List[ExecutionRecord]:
        """Retrieves all executions associated with a task_id ordered newest first."""
        sql = "SELECT * FROM executions WHERE task_id = ? ORDER BY created_at DESC, rowid DESC LIMIT ?;"
        with self._get_connection() as conn:
            cursor = conn.execute(sql, (task_id, limit))
            return [self._row_to_record(row) for row in cursor.fetchall()]

    def list_recent_executions(self, limit: int = 50) -> List[ExecutionRecord]:
        """Lists recent executions across all tasks ordered newest first."""
        sql = "SELECT * FROM executions ORDER BY created_at DESC, rowid DESC LIMIT ?;"
        with self._get_connection() as conn:
            cursor = conn.execute(sql, (limit,))
            return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_events_for_execution(self, execution_id: str) -> List[ExecutionEvent]:
        """Retrieves all chronological events for an execution."""
        sql = "SELECT * FROM execution_events WHERE execution_id = ? ORDER BY timestamp ASC, rowid ASC;"
        with self._get_connection() as conn:
            cursor = conn.execute(sql, (execution_id,))
            return [self._row_to_event(row) for row in cursor.fetchall()]

    def list_events(self, execution_id: str) -> List[ExecutionEvent]:
        """Alias for get_events_for_execution."""
        return self.get_events_for_execution(execution_id)

    def get_execution_summary(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Reconstructs a structured audit summary of an execution from records and events."""
        record = self.get_execution(execution_id)
        if not record:
            return None

        events = self.get_events_for_execution(execution_id)
        stages_executed = sorted(list({e.stage for e in events if e.stage}))

        return {
            "execution_id": record.execution_id,
            "task_id": record.task_id,
            "task_title": record.task_title,
            "overall_status": record.overall_status,
            "created_at": record.created_at,
            "started_at": record.started_at,
            "completed_at": record.completed_at,
            "token_usage": {
                "input_tokens": record.total_input_tokens,
                "output_tokens": record.total_output_tokens,
                "total_tokens": record.total_tokens,
            },
            "verification": {
                "passed": record.verification_passed,
                "summary": record.verification_summary,
            },
            "review": {
                "verdict": record.reviewer_verdict,
                "summary": record.reviewer_summary,
            },
            "human_signoff": {
                "approver": record.human_signoff_by,
                "notes": record.human_signoff_notes,
            },
            "git_delivery": {
                "commit_hash": record.git_commit_hash,
                "branch": record.git_branch,
                "pushed": record.git_pushed,
                "summary": record.git_delivery_summary,
            },
            "stages_executed": stages_executed,
            "event_count": len(events),
        }

    def get_latest_execution_for_task(self, task_id: str) -> Optional[ExecutionRecord]:
        """Retrieves the most recent execution record for a task_id."""
        execs = self.get_executions_for_task(task_id, limit=1)
        return execs[0] if execs else None

    def get_rework_history(self, execution_id: str) -> Dict[str, Any]:
        """
        Retrieves bounded historical rework data for an execution:
        - reviewer verdict
        - reviewer feedback / defect details
        - verification summary
        - files modified
        - diff summary
        """
        record = self.get_execution(execution_id)
        events = self.get_events_for_execution(execution_id)

        reviewer_feedback = None
        reviewer_defect_details = None
        diff_summary = None
        files_modified: List[str] = []

        # Extract latest relevant review and diff events
        for ev in reversed(events):
            if ev.event_type == "review_completed":
                if not reviewer_feedback:
                    reviewer_feedback = ev.summary
                if ev.error and not reviewer_defect_details:
                    reviewer_defect_details = ev.error
            elif ev.event_type == "diff_generated" and not diff_summary:
                diff_summary = ev.summary
                if ev.metadata and "files_modified" in ev.metadata:
                    files_modified = ev.metadata["files_modified"]

        # Fallback to execution record if available
        verdict = record.reviewer_verdict if record else None
        if not reviewer_feedback and record and record.reviewer_summary:
            reviewer_feedback = record.reviewer_summary
        verification_summary = record.verification_summary if record else None

        return {
            "execution_id": execution_id,
            "task_id": record.task_id if record else None,
            "reviewer_verdict": verdict,
            "reviewer_feedback": reviewer_feedback,
            "reviewer_defect_details": reviewer_defect_details,
            "verification_summary": verification_summary,
            "diff_summary": diff_summary,
            "files_modified": files_modified,
        }
