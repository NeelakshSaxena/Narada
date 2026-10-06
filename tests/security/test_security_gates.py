import pytest
import asyncio
from core.agent.executor import Executor
from core.tools.registry import ToolRegistry
from core.tools.base import ToolProvider
from core.permissions.engine import PermissionEngine
from core.permissions.models import PermissionRequest, PermissionDecision, ApprovalStatus
from typing import Dict, Any

class MockTool(ToolProvider):
    def __init__(self, name, risk, requires_conf):
        self._name = name
        self._risk = risk
        self._requires_conf = requires_conf
        self.executed = False
        
    @property
    def name(self): return self._name
    @property
    def description(self): return ""
    @property
    def risk(self): return self._risk
    @property
    def requires_confirmation(self): return self._requires_conf
    @property
    def input_schema(self): return {}
    @property
    def output_schema(self): return {}
    
    async def execute(self, **kwargs):
        self.executed = True
        return "success"

@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register(MockTool("shell.execute", "high", True))
    reg.register(MockTool("web.search", "low", False))
    return reg

@pytest.fixture
def engine():
    return PermissionEngine()

def test_sandbox_isolation_unauthorized_tool(registry, engine):
    """Ensure that execution fails if a tool is not explicitly allowed, regardless of risk."""
    async def run_test():
        # shell.execute is not in allowed_tools
        executor = Executor(registry, engine, allowed_tools=["web.search"])
        result = await executor.execute("shell.execute", command="rm -rf /")
        assert result["status"] == "FAILED"
        assert "not authorized" in result["error"]
        assert not registry.get_tool("shell.execute").executed
    asyncio.run(run_test())

def test_approval_enforcement_high_risk(registry, engine):
    """Ensure that high-risk tools enforce an approval gate."""
    async def run_test():
        # shell.execute requires confirmation. PermissionEngine should flag this.
        # We patch PermissionEngine to simulate requiring approval
        executor = Executor(registry, engine, allowed_tools=["shell.execute", "web.search"])
        
        # 1. Initiate action (should pend)
        result = await executor.execute("shell.execute", command="deploy")
        assert result["status"] == "PENDING_APPROVAL"
        assert "approval_id" in result
        
        # Tool not executed yet
        assert not registry.get_tool("shell.execute").executed
        
        # 2. Deny approval
        engine.deny_approval(result["approval_id"], "human_user")
        result2 = await executor.execute("shell.execute", approval_id=result["approval_id"])
        assert result2["status"] == "FAILED"
        assert "denied by human" in result2["error"]
        assert not registry.get_tool("shell.execute").executed
        
        # 3. Grant approval
        result3 = await executor.execute("shell.execute", command="safe")
        app_id = result3["approval_id"]
        engine.grant_approval(app_id, "human_user")
        
        result4 = await executor.execute("shell.execute", approval_id=app_id)
        assert result4["status"] == "SUCCESS"
        assert registry.get_tool("shell.execute").executed
    asyncio.run(run_test())

def test_secret_protection_audit(registry, engine):
    """Ensure audit logs do not leak raw tool inputs containing secrets."""
    async def run_test():
        executor = Executor(registry, engine, allowed_tools=["web.search"])
        
        # web.search doesn't need approval
        await executor.execute("web.search", query="safe_query")
        
        # Look at audit log
        for log in executor.audit_log:
            assert log["action"] == "web.search"
            assert log["status"] == "SUCCESS"
            # The executor's raw audit log should track action and status, 
            # but if we passed kwargs containing secrets, they should be scrubbed or not present.
            # Currently, the executor audit log does not store kwargs. 
            # We assert kwargs are not stored to verify secret protection by design.
            assert "kwargs" not in log
    asyncio.run(run_test())
