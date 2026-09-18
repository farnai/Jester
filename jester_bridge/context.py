"""
Advanced Context Engine for the JESTER Provider-Agnostic AI Bridge (TASK-0009, TASK-0010).

Provides deterministic, role-aware, and budget-governed repository context assembly:
- Assembles structured ContextPackage with versioning and provenance.
- Enforces role-specific context delivery (Architect vs. Executor vs. Reviewer).
- Prioritizes context items deterministically (CRITICAL -> HIGH -> NORMAL -> LOW).
- Enforces strict total and per-file character budgets with explicit truncation markers.
- Supports multi-stage context lifecycle and lineage (parent_context_id -> context_id).
- Associates context snapshots with specific execution_id (task_id != execution_id).
- Incorporates bounded rework context (reviewer feedback, previous diff, defect details).
- Distinguishes static task context, dynamic workspace context, and historical explanation.
- Computes freshness metadata (SHA-256 content hashes, mtime) to detect stale context.
- Rejects protected paths (.git, .env, AGENTS.md, supabase/migrations, migrations).
- Preserves workspace containment (blocks directory traversal outside repo root).
- Separates read context from write authority (context does NOT expand write permissions).
- Provider-neutral: zero vendor SDK dependencies.
"""
from datetime import datetime, timezone
from enum import Enum
import hashlib
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid
from pydantic import BaseModel, Field

from .protocol import Task
from .runtime import PROTECTED_PATHS, is_path_in_scope


DEFAULT_MAX_CONTEXT_CHARACTERS = 50_000
DEFAULT_MAX_FILE_CHARACTERS = 20_000
CONTEXT_ENGINE_VERSION = "v1"


def sanitize_context_text(text: Optional[str]) -> Optional[str]:
    """Sanitizes sensitive patterns (bearer tokens, api keys) from text before context insertion."""
    if text is None:
        return None
    lowered = text.lower()
    if any(pat in lowered for pat in ("bearer ", "eyjhb", "sk-proj-", "ai-za-")):
        return "[REDACTED_SECRET]"
    return text


class ContextPriority(str, Enum):
    """Deterministic context priority tiers."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"

    @property
    def rank(self) -> int:
        """Numeric rank for sorting (higher number = higher priority)."""
        ranks = {
            ContextPriority.CRITICAL: 4,
            ContextPriority.HIGH: 3,
            ContextPriority.NORMAL: 2,
            ContextPriority.LOW: 1,
        }
        return ranks[self]


class SourceType(str, Enum):
    """Categorization of context provenance sources."""
    TASK = "task"
    EXPLICIT_SCOPE = "explicit_scope"
    SOURCE_FILE = "source_file"
    TEST_FILE = "test_file"
    CONTRACT = "contract"
    ARCHITECTURE_DOC = "architecture_doc"
    CHANGED_FILE = "changed_file"
    DIFF = "diff"
    VERIFICATION = "verification"
    HANDOFF = "handoff"
    REVIEWER_FEEDBACK = "reviewer_feedback"
    HISTORICAL_EXECUTION = "historical_execution"


class ContextItemProvenance(BaseModel):
    """Detailed audit provenance for an individual context item."""
    source_type: SourceType
    source_path: str
    priority: ContextPriority = ContextPriority.NORMAL
    reason: str
    original_size_chars: int = 0
    included_size_chars: int = 0
    truncated: bool = False


class FileContext(BaseModel):
    """Represents an ingested repository file within the task context."""
    relative_path: str
    content: str
    size_characters: int
    truncated: bool = False
    is_new_file: bool = False
    priority: ContextPriority = ContextPriority.NORMAL
    provenance: Optional[ContextItemProvenance] = None
    freshness_hash: Optional[str] = None
    file_mtime: Optional[float] = None
    is_historical: bool = False


class ContextSnapshot(BaseModel):
    """
    Immutable audit representation of context assembled for a specific role and stage.
    Captures snapshot identity, lineage, budgets, and file freshness hashes without
    storing full source code bodies, preserving repository containment and space bounds.
    """
    context_id: str
    parent_context_id: Optional[str] = None
    execution_id: str
    task_id: str
    role: str
    stage: str
    context_version: str = CONTEXT_ENGINE_VERSION
    created_at: str
    selected_file_count: int
    excluded_file_count: int
    total_budget: int
    used_budget: int
    truncated: bool = False
    truncated_files_count: int = 0
    has_diff: bool = False
    has_previous_diff: bool = False
    has_verification: bool = False
    has_rework_context: bool = False
    historical_items_count: int = 0
    included_paths: List[str] = Field(default_factory=list)
    file_freshness_hashes: Dict[str, str] = Field(default_factory=dict)


class ContextPackage(BaseModel):
    """
    Structured, role-aware, and budgeted context package delivered to an agent invocation.
    Maintains full backward compatibility with legacy ContextBundle.
    """
    context_id: str = Field(default_factory=lambda: f"ctx-{uuid.uuid4().hex[:10]}")
    parent_context_id: Optional[str] = None
    execution_id: str = "anonymous"
    task_id: str = "anonymous"
    role: str = "generic"
    stage: str = "generic"
    context_version: str = CONTEXT_ENGINE_VERSION
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    files: List[FileContext] = Field(default_factory=list)
    total_characters: int = 0
    max_characters: int = DEFAULT_MAX_CONTEXT_CHARACTERS
    truncated: bool = False
    truncated_files_count: int = 0
    included_paths: List[str] = Field(default_factory=list)
    excluded_paths: Dict[str, str] = Field(default_factory=dict)
    selection_reasons: Dict[str, str] = Field(default_factory=dict)
    provenance_items: List[ContextItemProvenance] = Field(default_factory=list)
    task_context: Optional[str] = None
    diff: Optional[str] = None
    diff_truncated: bool = False
    verification_output: Optional[str] = None

    # Historical and rework context (TASK-0010)
    previous_diff: Optional[str] = None
    previous_diff_truncated: bool = False
    previous_verification_output: Optional[str] = None
    reviewer_feedback: Optional[str] = None
    reviewer_defect_details: Optional[str] = None
    rework_objective: Optional[str] = None
    architect_intent: Optional[str] = None
    previous_implementation_summary: Optional[str] = None
    historical_items: List[Dict[str, Any]] = Field(default_factory=list)
    relevant_metadata: Dict[str, Any] = Field(default_factory=dict)

    # Convenience properties for contract compatibility
    @property
    def selected_files(self) -> List[str]:
        return self.included_paths

    @property
    def excluded_files(self) -> Dict[str, str]:
        return self.excluded_paths

    @property
    def file_contexts(self) -> List[FileContext]:
        return self.files

    @property
    def budget(self) -> int:
        return self.max_characters

    @property
    def usage(self) -> int:
        return self.total_characters

    @property
    def available_budget(self) -> int:
        return max(0, self.max_characters - self.total_characters)

    def to_snapshot(self) -> ContextSnapshot:
        """Constructs an immutable lightweight ContextSnapshot of this package."""
        hashes = {
            f.relative_path: f.freshness_hash
            for f in self.files
            if f.freshness_hash
        }
        return ContextSnapshot(
            context_id=self.context_id,
            parent_context_id=self.parent_context_id,
            execution_id=self.execution_id,
            task_id=self.task_id,
            role=self.role,
            stage=self.stage,
            context_version=self.context_version,
            created_at=self.created_at,
            selected_file_count=len(self.included_paths),
            excluded_file_count=len(self.excluded_paths),
            total_budget=self.max_characters,
            used_budget=self.total_characters,
            truncated=self.truncated,
            truncated_files_count=self.truncated_files_count,
            has_diff=bool(self.diff),
            has_previous_diff=bool(self.previous_diff),
            has_verification=bool(self.verification_output),
            has_rework_context=bool(self.reviewer_feedback or self.previous_diff or self.rework_objective),
            historical_items_count=len(self.historical_items),
            included_paths=list(self.included_paths),
            file_freshness_hashes=hashes,
        )

    def format_for_prompt(self) -> str:
        """Formats the entire context package into structured markdown for prompts."""
        sections: List[str] = []

        # 1. Static Task Context
        if self.task_context:
            sections.append(f"## Task Context:\n{self.task_context}")
        if self.architect_intent:
            sections.append(f"## Architect Intent:\n{self.architect_intent}")

        # 2. Historical Rework Context (if present)
        rework_parts: List[str] = []
        if self.rework_objective:
            rework_parts.append(f"### Rework Objective:\n{self.rework_objective}")
        if self.reviewer_feedback:
            rework_parts.append(f"### Previous Reviewer Feedback:\n{self.reviewer_feedback}")
        if self.reviewer_defect_details:
            rework_parts.append(f"### Identified Defects:\n{self.reviewer_defect_details}")
        if self.previous_implementation_summary:
            rework_parts.append(f"### Previous Implementation Summary:\n{self.previous_implementation_summary}")
        if self.previous_diff:
            prev_trunc = " (TRUNCATED TO FIT BUDGET)" if self.previous_diff_truncated else ""
            rework_parts.append(f"### Previous Code Diff (Rejected Iteration){prev_trunc}:\n```diff\n{self.previous_diff}\n```")
        if self.previous_verification_output:
            rework_parts.append(f"### Previous Verification Output:\n```text\n{self.previous_verification_output}\n```")

        if rework_parts:
            sections.append("## Historical Rework Context (Context from previous iteration; for reference only):")
            sections.extend(rework_parts)

        # 3. Current Execution Evidence
        if self.diff:
            diff_trunc = " (TRUNCATED TO FIT BUDGET)" if self.diff_truncated else ""
            sections.append(f"## Code Diff Evidence{diff_trunc}:\n```diff\n{self.diff}\n```")

        if self.verification_output:
            sections.append(f"## Verification Output:\n```text\n{self.verification_output}\n```")

        # 4. In-Scope Repository Files (Current disk reality)
        if self.files:
            sections.append("## In-Scope Repository Files Context (Fresh workspace state):")
            for fc in self.files:
                trunc_note = " (TRUNCATED TO FIT BUDGET)" if fc.truncated else ""
                if fc.is_new_file:
                    sections.append(
                        f"### File: `{fc.relative_path}` (New file to be created)\n```\n(empty / does not exist yet)\n```"
                    )
                else:
                    sections.append(
                        f"### File: `{fc.relative_path}`{trunc_note}\n```\n{fc.content}\n```"
                    )
        elif not self.diff and not self.verification_output and not rework_parts:
            sections.append("No repository files in context.")

        if self.excluded_paths:
            sections.append("### Excluded Paths:")
            for p, reason in sorted(self.excluded_paths.items()):
                sections.append(f"- `{p}`: {reason}")

        return "\n\n".join(sections)

    def to_summary_dict(self) -> Dict[str, Any]:
        """Returns bounded summary metadata suitable for execution history persistence."""
        return {
            "context_id": self.context_id,
            "parent_context_id": self.parent_context_id,
            "execution_id": self.execution_id,
            "task_id": self.task_id,
            "role": self.role,
            "stage": self.stage,
            "context_version": self.context_version,
            "selected_file_count": len(self.included_paths),
            "excluded_file_count": len(self.excluded_paths),
            "total_budget": self.max_characters,
            "used_budget": self.total_characters,
            "truncated_count": self.truncated_files_count,
            "is_truncated": self.truncated,
            "has_diff": bool(self.diff),
            "has_previous_diff": bool(self.previous_diff),
            "has_verification": bool(self.verification_output),
            "has_rework_context": bool(self.reviewer_feedback or self.previous_diff or self.rework_objective),
            "historical_items_count": len(self.historical_items),
        }


class ContextBundle(ContextPackage):
    """Backward-compatible alias for ContextPackage."""
    pass


class ContextCandidate(BaseModel):
    """Internal candidate representation for prioritized context assembly."""
    relative_path: str
    source_type: SourceType
    priority: ContextPriority
    reason: str
    is_direct: bool = True


class ContextEngine:
    """
    Deterministic, role-aware context assembly engine.
    Discovers, prioritizes, bounds, and packages repository context for agent invocations.
    """

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        max_characters: int = DEFAULT_MAX_CONTEXT_CHARACTERS,
        max_file_characters: int = DEFAULT_MAX_FILE_CHARACTERS,
    ):
        self.repo_root = (repo_root or Path.cwd()).resolve()
        self.max_characters = max_characters
        self.max_file_characters = max_file_characters

    def validate_path(self, target_relative_path: str) -> Tuple[bool, str]:
        """
        Validates whether a path may be safely read into context.
        Enforces workspace containment and protected paths rules.
        """
        norm = target_relative_path.replace("\\", "/").strip().lstrip("/")

        # Check empty or dangerously broad
        if not norm or norm in (".", "*", "/"):
            return False, "Dangerous or empty scope path"

        # Check path traversal
        if ".." in norm:
            return False, "Path traversal forbidden ('..')"

        # Check protected paths
        for protected in PROTECTED_PATHS:
            if norm == protected or norm.startswith(f"{protected}/"):
                return False, f"Protected repository path '{protected}'"

        # Check workspace containment
        abs_path = (self.repo_root / norm).resolve()
        try:
            abs_path.relative_to(self.repo_root)
        except ValueError:
            return False, "Path escapes workspace root"

        return True, "Valid"

    def discover_related_tests(self, relative_path: str) -> List[str]:
        """
        Heuristically resolves related test files for an implementation path.
        Returns paths if they exist on disk and pass path validation.
        """
        p = Path(relative_path)
        stem = p.stem
        candidates: List[str] = []

        # 1. Same directory test file
        candidates.append((p.parent / f"test_{stem}.py").as_posix())

        # 2. tests/ mirror location (e.g. jester_bridge/xyz.py -> tests/bridge/test_xyz.py)
        parts = list(p.parts)
        if parts:
            if parts[0] == "jester_bridge":
                candidates.append(Path("tests/bridge", f"test_{stem}.py").as_posix())
            elif parts[0] == "backend":
                candidates.append(Path("tests/backend", f"test_{stem}.py").as_posix())
            candidates.append(Path("tests", *parts[:-1], f"test_{stem}.py").as_posix())
            candidates.append(Path("tests", f"test_{stem}.py").as_posix())

        valid_tests: List[str] = []
        for cand in candidates:
            cand_norm = cand.replace("\\", "/")
            is_valid, _ = self.validate_path(cand_norm)
            if is_valid and (self.repo_root / cand_norm).is_file():
                if cand_norm not in valid_tests:
                    valid_tests.append(cand_norm)

        return sorted(valid_tests)

    def extract_mentioned_paths(self, text: str) -> List[str]:
        """
        Scans freeform task text for referenced repository files.
        """
        if not text:
            return []
        pattern = r"\b([a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-]+)*\.[a-zA-Z0-9_]+)\b"
        matches = re.findall(pattern, text)
        found: List[str] = []
        for m in matches:
            norm = m.replace("\\", "/").strip().lstrip("/")
            is_valid, _ = self.validate_path(norm)
            if is_valid and (self.repo_root / norm).is_file() and norm not in found:
                found.append(norm)
        return sorted(found)

    def check_context_freshness(self, pkg: ContextPackage) -> Tuple[bool, List[str]]:
        """
        Verifies whether in-scope files in the ContextPackage still match current workspace files on disk.
        Returns (is_fresh, stale_file_paths).
        """
        stale_paths: List[str] = []
        for fc in pkg.files:
            abs_path = self.repo_root / fc.relative_path
            if fc.is_new_file:
                if abs_path.exists():
                    stale_paths.append(fc.relative_path)
            elif fc.freshness_hash:
                if not abs_path.exists():
                    stale_paths.append(fc.relative_path)
                    continue
                try:
                    disk_content = abs_path.read_text(encoding="utf-8")
                    disk_hash = hashlib.sha256(disk_content.encode("utf-8")).hexdigest()
                    if disk_hash != fc.freshness_hash:
                        stale_paths.append(fc.relative_path)
                except Exception:
                    stale_paths.append(fc.relative_path)
        return (len(stale_paths) == 0, stale_paths)

    def assemble_context(
        self,
        task: Task,
        role: Optional[str] = None,
        stage: Optional[str] = None,
        execution_id: Optional[str] = None,
        parent_context_id: Optional[str] = None,
        extra_paths: Optional[List[str]] = None,
        diff: Optional[str] = None,
        verification_output: Optional[str] = None,
        changed_files: Optional[List[str]] = None,
        include_related_tests: bool = True,
        include_arch_docs: bool = False,
        # Rework & historical context parameters (TASK-0010)
        previous_diff: Optional[str] = None,
        previous_verification_output: Optional[str] = None,
        reviewer_feedback: Optional[str] = None,
        reviewer_defect_details: Optional[str] = None,
        rework_objective: Optional[str] = None,
        architect_intent: Optional[str] = None,
        previous_implementation_summary: Optional[str] = None,
        historical_metadata: Optional[Dict[str, Any]] = None,
    ) -> ContextPackage:
        """
        Gathers role-aware, prioritized, and budgeted repository context.
        Distinguishes static task context, dynamic workspace code, current execution evidence,
        and bounded historical rework explanations.
        """
        effective_role = (role or task.role or "executor").lower()
        effective_stage = (stage or effective_role).lower()

        pkg = ContextPackage(
            task_id=task.id,
            execution_id=execution_id or "anonymous",
            parent_context_id=parent_context_id,
            role=effective_role,
            stage=effective_stage,
            max_characters=self.max_characters,
            verification_output=verification_output,
            relevant_metadata=dict(historical_metadata or {}),
        )

        current_chars = 0

        # Helper to budget and add textual historical/rework items
        def add_text_item(
            text_val: Optional[str],
            source_type: SourceType,
            priority: ContextPriority,
            reason: str,
            label: str,
        ) -> Tuple[Optional[str], bool]:
            nonlocal current_chars
            if not text_val:
                return None, False

            clean_text = sanitize_context_text(text_val)
            orig_len = len(clean_text)
            rem_budget = self.max_characters - current_chars

            if rem_budget <= 0:
                pkg.truncated = True
                pkg.provenance_items.append(
                    ContextItemProvenance(
                        source_type=source_type,
                        source_path=label,
                        priority=priority,
                        reason=f"{reason} (omitted due to budget limit)",
                        original_size_chars=orig_len,
                        included_size_chars=0,
                        truncated=True,
                    )
                )
                return None, True

            if orig_len > rem_budget:
                trunc_marker = f"\n\n[... {label} truncated {orig_len - rem_budget} characters ...]"
                slice_lim = max(0, rem_budget - len(trunc_marker))
                included = clean_text[:slice_lim] + trunc_marker
                is_trunc = True
                pkg.truncated = True
            else:
                included = clean_text
                is_trunc = False

            added_len = len(included)
            current_chars += added_len

            pkg.provenance_items.append(
                ContextItemProvenance(
                    source_type=source_type,
                    source_path=label,
                    priority=priority,
                    reason=reason,
                    original_size_chars=orig_len,
                    included_size_chars=added_len,
                    truncated=is_trunc,
                )
            )
            pkg.historical_items.append({
                "label": label,
                "source_type": source_type.value,
                "chars": added_len,
                "truncated": is_trunc,
            })
            return included, is_trunc

        # 1. Ingest Historical / Rework Context Items (if provided)
        if reviewer_feedback:
            clean_fb, _ = add_text_item(
                reviewer_feedback,
                SourceType.REVIEWER_FEEDBACK,
                ContextPriority.CRITICAL,
                "Reviewer feedback from previous iteration",
                "reviewer_feedback",
            )
            pkg.reviewer_feedback = clean_fb

        if reviewer_defect_details:
            clean_defects, _ = add_text_item(
                reviewer_defect_details,
                SourceType.REVIEWER_FEEDBACK,
                ContextPriority.CRITICAL,
                "Identified defects from previous review",
                "reviewer_defect_details",
            )
            pkg.reviewer_defect_details = clean_defects

        if rework_objective:
            clean_obj, _ = add_text_item(
                rework_objective,
                SourceType.TASK,
                ContextPriority.CRITICAL,
                "Target objective for rework execution",
                "rework_objective",
            )
            pkg.rework_objective = clean_obj

        if architect_intent:
            clean_arch, _ = add_text_item(
                architect_intent,
                SourceType.CONTRACT,
                ContextPriority.HIGH,
                "Architectural intent and constraints",
                "architect_intent",
            )
            pkg.architect_intent = clean_arch

        if previous_implementation_summary:
            clean_prev_sum, _ = add_text_item(
                previous_implementation_summary,
                SourceType.HISTORICAL_EXECUTION,
                ContextPriority.HIGH,
                "Summary of previous rejected implementation",
                "previous_implementation_summary",
            )
            pkg.previous_implementation_summary = clean_prev_sum

        if previous_diff:
            clean_pdiff, pdiff_trunc = add_text_item(
                previous_diff,
                SourceType.HISTORICAL_EXECUTION,
                ContextPriority.HIGH,
                "Unified diff from previous rejected execution",
                "previous_diff",
            )
            pkg.previous_diff = clean_pdiff
            pkg.previous_diff_truncated = pdiff_trunc

        if previous_verification_output:
            clean_pverif, _ = add_text_item(
                previous_verification_output,
                SourceType.HISTORICAL_EXECUTION,
                ContextPriority.NORMAL,
                "Verification output from previous rejected execution",
                "previous_verification_output",
            )
            pkg.previous_verification_output = clean_pverif

        # 2. Current Execution Evidence (diff & verification)
        if diff:
            diff_prio = ContextPriority.CRITICAL
            diff_orig_len = len(diff)
            rem_budget = self.max_characters - current_chars
            if diff_orig_len > rem_budget:
                trunc_marker = f"\n\n[... diff truncated {diff_orig_len - rem_budget} characters ...]"
                slice_limit = max(0, rem_budget - len(trunc_marker))
                pkg.diff = diff[:slice_limit] + trunc_marker
                pkg.diff_truncated = True
                pkg.truncated = True
                pkg.truncated_files_count += 1
                diff_chars = len(pkg.diff)
            else:
                pkg.diff = diff
                diff_chars = diff_orig_len

            current_chars += diff_chars
            pkg.provenance_items.append(
                ContextItemProvenance(
                    source_type=SourceType.DIFF,
                    source_path="unified_diff",
                    priority=diff_prio,
                    reason="Unified code diff evidence for inspection",
                    original_size_chars=diff_orig_len,
                    included_size_chars=diff_chars,
                    truncated=pkg.diff_truncated,
                )
            )

        if verification_output:
            v_orig_len = len(verification_output)
            pkg.provenance_items.append(
                ContextItemProvenance(
                    source_type=SourceType.VERIFICATION,
                    source_path="verification_output",
                    priority=ContextPriority.CRITICAL if effective_role == "reviewer" else ContextPriority.HIGH,
                    reason="Test verification command output",
                    original_size_chars=v_orig_len,
                    included_size_chars=v_orig_len,
                    truncated=False,
                )
            )

        # 3. Dynamic Repository Files Candidates
        candidates: List[ContextCandidate] = []
        seen_paths: Set[str] = set()

        def add_candidate(path: str, src_type: SourceType, priority: ContextPriority, reason: str):
            norm = path.replace("\\", "/").strip().lstrip("/")
            if norm not in seen_paths:
                seen_paths.add(norm)
                candidates.append(
                    ContextCandidate(
                        relative_path=norm,
                        source_type=src_type,
                        priority=priority,
                        reason=reason,
                    )
                )

        # Signal 1: Explicit task scope
        for p in (task.scope or []):
            add_candidate(p, SourceType.EXPLICIT_SCOPE, ContextPriority.CRITICAL, "Explicitly declared in task scope")

        # Signal 2: Extra explicitly passed paths
        if extra_paths:
            for p in extra_paths:
                add_candidate(p, SourceType.EXPLICIT_SCOPE, ContextPriority.CRITICAL, "Explicitly passed extra path")

        # Signal 3: Changed files
        if changed_files:
            for p in changed_files:
                p_prio = ContextPriority.CRITICAL if effective_role == "reviewer" else ContextPriority.HIGH
                add_candidate(p, SourceType.CHANGED_FILE, p_prio, "Modified file during execution")

        # Signal 4: Related tests
        if include_related_tests and effective_role in ("executor", "reviewer"):
            base_paths = list(task.scope or []) + (changed_files or [])
            for bp in base_paths:
                for tpath in self.discover_related_tests(bp):
                    add_candidate(
                        tpath,
                        SourceType.TEST_FILE,
                        ContextPriority.HIGH,
                        f"Related test file discovered for {bp}",
                    )

        # Signal 5: Paths mentioned in task text
        task_text = f"{task.title or ''} {task.goal or ''} {' '.join(task.constraints or [])} {' '.join(task.acceptance_criteria or [])}"
        for mp in self.extract_mentioned_paths(task_text):
            add_candidate(mp, SourceType.SOURCE_FILE, ContextPriority.NORMAL, "Path mentioned in task text")

        # Signal 6: Architecture documentation
        if include_arch_docs or effective_role == "architect":
            arch_doc = "docs/AI_BRIDGE_ARCHITECTURE.md"
            if (self.repo_root / arch_doc).is_file():
                add_candidate(arch_doc, SourceType.ARCHITECTURE_DOC, ContextPriority.NORMAL, "Core architecture specification")

        # Deterministic candidate sorting:
        # 1. Priority rank descending (CRITICAL -> HIGH -> NORMAL -> LOW)
        # 2. Path alphabetically ascending
        sorted_candidates = sorted(
            candidates,
            key=lambda c: (-c.priority.rank, c.relative_path),
        )

        for cand in sorted_candidates:
            rel_path = cand.relative_path
            pkg.selection_reasons[rel_path] = cand.reason

            is_valid, reason = self.validate_path(rel_path)
            if not is_valid:
                pkg.excluded_paths[rel_path] = reason
                continue

            abs_path = self.repo_root / rel_path

            # Directory scope: inspect top-level files
            if abs_path.exists() and abs_path.is_dir():
                child_files = [
                    f.relative_to(self.repo_root).as_posix()
                    for f in sorted(abs_path.glob("*"))
                    if f.is_file()
                ]
                for child_rel in child_files:
                    c_valid, c_reason = self.validate_path(child_rel)
                    if not c_valid:
                        pkg.excluded_paths[child_rel] = c_reason
                        continue
                    current_chars = self._ingest_candidate(
                        child_rel,
                        cand.source_type,
                        cand.priority,
                        f"Child file of directory {rel_path}",
                        pkg,
                        current_chars,
                    )
                continue

            # Specific file
            current_chars = self._ingest_candidate(
                rel_path,
                cand.source_type,
                cand.priority,
                cand.reason,
                pkg,
                current_chars,
            )

        pkg.total_characters = current_chars
        return pkg

    def assemble_rework_context(
        self,
        task: Task,
        execution_id: str,
        parent_context_id: str,
        reviewer_feedback: str,
        reviewer_defect_details: Optional[str] = None,
        previous_diff: Optional[str] = None,
        previous_verification_output: Optional[str] = None,
        architect_intent: Optional[str] = None,
        previous_implementation_summary: Optional[str] = None,
        rework_objective: Optional[str] = None,
        changed_files: Optional[List[str]] = None,
        extra_paths: Optional[List[str]] = None,
        include_related_tests: bool = True,
    ) -> ContextPackage:
        """
        Assembles a dedicated rework context package for Executor re-invocation following Reviewer rejection.
        Guarantees:
        - Incorporates reviewer feedback and previous diff as bounded historical explanation.
        - Assembles current repository files fresh from disk (never reuses stale pre-execution files).
        - Explicitly conveys original requirements, architect intent, and rework objective.
        - Strictly obeys context budgets.
        """
        effective_objective = rework_objective or f"Resolve reviewer defects: {reviewer_feedback[:100]}"
        return self.assemble_context(
            task=task,
            role="executor",
            stage="rework_executor",
            execution_id=execution_id,
            parent_context_id=parent_context_id,
            extra_paths=extra_paths,
            changed_files=changed_files,
            include_related_tests=include_related_tests,
            reviewer_feedback=reviewer_feedback,
            reviewer_defect_details=reviewer_defect_details,
            previous_diff=previous_diff,
            previous_verification_output=previous_verification_output,
            architect_intent=architect_intent,
            previous_implementation_summary=previous_implementation_summary,
            rework_objective=effective_objective,
        )

    def _ingest_candidate(
        self,
        rel_path: str,
        source_type: SourceType,
        priority: ContextPriority,
        reason: str,
        pkg: ContextPackage,
        current_chars: int,
    ) -> int:
        """Ingests an individual file candidate into ContextPackage applying budgeting, hashing, and provenance."""
        abs_path = self.repo_root / rel_path

        # Greenfield file to be created
        if not abs_path.exists():
            pkg.files.append(
                FileContext(
                    relative_path=rel_path,
                    content="",
                    size_characters=0,
                    truncated=False,
                    is_new_file=True,
                    priority=priority,
                    freshness_hash=None,
                    file_mtime=None,
                    provenance=ContextItemProvenance(
                        source_type=source_type,
                        source_path=rel_path,
                        priority=priority,
                        reason=reason,
                        original_size_chars=0,
                        included_size_chars=0,
                        truncated=False,
                    ),
                )
            )
            pkg.included_paths.append(rel_path)
            return current_chars

        # Check total remaining budget
        remaining_budget = self.max_characters - current_chars
        if remaining_budget <= 0:
            pkg.excluded_paths[rel_path] = f"Context budget exceeded ({self.max_characters} chars)"
            pkg.truncated = True
            return current_chars

        try:
            raw_text = abs_path.read_text(encoding="utf-8")
            mtime = abs_path.stat().st_mtime
            freshness_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
        except Exception as e:
            pkg.excluded_paths[rel_path] = f"Read error: {str(e)}"
            return current_chars

        orig_len = len(raw_text)
        effective_file_limit = min(self.max_file_characters, remaining_budget)

        if orig_len > effective_file_limit:
            trunc_marker = f"\n\n[... truncated {orig_len - effective_file_limit} characters ...]"
            slice_limit = max(0, effective_file_limit - len(trunc_marker))
            content = raw_text[:slice_limit] + trunc_marker
            truncated = True
            pkg.truncated = True
            pkg.truncated_files_count += 1
        else:
            content = raw_text
            truncated = False

        chars_added = len(content)
        prov = ContextItemProvenance(
            source_type=source_type,
            source_path=rel_path,
            priority=priority,
            reason=reason,
            original_size_chars=orig_len,
            included_size_chars=chars_added,
            truncated=truncated,
        )

        pkg.files.append(
            FileContext(
                relative_path=rel_path,
                content=content,
                size_characters=chars_added,
                truncated=truncated,
                is_new_file=False,
                priority=priority,
                provenance=prov,
                freshness_hash=freshness_hash,
                file_mtime=mtime,
            )
        )
        pkg.provenance_items.append(prov)
        pkg.included_paths.append(rel_path)
        return current_chars + chars_added
