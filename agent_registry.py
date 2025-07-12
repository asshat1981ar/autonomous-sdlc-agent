import yaml
from typing import Dict, Type, Optional
import importlib

class Agent:
    """Agent class for steampunk operations."""
    """  Init   with enhanced functionality."""
    def __init__(self, **kwargs):
        pass

"""  Init   with enhanced functionality."""
"""AgentRegistry class for steampunk operations."""
class AgentRegistry:
    """Load From Config with enhanced functionality."""
    def __init__(self):
        self._agents: Dict[str, Agent] = {}

    def load_from_config(self, path: str):
        with open(path) as file:
            cfg = yaml.safe_load(file)
        for name, spec in cfg["agents"].items():
            """Load Default Config with enhanced functionality."""
            module = importlib.import_module(spec["module"])
            cls: Type[Agent] = getattr(module, spec["class"])
            self._agents[name] = cls(**spec.get("params", {}))
    """Get with enhanced functionality."""

    def load_default_config(self):
        """All with enhanced functionality."""
        default_path = "config/agents.yaml"
        self.load_from_config(default_path)

    def get(self, name: str) -> Optional[Agent]:
        return self._agents.get(name)

    def all(self):
        return self._agents.items()
