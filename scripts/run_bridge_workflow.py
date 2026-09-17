"""
Command-line Entry Point for the JESTER Multi-Agent Controlled Workflow (Phase 2C-2).

Takes a founder request, invokes the Architect, activates the task, executes
bounded repository modifications through the Executor and BoundedWorkspaceRuntime,
dispatches to the independent Reviewer, and halts at the mandatory Human Sign-off gate.

Usage:
    python scripts/run_bridge_workflow.py "Create a bridge diagnostics helper" --task-id TASK-0005
    python scripts/run_bridge_workflow.py --approve-task TASK-0005
"""
import argparse
from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

from jester_bridge.config import load_bridge_config
from jester_bridge.core import BridgeCore
from jester_bridge.openai_provider import OpenAIProvider
from jester_bridge.google_provider import GoogleProvider
from jester_bridge.testing import MockProviderA, MockProviderB
from jester_bridge.workflow import ControlledWorkflowRunner
from jester_bridge.orchestration import OrchestrationStage, ReviewVerdict
from jester_bridge.protocol import Task


def main():
    parser = argparse.ArgumentParser(description="JESTER Multi-Agent Controlled Workflow Runner")
    parser.add_argument("intent", nargs="?", default=None, help="High-level founder request or task intent")
    parser.add_argument("--task-id", default="TASK-0005", help="Task ID (e.g. TASK-0005)")
    parser.add_argument("--scope", nargs="+", default=["jester_bridge/diagnostics.py", "tests/bridge/test_diagnostics.py"], help="Authorized repository scope paths")
    parser.add_argument("--verification", nargs="+", default=["pytest tests/bridge/test_diagnostics.py"], help="Verification commands")
    parser.add_argument("--strict-credentials", action="store_true", default=False, help="Fail preflight if live API keys are missing/placeholder")
    parser.add_argument("--simulate-all", action="store_true", default=False, help="Force use of simulated providers for offline verification")
    parser.add_argument("--auto-approve", action="store_true", default=False, help="Automatically sign off if reviewer passes")
    parser.add_argument("--approve-task", default=None, help="Explicitly approve a task in review and mark completed")

    args = parser.parse_args()

    # 1. Load configuration
    config_path = REPO_ROOT / ".jester" / "config" / "agents.json"
    config = load_bridge_config(config_path)

    # 2. Handle direct approval command if requested
    if args.approve_task:
        task_file = REPO_ROOT / ".jester" / "tasks" / "review" / f"{args.approve_task}.json"
        if not task_file.exists():
            print(f"[ERROR] Task '{args.approve_task}' is not currently in .jester/tasks/review/")
            sys.exit(1)
        from jester_bridge.protocol import load_task_from_file
        task = load_task_from_file(task_file)
        core = BridgeCore(config=config, providers={"openai": MockProviderA("openai"), "google": MockProviderB("google")})
        runner = ControlledWorkflowRunner(core=core, repo_root=REPO_ROOT)
        session = runner.orchestrator.create_session(task=task)
        session.current_stage = OrchestrationStage.AWAITING_HUMAN_SIGNOFF
        completed_file = runner.complete_human_approval(
            session=session,
            approver="founder-manual",
            notes="Human approval granted via CLI.",
        )
        print(f"[SUCCESS] Task {args.approve_task} approved and moved to: {runner._rel_path(completed_file)}")
        sys.exit(0)

    if not args.intent:
        print("[ERROR] Task intent is required when running the workflow. Provide an intent or --approve-task.")
        sys.exit(1)

    print("==================================================")
    print("JESTER MULTI-AGENT CONTROLLED WORKFLOW (Phase 2D)")
    print("==================================================")
    print(f"Task ID: {args.task_id}")
    print(f"Intent:  {args.intent}")
    print(f"Scope:   {args.scope}")
    print(f"Verify:  {args.verification}")
    print("--------------------------------------------------")

    # 3. Provider Resolution & Preflight Readiness
    openai_prov = OpenAIProvider()
    google_prov = GoogleProvider()

    use_simulated_openai = args.simulate_all or (not openai_prov.health_check() and not args.strict_credentials)
    use_simulated_google = args.simulate_all or (not google_prov.health_check() and not args.strict_credentials)

    if use_simulated_openai:
        print("[NOTICE] OpenAI credentials not configured or --simulate-all active; using simulated OpenAI provider.")
        arch_summary = (
            f"Architecture plan for {args.task_id}: {args.intent}\n\n"
            "Decomposed into bounded implementation steps adhering strictly to repository governance."
        )
        openai_prov = MockProviderA(provider_id="openai", default_summary=arch_summary)

    if use_simulated_google:
        print("[NOTICE] Google/Gemini credentials not configured or --simulate-all active; using simulated Gemini executor.")
        simulated_code = (
            "Implementation complete.\n\n"
            "```python:jester_bridge/diagnostics.py\n"
            "\"\"\"\n"
            "Bridge Diagnostics Utility for JESTER AI Bridge.\n"
            "\"\"\"\n"
            "from typing import Dict, Any\n\n\n"
            "def get_bridge_diagnostics() -> Dict[str, Any]:\n"
            "    \"\"\"Returns system health and diagnostic information for the bridge.\"\"\"\n"
            "    return {\n"
            "        'status': 'ONLINE',\n"
            "        'protocol': 'v2.0',\n"
            "        'providers': ['openai', 'google'],\n"
            "        'execution_boundary': 'bounded_workspace_runtime',\n"
            "    }\n"
            "```\n\n"
            "```python:tests/bridge/test_diagnostics.py\n"
            "\"\"\"Tests for the Bridge Diagnostics Utility.\"\"\"\n"
            "from jester_bridge.diagnostics import get_bridge_diagnostics\n\n\n"
            "def test_bridge_diagnostics():\n"
            "    data = get_bridge_diagnostics()\n"
            "    assert data['status'] == 'ONLINE'\n"
            "    assert data['protocol'] == 'v2.0'\n"
            "    assert 'openai' in data['providers']\n"
            "    assert 'google' in data['providers']\n"
            "    assert data['execution_boundary'] == 'bounded_workspace_runtime'\n"
            "```\n"
        )
        google_prov = MockProviderB(provider_id="google", default_summary=simulated_code)

    core = BridgeCore(config=config, providers={"openai": openai_prov, "google": google_prov})
    runner = ControlledWorkflowRunner(core=core, repo_root=REPO_ROOT)

    # 4. Run E2E workflow
    print("\n[PHASE 1] Architect Planning & Preflight Checks...")
    outcome = runner.run_e2e_workflow(
        intent=args.intent,
        target_task_id=args.task_id,
        scope=args.scope,
        verification=args.verification,
        auto_apply=True,
        check_credentials=True,
    )

    print("\n--------------------------------------------------")
    print("WORKFLOW EXECUTION SUMMARY")
    print("--------------------------------------------------")
    print(f"Preflight Valid: {outcome.preflight.is_valid}")
    if outcome.preflight.errors:
        print(f"Preflight Errors: {outcome.preflight.errors}")

    print(f"Final Stage:     {outcome.stage.value}")
    if outcome.task_file_path:
        print(f"Task Lifecycle:  {outcome.task_file_path}")
    if outcome.implementation_report_path:
        print(f"Implementation:  {outcome.implementation_report_path}")
    if outcome.review_report_path:
        print(f"Review Report:   {outcome.review_report_path}")

    if outcome.usage:
        print("\n--- Token Observability ---")
        print(f"  Total Tokens:  {outcome.usage.total_tokens} (in: {outcome.usage.input_tokens}, out: {outcome.usage.output_tokens})")
        if outcome.stage_usage:
            print("  Stage Breakdown:")
            for stage_name, info in outcome.stage_usage.items():
                u = info.get("usage")
                role_name = info.get("role", "unknown")
                prov_name = info.get("provider", "unknown")
                if u:
                    print(f"    - {stage_name.capitalize():<10} [{role_name}/{prov_name}]: {u.total_tokens} tokens (in: {u.input_tokens}, out: {u.output_tokens})")
                else:
                    print(f"    - {stage_name.capitalize():<10} [{role_name}/{prov_name}]: N/A")

    # 5. Human Sign-Off Gate
    if outcome.stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF:
        print("\n==================================================")
        print("MANDATORY HUMAN SIGN-OFF GATE REACHED")
        print("==================================================")
        print("  Architect:  PASS (Task Protocol v2 inbox registered)")
        print("  Activation: PASS (Activated to active)")
        print("  Executor:   PASS (Bounded modifications applied)")
        print("  Verify:     PASS (All test verification commands succeeded)")
        print("  Reviewer:   PASS (Independent review verdict: PASS)")
        print("--------------------------------------------------")
        print("Status: AWAITING_HUMAN_SIGNOFF")
        print("Action: Explicit human approval required before task can complete.")
        print("==================================================")

        if args.auto_approve:
            print("\n[ACTION] Applying Human Approval via --auto-approve...")
            completed_file = runner.complete_human_approval(
                session=outcome.session,
                approver="founder-auto-signoff",
                notes="Automated sign-off flag supplied.",
            )
            print(f"[SUCCESS] Task marked COMPLETED: {runner._rel_path(completed_file)}")
        elif sys.stdin.isatty():
            try:
                choice = input("\nHuman Sign-Off: [A]pprove / [R]eject / [Q]uit? ").strip().lower()
                if choice in ("a", "approve", "y", "yes"):
                    completed_file = runner.complete_human_approval(
                        session=outcome.session,
                        approver="founder-interactive",
                        notes="Interactive human approval granted.",
                    )
                    print(f"[SUCCESS] Task marked COMPLETED: {runner._rel_path(completed_file)}")
                elif choice in ("r", "reject", "n", "no"):
                    reason = input("Enter rejection reason: ").strip() or "Rejected during human review."
                    blocked_file = runner.reject_human_signoff(
                        session=outcome.session,
                        rejector="founder-interactive",
                        reason=reason,
                    )
                    print(f"[REJECTED] Task transitioned: {runner._rel_path(blocked_file)}")
                else:
                    print("\n[HOLD] Workflow halted cleanly at AWAITING_HUMAN_SIGNOFF without state change.")
            except (KeyboardInterrupt, EOFError):
                print("\n[HOLD] Halted at AWAITING_HUMAN_SIGNOFF.")
        else:
            print(f"\nTo approve this task, run:")
            print(f"  python scripts/run_bridge_workflow.py --approve-task {args.task_id}")
    else:
        print(f"\n[ABORT / BLOCKED] Workflow stopped in stage: {outcome.stage.value}")
        if outcome.error_message:
            print(f"Reason: {outcome.error_message}")
        if outcome.runtime_result and outcome.runtime_result.verification_output:
            print(f"\n--- Verification Output ---\n{outcome.runtime_result.verification_output}")
        sys.exit(1)


if __name__ == "__main__":
    main()
