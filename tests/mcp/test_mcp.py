import pytest
from core.mcp.client import MockMCPServer
from core.mcp.adapter import discover_and_register_mcp_tools
from core.tools.registry import ToolRegistry
from core.permissions.engine import PermissionEngine
from core.agent.executor import Executor

@pytest.mark.asyncio
async def test_mcp_tool_discovery_and_registration():
    registry = ToolRegistry()
    engine = PermissionEngine()
    client = MockMCPServer()
    
    await discover_and_register_mcp_tools(client, registry, engine)
    
    # Verify tools were registered
    tools = registry.list_tools()
    assert "mcp.filesystem.read" in tools
    assert "mcp.shell.execute" in tools
    
    read_tool = registry.get_tool("mcp.filesystem.read")
    assert read_tool.risk == "LOW"
    assert read_tool.requires_confirmation is False
    
    shell_tool = registry.get_tool("mcp.shell.execute")
    assert shell_tool.risk == "HIGH"
    assert shell_tool.requires_confirmation is True

@pytest.mark.asyncio
async def test_mcp_tool_execution_with_permissions():
    registry = ToolRegistry()
    engine = PermissionEngine()
    client = MockMCPServer()
    
    await discover_and_register_mcp_tools(client, registry, engine)
    
    # We must explicitly authorize the tools in Executor allowed_tools
    executor = Executor(tool_registry=registry, permission_engine=engine, allowed_tools=["mcp.filesystem.read", "mcp.shell.execute"])
    
    # 1. Low risk MCP tool executes directly and returns observation
    res1 = await executor.execute("mcp.filesystem.read", path="/tmp/test.txt")
    assert res1["status"] == "SUCCESS"
    assert "Mock read content of /tmp/test.txt" in res1["result"]
    assert executor.audit_log[-1]["action"] == "mcp.filesystem.read"
    assert executor.audit_log[-1]["status"] == "SUCCESS"
    
    # 2. High risk MCP tool triggers Narada's PENDING_APPROVAL pause
    res2 = await executor.execute("mcp.shell.execute", command="rm -rf /")
    assert res2["status"] == "PENDING_APPROVAL"
    assert "approval_id" in res2
    
    # Audit log should show pending
    assert executor.audit_log[-1]["action"] == "mcp.shell.execute"
    assert executor.audit_log[-1]["status"] == "PENDING_APPROVAL"
    
    # 3. Human grants approval
    approval_id = res2["approval_id"]
    engine.grant_approval(approval_id, "human_user")
    
    # 4. Retry MCP execution
    res3 = await executor.execute("mcp.shell.execute", approval_id=approval_id, command="rm -rf /")
    assert res3["status"] == "SUCCESS"
    assert "Mock executed rm -rf /" in res3["result"]
