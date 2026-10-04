import pytest
from core.tools.registry import ToolRegistry
from core.agent.executor import Executor
from providers.tools.filesystem import FileSystemReadTool, FileSystemWriteTool

@pytest.mark.asyncio
async def test_unknown_tool_fails():
    registry = ToolRegistry()
    executor = Executor(tool_registry=registry, allowed_tools=[])
    
    result = await executor.execute("unknown_tool")
    assert result["status"] == "FAILED"
    assert "not found in registry" in result["error"]
    
@pytest.mark.asyncio
async def test_denied_tool_fails():
    registry = ToolRegistry()
    registry.register(FileSystemReadTool())
    
    # tool is registered but NOT in allowed_tools list
    executor = Executor(tool_registry=registry, allowed_tools=[])
    
    result = await executor.execute("filesystem.read", path="test.txt")
    assert result["status"] == "FAILED"
    assert "not authorized" in result["error"]
    assert executor.audit_log[-1]["status"] == "DENIED"
    
@pytest.mark.asyncio
async def test_permitted_tool_executes(tmp_path):
    registry = ToolRegistry()
    registry.register(FileSystemReadTool())
    
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")
    
    executor = Executor(tool_registry=registry, allowed_tools=["filesystem.read"])
    
    result = await executor.execute("filesystem.read", path=str(test_file))
    assert result["status"] == "SUCCESS"
    assert result["result"] == "hello world"
    assert executor.audit_log[-1]["status"] == "SUCCESS"
