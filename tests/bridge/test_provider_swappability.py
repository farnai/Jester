"""
Acceptance Criteria Verification Test: Provider Swappability.

Proves that given the EXACT same task:
1. It executes through Agent A / Provider A
2. The assignment is swapped to Agent B / Provider B
3. It executes through Agent B / Provider B
Without modifying task schema, task lifecycle, state machine, or core orchestration code.
"""
import pytest

from jester_bridge.agent import AgentProfile
from jester_bridge.config import BridgeConfig
from jester_bridge.contracts import InvocationStatus
from jester_bridge.core import BridgeCore
from jester_bridge.protocol import Task
from jester_bridge.roles import Role
from jester_bridge.testing import MockProviderA, MockProviderB


def test_provider_swappability():
    # 1. Setup two completely different providers implementing the same AgentProvider contract
    provider_a = MockProviderA(default_summary="Executed via Provider A engine")
    provider_b = MockProviderB(default_summary="Executed via Provider B engine")

    # 2. Configure two distinct agents bound to different providers
    agent_a = AgentProfile(
        id="agent-alpha",
        role=Role.EXECUTOR.value,
        provider=provider_a.provider_id,
        model="vendor-a-large",
        capabilities={"repository_read", "repository_write", "command_execution", "testing"},
    )
    agent_b = AgentProfile(
        id="agent-beta",
        role=Role.EXECUTOR.value,
        provider=provider_b.provider_id,
        model="vendor-b-pro",
        capabilities={"repository_read", "repository_write", "command_execution", "testing"},
    )

    # 3. Create a single invariant Task under Task Protocol v2
    task = Task(
        id="TASK-SWAP-001",
        title="Cross-Provider Feature Implementation",
        type="feature",
        status="inbox",
        priority="high",
        role=Role.EXECUTOR.value,
        required_capabilities={"repository_read", "repository_write", "testing"},
        goal="Implement feature deterministically regardless of provider",
        scope=["backend/app/core/"],
        constraints=["Do not modify migrations"],
        acceptance_criteria=["Unit tests pass"],
        verification=["pytest tests/core"],
    )

    # Verify task attributes before execution
    original_task_dict = task.to_dict()

    # --- EXECUTION RUN 1: Execute with Agent A / Provider A ---
    config_a = BridgeConfig(
        role_bindings={"executor": "agent-alpha"},
        agents={"agent-alpha": agent_a, "agent-beta": agent_b},
    )
    core_a = BridgeCore(
        config=config_a,
        providers={provider_a.provider_id: provider_a, provider_b.provider_id: provider_b},
    )

    result_a = core_a.dispatch(task)

    assert result_a.status == InvocationStatus.SUCCESS
    assert result_a.agent_id == "agent-alpha"
    assert result_a.provider == "mock-provider-a"
    assert result_a.model == "vendor-a-large"
    assert "Provider A" in result_a.summary
    assert len(provider_a.invocations) == 1
    assert len(provider_b.invocations) == 0

    # --- SWAP AGENT / PROVIDER ASSIGNMENT ---
    # The task definition and core engine remain 100% UNCHANGED.
    # Only the configuration role binding (or task.assigned_agent) is updated.
    config_b = BridgeConfig(
        role_bindings={"executor": "agent-beta"},
        agents={"agent-alpha": agent_a, "agent-beta": agent_b},
    )
    core_b = BridgeCore(
        config=config_b,
        providers={provider_a.provider_id: provider_a, provider_b.provider_id: provider_b},
    )

    # --- EXECUTION RUN 2: Execute with Agent B / Provider B ---
    result_b = core_b.dispatch(task)

    assert result_b.status == InvocationStatus.SUCCESS
    assert result_b.agent_id == "agent-beta"
    assert result_b.provider == "mock-provider-b"
    assert result_b.model == "vendor-b-pro"
    assert "Provider B" in result_b.summary
    assert len(provider_a.invocations) == 1
    assert len(provider_b.invocations) == 1  # Provider B received the invocation

    # --- INVARIANCE ASSERTION ---
    # Assert that the task payload received by both providers was byte-for-byte identical in structure
    payload_a = provider_a.invocations[0].payload
    payload_b = provider_b.invocations[0].payload
    assert payload_a == payload_b
    assert task.to_dict() == original_task_dict


def test_provider_swappability_mock_to_openai():
    """Proves swappability between MockProvider and real OpenAIProvider contract on the identical task."""
    from unittest.mock import MagicMock
    from jester_bridge.openai_provider import OpenAIProvider

    mock_provider = MockProviderA(default_summary="Plan created by Mock Provider")

    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Plan created by OpenAI ChatGPT Provider"
    mock_choice.finish_reason = "stop"
    mock_response.choices = [mock_choice]
    mock_response.model = "gpt-4o"
    mock_response.id = "mock-openai-id"
    mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=10, total_tokens=20)

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    openai_provider = OpenAIProvider(api_key="mock", client=mock_client)

    task = Task(
        id="TASK-SWAP-ARCH",
        title="Cross-Provider Architecture Task",
        role=Role.ARCHITECT.value,
        required_capabilities={"planning", "reasoning"},
        goal="Produce architecture decomposition",
    )

    # 1. Execute with Mock Provider
    config_mock = BridgeConfig(
        role_bindings={"architect": "mock-arch"},
        agents={
            "mock-arch": AgentProfile(id="mock-arch", role="architect", provider="mock-provider-a", capabilities={"planning", "reasoning"})
        }
    )
    core_mock = BridgeCore(config=config_mock, providers={"mock-provider-a": mock_provider, "openai": openai_provider})
    res_mock = core_mock.dispatch(task)
    assert res_mock.status == InvocationStatus.SUCCESS
    assert "Mock Provider" in res_mock.summary

    # 2. Swap to OpenAI Provider (Task remains 100% untouched)
    config_openai = BridgeConfig(
        role_bindings={"architect": "chatgpt-lead"},
        agents={
            "chatgpt-lead": AgentProfile(id="chatgpt-lead", role="architect", provider="openai", model="gpt-4o", capabilities={"planning", "reasoning"})
        }
    )
    core_openai = BridgeCore(config=config_openai, providers={"mock-provider-a": mock_provider, "openai": openai_provider})
    res_openai = core_openai.dispatch(task)
    assert res_openai.status == InvocationStatus.SUCCESS
    assert "OpenAI ChatGPT Provider" in res_openai.summary
    assert res_openai.provider == "openai"


def test_provider_swappability_openai_to_google():
    """
    Acceptance Criteria Test: Proves that the EXACT SAME task can be processed through
    OpenAIProvider (Agent A) and then swapped to GoogleProvider (Agent B) without modifying
    Task Protocol, BridgeCore, lifecycle, or governance.
    """
    from unittest.mock import MagicMock
    import httpx
    from jester_bridge.openai_provider import OpenAIProvider
    from jester_bridge.google_provider import GoogleProvider

    # Setup mock OpenAI
    mock_openai_resp = MagicMock()
    mock_openai_resp.choices = [MagicMock(message=MagicMock(content="OpenAI generated execution response."))]
    mock_openai_resp.model = "gpt-4o"
    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.return_value = mock_openai_resp
    openai_provider = OpenAIProvider(api_key="mock-openai", client=mock_openai_client)

    # Setup mock Google
    mock_google_http = MagicMock(spec=httpx.Response)
    mock_google_http.status_code = 200
    mock_google_http.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Google Gemini generated execution response."}]}}],
        "usageMetadata": {"promptTokenCount": 20, "candidatesTokenCount": 20, "totalTokenCount": 40},
    }
    mock_google_client = MagicMock(spec=httpx.Client)
    mock_google_client.post.return_value = mock_google_http
    google_provider = GoogleProvider(api_key="mock-google", client=mock_google_client)

    # A single, identical task definition
    task = Task(
        id="TASK-SWAP-DUAL",
        title="Dual-Provider Feature Implementation",
        type="feature",
        status="active",
        priority="high",
        role=Role.EXECUTOR.value,
        required_capabilities={"code_generation", "reasoning"},
        goal="Implement feature deterministically",
        scope=["backend/app/core/"],
        constraints=["Do not modify migrations"],
        acceptance_criteria=["Clean deterministic output"],
        verification=["pytest tests/core"],
    )
    initial_task_dump = task.to_dict()

    # --- RUN 1: Dispatch to Agent A (OpenAI) ---
    config_a = BridgeConfig(
        role_bindings={"executor": "agent-openai"},
        agents={
            "agent-openai": AgentProfile(id="agent-openai", role="executor", provider="openai", capabilities={"code_generation", "reasoning"}),
            "agent-gemini": AgentProfile(id="agent-gemini", role="executor", provider="google", capabilities={"code_generation", "reasoning"}),
        },
    )
    core_a = BridgeCore(config=config_a, providers={"openai": openai_provider, "google": google_provider})
    result_a = core_a.dispatch(task)
    assert result_a.status == InvocationStatus.SUCCESS
    assert result_a.provider == "openai"
    assert "OpenAI generated" in result_a.summary

    # --- RUN 2: Swap assignment to Agent B (Google Gemini) ---
    # Task schema, lifecycle, BridgeCore, and governance remain 100% UNCHANGED.
    config_b = BridgeConfig(
        role_bindings={"executor": "agent-gemini"},
        agents={
            "agent-openai": AgentProfile(id="agent-openai", role="executor", provider="openai", capabilities={"code_generation", "reasoning"}),
            "agent-gemini": AgentProfile(id="agent-gemini", role="executor", provider="google", capabilities={"code_generation", "reasoning"}),
        },
    )
    core_b = BridgeCore(config=config_b, providers={"openai": openai_provider, "google": google_provider})
    result_b = core_b.dispatch(task)
    assert result_b.status == InvocationStatus.SUCCESS
    assert result_b.provider == "google"
    assert "Google Gemini generated" in result_b.summary

    # --- INVARIANCE VERIFICATION ---
    assert task.to_dict() == initial_task_dump
