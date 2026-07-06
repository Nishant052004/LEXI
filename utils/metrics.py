import time
import functools
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger("metrics")

class MetricsCollector:
    """In-memory metrics collector for monitoring and performance tracking."""
    def __init__(self):
        self.request_counts: Dict[str, int] = {}
        self.agent_execution_times: Dict[str, List[float]] = {}
        self.agent_execution_counts: Dict[str, int] = {}
        self.error_counts: Dict[str, int] = {}

    def record_request(self, endpoint: str):
        self.request_counts[endpoint] = self.request_counts.get(endpoint, 0) + 1

    def record_agent_execution(self, agent_name: str, execution_time_s: float):
        self.agent_execution_counts[agent_name] = self.agent_execution_counts.get(agent_name, 0) + 1
        if agent_name not in self.agent_execution_times:
            self.agent_execution_times[agent_name] = []
        self.agent_execution_times[agent_name].append(execution_time_s)
        # Keep only last 100 entries to prevent memory leak
        if len(self.agent_execution_times[agent_name]) > 100:
            self.agent_execution_times[agent_name].pop(0)

    def record_error(self, component: str):
        self.error_counts[component] = self.error_counts.get(component, 0) + 1

    def get_metrics(self) -> Dict[str, Any]:
        avg_times = {}
        for agent, times in self.agent_execution_times.items():
            if times:
                avg_times[agent] = sum(times) / len(times)
            else:
                avg_times[agent] = 0.0
        
        return {
            "total_requests": self.request_counts,
            "agent_execution_counts": self.agent_execution_counts,
            "agent_average_execution_time_s": avg_times,
            "error_counts": self.error_counts
        }

metrics_collector = MetricsCollector()

def track_execution_time(agent_name: str):
    """Decorator to measure agent/function execution time and log it."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                exc_time = time.perf_counter() - start_time
                metrics_collector.record_agent_execution(agent_name, exc_time)
                logger.debug(
                    f"Agent {agent_name} executed successfully",
                    extra={"agent_name": agent_name, "execution_time_ms": exc_time * 1000}
                )
                return result
            except Exception as e:
                metrics_collector.record_error(agent_name)
                logger.error(
                    f"Agent {agent_name} failed with error: {str(e)}",
                    extra={"agent_name": agent_name}
                )
                raise e
        return wrapper
    return decorator
