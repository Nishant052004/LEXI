from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the agent for routing and logging purposes."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of what the agent does."""
        pass

    @abstractmethod
    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the agent's logic.
        
        Args:
            prompt (str): The current user prompt/input.
            context (Dict[str, Any]): Session context, database sessions, memory records, etc.
            
        Returns:
            Dict[str, Any]: A dictionary containing execution logs, outputs, and status.
        """
        pass
