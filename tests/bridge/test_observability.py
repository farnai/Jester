"""
Unit and integration tests for Token/Context Observability (Phase 2D).

Verifies:
1. Provider-neutral UsageMetrics contract (input, output, total).
2. OpenAI provider token usage capture.
3. Google Gemini provider token usage capture.
4. OrchestrationSession aggregation across stages (architect, executor, reviewer).
5. Provider neutrality: zero provider-specific branching in orchestration or workflow.
"""
from typing import Dict, Any
from unittest.mock import MagicMock
import inspect
import httpx
import pytest

from jester_bridge.contracts import UsageMetrics, InvocationRequest, InvocationResult, InvocationStatus
from jester_bridge.openai_provider import OpenAIProvider
from jester_bridge.google_provider import GoogleProvider
from jester_bridge.orchestration import (
    BridgeOrchestrator,
    OrchestrationSession,
    OrchestrationStage,
    ArchitectResult,
    ExecutorResult,
    ReviewResult,
    ReviewVerdict,
)
from jester_bridge.protocol import Task
from jester_bridge.testing import MockProviderA, MockProviderB
import jester_bridge.orchestration as orchestration_mod
import jester_bridge.workflow as workflow_mod
import jester_bridge.core as core_mod


def _create_test_request(role: str = "architect", provider: str = "openai", model: str = "test-model") -> InvocationRequest:
    return InvocationRequest(
        request_id="req-obs-001",
        task_id="TASK-OBS",
        role=role,
        agent_id=f"{provider}-agent",
        provider=provider,
        model=model,
        payload={"prompt": "test observability prompt"},
        created_at="2026-09-18T00:00:00Z",
    )


def test_usage_metrics_addition():
    u1 = UsageMetrics(input_tokens=100, output_tokens=50, total_tokens=150)
    u2 = UsageMetrics(input_tokens=200, output_tokens=75, total_tokens=275)

    u3 = u1.add(u2)
    assert u3.input_tokens == 300
    assert u3.output_tokens == 125
    assert u3.total_tokens == 425

    # Adding None should return identical copy
    u4 = u1.add(None)
    assert u4.input_tokens == 100
    assert u4.output_tokens == 50
    assert u4.total_tokens == 150

    # Partial / None fields
    u5 = UsageMetrics(input_tokens=50, output_tokens=None, total_tokens=50)
    u6 = u1.add(u5)
    assert u6.input_tokens == 150
    assert u6.output_tokens == 50
    assert u6.total_tokens == 200


def test_openai_provider_usage_capture():
    provider = OpenAIProvider(api_key="test-key")

    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Architectural blueprint response."
    mock_choice.finish_reason = "stop"

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 150
    mock_usage.completion_tokens = 45
    mock_usage.total_tokens = 195

    mock_response = MagicMock()
    mock_response.id = "chatcmpl-test-01"
    mock_response.choices = [mock_choice]
    mock_response.usage = mock_usage
    mock_response.model = "gpt-4o"
    mock_client.chat.completions.create.return_value = mock_response

    provider._client = mock_client

    req = _create_test_request(role="architect", provider="openai", model="gpt-4o")
    result = provider.invoke(req)

    assert result.status == InvocationStatus.SUCCESS
    assert result.usage is not None
    assert result.usage.input_tokens == 150
    assert result.usage.output_tokens == 45
    assert result.usage.total_tokens == 195


def test_openai_provider_missing_usage():
    provider = OpenAIProvider(api_key="test-key")

    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Response without usage."
    mock_choice.finish_reason = "stop"

    mock_response = MagicMock()
    mock_response.id = "chatcmpl-test-02"
    mock_response.choices = [mock_choice]
    mock_response.usage = None
    mock_response.model = "gpt-4o"
    mock_client.chat.completions.create.return_value = mock_response

    provider._client = mock_client

    req = _create_test_request(role="architect", provider="openai", model="gpt-4o")
    result = provider.invoke(req)

    assert result.status == InvocationStatus.SUCCESS
    assert result.usage is None


def test_google_provider_usage_capture():
    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = {
        "candidates": [
            {
                "content": {"parts": [{"text": "Gemini code response"}]},
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 220,
            "candidatesTokenCount": 95,
            "totalTokenCount": 315,
        },
    }

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_http_response

    provider = GoogleProvider(api_key="test-key", client=mock_client)

    req = _create_test_request(role="executor", provider="google", model="gemini-1.5-pro")
    result = provider.invoke(req)

    assert result.status == InvocationStatus.SUCCESS
    assert result.usage is not None
    assert result.usage.input_tokens == 220
    assert result.usage.output_tokens == 95
    assert result.usage.total_tokens == 315


def test_google_provider_missing_usage():
    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = {
        "candidates": [
            {
                "content": {"parts": [{"text": "Gemini response without usage"}]},
                "finishReason": "STOP",
            }
        ],
    }

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_http_response

    provider = GoogleProvider(api_key="test-key", client=mock_client)

    req = _create_test_request(role="executor", provider="google", model="gemini-1.5-pro")
    result = provider.invoke(req)

    assert result.status == InvocationStatus.SUCCESS
    assert result.usage is None


def test_session_usage_aggregation():
    task = Task(id="TASK-TEST", title="Test Task", description="Testing token aggregation")
    session = OrchestrationSession(session_id="sess-001", task=task)

    # 1. Add Architect Result
    arch_usage = UsageMetrics(input_tokens=100, output_tokens=50, total_tokens=150)
    session.architect_result = ArchitectResult(
        task=task,
        summary="Arch summary",
        raw_result=InvocationResult(
            request_id="req-1",
            task_id="TASK-TEST",
            status=InvocationStatus.SUCCESS,
            agent_id="agent-architect",
            role="architect",
            provider="openai",
            model="gpt-4o",
            summary="Arch summary",
            usage=arch_usage,
            completed_at="2026-09-18T00:00:00Z",
        ),
    )

    # 2. Add Executor Result
    exec_usage = UsageMetrics(input_tokens=300, output_tokens=150, total_tokens=450)
    session.executor_result = ExecutorResult(
        task_id="TASK-TEST",
        status=InvocationStatus.SUCCESS,
        summary="Code summary",
        raw_result=InvocationResult(
            request_id="req-2",
            task_id="TASK-TEST",
            status=InvocationStatus.SUCCESS,
            agent_id="agent-executor",
            role="executor",
            provider="google",
            model="gemini-1.5-pro",
            summary="Code summary",
            usage=exec_usage,
            completed_at="2026-09-18T00:01:00Z",
        ),
    )

    # 3. Add Reviewer Result
    rev_usage = UsageMetrics(input_tokens=200, output_tokens=60, total_tokens=260)
    session.review_result = ReviewResult(
        task_id="TASK-TEST",
        verdict=ReviewVerdict.PASS,
        summary="Review summary",
        raw_result=InvocationResult(
            request_id="req-3",
            task_id="TASK-TEST",
            status=InvocationStatus.SUCCESS,
            agent_id="agent-reviewer",
            role="reviewer",
            provider="openai",
            model="gpt-4o",
            summary="Review summary",
            usage=rev_usage,
            completed_at="2026-09-18T00:02:00Z",
        ),
    )

    total = session.get_total_usage()
    assert total.input_tokens == 600
    assert total.output_tokens == 260
    assert total.total_tokens == 860

    stage_breakdown = session.get_stage_usage()
    assert "architect" in stage_breakdown
    assert stage_breakdown["architect"]["role"] == "architect"
    assert stage_breakdown["architect"]["provider"] == "openai"
    assert stage_breakdown["architect"]["usage"].total_tokens == 150

    assert "executor" in stage_breakdown
    assert stage_breakdown["executor"]["role"] == "executor"
    assert stage_breakdown["executor"]["provider"] == "google"
    assert stage_breakdown["executor"]["usage"].total_tokens == 450

    assert "reviewer" in stage_breakdown
    assert stage_breakdown["reviewer"]["role"] == "reviewer"
    assert stage_breakdown["reviewer"]["provider"] == "openai"
    assert stage_breakdown["reviewer"]["usage"].total_tokens == 260


def test_zero_provider_branching_in_orchestration():
    """
    Guarantees that orchestration, workflow, and core modules contain
    NO provider-specific branching (e.g. `if provider == 'openai'` or `if provider == 'google'`)
    to interpret or calculate usage metrics.
    """
    for mod in [orchestration_mod, workflow_mod, core_mod]:
        source = inspect.getsource(mod)
        assert 'if provider == "openai"' not in source
        assert "if provider == 'openai'" not in source
        assert 'if provider == "google"' not in source
        assert "if provider == 'google'" not in source
        assert "promptTokenCount" not in source
        assert "prompt_tokens" not in source
