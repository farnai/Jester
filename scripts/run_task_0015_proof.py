"""
TASK-0015: Real End-to-End Execution Proof via Authenticated Antigravity CLI.

Executes the real Bridge workflow:
Founder/Task Intake -> Task Protocol -> Architect -> Task/Context/Handoff ->
Executor -> RuntimeRouter -> Google Provider -> Antigravity CLI Runtime ->
real `agy` execution -> real file creation -> real pytest execution ->
real diff generation -> Reviewer -> AWAITING_HUMAN_SIGNOFF.

Invariants:
- Zero mocks, zero simulation, zero API-key fallbacks.
- Strictly halts at AWAITING_HUMAN_SIGNOFF without automatic approval.
- Zero commits, zero pushes, zero staged changes.
"""
from pathlib import Path
import subprocess
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from jester_bridge.adapters import CLIRuntimeAdapter
from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig
from jester_bridge.core import BridgeCore
from jester_bridge.execution_history import ExecutionHistoryStore
from jester_bridge.orchestration import OrchestrationStage, ReviewVerdict
from jester_bridge.runtimes import (
    RuntimeReadiness,
    RuntimeStatus,
    create_antigravity_runtime,
)
from jester_bridge.workflow import ControlledWorkflowRunner


def run_proof():
    print("==================================================================")
    print("TASK-0015: REAL ANTIGRAVITY CLI END-TO-END EXECUTION PROOF")
    print("==================================================================")

    # 1. Verify Antigravity CLI readiness
    adapter = CLIRuntimeAdapter(
        provider_id="google",
        executable_name="agy",
        account_id="google-ai-pro",
        timeout=120.0,
    )
    print("\n[STEP 1] Checking Antigravity CLI readiness...")
    readiness = adapter.check_readiness()
    print(f"Readiness Status:  {readiness.status.value}")
    print(f"Readiness Message: {readiness.message}")

    if readiness.status != RuntimeStatus.READY:
        print(f"[FATAL] Antigravity CLI is not READY. Cannot proceed with real proof.")
        sys.exit(1)

    # 2. Setup Multi-Agent Topology for Google / Antigravity CLI
    config = BridgeConfig(
        role_bindings={
            "architect": "gemini-architect",
            "executor": "gemini-dev",
            "reviewer": "gemini-reviewer",
        },
        agents={
            "gemini-architect": AgentProfile(
                id="gemini-architect",
                role="architect",
                provider="google",
                model="gemini-3.8-flash-low",
                capabilities={"planning", "reasoning", "repository_read"},
            ),
            "gemini-dev": AgentProfile(
                id="gemini-dev",
                role="executor",
                provider="google",
                model="gemini-3.8-flash-low",
                capabilities={"planning", "reasoning", "code_generation", "repository_read"},
            ),
            "gemini-reviewer": AgentProfile(
                id="gemini-reviewer",
                role="reviewer",
                provider="google",
                model="gemini-3.8-flash-low",
                capabilities={"reasoning", "repository_read", "review", "testing"},
            ),
        },
    )

    core = BridgeCore(config=config)
    runtime_entry = create_antigravity_runtime(
        account_id="google-ai-pro",
        account_label="Google AI Pro (Antigravity CLI)",
        model="gemini-3.8-flash-low",
        priority=1,
        adapter=adapter,
    )
    core.register_runtime(runtime_entry)

    # Verify Router selects Antigravity CLI runtime
    from jester_bridge.protocol import Task
    dummy_task = Task(id="TASK-PROBE", title="Probe", role="executor", goal="Probe")
    router_probe = core.runtime_router.route(
        task=dummy_task,
        target_role="executor",
        target_provider="google",
        target_runtime_id="google-antigravity-cli",
    )
    assert router_probe.status == "SUCCESS"
    assert router_probe.selected_runtime is not None
    assert router_probe.selected_runtime.runtime_id == "google-antigravity-cli"
    print(f"[STEP 2] RuntimeRouter verified: selected {router_probe.selected_runtime.runtime_id} "
          f"(model={router_probe.selected_runtime.model}, account={router_probe.selected_runtime.account.account_id})")

    # 3. Initialize Controlled Workflow Runner
    history_store = ExecutionHistoryStore(repo_root=REPO_ROOT)
    runner = ControlledWorkflowRunner(
        core=core,
        repo_root=REPO_ROOT,
        history_store=history_store,
    )

    target_task_id = "TASK-0015"
    probe_rel_path = "tests/bridge/task_0015_antigravity_cli_e2e_probe.py"
    probe_abs_path = REPO_ROOT / probe_rel_path

    # Ensure probe file does not exist beforehand
    if probe_abs_path.exists():
        probe_abs_path.unlink()

    intent = (
        f"Create a new file at {probe_rel_path} containing a single minimal pytest test "
        f"that proves 2 + 2 equals 4. Include a standard docstring and 'assert 2 + 2 == 4'."
    )
    scope = [probe_rel_path]
    constraints = [
        f"Create only {probe_rel_path}.",
        "Do not modify any other files.",
        "Keep the test minimal and conform to pytest standards.",
    ]
    criteria = [
        f"File {probe_rel_path} must exist on disk.",
        "Must define a test function that asserts 2 + 2 == 4.",
        "Pytest must pass cleanly.",
    ]
    verification = [
        f"pytest {probe_rel_path} -v"
    ]

    print(f"\n[STEP 3] Executing Real Workflow for {target_task_id}...")
    print(f"  Target File:  {probe_rel_path}")
    print(f"  Scope:        {scope}")
    print(f"  Verification: {verification}")
    print(f"  Runtime:      google-antigravity-cli (Google AI Pro)")

    outcome = runner.run_e2e_workflow(
        intent=intent,
        target_task_id=target_task_id,
        scope=scope,
        constraints=constraints,
        acceptance_criteria=criteria,
        verification=verification,
        auto_apply=True,
        check_credentials=True,
        target_runtime_id="google-antigravity-cli",
    )

    print("\n==================================================================")
    print("WORKFLOW OUTCOME EVIDENCE")
    print("==================================================================")
    print(f"Outcome Stage:    {outcome.stage.value}")
    print(f"Preflight Valid:  {outcome.preflight.is_valid}")
    print(f"Execution ID:     {outcome.execution_id}")
    print(f"Task File:        {outcome.task_file_path}")
    print(f"Impl Report:      {outcome.implementation_report_path}")
    print(f"Review Report:    {outcome.review_report_path}")

    # Evidence 1: Workflow Stage
    assert outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF, (
        f"Workflow failed to reach AWAITING_HUMAN_SIGNOFF; ended in {outcome.stage}"
    )

    # Evidence 2: Probe file exists on disk
    assert probe_abs_path.exists(), f"Probe file was not created: {probe_abs_path}"
    probe_content = probe_abs_path.read_text(encoding="utf-8")
    print(f"\n[EVIDENCE 2: Probe File Content ({probe_rel_path})]:\n{probe_content}")
    assert "2 + 2 == 4" in probe_content or "4" in probe_content, "Probe test does not contain expected assertion"

    # Evidence 3: Pytest actually passes
    print("\n[EVIDENCE 3: Independent Pytest Execution]...")
    pytest_proc = subprocess.run(
        [sys.executable, "-m", "pytest", probe_rel_path, "-v"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    print(f"Pytest returncode: {pytest_proc.returncode}")
    print(f"Pytest output:\n{pytest_proc.stdout}")
    assert pytest_proc.returncode == 0, f"Pytest failed: {pytest_proc.stderr}"
    assert "1 passed" in pytest_proc.stdout

    # Evidence 4: Real Unified Diff
    print(f"\n[EVIDENCE 4: Real Unified Diff]:\n{outcome.diff}")
    assert outcome.diff is not None and outcome.diff.strip() != "", "Diff is empty!"
    assert probe_rel_path in outcome.diff or "task_0015_antigravity_cli_e2e_probe.py" in outcome.diff

    # Evidence 5: Reviewer Verdict
    rev_res = outcome.session.review_result
    assert rev_res is not None, "Review result missing"
    print(f"\n[EVIDENCE 5: Reviewer Verdict]: {rev_res.verdict.value}")
    print(f"Reviewer Summary: {rev_res.summary}")
    assert rev_res.verdict == ReviewVerdict.PASS, f"Reviewer did not pass: {rev_res.verdict}"

    # Evidence 6: Execution History Metadata
    history = history_store.get_execution(outcome.execution_id)
    assert history is not None, "History record missing"
    print("\n[EVIDENCE 6: Execution History Metadata]:")
    print(f"  Execution ID:   {history.execution_id}")
    print(f"  Current Stage:  {history.current_stage}")
    print(f"  Overall Status: {history.overall_status}")
    print(f"  Runtimes:       {history.metadata.get('runtimes')}")

    events = history_store.list_events(outcome.execution_id)
    print(f"\n  Event Count:    {len(events)}")
    for ev in events:
        print(f"    - [{ev.stage}] {ev.event_type} ({ev.status}): {ev.summary[:80] if ev.summary else ''}")

    # Evidence 7: Git Safety Invariants
    git_proc = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True)
    git_lines = [l for l in git_proc.stdout.splitlines() if l.strip()]
    staged = [l for l in git_lines if l.startswith("A ") or l.startswith("M ") or l.startswith("D ")]
    print("\n[EVIDENCE 7: Git Safety Boundaries]:")
    print(f"  Staged changes count: {len(staged)}")
    assert len(staged) == 0, f"Unwanted staged changes found: {staged}"

    print("\n==================================================================")
    print("SUCCESS: REAL ANTIGRAVITY CLI PROOF COMPLETE (AWAITING_HUMAN_SIGNOFF)")
    print("==================================================================")


if __name__ == "__main__":
    run_proof()
