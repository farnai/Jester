"""
Unit and Integration Tests for BridgeCore Orchestrator.
"""
from pathlib import Path
import pytest

from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig, load_bridge_config
from jester_bridge.contracts import InvocationStatus
from jester_bridge.core import (
    BridgeCore,
    CapabilityMismatchError,
    ConfigurationError,
)
from jester_bridge.protocol import Task
from jester_bridge.roles import Role
from jester_bridge.testing import MockProviderA


def test_load_real_agents_config():
    config_path = Path(".jester/config/agents.json")
    assert config_path.exists(), "agents.json must exist in .jester/config/"

    config = load_bridge_config(config_path)
    assert config.version == "2.0"
    assert config.role_bindings["executor"] == "gemini-dev"
    assert config.role_bindings["architect"] == "chatgpt-lead"

    gemini_dev = config.get_agent("gemini-dev")
    assert gemini_dev is not None
    assert gemini_dev.provider == "google"
    assert "command_execution" in gemini_dev.capabilities


def test_bridge_core_dispatch_successful():
    config = BridgeConfig(
        role_bindings={"executor": "agent-1"},
        agents={
            "agent-1": AgentProfile(
                id="agent-1",
                role="executor",
                provider="mock-provider-a",
                model="mock-v1",
                capabilities={"repository_read", "repository_write", "command_execution", "testing"},
            )
        },
    )
    provider_a = MockProviderA()
    core = BridgeCore(config=config, providers={"mock-provider-a": provider_a})

    task = Task(
        id="TASK-TEST-01",
        title="Test Task",
        role=Role.EXECUTOR.value,
        required_capabilities={"repository_read", "testing"},
        goal="Validate core dispatch",
    )

    result = core.dispatch(task)
    assert result.status == InvocationStatus.SUCCESS
    assert result.task_id == "TASK-TEST-01"
    assert result.agent_id == "agent-1"
    assert result.provider == "mock-provider-a"
    assert len(provider_a.invocations) == 1
    assert provider_a.invocations[0].task_id == "TASK-TEST-01"


def test_bridge_core_capability_mismatch_rejection():
    config = BridgeConfig(
        role_bindings={"executor": "weak-agent"},
        agents={
            "weak-agent": AgentProfile(
                id="weak-agent",
                role="executor",
                provider="mock-provider-a",
                capabilities={"repository_read"},  # Missing command_execution and testing
            )
        },
    )
    provider_a = MockProviderA()
    core = BridgeCore(config=config, providers={"mock-provider-a": provider_a})

    task = Task(
        id="TASK-TEST-02",
        title="High Capability Task",
        role=Role.EXECUTOR.value,
        required_capabilities={"repository_read", "command_execution", "testing"},
    )

    with pytest.raises(CapabilityMismatchError) as exc_info:
        core.dispatch(task)

    assert "command_execution" in exc_info.value.missing_capabilities or "testing" in exc_info.value.missing_capabilities
    assert len(provider_a.invocations) == 0  # Rejection happened BEFORE dispatch!


def test_bridge_core_unregistered_provider_error():
    config = BridgeConfig(
        role_bindings={"executor": "orphan-agent"},
        agents={
            "orphan-agent": AgentProfile(
                id="orphan-agent",
                role="executor",
                provider="non-existent-provider",
                capabilities={"repository_read"},
            )
        },
    )
    core = BridgeCore(config=config, providers={})

    task = Task(id="TASK-TEST-03", title="Orphan Task", role="executor")
    with pytest.raises(ConfigurationError, match="Provider 'non-existent-provider'"):
        core.dispatch(task)
