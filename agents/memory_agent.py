from typing import Dict, Any
from agents.base_agent import BaseAgent
from memory.memory_manager import memory_manager
from utils.logger import setup_logger

logger = setup_logger("memory_agent")

class MemoryAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "MemoryAgent"

    @property
    def description(self) -> str:
        return "Fetches conversation history, user profiles, preferences, and analyzes memory analytics."

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        db = context.get("db")
        convo_id = context.get("conversation_id")
        user_id = context.get("user_id")
        
        history_summary = []
        user_prefs = {}
        freq_topics = []

        if db and user_id:
            user_prefs = memory_manager.get_user_preferences(db, user_id)
            context["user_preferences"] = user_prefs
            
        if db and convo_id:
            # Fetch past history context
            history = memory_manager.get_conversation_history(db, convo_id, limit=6)
            history_summary = [f"{msg['role']}: {msg['content']}" for msg in history]
            context["history_context"] = history_summary
            
            # Fetch frequently asked topics
            topics = memory_manager.get_frequently_asked_topics(db, convo_id)
            freq_topics = [f"{t[0]} (count: {t[1]})" for t in topics]
            context["frequent_topics"] = freq_topics
            
        logger.info(f"Memory Agent retrieved {len(history_summary)} history items and user preferences.")
        
        return {
            "status": "success",
            "agent": self.name,
            "output": {
                "preferences": user_prefs,
                "history_length": len(history_summary),
                "frequent_topics": freq_topics
            }
        }
