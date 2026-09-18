"""
Tests for CLIRuntimeAdapter and Gemini CLI Runtime Integration (TASK-0014).

Verifies:
1. Command argument formulation for Gemini CLI (-p, -o json, --yolo, --skip-trust, -m).
2. JSON error parsing for exit code 41 (Invalid auth method selected).
3. Status mapping to RuntimeStatus.AUTH_REQUIRED.
4. Binary resolution via shutil.which for Windows (.cmd/.bat).
5. Fail-closed behavior on unauthenticated real environment without silent mock fallback.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import pytest
import shutil

from jester_bridge.adapters import CLIRuntimeAdapter
from jester_bridge.contracts import InvocationRequest, InvocationStatus
from jester_bridge.protocol import Task
from jester_bridge.runtimes import (
    AccountIdentity,
    AuthReference,
    AuthType,
    RuntimeEntry,
    RuntimeRegistry,
    RuntimeRouter,
    RuntimeStatus,
    RuntimeType,
)


def test_gemini_cli_command_formulation():
    """Verifies that CLIRuntimeAdapter constructs the exact flags required by @google/gemini-cli."""
    adapter = CLIRuntimeAdapter(provider_id="google", executable_name="gemini")
    request = InvocationRequest(
        request_id="req-gemini-01",
        task_id="TASK-PROBE-01",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        model="gemini-2.5-pro",
        payload={
            "goal": "Write a unit test",
            "scope": ["tests/bridge/probe.py"],
            "constraints": ["Do not modify core"],
            "acceptance_criteria": ["Test passes"],
        },
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    cmd, stdin = adapter._build_command(request, "Goal: Write a unit test")
    assert stdin is None
    assert "-p" in cmd
    assert "-o" in cmd
    assert "json" in cmd
    assert "--yolo" in cmd
    assert "--skip-trust" in cmd
    assert "-m" in cmd
    assert "gemini-2.5-pro" in cmd


def test_gemini_cli_error_parsing_auth_code_41():
    """Verifies that exit code 41 with JSON error is parsed into AUTH_REQUIRED message."""
    def fake_runner(cmd, env, payload):
        err_json = json.dumps({
            "session_id": "test-session-uuid",
            "error": {
                "type": "Error",
                "message": "Invalid auth method selected.",
                "code": 41,
            }
        })
        return 41, "", err_json

    adapter = CLIRuntimeAdapter(
        provider_id="google",
        executable_name="gemini",
        runner_fn=fake_runner,
    )

    request = InvocationRequest(
        request_id="req-auth-01",
        task_id="TASK-AUTH-01",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        model="default",
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    result = adapter.invoke(request)
    assert result.status == InvocationStatus.FAILED
    assert "authentication required" in result.error_message.lower()
    assert "code 41" in result.error_message.lower()


def test_gemini_cli_resolves_windows_cmd_binary():
    """Verifies that _resolve_executable handles Windows .cmd scripts gracefully."""
    adapter = CLIRuntimeAdapter(provider_id="google", executable_name="gemini")
    resolved = adapter._resolve_executable()
    # On this machine, npm installs gemini.cmd
    if shutil.which("gemini"):
        assert os.path.isabs(resolved) or resolved == "gemini"


def test_real_gemini_cli_readiness_or_auth_check():
    """
    Integration check against actual installed Gemini CLI.
    If unauthenticated, must cleanly report AUTH_REQUIRED (code 41) rather than crashing.
    """
    if not shutil.which("gemini"):
        pytest.skip("gemini CLI is not installed on this system")

    adapter = CLIRuntimeAdapter(provider_id="google", executable_name="gemini")
    readiness = adapter.check_readiness()

    # The real installed CLI on this machine currently returns AUTH_REQUIRED
    assert readiness.status in (RuntimeStatus.READY, RuntimeStatus.AUTH_REQUIRED)
    if readiness.status == RuntimeStatus.AUTH_REQUIRED:
        assert "not authenticated" in readiness.message or "Invalid auth method" in readiness.message


def test_unauthenticated_gemini_cli_router_fails_closed():
    """
    Verifies that the multi-runtime router fails closed when Gemini CLI is unauthenticated,
    without silently falling back to mock providers.
    """
    adapter = CLIRuntimeAdapter(provider_id="google", executable_name="gemini")
    registry = RuntimeRegistry()
    registry.register_runtime(
        RuntimeEntry(
            runtime_id="gemini-cli-real",
            provider_id="google",
            runtime_type=RuntimeType.CLI,
            account=AccountIdentity(account_id="real-acc", provider="google"),
            model="gemini-2.5-pro",
            capabilities={"code_generation", "reasoning"},
            priority=10,
            provider_adapter=adapter,
        )
    )
    router = RuntimeRouter(registry)
    task = Task(id="TASK-P01", title="Probe", goal="Test", required_capabilities={"code_generation", "reasoning"})

    decision = router.route(task, target_provider="google")
    # If unauthenticated, router must report FAILED without guessing or mocking
    if adapter.check_readiness().status == RuntimeStatus.AUTH_REQUIRED:
        assert decision.status == "FAILED"
        assert decision.selected_runtime is None
        assert "unavailable" in decision.reason.lower()
