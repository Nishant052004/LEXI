import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*duckduckgo_search.*")

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

def search_web(query: str) -> str:
    """Searches the web via DuckDuckGo and returns snippets."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                if isinstance(r, dict) and "body" in r:
                    results.append(r["body"])
    except Exception as e:
        return f"Live search unavailable or timed out: {str(e)}"
    return "\n".join(results)