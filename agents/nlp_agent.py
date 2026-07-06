from typing import Dict, Any
from agents.base_agent import BaseAgent
from nlp.nlp_module import nlp_processor

class NLPAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "NLPAgent"

    @property
    def description(self) -> str:
        return "Analyzes user query intents, sentiments, keywords, and performs text preprocessing."

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        nlp_results = nlp_processor.process_all(prompt)
        
        # Save results to context for subsequent agents to use
        context["nlp_analysis"] = nlp_results
        
        return {
            "status": "success",
            "agent": self.name,
            "output": {
                "intent": nlp_results["intent"],
                "sentiment": nlp_results["sentiment"],
                "keywords": nlp_results["keywords"],
                "category": nlp_results["category"]
            }
        }
