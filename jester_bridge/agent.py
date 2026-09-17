"""
Agent Abstraction for the JESTER Provider-Agnostic AI Bridge.

An Agent represents a configured worker profile assigned to an operational role,
binding it to a provider integration and declaring its supported capabilities.
"""
from typing import Any, Dict, Optional, Set
from pydantic import BaseModel, Field


class AgentProfile(BaseModel):
    """
    Provider-independent specification of an AI agent or human operator.
    """
    id: str
    role: str
    provider: str
    model: Optional[str] = None
    capabilities: Set[str] = Field(default_factory=set)
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def can_satisfy_capabilities(self, required: Set[str]) -> bool:
        """Checks whether this agent supports all required capabilities."""
        return set(required).issubset(self.capabilities)
