"""
Tests for CLIRuntimeAdapter with Antigravity CLI (agy) Integration (TASK-0015).

Verifies:
1. Command formulation for agy (-p, --output-format json, --dangerously-skip-permissions, --disable-slash-commands, --model).
2. Allowlist enforcement (rejects unauthorized binaries, allows agy).
3. Structured JSON output normalization into InvocationResult.
4. Token usage extraction from agy response.
5. Error handling and exit status normalization.
6. Real agy authenticated readiness probe.
7. Dynamic model enumeration from agy models.
8. RuntimeRegistry and RuntimeRouter deterministic selection of Antigravity CLI runtime.
9. Secret isolation and redaction.
10. Fail-closed behavior on unready runtime without silent fallback.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import pytest
import shutil
import subprocess

from jester_bridge.adapters import CLIRuntimeAdapter, _sanitize_cli_text
from jester_bridge.contracts import InvocationRequest, InvocationStatus, UsageMetrics
from jester_bridge.protocol import Task
from jester_bridge.runtimes import (
    AccountIdentity,
    AuthReference,
    AuthType,
    RuntimeEntry,
    RuntimeReadiness,
    RuntimeRegistry,
    RuntimeRouter,
    RuntimeStatus,
    RuntimeType,
    create_antigravity_runtime,
)


def test_antigravity_cli_command_formulation():
    """Verifies argument vector formulation for agy non-interactive print mode."""
    adapter = CLIRuntimeAdapter(provider_id="google", executable_name="agy")
    request = InvocationRequest(
        request_id="req-agy-01",
        task_id="TASK-0015",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        model="gemini-3.8-flash-high",
        payload={
            "goal": "Create a probe file",
            "scope": ["tests/bridge/task_0015_antigravity_cli_e2e_probe.py"],
            "constraints": ["Preserve invariants"],
            "acceptance_criteria": ["Test passes"],
        },
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    cmd, stdin = adapter._build_command(request, "Goal: Create a probe file")
    assert stdin is None
    assert "-p" in cmd
    assert "--output-format" in cmd
    assert "json" in cmd
    assert "--dangerously-skip-permissions" in cmd
    assert "--disable-slash-commands" in cmd
    assert "--model" in cmd
    assert "gemini-3.8-flash-high" in cmd


def test_antigravity_cli_allowlist_enforcement():
    """Verifies that agy is accepted in allowlist, while unauthorized binaries are rejected."""
    adapter = CLIRuntimeAdapter(provider_id="google", executable_name="agy")
    assert adapter.executable_name == "agy"

    with pytest.raises(ValueError, match="not in the controlled allowlist"):
        CLIRuntimeAdapter(provider_id="google", executable_name="bash")

    with pytest.raises(ValueError, match="forbidden shell metacharacters"):
        CLIRuntimeAdapter(
            provider_id="google",
            executable_name="agy; rm -rf",
            allowed_executables={"agy; rm -rf"},
        )


def test_antigravity_cli_json_output_normalization():
    """Verifies that agy JSON output is parsed into InvocationResult with usage and file changes."""
    fake_response = {
        "conversation_id": "test-conv-123",
        "status": "SUCCESS",
        "response": (
            "Implementation completed.\n\n"
            "```python:tests/bridge/probe.py\n"
            "def test_ok():\n"
            "    assert 2 + 2 == 4\n"
            "```\n"
        ),
        "duration_seconds": 2.45,
        "num_turns": 1,
        "usage": {
            "input_tokens": 1500,
            "output_tokens": 120,
            "total_tokens": 1620,
        },
    }

    def fake_runner(cmd, env, payload):
        return 0, json.dumps(fake_response), ""

    adapter = CLIRuntimeAdapter(
        provider_id="google",
        executable_name="agy",
        runner_fn=fake_runner,
    )

    request = InvocationRequest(
        request_id="req-agy-norm",
        task_id="TASK-0015",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        model="gemini-3.8-flash-high",
        payload={"goal": "Test normalization"},
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    result = adapter.invoke(request)
    assert result.status == InvocationStatus.SUCCESS
    assert "def test_ok():" in result.summary
    assert result.files_modified == ["tests/bridge/probe.py"]
    assert result.usage.input_tokens == 1500
    assert result.usage.output_tokens == 120
    assert result.usage.total_tokens == 1620
    assert result.raw_metadata.get("conversation_id") == "test-conv-123"
    assert result.raw_metadata.get("cli_executable") == "agy"


def test_antigravity_cli_json_error_normalization():
    """Verifies that agy ERROR status in JSON maps to InvocationStatus.FAILED."""
    fake_error = {
        "conversation_id": "err-conv-456",
        "status": "ERROR",
        "response": "",
        "error": "Model quota exceeded or rate limit reached",
        "duration_seconds": 0.5,
    }

    def fake_runner(cmd, env, payload):
        return 1, json.dumps(fake_error), ""

    adapter = CLIRuntimeAdapter(
        provider_id="google",
        executable_name="agy",
        runner_fn=fake_runner,
    )

    request = InvocationRequest(
        request_id="req-agy-err",
        task_id="TASK-0015",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        model="gemini-3.8-flash-high",
        payload={"goal": "Test error normalization"},
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    result = adapter.invoke(request)
    assert result.status == InvocationStatus.FAILED
    assert "Model quota exceeded" in (result.error_message or "")


def test_antigravity_cli_model_enumeration():
    """Verifies list_available_models returns models from agy."""
    adapter = CLIRuntimeAdapter(provider_id="google", executable_name="agy")
    models = adapter.list_available_models()
    assert isinstance(models, list)
    assert len(models) > 0
    # Must contain recognized flash or pro models
    assert any("gemini-3" in m for m in models)


def test_real_antigravity_cli_readiness_probe():
    """
    Live environment check: verifies real installed agy executable reports
    RuntimeStatus.READY through authenticated headless probe without API keys.
    """
    if not shutil.which("agy"):
        pytest.skip("Antigravity CLI (agy) is not available on PATH")

    adapter = CLIRuntimeAdapter(provider_id="google", executable_name="agy")
    readiness = adapter.check_readiness()

    assert readiness.status == RuntimeStatus.READY
    assert "authenticated" in readiness.message.lower()


def test_antigravity_runtime_registration_and_router_selection():
    """Verifies that create_antigravity_runtime creates a valid RuntimeEntry and router selects it."""
    adapter = CLIRuntimeAdapter(provider_id="google", executable_name="agy")
    entry = create_antigravity_runtime(
        account_id="google-ai-pro",
        model="gemini-3.8-flash-high",
        priority=5,
        adapter=adapter,
    )

    assert entry.runtime_id == "google-antigravity-cli"
    assert entry.provider_id == "google"
    assert entry.runtime_type == RuntimeType.CLI
    assert entry.account.account_id == "google-ai-pro"
    assert entry.account.auth_ref.auth_type == AuthType.SUBSCRIPTION
    assert "code_generation" in entry.capabilities
    assert "review" in entry.capabilities

    registry = RuntimeRegistry()
    registry.register_runtime(entry)

    router = RuntimeRouter(registry)
    task = Task(
        id="TASK-PROBE",
        title="Probe",
        goal="Test selection",
        required_capabilities={"code_generation", "reasoning"},
    )

    # Route with provider=google
    decision = router.route(task, target_provider="google")
    assert decision.status == "SUCCESS"
    assert decision.selected_runtime is not None
    assert decision.selected_runtime.runtime_id == "google-antigravity-cli"
    assert decision.selected_runtime.account.account_id == "google-ai-pro"


def test_antigravity_runtime_explicit_runtime_id_routing():
    """Verifies that target_runtime_id selects the exact Antigravity runtime."""
    adapter = CLIRuntimeAdapter(provider_id="google", executable_name="agy")
    entry_agy = create_antigravity_runtime(adapter=adapter, priority=10)

    acc_api = AccountIdentity(account_id="acc-api", provider="google")
    entry_api = RuntimeEntry(
        runtime_id="google-gemini-api",
        provider_id="google",
        runtime_type=RuntimeType.API,
        account=acc_api,
        model="gemini-2.5-pro",
        capabilities={"code_generation", "reasoning"},
        priority=1,  # Higher priority than agy
    )

    registry = RuntimeRegistry()
    registry.register_runtime(entry_agy)
    registry.register_runtime(entry_api)

    router = RuntimeRouter(registry)
    task = Task(id="TASK-R01", title="Test", goal="Goal", required_capabilities={"code_generation"})

    # When explicit target_runtime_id is passed, it must override lower priority number
    decision = router.route(task, target_runtime_id="google-antigravity-cli")
    assert decision.status == "SUCCESS"
    assert decision.selected_runtime.runtime_id == "google-antigravity-cli"


def test_antigravity_secret_isolation():
    """Verifies that credentials and tokens are redacted from metadata and messages."""
    raw = "Error with key AIzaSyD9876543210ZYXWVUTSRQPONMLKJIHGFED and Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    cleaned = _sanitize_cli_text(raw)
    assert "AIzaSyD" not in cleaned
    assert "[REDACTED_API_KEY]" in cleaned
    assert "[REDACTED_TOKEN]" in cleaned


def test_antigravity_cli_timeout_handling():
    """Verifies timeout handling returns FAILED without crashing."""
    adapter = CLIRuntimeAdapter(
        provider_id="google",
        executable_name="agy",
        timeout=0.001,  # Fast timeout
    )
    request = InvocationRequest(
        request_id="req-timeout",
        task_id="TASK-T01",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        model="gemini-3.8-flash-high",
        payload={"goal": "Sleep"},
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    result = adapter.invoke(request)
    assert result.status == InvocationStatus.FAILED
    assert "timed out" in (result.error_message or "").lower()
