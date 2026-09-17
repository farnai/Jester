"""
Google Gemini Provider Adapter for the JESTER Provider-Agnostic AI Bridge.

Implements the AgentProvider interface for Google Gemini models.
Communicates via the official Google Generative Language API using httpx,
maintaining a lightweight, zero-dependency, and deterministic transport boundary.
Translates InvocationRequest into Gemini generateContent requests and normalizes
responses into vendor-neutral InvocationResult objects.
"""
from datetime import datetime, timezone
import json
import os
import re
from typing import Any, Dict, List, Optional, Set

import httpx

from .contracts import InvocationRequest, InvocationResult, InvocationStatus, UsageMetrics
from .provider import AgentProvider
from .roles import Role


DEFAULT_GOOGLE_CAPABILITIES: Set[str] = {
    "planning",
    "reasoning",
    "repository_read",
    "code_generation",
}

DEFAULT_MODEL = "gemini-2.5-pro"
DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def _sanitize_error_message(msg: str) -> str:
    """Removes potential Google API key patterns (e.g. AIzaSy...) from error messages."""
    return re.sub(r"AIza[A-Za-z0-9_-]{35}", "AIza***", msg)


class GoogleProvider(AgentProvider):
    """
    Google / Gemini Adapter implementing AgentProvider.

    Responsibilities:
    - Encapsulates Gemini API communication behind the provider boundary
    - Reads credentials from environment variables (GEMINI_API_KEY or GOOGLE_API_KEY)
    - Formulates role-aware system instructions and structured user contexts
    - Normalizes Gemini responses into vendor-neutral InvocationResult objects
    - Normalizes all errors without leaking HTTP or SDK exception objects into core
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: str = DEFAULT_MODEL,
        timeout: float = 60.0,
        supported_capabilities: Optional[Set[str]] = None,
        client: Optional[httpx.Client] = None,
    ):
        self._api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        self._base_url = (base_url or os.getenv("GEMINI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self._default_model = default_model
        self._timeout = timeout
        self._capabilities = set(supported_capabilities or DEFAULT_GOOGLE_CAPABILITIES)
        self._client = client

    @property
    def provider_id(self) -> str:
        return "google"

    @property
    def default_model(self) -> str:
        return self._default_model

    def get_supported_capabilities(self) -> Set[str]:
        return set(self._capabilities)

    def health_check(self) -> bool:
        """
        Verifies provider readiness.
        Returns True if a custom client is injected or a valid API key is present in environment.
        Does not perform external network calls during basic readiness checks.
        """
        if self._client is not None:
            return True
        key = (
            self._api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        if not key or not key.strip():
            return False
        clean_key = key.strip().lower()
        if clean_key.startswith("your_") or "placeholder" in clean_key:
            return False
        return True

    def _build_system_instruction(self, role: str) -> str:
        """Constructs an operational system instruction tailored to the canonical role."""
        if role == Role.EXECUTOR.value:
            return (
                "You are an expert software engineer acting as an Executor in the JESTER engineering workflow. "
                "Your objective is to implement bounded code modifications within the authorized scope, adhere strictly "
                "to constraints, satisfy acceptance criteria, preserve repository invariants, and produce precise, verifiable code."
            )
        elif role == Role.ARCHITECT.value:
            return (
                "You are an expert software architect in the JESTER engineering workflow. "
                "Your objective is to analyze goals, decompose work into bounded tasks under Task Protocol v2, "
                "define explicit boundaries and dependencies, and produce unambiguous architectural plans."
            )
        elif role == Role.REVIEWER.value:
            return (
                "You are an independent code reviewer in the JESTER engineering workflow. "
                "Your objective is to inspect code diffs, verify acceptance criteria, check test outcomes, "
                "and identify regressions or security violations."
            )
        elif role == Role.AUDITOR.value:
            return (
                "You are a compliance auditor in the JESTER engineering workflow. "
                "Your objective is to inspect repository integrity, documentation portability, "
                "and architectural governance rules."
            )
        return f"You are a specialized AI agent in the JESTER engineering workflow operating in role: {role}."

    def _build_user_prompt(self, request: InvocationRequest) -> str:
        """Formats the normalized task context into a structured prompt."""
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

        extra_keys = set(payload.keys()) - {
            "title", "goal", "scope", "constraints", "acceptance_criteria", "verification", "dependencies"
        }
        for key in sorted(extra_keys):
            lines.append(f"\n{key.upper()}:\n{payload[key]}")

        return "\n".join(lines)

    def invoke(self, request: InvocationRequest) -> InvocationResult:
        """
        Executes an InvocationRequest against the Google Gemini generateContent endpoint.
        Normalizes all outcomes into an InvocationResult without leaking HTTP/SDK exceptions.
        """
        completed_at = datetime.now(timezone.utc).isoformat()
        model_to_use = request.model or self._default_model

        # Ensure API key is available
        api_key = (
            self._api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        if not api_key and self._client is None:
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.FAILED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=model_to_use,
                summary="Client initialization failed.",
                error_message="GEMINI_API_KEY or GOOGLE_API_KEY is not configured in environment or provider constructor.",
                completed_at=completed_at,
            )

        system_text = self._build_system_instruction(request.role)
        user_text = self._build_user_prompt(request)

        # Build standard Gemini generateContent payload
        request_body: Dict[str, Any] = {
            "system_instruction": {
                "parts": [{"text": system_text}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_text}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2
            }
        }

        url = f"{self._base_url}/models/{model_to_use}:generateContent"
        headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            headers["x-goog-api-key"] = api_key

        try:
            if self._client is not None:
                response = self._client.post(
                    url,
                    json=request_body,
                    headers=headers,
                    timeout=self._timeout,
                )
            else:
                with httpx.Client(timeout=self._timeout) as client:
                    response = client.post(
                        url,
                        json=request_body,
                        headers=headers,
                    )
        except Exception as e:
            error_class = type(e).__name__
            clean_error = _sanitize_error_message(str(e))
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.FAILED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=model_to_use,
                summary=f"Google Gemini network/transport error ({error_class}).",
                error_message=f"{error_class}: {clean_error}",
                completed_at=completed_at,
            )

        # Handle HTTP status codes
        if response.status_code != 200:
            status_code = response.status_code
            clean_text = _sanitize_error_message(response.text)
            if status_code in (401, 403):
                summary = "Google Gemini authentication failed: Invalid or unauthorized API key."
            elif status_code == 429:
                summary = "Google Gemini rate limit exceeded."
            elif status_code == 400:
                summary = "Google Gemini bad request."
            elif status_code >= 500:
                summary = "Google Gemini server error."
            else:
                summary = f"Google Gemini API error ({status_code})."

            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.FAILED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=model_to_use,
                summary=summary,
                error_message=f"HTTP {status_code}: {clean_text}",
                completed_at=completed_at,
            )

        # Parse JSON response
        try:
            data = response.json()
        except Exception as e:
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.FAILED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=model_to_use,
                summary="Failed to parse Google Gemini JSON response.",
                error_message=f"JSONDecodeError: {_sanitize_error_message(str(e))}",
                completed_at=completed_at,
            )

        candidates = data.get("candidates") or []
        if not candidates:
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.FAILED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=model_to_use,
                summary="Google Gemini returned no candidates.",
                error_message="Malformed response: candidates array is empty.",
                completed_at=completed_at,
            )

        first_candidate = candidates[0]
        content_obj = first_candidate.get("content") or {}
        parts = content_obj.get("parts") or []
        if not parts:
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.FAILED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=model_to_use,
                summary="Google Gemini returned empty candidate content.",
                error_message="Received empty parts array from model.",
                completed_at=completed_at,
            )

        text_content = parts[0].get("text", "")
        if not text_content.strip():
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.FAILED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=model_to_use,
                summary="Google Gemini returned blank text content.",
                error_message="Received empty text string in candidate part.",
                completed_at=completed_at,
            )

        # Extract summary
        paragraphs = [p.strip() for p in text_content.split("\n\n") if p.strip()]
        first_p = paragraphs[0] if paragraphs else text_content[:200]
        summary = first_p[:300] + ("..." if len(first_p) > 300 else "")

        # Extract usage metadata safely
        usage = data.get("usageMetadata") or {}
        raw_meta: Dict[str, Any] = {
            "model": model_to_use,
            "finish_reason": first_candidate.get("finishReason"),
            "prompt_tokens": usage.get("promptTokenCount"),
            "completion_tokens": usage.get("candidatesTokenCount"),
            "total_tokens": usage.get("totalTokenCount"),
        }
        usage_metrics = None
        if usage:
            usage_metrics = UsageMetrics(
                input_tokens=usage.get("promptTokenCount"),
                output_tokens=usage.get("candidatesTokenCount"),
                total_tokens=usage.get("totalTokenCount"),
            )

        return InvocationResult(
            request_id=request.request_id,
            task_id=request.task_id,
            status=InvocationStatus.SUCCESS,
            agent_id=request.agent_id,
            provider=self.provider_id,
            model=model_to_use,
            summary=summary,
            files_modified=[],
            reports_generated=[],
            error_message=None,
            usage=usage_metrics,
            raw_metadata=raw_meta,
            completed_at=completed_at,
        )
