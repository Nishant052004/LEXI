from typing import Dict, Any, Optional
from agents.registry import agent_registry
from agents.base_agent import BaseAgent
from utils.logger import setup_logger

logger = setup_logger("agent_router")

class AgentRouter:
    def __init__(self):
        # Default mapping of intents to agent names
        self.intent_to_agent_map = {
            "greeting": "memoryagent",
            "coding": "codingagent",
            "research": "researchagent",
            "memory": "memoryagent",
            "ner": "neragent"
        }

    def register_route(self, intent: str, agent_name: str):
        """Allows dynamic routing of new intents to new agents at runtime."""
        self.intent_to_agent_map[intent.lower()] = agent_name.lower()
        logger.info(f"Registered routing path: Intent '{intent}' -> Agent '{agent_name}'")

    def route(self, intent: str, prompt: str) -> Optional[BaseAgent]:
        """
        Determines and returns the correct agent based on classified intent.
        
        Args:
            intent (str): The classified intent from NLP analysis
            prompt (str): The raw text prompt for inspection
            
        Returns:
            Optional[BaseAgent]: The agent instance to execute or None
        """
        agent_name = self.intent_to_agent_map.get(intent.lower())
        
        if not agent_name:
            # Fallback heuristic: check if any registered agent name is in the prompt
            for registered_agent in agent_registry.list_agents():
                name = registered_agent["name"].lower().replace("agent", "")
                if name in prompt.lower():
                    agent_name = registered_agent["name"].lower()
                    break
        
        if agent_name:
            agent = agent_registry.get_agent(agent_name)
            if agent:
                logger.info(f"Routed intent '{intent}' to Agent '{agent.name}'")
                return agent

        # Default fallback
        logger.info(f"No specific route for intent '{intent}'. Falling back to default generation.")
        return None

agent_router = AgentRouter()
