from core.tools.registry import ToolRegistry
from typing import Dict, Any

class Executor:
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry

    async def execute(self, action_name: str, **kwargs) -> Any:
        """
        Validates that the action is registered and executes it.
        """
        try:
            tool = self.tool_registry.get_tool(action_name)
            # In a full implementation, check permissions/approvals here.
            result = await tool.execute(**kwargs)
            return result
        except Exception as e:
            return f"Error executing {action_name}: {str(e)}"
