from agents.registry import agent_registry
from agents.nlp_agent import NLPAgent
from agents.ner_agent import NERAgent
from agents.research_agent import ResearchAgent
from agents.coding_agent import CodingAgent
from agents.memory_agent import MemoryAgent
from agents.response_generation_agent import ResponseGenerationAgent
from agents.router import agent_router

# Register default core agents
agent_registry.register(NLPAgent())
agent_registry.register(NERAgent())
agent_registry.register(ResearchAgent())
agent_registry.register(CodingAgent())
agent_registry.register(MemoryAgent())
agent_registry.register(ResponseGenerationAgent())

__all__ = [
    "agent_registry",
    "agent_router",
    "NLPAgent",
    "NERAgent",
    "ResearchAgent",
    "CodingAgent",
    "MemoryAgent",
    "ResponseGenerationAgent"
]
