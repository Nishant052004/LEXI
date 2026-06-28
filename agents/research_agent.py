from typing import Dict, Any
from agents.base_agent import BaseAgent
from web_agent import search_web
from utils.logger import setup_logger

logger = setup_logger("research_agent")

class ResearchAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "ResearchAgent"

    @property
    def description(self) -> str:
        return "Queries the internet using DuckDuckGo to obtain external real-time information."

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Research agent searching for query: {prompt}")
        
        # Clean query by removing keywords
        query = prompt.replace("search", "").replace("google", "").strip()
        if not query:
            query = prompt

        try:
            search_results = search_web(query)
            context["research_data"] = search_results
            return {
                "status": "success",
                "agent": self.name,
                "output": {
                    "query": query,
                    "results_preview": search_results[:200] + "..." if len(search_results) > 200 else search_results
                }
            }
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {str(e)}")
            context["research_data"] = "Search unavailable due to connection issues."
            return {
                "status": "failed",
                "agent": self.name,
                "error": str(e)
            }
        
