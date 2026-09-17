"""
Configuration Loader and Schema for the JESTER Provider-Agnostic AI Bridge.

Provides declarative configuration for:
- Role-to-agent bindings
- Agent definitions and capability declarations
- Provider registrations
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field

from .agent import AgentProfile
from .roles import is_valid_role


class BridgeConfig(BaseModel):
    """
    Validated configuration for AI Bridge agents, role bindings, and providers.
    """
    version: str = "2.0"
    role_bindings: Dict[str, str] = Field(default_factory=dict)
    agents: Dict[str, AgentProfile] = Field(default_factory=dict)
    providers: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    def get_agent_for_role(self, role: str) -> Optional[AgentProfile]:
        """Resolves the AgentProfile bound to a given canonical role."""
        if not is_valid_role(role):
            return None
        agent_id = self.role_bindings.get(role)
        if not agent_id:
            return None
        return self.agents.get(agent_id)

    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        """Returns the AgentProfile for a specific agent ID."""
        return self.agents.get(agent_id)


def load_bridge_config(source: Union[str, Path, Dict[str, Any]]) -> BridgeConfig:
    """
    Loads and validates BridgeConfig from a JSON file or dictionary.
    """
    if isinstance(source, (str, Path)):
        file_path = Path(source)
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    elif isinstance(source, dict):
        raw_data = source
    else:
        raise ValueError(f"Unsupported config source type: {type(source)}")

    # Parse agents into AgentProfile instances
    agents_raw = raw_data.get("agents", {})
    parsed_agents: Dict[str, AgentProfile] = {}
    for agent_id, agent_dict in agents_raw.items():
        if "id" not in agent_dict:
            agent_dict["id"] = agent_id
        if "capabilities" in agent_dict and isinstance(agent_dict["capabilities"], list):
            agent_dict["capabilities"] = set(agent_dict["capabilities"])
        parsed_agents[agent_id] = AgentProfile(**agent_dict)

    return BridgeConfig(
        version=raw_data.get("version", "2.0"),
        role_bindings=raw_data.get("role_bindings", {}),
        agents=parsed_agents,
        providers=raw_data.get("providers", {}),
    )
