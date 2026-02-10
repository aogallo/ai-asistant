from collections.abc import Callable
from typing import Any


class ToolRegistry:
    def __init__(self) -> None:
        self.tools: dict[str, Callable[..., Any]] = {}

    def registry(self, name: str, func: Callable[..., Any]):
        self.tools[name] = func

    def execute(self, name: str, args: dict):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not registered")

        return self.tools[name](**args)
