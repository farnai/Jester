"""
Tests for the JESTER AI Bridge Context Engine (TASK-0006).

Verifies:
- TEST 1: Ingestion of in-scope repository files.
- TEST 2: Rejection of protected paths (.env, .git/, AGENTS.md, supabase/migrations).
- TEST 3: Workspace containment (blocking directory traversal / escaping workspace root).
- TEST 4: Context budgeting and deterministic truncation.
"""
from pathlib import Path
import pytest

from jester_bridge.context import (
    ContextBundle,
    ContextEngine,
    ContextItemProvenance,
    ContextPackage,
    ContextPriority,
    FileContext,
    SourceType,
)
from jester_bridge.protocol import Task
from jester_bridge.runtime import BoundedWorkspaceRuntime, FileChange, ScopeViolationError


def test_context_ingestion_in_scope_file(tmp_path: Path):
    # Setup test repository structure
    repo_file = tmp_path / "jester_bridge" / "sample.py"
    repo_file.parent.mkdir(parents=True, exist_ok=True)
    repo_file.write_text("def sample_utility():\n    return 'OK'\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="TASK-CTX-01",
        title="Sample Context Task",
        role="executor",
        goal="Add feature to sample utility",
        scope=["jester_bridge/sample.py"],
    )

    bundle = engine.assemble_context(task)

    assert "jester_bridge/sample.py" in bundle.included_paths
    assert len(bundle.files) == 1
    fc = bundle.files[0]
    assert fc.relative_path == "jester_bridge/sample.py"
    assert "def sample_utility():" in fc.content
    assert fc.is_new_file is False
    assert fc.truncated is False

    formatted = bundle.format_for_prompt()
    assert "### File: `jester_bridge/sample.py`" in formatted
    assert "def sample_utility():" in formatted


def test_context_rejection_protected_paths(tmp_path: Path):
    # Create protected files on disk in mock workspace
    (tmp_path / ".env").write_text("SECRET_KEY=supersecret\n", encoding="utf-8")
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\nrepositoryformatversion = 0\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# Core governance rules\n", encoding="utf-8")
    mig_dir = tmp_path / "supabase" / "migrations"
    mig_dir.mkdir(parents=True)
    (mig_dir / "0001_init.sql").write_text("CREATE TABLE users ();\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="TASK-CTX-02",
        title="Malicious Scope Task",
        role="executor",
        goal="Attempt to read protected paths",
        scope=[".env", ".git/config", "AGENTS.md", "supabase/migrations/0001_init.sql"],
    )

    bundle = engine.assemble_context(task)

    # Invariants: None of the protected paths may be included
    assert len(bundle.included_paths) == 0
    assert len(bundle.files) == 0
    assert ".env" in bundle.excluded_paths
    assert ".git/config" in bundle.excluded_paths
    assert "AGENTS.md" in bundle.excluded_paths
    assert "supabase/migrations/0001_init.sql" in bundle.excluded_paths

    formatted = bundle.format_for_prompt()
    assert "SECRET_KEY" not in formatted
    assert "supersecret" not in formatted


def test_context_workspace_containment_path_traversal(tmp_path: Path):
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="TASK-CTX-03",
        title="Traversal Task",
        role="executor",
        goal="Attempt to escape workspace",
        scope=["../outside_file.py", "..\\secret.txt", "../../etc/passwd"],
    )

    bundle = engine.assemble_context(task)

    assert len(bundle.included_paths) == 0
    assert len(bundle.files) == 0
    for p in task.scope:
        norm = p.replace("\\", "/")
        assert norm in bundle.excluded_paths
        assert "traversal" in bundle.excluded_paths[norm].lower() or "escapes" in bundle.excluded_paths[norm].lower()


def test_context_budgeting_and_truncation(tmp_path: Path):
    large_content = "X" * 1500
    file_path = tmp_path / "large_file.txt"
    file_path.write_text(large_content, encoding="utf-8")

    # Limit budget to 500 characters
    engine = ContextEngine(repo_root=tmp_path, max_characters=500, max_file_characters=500)
    task = Task(
        id="TASK-CTX-04",
        title="Budget Test Task",
        role="executor",
        goal="Ingest large file",
        scope=["large_file.txt"],
    )

    bundle = engine.assemble_context(task)

    assert bundle.truncated is True
    assert len(bundle.files) == 1
    fc = bundle.files[0]
    assert fc.truncated is True
    assert len(fc.content) < len(large_content)
    assert "[... truncated" in fc.content


def test_context_budgeting_multi_file_overflow(tmp_path: Path):
    (tmp_path / "f1.txt").write_text("A" * 300, encoding="utf-8")
    (tmp_path / "f2.txt").write_text("B" * 300, encoding="utf-8")
    (tmp_path / "f3.txt").write_text("C" * 300, encoding="utf-8")

    # Budget allows 500 characters total
    engine = ContextEngine(repo_root=tmp_path, max_characters=500, max_file_characters=500)
    task = Task(
        id="TASK-CTX-05",
        title="Multi-File Budget Overflow",
        role="executor",
        goal="Ingest multiple files",
        scope=["f1.txt", "f2.txt", "f3.txt"],
    )

    bundle = engine.assemble_context(task)

    assert "f1.txt" in bundle.included_paths
    assert "f2.txt" in bundle.included_paths
    assert "f3.txt" in bundle.excluded_paths
    assert "budget exceeded" in bundle.excluded_paths["f3.txt"].lower()


def test_context_greenfield_new_file(tmp_path: Path):
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="TASK-CTX-06",
        title="Greenfield File Task",
        role="executor",
        goal="Create brand new file",
        scope=["components/brand_new.py"],
    )

    bundle = engine.assemble_context(task)

    assert "components/brand_new.py" in bundle.included_paths
    assert len(bundle.files) == 1
    fc = bundle.files[0]
    assert fc.is_new_file is True
    assert fc.content == ""
    assert "(empty / does not exist yet)" in bundle.format_for_prompt()


def test_context_package_creation_and_properties(tmp_path: Path):
    """TEST 1: ContextPackage creation, fields, properties, and serialization."""
    f = tmp_path / "mod.py"
    f.write_text("print('hello')", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path, max_characters=10_000)
    task = Task(
        id="TASK-PKG-01",
        title="Package Test",
        role="executor",
        goal="Test context package creation",
        scope=["mod.py"],
    )

    pkg = engine.assemble_context(task)
    assert isinstance(pkg, ContextPackage)
    assert pkg.context_version == "v1"
    assert pkg.task_id == "TASK-PKG-01"
    assert pkg.role == "executor"
    assert pkg.budget == 10_000
    assert pkg.usage > 0
    assert pkg.available_budget == 10_000 - pkg.usage
    assert pkg.selected_files == ["mod.py"]
    assert len(pkg.file_contexts) == 1
    assert pkg.truncated is False

    # Check serializability
    dumped = pkg.model_dump()
    assert dumped["task_id"] == "TASK-PKG-01"
    assert dumped["context_version"] == "v1"
    assert "mod.py" in dumped["included_paths"]


def test_context_priority_ordering_and_budget_truncation(tmp_path: Path):
    """TEST 2: Priority ordering (CRITICAL before HIGH before NORMAL) and budget truncation."""
    # Create 3 files:
    # f_crit: in scope (CRITICAL)
    # f_test: related test (HIGH)
    # f_norm: mentioned in text (NORMAL)
    f_crit = tmp_path / "jester_bridge" / "service.py"
    f_crit.parent.mkdir(parents=True, exist_ok=True)
    f_crit.write_text("S" * 200, encoding="utf-8")

    t_dir = tmp_path / "tests" / "bridge"
    t_dir.mkdir(parents=True, exist_ok=True)
    f_test = t_dir / "test_service.py"
    f_test.write_text("T" * 200, encoding="utf-8")

    f_norm = tmp_path / "docs" / "notes.txt"
    f_norm.parent.mkdir(parents=True, exist_ok=True)
    f_norm.write_text("N" * 200, encoding="utf-8")

    # Set total budget to 350 chars (enough for f_crit (200) + part of f_test (150), but excludes f_norm)
    engine = ContextEngine(repo_root=tmp_path, max_characters=350, max_file_characters=500)
    task = Task(
        id="TASK-PRIO-01",
        title="Priority Test",
        role="executor",
        goal="Inspect docs/notes.txt and update service",
        scope=["jester_bridge/service.py"],
    )

    pkg = engine.assemble_context(task, include_related_tests=True)

    # Invariants:
    # 1. CRITICAL (jester_bridge/service.py) must be included first
    # 2. HIGH (tests/bridge/test_service.py) must be included next (and truncated if needed)
    # 3. NORMAL (docs/notes.txt) must be excluded because budget is exhausted
    assert "jester_bridge/service.py" in pkg.included_paths
    fc_crit = next(f for f in pkg.files if f.relative_path == "jester_bridge/service.py")
    assert fc_crit.priority == ContextPriority.CRITICAL

    assert "tests/bridge/test_service.py" in pkg.included_paths
    fc_test = next(f for f in pkg.files if f.relative_path == "tests/bridge/test_service.py")
    assert fc_test.priority == ContextPriority.HIGH
    assert fc_test.truncated is True

    assert "docs/notes.txt" in pkg.excluded_paths
    assert "budget exceeded" in pkg.excluded_paths["docs/notes.txt"].lower()


def test_context_role_aware_selection(tmp_path: Path):
    """TEST 3: Role-aware context assembly (Architect vs Reviewer)."""
    # Architecture doc
    arch_doc = tmp_path / "docs" / "AI_BRIDGE_ARCHITECTURE.md"
    arch_doc.parent.mkdir(parents=True, exist_ok=True)
    arch_doc.write_text("# Core Bridge Architecture\n", encoding="utf-8")

    # Implementation file
    impl = tmp_path / "jester_bridge" / "core.py"
    impl.parent.mkdir(parents=True, exist_ok=True)
    impl.write_text("class Core:\n    pass\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="TASK-ROLE-01",
        title="Role Test",
        role="architect",
        goal="Design architecture component",
        scope=["jester_bridge/core.py"],
    )

    # Architect invocation includes architecture documentation automatically
    arch_pkg = engine.assemble_context(task, role="architect", include_arch_docs=True)
    assert "docs/AI_BRIDGE_ARCHITECTURE.md" in arch_pkg.included_paths
    assert arch_pkg.role == "architect"

    # Reviewer invocation with diff and verification
    diff_content = "--- a/core.py\n+++ b/core.py\n@@ -1 +1 @@\n-old\n+new\n"
    rev_pkg = engine.assemble_context(
        task,
        role="reviewer",
        diff=diff_content,
        verification_output="All 10 tests passed.",
        changed_files=["jester_bridge/core.py"],
    )
    assert rev_pkg.role == "reviewer"
    assert rev_pkg.diff == diff_content
    assert rev_pkg.verification_output == "All 10 tests passed."
    assert "Code Diff Evidence" in rev_pkg.format_for_prompt()
    assert "All 10 tests passed." in rev_pkg.format_for_prompt()


def test_context_diff_budget_truncation(tmp_path: Path):
    """TEST 4: Massive code diff is deterministically truncated when exceeding budget."""
    engine = ContextEngine(repo_root=tmp_path, max_characters=200)
    huge_diff = "--- a/file.py\n+++ b/file.py\n" + ("+line\n" * 50)

    task = Task(
        id="TASK-DIFF-TRUNC",
        title="Diff Trunc Test",
        role="reviewer",
        goal="Review massive diff",
        scope=[],
    )

    pkg = engine.assemble_context(task, role="reviewer", diff=huge_diff)
    assert pkg.diff_truncated is True
    assert pkg.truncated is True
    assert "[... diff truncated" in pkg.diff
    assert len(pkg.diff) <= 250  # Bounded by character budget + marker


def test_context_provenance_and_exclusion_reasons(tmp_path: Path):
    """TEST 5: Explicit audit provenance and exclusion tracking."""
    # Valid file
    f_ok = tmp_path / "valid.py"
    f_ok.write_text("VALID_DATA = 1\n", encoding="utf-8")

    # Protected file
    (tmp_path / ".env").write_text("API_KEY=123\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="TASK-PROV-01",
        title="Provenance Test",
        role="executor",
        goal="Audit provenance",
        scope=["valid.py", ".env", "../outside.txt"],
    )

    pkg = engine.assemble_context(task)

    # Check provenance on included file
    assert len(pkg.provenance_items) >= 1
    prov = next(p for p in pkg.provenance_items if p.source_path == "valid.py")
    assert prov.source_type == SourceType.EXPLICIT_SCOPE
    assert prov.priority == ContextPriority.CRITICAL
    assert "Explicitly declared in task scope" in prov.reason
    assert prov.truncated is False

    # Check exclusion reasons
    assert ".env" in pkg.excluded_paths
    assert "protected" in pkg.excluded_paths[".env"].lower()
    assert "../outside.txt" in pkg.excluded_paths
    assert "traversal" in pkg.excluded_paths["../outside.txt"].lower() or "escapes" in pkg.excluded_paths["../outside.txt"].lower()


def test_context_deterministic_repeated_assembly(tmp_path: Path):
    """TEST 6: Given same workspace and task, context ordering and budgeting is 100% reproducible."""
    for i in range(5):
        (tmp_path / f"file_{i}.txt").write_text(f"Content {i}\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="TASK-DET-01",
        title="Determinism Test",
        role="executor",
        goal="Verify deterministic assembly",
        scope=["file_4.txt", "file_1.txt", "file_3.txt", "file_0.txt", "file_2.txt"],
    )

    pkg1 = engine.assemble_context(task)
    pkg2 = engine.assemble_context(task)

    assert pkg1.included_paths == pkg2.included_paths
    assert [f.relative_path for f in pkg1.files] == [f.relative_path for f in pkg2.files]
    assert pkg1.total_characters == pkg2.total_characters
    assert pkg1.format_for_prompt() == pkg2.format_for_prompt()


def test_context_does_not_expand_write_scope(tmp_path: Path):
    """TEST 7: Critical Governance Invariant - Context access does NOT grant write authority."""
    # Create two files:
    # 1. target.py (in task.scope - writable)
    # 2. readonly_reference.py (discovered or read into context - NOT in task.scope)
    (tmp_path / "target.py").write_text("val = 1\n", encoding="utf-8")
    (tmp_path / "readonly_reference.py").write_text("SECRET_REF = 99\n", encoding="utf-8")

    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="TASK-WRITE-SCOPE",
        title="Scope Invariant Test",
        role="executor",
        goal="Read readonly_reference.py and update target.py",
        scope=["target.py"],  # ONLY target.py is in write scope!
    )

    # Assemble context with readonly_reference.py included as extra read path
    pkg = engine.assemble_context(task, extra_paths=["readonly_reference.py"])
    assert "readonly_reference.py" in pkg.included_paths

    # Now verify with BoundedWorkspaceRuntime that attempting to write to readonly_reference.py fails closed!
    runtime = BoundedWorkspaceRuntime(repo_root=tmp_path)
    illegal_changes = [
        FileChange(relative_path="readonly_reference.py", content="MALICIOUS_OVERWRITE\n")
    ]

    exec_result = runtime.execute_and_verify(changes=illegal_changes, task=task)
    assert exec_result.status == "FAILED"
    assert "violates authorized scope" in (exec_result.error_message or "").lower()
    assert "readonly_reference.py" not in exec_result.files_modified
    # Verify file was never modified on disk
    assert (tmp_path / "readonly_reference.py").read_text(encoding="utf-8") == "SECRET_REF = 99\n"


def test_context_summary_dict_bounded_for_history(tmp_path: Path):
    """TEST 8: ContextPackage.to_summary_dict() produces bounded, credential-free metadata."""
    (tmp_path / "file.py").write_text("def run(): pass\n", encoding="utf-8")
    engine = ContextEngine(repo_root=tmp_path)
    task = Task(
        id="TASK-SUMM-01",
        title="Summary Test",
        role="executor",
        goal="Check summary dict",
        scope=["file.py"],
    )

    pkg = engine.assemble_context(task)
    summ = pkg.to_summary_dict()

    assert summ["role"] == "executor"
    assert summ["context_version"] == "v1"
    assert summ["selected_file_count"] == 1
    assert summ["excluded_file_count"] == 0
    assert summ["used_budget"] > 0
    assert "content" not in summ  # Never store raw code in summary dict!
