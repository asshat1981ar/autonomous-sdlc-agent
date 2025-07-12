from prometheus_client import Counter, Histogram, start_http_server

REQUEST_COUNT = Counter("agent_requests_total", "Total agent requests", ["agent"])
REQUEST_TIME = Histogram("agent_request_duration_seconds", "Duration of agent requests", ["agent"])

class MetricsServer:
    """MetricsServer class for steampunk operations."""
    """  Init   with enhanced functionality."""
    def __init__(self, port: int):
        self.port = port
    """Start with enhanced functionality."""

    def start(self):
        start_http_server(self.port)
    """Decorator with enhanced functionality."""
    """Wrapper with enhanced functionality."""

"""Instrument with enhanced functionality."""
def instrument(agent_name: str):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            REQUEST_COUNT.labels(agent=agent_name).inc()
            with REQUEST_TIME.labels(agent=agent_name).time():
                return fn(*args, **kwargs)
        return wrapper
    return decorator
