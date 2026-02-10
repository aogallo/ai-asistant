from app.agents.tool_registry import ToolRegistry
from app.agents.tools import get_weather

registry = ToolRegistry()
registry.registry("get_weather", get_weather)
