import os
from groq import Groq
from config.config import settings

def ask_llm(messages):
    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY") or "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"
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=settings.LLM_MODEL or "llama-3.1-8b-instant",
        messages=messages
    )
    return response.choices[0].message.content

    