"""
Provider Abstraction for the JESTER Provider-Agnostic AI Bridge.

A Provider represents the technical integration layer that communicates with an AI
service, local engine, CLI runtime, or human interface. It provides a generic
invocation mechanism and does not embed role-specific concepts.
"""
from abc import ABC, abstractmethod
from typing import Set
from .contracts import InvocationRequest, InvocationResult


class AgentProvider(ABC):
    """
    Vendor-neutral interface for AI provider adapters.

    Responsibilities:
    - Technical communication with models / engines
    - Transport health checking
    - Reporting technical capabilities supported by the runtime
    - Executing generic invocation requests and returning normalized results
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Stable identifier of this provider (e.g. 'openai', 'google', 'anthropic', 'mock')."""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Verifies connectivity, runtime availability, and environment readiness."""
        ...

    @abstractmethod
    def get_supported_capabilities(self) -> Set[str]:
        """Returns the set of technical capabilities supported by this provider."""
        ...

    @abstractmethod
    def invoke(self, request: InvocationRequest) -> InvocationResult:
        """
        Executes a normalized invocation request and returns a normalized result.
        Must not raise vendor SDK exceptions; errors must be captured in InvocationResult.
        """
        ...
