from memory.memory_manager import memory_manager

def add_memory(messages: list, role: str, content: str) -> list:
    """Legacy helper function preserved from the original chatbot memory.py."""
    messages.append({
        "role": role,
        "content": content
    })
    return messages

__all__ = ["memory_manager", "add_memory"]
