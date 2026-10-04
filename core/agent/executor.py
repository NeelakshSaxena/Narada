from core.tools.registry import ToolRegistry
from core.permissions.engine import PermissionEngine
from core.permissions.models import PermissionRequest, ApprovalStatus
from typing import Dict, Any, List

class Executor:
    def __init__(self, tool_registry: ToolRegistry, permission_engine: PermissionEngine = None, allowed_tools: List[str] = None, skill_registry = None):
        self.tool_registry = tool_registry
        self.permission_engine = permission_engine or PermissionEngine()
        self.allowed_tools = allowed_tools if allowed_tools is not None else []
        self.skill_registry = skill_registry
        self.audit_log = []

    async def execute(self, action_name: str, approval_id: str = None, **kwargs) -> Any:
        """
        Validates that the action is registered, authorized, approved if needed, and executes it.
        """
        try:
            # 1. Discover
            tool = self.tool_registry.get_tool(action_name)
            
            # 2. Authorize globally
            if action_name not in self.allowed_tools:
                self.audit_log.append({"action": action_name, "status": "DENIED", "reason": "Not in allowed tools"})
                raise PermissionError(f"Tool {action_name} is not authorized.")
                
            # 3. Evaluate Permission via Engine
            if approval_id:
                # This is a retry of a pending action
                status = self.permission_engine.check_approval_status(approval_id)
                if status == ApprovalStatus.PENDING:
                    self.audit_log.append({"action": action_name, "status": "PENDING", "approval_id": approval_id})
                    return {"status": "PENDING", "approval_id": approval_id, "message": "Still waiting for approval"}
                elif status == ApprovalStatus.DENIED:
                    self.audit_log.append({"action": action_name, "status": "DENIED", "approval_id": approval_id})
                    raise PermissionError(f"Tool {action_name} execution was denied by human.")
            else:
                # New request
                request = PermissionRequest(identity="agent_1", tool=action_name, action="execute")
                decision = self.permission_engine.evaluate(request)
                
                if decision.requires_approval:
                    self.audit_log.append({"action": action_name, "status": "PENDING_APPROVAL", "approval_id": decision.approval_id})
                    return {"status": "PENDING_APPROVAL", "approval_id": decision.approval_id, "message": decision.reason}

            # 4. Execute (only reached if NOT_REQUIRED or APPROVED)
            result = await tool.execute(**kwargs)
            
            # 5. Observe
            observation = {"status": "SUCCESS", "result": result}
            
            # 6. Audit
            self.audit_log.append({"action": action_name, "status": "SUCCESS", "approval_id": approval_id})
            
            return observation
            
        except Exception as e:
            self.audit_log.append({"action": action_name, "status": "FAILED", "error": str(e)})
            return {"status": "FAILED", "error": str(e)}

    def load_skill(self, skill_name: str) -> str:
        """Loads a predefined procedural workflow constraint for the LLM"""
        if not self.skill_registry:
            raise ValueError("No SkillRegistry configured")
        return self.skill_registry.get_prompt_for_skill(skill_name)
