from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from config.config import settings
from utils.logger import setup_logger

logger = setup_logger("response_generation_agent")

# Try to import groq client
try:
    from groq import Groq
    groq_available = True
except ImportError:
    groq_available = False
    logger.warning("Groq library not installed. ResponseGenerationAgent will run in mock mode.")

class ResponseGenerationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "ResponseGenerationAgent"

    @property
    def description(self) -> str:
        return "Aggregates agent outputs and generates the final, context-aware user response using Groq."

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Response Generation Agent compiling response.")
        
        # Extract components from context
        nlp_analysis = context.get("nlp_analysis", {})
        entities = context.get("extracted_entities", [])
        research_data = context.get("research_data", "")
        history_context = context.get("history_context", [])
        frequent_topics = context.get("frequent_topics", [])
        user_prefs = context.get("user_preferences", {})
        user_id = context.get("user_id")
        username = context.get("username", "Nishant")
        
        # Build systemic instruction prompt
        system_instruction = (
            f"You are a production-ready, future-proof AI assistant. "
            f"The user you are communicating with is named: {username}. "
        )
        
        # Requirements: Greeting Nishant
        if username.lower() == "nishant":
            system_instruction += "\nIf this is the beginning of the chat or a login/greeting query, greet the user with: 'Hi Nishant 👋, Welcome to Multi-Agent AI Chatbot'\n"
        else:
            system_instruction += f"\nIf this is the beginning of the chat or a login/greeting query, greet the user with: 'Hi {username} 👋, Welcome to Multi-Agent AI Chatbot'\n"
            
        if user_prefs:
            system_instruction += f"\nUser Preferences: {user_prefs}. Respect these preferences (e.g. style, constraints) in your replies."
 
        if history_context:
            system_instruction += "\nHere is the recent conversation history for context (do not repeat it directly unless asked, just keep it in mind):\n"
            system_instruction += "\n".join(history_context)
 
        if entities:
            system_instruction += f"\nNamed Entities detected in user prompt: {[(e['text'], e['label']) for e in entities]}. You can reference these names/locations/dates if relevant."
 
        if research_data:
            system_instruction += f"\nReal-time Web Search Results: \n{research_data}\nUtilize these results to provide factual, up-to-date answers."
 
        if frequent_topics:
            system_instruction += f"\nFrequently discussed intents: {frequent_topics}."
 
        if context.get("developer_guidelines"):
            system_instruction += f"\nDeveloper Guidelines: {context.get('developer_guidelines')}"


        # Make the LLM API call
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]

        response_content = ""
        
        if groq_available and settings.GROQ_API_KEY:
            try:
                client = Groq(api_key=settings.GROQ_API_KEY)
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=settings.LLM_MODEL,
                    temperature=user_prefs.get("temperature", 0.7)
                )
                response_content = chat_completion.choices[0].message.content
                logger.info("Successfully fetched response from Groq API.")
            except Exception as e:
                logger.error(f"Groq API call failed: {str(e)}")
                response_content = self._get_fallback_response(prompt, context)
        else:
            logger.warning("Groq API not configured or unavailable. Emulating fallback response.")
            response_content = self._get_fallback_response(prompt, context)

        # Update context with the final reply
        context["final_response"] = response_content

        return {
            "status": "success",
            "agent": self.name,
            "output": {
                "response": response_content,
                "system_instruction_preview": system_instruction[:200]
            }
        }

    def _get_fallback_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Returns a generic fallback response containing context facts if API fails."""
        username = context.get("username", "Nishant")
        greeting = f"Hi {username} 👋, Welcome to Multi-Agent AI Chatbot."
        
        entities = context.get("extracted_entities", [])
        entity_str = ", ".join([f"'{e['text']}' ({e['label']})" for e in entities]) if entities else "None"
        
        intent = context.get("nlp_analysis", {}).get("intent", "general")
        research = context.get("research_data", "")
        
        response = f"{greeting}\n\n[System Alert: Connected without LLM API key or Library Error]\n"
        response += f"I analyzed your request:\n"
        response += f"- **Primary Intent Classified**: {intent}\n"
        response += f"- **Entities Extracted**: {entity_str}\n"
        
        if research:
            response += f"\nHere is what I found on the web:\n{research}\n"
            
        response += f"\nPlease configure your `GROQ_API_KEY` in the `.env` file to enable full cognitive responses!"
        return response
