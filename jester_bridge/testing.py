"""
Test utilities and Mock Providers for the JESTER Provider-Agnostic AI Bridge.

Used exclusively in tests to prove swappability and test error handling without
requiring external network calls or vendor SDKs.
"""
from datetime import datetime, timezone
from typing import List, Optional, Set
from .contracts import InvocationRequest, InvocationResult, InvocationStatus, UsageMetrics
from .provider import AgentProvider


class BaseMockProvider(AgentProvider):
    """Base test mock provider recording invocation history."""

    def __init__(
        self,
        provider_id: str,
        supported_capabilities: Optional[Set[str]] = None,
        default_status: InvocationStatus = InvocationStatus.SUCCESS,
        default_summary: str = "Execution succeeded.",
        is_healthy: bool = True,
        default_usage: Optional[UsageMetrics] = None,
    ):
        self._provider_id = provider_id
        self._capabilities = supported_capabilities or {
            "planning",
            "reasoning",
            "repository_read",
            "repository_write",
            "command_execution",
            "testing",
            "review",
            "local_runtime",
            "code_generation",
        }
        self.default_status = default_status
        self.default_summary = default_summary
        self.is_healthy = is_healthy
        self.default_usage = default_usage if default_usage is not None else UsageMetrics(input_tokens=100, output_tokens=50, total_tokens=150)
        self.invocations: List[InvocationRequest] = []

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def health_check(self) -> bool:
        return self.is_healthy

    def get_supported_capabilities(self) -> Set[str]:
        return set(self._capabilities)

    def invoke(self, request: InvocationRequest) -> InvocationResult:
        self.invocations.append(request)
        return InvocationResult(
            request_id=request.request_id,
            task_id=request.task_id,
            status=self.default_status,
            agent_id=request.agent_id,
            provider=self._provider_id,
            model=request.model,
            summary=f"[{self._provider_id}] {self.default_summary}",
            files_modified=["example/modified.py"] if self.default_status == InvocationStatus.SUCCESS else [],
            reports_generated=["reports/TASK_report.md"] if self.default_status == InvocationStatus.SUCCESS else [],
            error_message=None if self.default_status == InvocationStatus.SUCCESS else "Mock execution failed",
            usage=self.default_usage,
            completed_at=datetime.now(timezone.utc).isoformat(),
        )


class MockProviderA(BaseMockProvider):
    """Concrete mock provider A."""
    def __init__(self, provider_id: str = "mock-provider-a", **kwargs):
        super().__init__(provider_id=provider_id, **kwargs)


class MockProviderB(BaseMockProvider):
    """Concrete mock provider B."""
    def __init__(self, provider_id: str = "mock-provider-b", **kwargs):
        super().__init__(provider_id=provider_id, **kwargs)
