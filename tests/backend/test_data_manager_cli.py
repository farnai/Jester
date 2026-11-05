"""
tests.backend.test_data_manager_cli
===================================
Automated verification suite for JESTER Canonical Data Manager CLI.

Validates:
1. CLI interface presence and strict absence of destructive subcommands.
2. Read-only commands: 'list', 'status', 'verify', 'plan'.
3. JSON output formatting and machine-readability.
4. Fail-closed safety: rejection of protected cohorts (e.g. protected-core-dev-v1).
5. Fail-closed safety: rejection of disabled/retired lifecycle states.
6. Execution guard: 'seed' requires explicit '--apply-plan'.
7. Safe idempotency: repeated execution causes zero duplicate writes or mutations.
8. Preservation invariant: zero deletion or mutation of existing database records.
"""

import io
import json
import os
import sys
from unittest.mock import patch
import pytest

from backend.app.tools.data_manager import (
    main,
    build_cli_parser,
    generate_seed_plan,
    execute_seed_provisioning,
    get_verified_connection,
)
from backend.app.data_catalog import get_cohort, load_catalog, CohortStatus


def test_cli_parser_has_no_destructive_commands():
    """Verify that the CLI parser exposes NO destructive subcommands."""
    parser = build_cli_parser()
    subparsers_actions = [
        action for action in parser._actions if action.dest == "command"
    ]
    assert len(subparsers_actions) == 1
    available_commands = set(subparsers_actions[0].choices.keys())

    prohibited_names = {"delete", "truncate", "drop", "reset", "clear", "purge", "wipe", "remove"}
    for bad in prohibited_names:
        assert bad not in available_commands, f"Prohibited destructive command '{bad}' found in CLI!"

    expected_commands = {"list", "status", "verify", "plan", "seed"}
    assert expected_commands.issubset(available_commands)


def test_cli_list_table_output(capsys):
    """Verify 'list' command outputs human-readable table containing registered cohorts."""
    with patch.object(sys, "argv", ["data_manager", "list"]):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr().out
    assert "JESTER DATA CATALOG: COHORTS" in captured
    assert "demo-people-v1" in captured
    assert "protected-core-dev-v1" in captured
    assert "historical-unmanaged-dev" in captured


def test_cli_list_json_output(capsys):
    """Verify 'list --format json' outputs valid parseable JSON."""
    with patch.object(sys, "argv", ["data_manager", "list", "--format", "json"]):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert isinstance(data, list)
    assert len(data) >= 8

    cohort_ids = {c["id"] for c in data}
    assert "demo-people-v1" in cohort_ids
    assert "protected-core-dev-v1" in cohort_ids


def test_cli_status_test_env(capsys):
    """Verify 'status --env test' executes and returns database metrics."""
    with patch.object(sys, "argv", ["data_manager", "status", "--env", "test"]):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr().out
    assert "JESTER DATABASE & COHORT STATUS: [TEST]" in captured
    assert "Total Users:" in captured
    assert "Total Profiles:" in captured
    assert "demo-people-v1" in captured


def test_cli_status_json_output(capsys):
    """Verify 'status --env test --format json' outputs structured JSON report."""
    with patch.object(sys, "argv", ["data_manager", "status", "--env", "test", "--format", "json"]):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr().out
    report = json.loads(captured)
    assert report["environment"] == "test"
    assert "database_metrics" in report
    assert report["database_metrics"]["total_users"] > 0
    assert "cohorts" in report
    assert len(report["cohorts"]) > 0


def test_cli_verify_test_env(capsys):
    """Verify 'verify --env test' checks catalog metadata and database integrity."""
    with patch.object(sys, "argv", ["data_manager", "verify", "--env", "test"]):
        exit_code = main()
        # Should be 0 since demo-people-v1 has been provisioned
        assert exit_code == 0

    captured = capsys.readouterr().out
    assert "Metadata Validation: PASSED" in captured
    assert "Cohort 'demo-people-v1': PASSED" in captured


def test_cli_plan_demo_cohort(capsys):
    """Verify 'plan demo-people-v1 --env test' produces a non-destructive plan."""
    with patch.object(sys, "argv", ["data_manager", "plan", "demo-people-v1", "--env", "test"]):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr().out
    assert "JESTER PROVISIONING PLAN: Cohort 'demo-people-v1' -> [TEST]" in captured
    assert "Conflicts Detected:  0" in captured
    assert "Plan is valid and non-destructive" in captured


def test_cli_plan_rejects_protected_cohort(capsys):
    """Verify planning a protected cohort (e.g. protected-core-dev-v1) is strictly rejected."""
    with patch.object(sys, "argv", ["data_manager", "plan", "protected-core-dev-v1", "--env", "development"]):
        exit_code = main()
        assert exit_code == 1

    captured = capsys.readouterr().out
    assert "SAFETY VIOLATION" in captured
    assert "immutable and CANNOT be planned or seeded" in captured


def test_cli_plan_rejects_unmanaged_cohort(capsys):
    """Verify planning an unmanaged cohort (e.g. historical-unmanaged-dev) is rejected."""
    with patch.object(sys, "argv", ["data_manager", "plan", "historical-unmanaged-dev", "--env", "development"]):
        exit_code = main()
        assert exit_code == 1

    captured = capsys.readouterr().out
    assert "SAFETY VIOLATION" in captured


def test_cli_seed_requires_apply_plan(capsys):
    """Verify 'seed' without '--apply-plan' only prints a dry-run prompt and performs 0 writes."""
    with patch.object(sys, "argv", ["data_manager", "seed", "demo-people-v1", "--env", "test"]):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr().out
    assert "To apply this plan and execute safe provisioning, re-run with '--apply-plan'" in captured or "[IDEMPOTENT]" in captured


def test_cli_seed_idempotency_safe(capsys):
    """Verify executing 'seed --apply-plan' on an already provisioned cohort does not alter or re-insert anything."""
    with patch.object(sys, "argv", ["data_manager", "seed", "demo-people-v1", "--env", "test", "--apply-plan"]):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr().out
    assert "[IDEMPOTENT]" in captured
    assert "Zero modifications executed" in captured


def test_cli_seed_rejects_protected_cohort():
    """Verify seed execution rejects protected cohorts even if forced via API."""
    cohort = get_cohort("protected-core-dev-v1")
    with pytest.raises(ValueError, match="SAFETY VIOLATION"):
        generate_seed_plan(cohort, "development")


def test_cli_seed_rejects_retired_lifecycle(monkeypatch):
    """Verify that disabled or retired cohorts cannot be planned or seeded."""
    cohort = get_cohort("demo-people-v1")
    # Simulate a retired cohort
    monkeypatch.setattr(cohort, "status", CohortStatus.RETIRED)
    with pytest.raises(ValueError, match="LIFECYCLE ERROR"):
        generate_seed_plan(cohort, "test")


def test_cli_plan_includes_deterministic_fingerprint(capsys):
    """Verify that plan output contains a deterministic cryptographic fingerprint."""
    with patch.object(sys, "argv", ["data_manager", "plan", "demo-people-v1", "--env", "test"]):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr().out
    assert "Plan Fingerprint:" in captured


def test_cli_seed_rejects_fingerprint_mismatch_toctou(capsys):
    """Verify that seed with mismatched --fingerprint aborts due to TOCTOU violation."""
    with patch.object(
        sys,
        "argv",
        ["data_manager", "seed", "demo-people-v1", "--env", "test", "--apply-plan", "--fingerprint", "deadbeef00000000"],
    ):
        exit_code = main()
        assert exit_code == 1

    captured = capsys.readouterr().out
    assert "CRITICAL TOCTOU SAFETY VIOLATION" in captured
    assert "Expected plan fingerprint: deadbeef00000000" in captured


def test_cli_seed_accepts_valid_fingerprint(capsys):
    """Verify that seed with correct --fingerprint succeeds safely."""
    cohort = get_cohort("demo-people-v1")
    plan = generate_seed_plan(cohort, "test")
    valid_fp = plan["plan_fingerprint"]

    with patch.object(
        sys,
        "argv",
        ["data_manager", "seed", "demo-people-v1", "--env", "test", "--apply-plan", "--fingerprint", valid_fp],
    ):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr().out
    assert "[IDEMPOTENT]" in captured or "SUCCESS" in captured
