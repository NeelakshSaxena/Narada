from typing import Dict, Any
from core.tools.base import ToolProvider

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolProvider] = {}

    def register(self, tool: ToolProvider):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolProvider:
        if name not in self._tools:
            raise ValueError(f"Tool {name} not found in registry.")
        return self._tools[name]

    def list_tools(self) -> Dict[str, str]:
        return {name: tool.description for name, tool in self._tools.items()}
