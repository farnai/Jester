"""
Unit and Integration Tests for GoogleProvider Adapter.

Verifies:
- GoogleProvider construction and configuration
- Missing API key error normalization
- Successful generateContent request translation and normalization
- API error, timeout, and malformed response normalization
- Model override per invocation request
- Role independence (executor vs architect vs reviewer)
- BridgeCore integration with GoogleProvider
- Zero leakage of HTTP/Google SDK objects into InvocationResult
- Multi-provider coordination (OpenAIProvider alongside GoogleProvider)
"""
from unittest.mock import MagicMock
import pytest
import httpx

from jester_bridge.contracts import (
    InvocationRequest,
    InvocationResult,
    InvocationStatus,
)
from jester_bridge.core import BridgeCore
from jester_bridge.config import BridgeConfig
from jester_bridge.agent import AgentProfile
from jester_bridge.protocol import Task
from jester_bridge.roles import Role
from jester_bridge.google_provider import GoogleProvider
from jester_bridge.openai_provider import OpenAIProvider


def _create_mock_gemini_json_response(
    text="def execute_feature():\n    return True\n\nImplementation complete.",
    prompt_tokens=110,
    candidates_tokens=42,
    total_tokens=152,
    finish_reason="STOP",
):
    """Helper returning a standard Google Gemini generateContent response dictionary."""
    return {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": text}],
                    "role": "model",
                },
                "finishReason": finish_reason,
                "index": 0,
            }
        ],
        "usageMetadata": {
            "promptTokenCount": prompt_tokens,
            "candidatesTokenCount": candidates_tokens,
            "totalTokenCount": total_tokens,
        },
    }


def test_google_provider_construction_and_properties():
    provider = GoogleProvider(
        api_key="mock-gemini-key",
        default_model="gemini-2.5-pro",
        timeout=45.0,
        supported_capabilities={"planning", "reasoning", "code_generation"},
    )
    assert provider.provider_id == "google"
    assert provider.default_model == "gemini-2.5-pro"
    assert "code_generation" in provider.get_supported_capabilities()
    assert "command_execution" not in provider.get_supported_capabilities()
    assert provider.health_check() is True


def test_google_provider_health_check_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    provider = GoogleProvider(api_key=None)
    assert provider.health_check() is False


def test_google_provider_missing_key_invocation(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    provider = GoogleProvider(api_key=None)

    req = InvocationRequest(
        request_id="req-g-1",
        task_id="TASK-0004",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        model="gemini-2.5-pro",
        created_at="2026-09-18T00:00:00Z",
    )
    result = provider.invoke(req)
    assert result.status == InvocationStatus.FAILED
    assert "GEMINI_API_KEY" in (result.error_message or "")


def test_google_provider_successful_invocation_and_normalization():
    mock_data = _create_mock_gemini_json_response(
        text="def compute_synastry():\n    return {'score': 88}\n\nCompleted successfully."
    )
    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_http_response

    provider = GoogleProvider(api_key="mock-key", client=mock_client)

    req = InvocationRequest(
        request_id="req-gemini-success",
        task_id="TASK-0004",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        model="gemini-2.5-flash",
        required_capabilities={"code_generation", "reasoning"},
        payload={
            "title": "Compute Synastry Score",
            "goal": "Implement deterministic algorithm",
            "scope": ["backend/app/compatibility/"],
            "constraints": ["Do not modify weights"],
            "acceptance_criteria": ["Deterministic output"],
            "verification": ["pytest tests/compatibility"],
        },
        created_at="2026-09-18T00:00:00Z",
    )

    result = provider.invoke(req)

    assert result.status == InvocationStatus.SUCCESS
    assert result.task_id == "TASK-0004"
    assert result.agent_id == "gemini-dev"
    assert result.provider == "google"
    assert result.model == "gemini-2.5-flash"
    assert "compute_synastry" in result.summary
    assert result.error_message is None

    # Check raw metadata extraction and assert zero HTTP/SDK object leakage
    assert result.raw_metadata["prompt_tokens"] == 110
    assert result.raw_metadata["completion_tokens"] == 42
    assert result.raw_metadata["total_tokens"] == 152
    assert result.raw_metadata["finish_reason"] == "STOP"
    assert not hasattr(result, "candidates")
    assert isinstance(result.raw_metadata, dict)

    # Verify HTTP request payload sent to Gemini API
    mock_client.post.assert_called_once()
    call_args, call_kwargs = mock_client.post.call_args
    assert "models/gemini-2.5-flash:generateContent" in call_args[0]
    json_body = call_kwargs["json"]
    assert "system_instruction" in json_body
    assert "software engineer acting as an Executor" in json_body["system_instruction"]["parts"][0]["text"]
    user_text = json_body["contents"][0]["parts"][0]["text"]
    assert "TASK ID: TASK-0004" in user_text
    assert "AUTHORIZED SCOPE:" in user_text


def test_google_provider_role_independence():
    mock_data = _create_mock_gemini_json_response(text="Architectural decomposition produced.")
    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_http_response

    provider = GoogleProvider(api_key="mock", client=mock_client)

    # Invoke as architect through GoogleProvider
    req_arch = InvocationRequest(
        request_id="req-arch-g",
        task_id="TASK-0005",
        role="architect",
        agent_id="gemini-architect",
        provider="google",
        model="gemini-2.5-pro",
        created_at="2026-09-18T00:00:00Z",
    )
    result = provider.invoke(req_arch)
    assert result.status == InvocationStatus.SUCCESS

    call_kwargs = mock_client.post.call_args[1]
    system_text = call_kwargs["json"]["system_instruction"]["parts"][0]["text"]
    assert "software architect" in system_text


def test_google_provider_auth_error_normalization():
    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 403
    mock_http_response.text = '{"error": {"code": 403, "message": "API key not valid", "status": "PERMISSION_DENIED"}}'

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_http_response

    provider = GoogleProvider(api_key="mock", client=mock_client)

    req = InvocationRequest(
        request_id="req-auth-fail",
        task_id="TASK-0004",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        created_at="2026-09-18T00:00:00Z",
    )
    result = provider.invoke(req)

    assert result.status == InvocationStatus.FAILED
    assert "authentication failed" in result.summary
    assert "HTTP 403" in (result.error_message or "")


def test_google_provider_rate_limit_error_normalization():
    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 429
    mock_http_response.text = '{"error": {"code": 429, "message": "Resource exhausted", "status": "RESOURCE_EXHAUSTED"}}'

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_http_response

    provider = GoogleProvider(api_key="mock", client=mock_client)

    req = InvocationRequest(
        request_id="req-rate-fail",
        task_id="TASK-0004",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        created_at="2026-09-18T00:00:00Z",
    )
    result = provider.invoke(req)

    assert result.status == InvocationStatus.FAILED
    assert "rate limit exceeded" in result.summary


def test_google_provider_timeout_error_normalization():
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.side_effect = httpx.TimeoutException("Read timed out after 60s")

    provider = GoogleProvider(api_key="mock", client=mock_client)

    req = InvocationRequest(
        request_id="req-timeout-g",
        task_id="TASK-0004",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        created_at="2026-09-18T00:00:00Z",
    )
    result = provider.invoke(req)

    assert result.status == InvocationStatus.FAILED
    assert "TimeoutException" in (result.error_message or "")


def test_google_provider_malformed_empty_candidates():
    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = {"candidates": []}

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_http_response

    provider = GoogleProvider(api_key="mock", client=mock_client)

    req = InvocationRequest(
        request_id="req-empty-c",
        task_id="TASK-0004",
        role="executor",
        agent_id="gemini-dev",
        provider="google",
        created_at="2026-09-18T00:00:00Z",
    )
    result = provider.invoke(req)

    assert result.status == InvocationStatus.FAILED
    assert "no candidates" in result.summary


def test_bridge_core_google_integration():
    """Validates that BridgeCore orchestrates GoogleProvider cleanly."""
    mock_data = _create_mock_gemini_json_response(text="Task implemented by Gemini.")
    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_http_response

    google_provider = GoogleProvider(
        api_key="mock",
        client=mock_client,
        supported_capabilities={"planning", "reasoning", "code_generation", "repository_read"},
    )

    config = BridgeConfig(
        role_bindings={"executor": "gemini-dev"},
        agents={
            "gemini-dev": AgentProfile(
                id="gemini-dev",
                role="executor",
                provider="google",
                model="gemini-2.5-pro",
                capabilities={"planning", "reasoning", "code_generation", "repository_read"},
            )
        },
    )

    core = BridgeCore(config=config, providers={"google": google_provider})

    task = Task(
        id="TASK-EXEC-01",
        title="Execute Function",
        role=Role.EXECUTOR.value,
        required_capabilities={"code_generation", "reasoning"},
        goal="Generate implementation",
    )

    result = core.dispatch(task)
    assert result.status == InvocationStatus.SUCCESS
    assert result.task_id == "TASK-EXEC-01"
    assert result.agent_id == "gemini-dev"
    assert result.provider == "google"
    assert "Task implemented by Gemini" in result.summary


def test_multi_provider_pipeline_openai_and_google():
    """
    Validates complete multi-provider coordination:
    Architect (OpenAI / ChatGPT) -> Executor (Google / Gemini) -> Reviewer (OpenAI / ChatGPT)
    under the identical BridgeCore orchestration core.
    """
    # 1. Setup mock OpenAI client
    mock_openai_resp = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Architecture specification generated."
    mock_choice.finish_reason = "stop"
    mock_openai_resp.choices = [mock_choice]
    mock_openai_resp.model = "o3-mini"
    mock_openai_resp.id = "openai-arch-1"
    mock_openai_resp.usage = MagicMock(prompt_tokens=50, completion_tokens=20, total_tokens=70)
    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.return_value = mock_openai_resp

    openai_provider = OpenAIProvider(api_key="mock-openai", client=mock_openai_client)

    # 2. Setup mock Google client
    mock_google_data = _create_mock_gemini_json_response(text="Code implementation generated by Gemini.")
    mock_google_http = MagicMock(spec=httpx.Response)
    mock_google_http.status_code = 200
    mock_google_http.json.return_value = mock_google_data
    mock_google_client = MagicMock(spec=httpx.Client)
    mock_google_client.post.return_value = mock_google_http

    google_provider = GoogleProvider(
        api_key="mock-google",
        client=mock_google_client,
        supported_capabilities={"planning", "reasoning", "code_generation", "repository_read"},
    )

    # 3. Configure multi-agent topology in BridgeConfig
    config = BridgeConfig(
        role_bindings={
            "architect": "chatgpt-lead",
            "executor": "gemini-dev",
            "reviewer": "chatgpt-critic",
        },
        agents={
            "chatgpt-lead": AgentProfile(
                id="chatgpt-lead",
                role="architect",
                provider="openai",
                model="o3-mini",
                capabilities={"planning", "reasoning", "repository_read"},
            ),
            "gemini-dev": AgentProfile(
                id="gemini-dev",
                role="executor",
                provider="google",
                model="gemini-2.5-pro",
                capabilities={"planning", "reasoning", "code_generation", "repository_read"},
            ),
            "chatgpt-critic": AgentProfile(
                id="chatgpt-critic",
                role="reviewer",
                provider="openai",
                model="gpt-4o",
                capabilities={"reasoning", "repository_read", "review"},
            ),
        },
    )

    core = BridgeCore(
        config=config,
        providers={"openai": openai_provider, "google": google_provider},
    )

    # Phase A: Architect dispatches through OpenAIProvider
    task_arch = Task(
        id="TASK-MULTI-01",
        title="Multi-Provider Feature",
        role=Role.ARCHITECT.value,
        required_capabilities={"planning", "reasoning"},
        goal="Produce architecture plan",
    )
    result_arch = core.dispatch(task_arch)
    assert result_arch.status == InvocationStatus.SUCCESS
    assert result_arch.provider == "openai"
    assert result_arch.agent_id == "chatgpt-lead"

    # Phase B: Executor dispatches through GoogleProvider
    task_exec = Task(
        id="TASK-MULTI-01",
        title="Multi-Provider Feature",
        role=Role.EXECUTOR.value,
        required_capabilities={"code_generation", "reasoning"},
        goal="Execute code modification",
    )
    result_exec = core.dispatch(task_exec)
    assert result_exec.status == InvocationStatus.SUCCESS
    assert result_exec.provider == "google"
    assert result_exec.agent_id == "gemini-dev"

    # Phase C: Reviewer dispatches through OpenAIProvider
    mock_choice.message.content = "Review verdict: PASS."
    task_rev = Task(
        id="TASK-MULTI-01",
        title="Multi-Provider Feature",
        role=Role.REVIEWER.value,
        required_capabilities={"reasoning", "review"},
        goal="Review code changes",
    )
    result_rev = core.dispatch(task_rev)
    assert result_rev.status == InvocationStatus.SUCCESS
    assert result_rev.provider == "openai"
    assert result_rev.agent_id == "chatgpt-critic"


def test_google_provider_placeholder_key_rejected():
    provider = GoogleProvider(api_key="your_gemini_api_key_here")
    assert provider.health_check() is False
