from typing import Dict, Any
from agents.base_agent import BaseAgent
from utils.logger import setup_logger

logger = setup_logger("coding_agent")

class CodingAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "CodingAgent"

    @property
    def description(self) -> str:
        return "Processes programming, syntax correction, code generation, and debugging requests."

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Coding agent activated for request: {prompt}")
        
        # Inject standard developer guidelines for code generation
        context["developer_guidelines"] = (
            "Provide production-ready, clean, modular code following SOLID principles. "
            "Add docstrings and comments. Format with markdown blocks."
        )
        
        return {
            "status": "success",
            "agent": self.name,
            "output": {
                "guidelines_injected": True
            }
        }
