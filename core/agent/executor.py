from core.tools.registry import ToolRegistry
from typing import Dict, Any, List

class Executor:
    def __init__(self, tool_registry: ToolRegistry, allowed_tools: List[str] = None):
        self.tool_registry = tool_registry
        self.allowed_tools = allowed_tools if allowed_tools is not None else []
        self.audit_log = []

    async def execute(self, action_name: str, **kwargs) -> Any:
        """
        Validates that the action is registered, authorized, and executes it.
        """
        try:
            # 1. Discover
            tool = self.tool_registry.get_tool(action_name)
            
            # 2. Validate (omitted deep JSON schema validation for brevity)
            
            # 3. Authorize
            if action_name not in self.allowed_tools:
                self.audit_log.append({"action": action_name, "status": "DENIED"})
                raise PermissionError(f"Tool {action_name} is not authorized.")
                
            # 4. Approve if needed
            if tool.requires_confirmation:
                # Stub: simulate manual approval process
                pass
                
            # 5. Execute
            result = await tool.execute(**kwargs)
            
            # 6. Observe
            observation = {"status": "SUCCESS", "result": result}
            
            # 7. Audit
            self.audit_log.append({"action": action_name, "status": "SUCCESS"})
            
            return observation
            
        except Exception as e:
            self.audit_log.append({"action": action_name, "status": "FAILED", "error": str(e)})
            return {"status": "FAILED", "error": str(e)}
