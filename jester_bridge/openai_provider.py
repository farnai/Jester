"""
OpenAI Provider Adapter for the JESTER Provider-Agnostic AI Bridge.

Implements the AgentProvider interface using the official OpenAI Python SDK.
Translates InvocationRequest into OpenAI chat completion requests and normalizes
OpenAI responses into vendor-neutral InvocationResult objects.
"""
from datetime import datetime, timezone
import os
import re
from typing import Any, Dict, List, Optional, Set

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:  # pragma: no cover
    openai = None
    OpenAI = None
    OPENAI_AVAILABLE = False

from .contracts import InvocationRequest, InvocationResult, InvocationStatus, UsageMetrics
from .provider import AgentProvider
from .roles import Role


DEFAULT_OPENAI_CAPABILITIES: Set[str] = {
    "planning",
    "reasoning",
    "repository_read",
    "review",
    "code_generation",
}

DEFAULT_MODEL = "gpt-4o"


def _sanitize_error_message(msg: str) -> str:
    """Removes potential API key patterns from error messages."""
    return re.sub(r"sk-[A-Za-z0-9_-]{10,}", "sk-***", msg)


class OpenAIProvider(AgentProvider):
    """
    OpenAI / ChatGPT Adapter implementing AgentProvider.

    Responsibilities:
    - Encapsulates OpenAI SDK communication behind the provider boundary
    - Reads credentials from environment variables (OPENAI_API_KEY)
    - Formulates role-aware prompt contexts
    - Normalizes OpenAI responses into vendor-neutral InvocationResult objects
    - Normalizes all errors without leaking SDK exception objects into core
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        default_model: str = DEFAULT_MODEL,
        timeout: float = 60.0,
        supported_capabilities: Optional[Set[str]] = None,
        client: Optional[Any] = None,
    ):
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self._organization = organization or os.getenv("OPENAI_ORG_ID")
        self._default_model = default_model
        self._timeout = timeout
        self._capabilities = set(supported_capabilities or DEFAULT_OPENAI_CAPABILITIES)
        self._client = client

    @property
    def provider_id(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return self._default_model

    def get_supported_capabilities(self) -> Set[str]:
        return set(self._capabilities)

    def _get_client(self) -> Any:
        """Returns the active or lazily initialized OpenAI client."""
        if self._client is not None:
            return self._client

        if not OPENAI_AVAILABLE:
            raise RuntimeError("The 'openai' Python package is not installed.")

        if not self._api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured in environment or provider constructor."
            )

        kwargs: Dict[str, Any] = {
            "api_key": self._api_key,
            "timeout": self._timeout,
        }
        if self._base_url:
            kwargs["base_url"] = self._base_url
        if self._organization:
            kwargs["organization"] = self._organization

        self._client = OpenAI(**kwargs)
        return self._client

    def health_check(self) -> bool:
        """
        Verifies provider readiness.
        Returns True if a client is injected or a valid API key is present.
        Does not perform external network calls during basic readiness checks.
        """
        if self._client is not None:
            return True
        if not OPENAI_AVAILABLE:
            return False
        key = self._api_key or os.getenv("OPENAI_API_KEY")
        if not key or not key.strip():
            return False
        clean_key = key.strip().lower()
        if clean_key.startswith("your_") or "placeholder" in clean_key:
            return False
        return True

    def _build_system_prompt(self, role: str) -> str:
        """Constructs an operational system prompt tailored to the canonical role."""
        if role == Role.ARCHITECT.value:
            return (
                "You are an expert software architect in the JESTER engineering workflow. "
                "Your objective is to analyze goals, decompose work into bounded tasks under "
                "Task Protocol v2, define explicit scope boundaries and dependencies, and "
                "produce unambiguous architectural plans adhering strictly to repository governance."
            )
        elif role == Role.REVIEWER.value:
            return (
                "You are an independent code reviewer in the JESTER engineering workflow. "
                "Your objective is to independently inspect the UNIFIED CODE DIFF, verify acceptance criteria, "
                "check test outcomes, identify potential regressions, syntax errors, security, or privacy invariant "
                "violations, and issue an objective verification report with a clear verdict. "
                "CRITICAL: Do NOT rely solely on the executor summary. If the unified code diff contains defects, "
                "logic errors, or contradicts the requirements, you MUST reject the implementation and emit "
                "REWORK_REQUIRED or FAILED with specific feedback citing the defect in the diff."
            )
        elif role == Role.AUDITOR.value:
            return (
                "You are a compliance auditor in the JESTER engineering workflow. "
                "Your objective is to inspect repository integrity, documentation portability, "
                "and architectural governance rules."
            )
        return (
            f"You are a specialized AI agent in the JESTER engineering workflow operating in role: {role}."
        )

    def _build_user_prompt(self, request: InvocationRequest) -> str:
        """Formats the normalized task context into a clear user instruction prompt."""
        payload = request.payload or {}
        lines: List[str] = [
            f"TASK ID: {request.task_id}",
            f"ROLE: {request.role}",
            f"TITLE: {payload.get('title', '')}",
            f"GOAL: {payload.get('goal', '')}",
        ]

        scope = payload.get("scope")
        if scope:
            lines.append("AUTHORIZED SCOPE:")
            for item in scope:
                lines.append(f"  - {item}")

        constraints = payload.get("constraints")
        if constraints:
            lines.append("CONSTRAINTS:")
            for item in constraints:
                lines.append(f"  - {item}")

        criteria = payload.get("acceptance_criteria")
        if criteria:
            lines.append("ACCEPTANCE CRITERIA:")
            for item in criteria:
                lines.append(f"  - {item}")

        verification = payload.get("verification")
        if verification:
            lines.append("VERIFICATION COMMANDS:")
            for item in verification:
                lines.append(f"  - {item}")

        # Structured repository context (for Executor)
        code_context = payload.get("code_context")
        if code_context:
            lines.append(f"\n{code_context}")

        # Unified code diff (for Reviewer)
        diff = payload.get("diff")
        if diff:
            lines.append(f"\nUNIFIED CODE DIFF (CRITICAL EVIDENCE):\n```diff\n{diff}\n```")

        # Any extra context (e.g. error traces, notes)
        handled_keys = {
            "title", "goal", "scope", "constraints", "acceptance_criteria",
            "verification", "dependencies", "code_context", "context_bundle", "diff",
        }
        extra_keys = set(payload.keys()) - handled_keys
        for key in sorted(extra_keys):
            lines.append(f"\n{key.upper()}:\n{payload[key]}")

        return "\n".join(lines)

    def invoke(self, request: InvocationRequest) -> InvocationResult:
        """
        Executes an InvocationRequest against the OpenAI chat completions API.
        Normalizes all outcomes into an InvocationResult without leaking SDK exceptions.
        """
        completed_at = datetime.now(timezone.utc).isoformat()
        model_to_use = request.model or self._default_model

        # Check client initialization
        try:
            client = self._get_client()
        except Exception as e:
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.FAILED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=model_to_use,
                summary="Client initialization failed.",
                error_message=_sanitize_error_message(str(e)),
                completed_at=completed_at,
            )

        system_prompt = self._build_system_prompt(request.role)
        user_prompt = self._build_user_prompt(request)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                timeout=self._timeout,
            )
        except Exception as e:
            # Handle and normalize any SDK, network, timeout, or authentication errors
            error_class = type(e).__name__
            clean_error = _sanitize_error_message(str(e))
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.FAILED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=model_to_use,
                summary=f"OpenAI API call failed ({error_class}).",
                error_message=f"{error_class}: {clean_error}",
                completed_at=completed_at,
            )

        # Validate response structure
        if not hasattr(response, "choices") or not response.choices:
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.FAILED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=model_to_use,
                summary="OpenAI returned an empty choices list.",
                error_message="Malformed response: no choices returned.",
                completed_at=completed_at,
            )

        first_choice = response.choices[0]
        message = getattr(first_choice, "message", None)
        content = getattr(message, "content", None) or ""

        if not content.strip():
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.FAILED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=model_to_use,
                summary="OpenAI returned empty message content.",
                error_message="Received empty text response from model.",
                completed_at=completed_at,
            )

        # Extract summary (first non-empty paragraph or up to 200 chars)
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        first_p = paragraphs[0] if paragraphs else content[:200]
        summary = first_p[:300] + ("..." if len(first_p) > 300 else "")

        # Extract raw metadata safely into pure python dict
        raw_meta: Dict[str, Any] = {
            "response_id": getattr(response, "id", None),
            "model": getattr(response, "model", model_to_use),
            "finish_reason": getattr(first_choice, "finish_reason", None),
        }
        usage_metrics = None
        usage = getattr(response, "usage", None)
        if usage:
            raw_meta["prompt_tokens"] = getattr(usage, "prompt_tokens", None)
            raw_meta["completion_tokens"] = getattr(usage, "completion_tokens", None)
            raw_meta["total_tokens"] = getattr(usage, "total_tokens", None)
            usage_metrics = UsageMetrics(
                input_tokens=getattr(usage, "prompt_tokens", None),
                output_tokens=getattr(usage, "completion_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
            )

        return InvocationResult(
            request_id=request.request_id,
            task_id=request.task_id,
            status=InvocationStatus.SUCCESS,
            agent_id=request.agent_id,
            provider=self.provider_id,
            model=getattr(response, "model", model_to_use),
            summary=summary,
            files_modified=[],
            reports_generated=[],
            error_message=None,
            usage=usage_metrics,
            raw_metadata=raw_meta,
            completed_at=completed_at,
        )
