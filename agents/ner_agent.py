from typing import Dict, Any
from agents.base_agent import BaseAgent
from ner.ner_module import ner_extractor
from memory.memory_manager import memory_manager

class NERAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "NERAgent"

    @property
    def description(self) -> str:
        return "Extracts structured entities (Person, Organization, Location, Dates, Emails, Phones) from queries."

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        entities = ner_extractor.extract_entities(prompt)
        
        # Save entities to shared context
        context["extracted_entities"] = entities
        
        # Store extracted entities in database if conversation_id and db are in context
        db = context.get("db")
        convo_id = context.get("conversation_id")
        if db and convo_id:
            memory_manager.save_entities(db, convo_id, entities)
            
        return {
            "status": "success",
            "agent": self.name,
            "output": {
                "entities_count": len(entities),
                "entities": entities
            }
        }
