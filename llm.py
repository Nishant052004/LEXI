import os
from config.config import settings
from utils.logger import setup_logger

logger = setup_logger("llm")

def ask_llm(messages):
    """Direct helper to invoke Groq LLM with safety fallbacks."""
    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Please configure your GROQ_API_KEY in the environment or .env file to enable full LLM responses."
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=settings.LLM_MODEL or "llama-3.1-8b-instant",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling Groq API: {str(e)}")
        return f"LLM inference error: {str(e)}"