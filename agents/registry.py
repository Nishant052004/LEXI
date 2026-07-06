from typing import Dict, List, Optional
from agents.base_agent import BaseAgent
from utils.logger import setup_logger

logger = setup_logger("agent_registry")

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Dynamically registers an agent."""
        if not isinstance(agent, BaseAgent):
            raise TypeError("Agent must implement BaseAgent interface.")
        self._agents[agent.name.lower()] = agent
        logger.info(f"Registered agent: {agent.name} - {agent.description}")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Retrieves a registered agent by name."""
        return self._agents.get(name.lower())

    def list_agents(self) -> List[Dict[str, str]]:
        """Lists all registered agents and their descriptions."""
        return [
            {"name": agent.name, "description": agent.description}
            for agent in self._agents.values()
        ]

    def deregister(self, name: str) -> None:
        """Removes an agent from the registry."""
        if name.lower() in self._agents:
            del self._agents[name.lower()]
            logger.info(f"Deregistered agent: {name}")

agent_registry = AgentRegistry()
