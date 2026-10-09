import pytest
from core.permissions.models import RiskLevel, ApprovalStatus, PermissionRequest
from core.permissions.engine import PermissionEngine
from core.tools.registry import ToolRegistry
from core.agent.executor import Executor
from providers.tools.filesystem import FileSystemReadTool, FileSystemWriteTool

def test_permission_engine_risk_levels():
    engine = PermissionEngine()
    assert engine.get_baseline_risk("filesystem.read") == RiskLevel.LOW
    assert engine.get_baseline_risk("filesystem.write") == RiskLevel.MEDIUM
    assert engine.get_baseline_risk("shell.execute") == RiskLevel.HIGH
    assert engine.get_baseline_risk("data.delete") == RiskLevel.CRITICAL
    assert engine.get_baseline_risk("unknown") == RiskLevel.HIGH

def test_llm_cannot_approve():
    engine = PermissionEngine()
    req = PermissionRequest(identity="agent_1", tool="filesystem.write", action="write")
    decision = engine.evaluate(req)
    
    assert decision.requires_approval is True
    assert decision.status == ApprovalStatus.PENDING
    
    # LLM tries to approve its own request
    success = engine.grant_approval(decision.approval_id, identity="llm")
    assert success is False
    assert engine.check_approval_status(decision.approval_id) == ApprovalStatus.PENDING
    
    # Human approves
    success = engine.grant_approval(decision.approval_id, identity="human_user")
    assert success is True
    assert engine.check_approval_status(decision.approval_id) == ApprovalStatus.APPROVED

@pytest.mark.asyncio
async def test_executor_enforces_approval(tmp_path):
    registry = ToolRegistry()
    registry.register(FileSystemWriteTool())
    engine = PermissionEngine()
    executor = Executor(tool_registry=registry, permission_engine=engine, allowed_tools=["filesystem.write"])
    
    test_file = tmp_path / "out.txt"
    
    # Initial request -> should require approval and NOT execute
    res1 = await executor.execute("filesystem.write", path=str(test_file), content="data")
    assert res1["status"] == "PENDING_APPROVAL"
    assert "approval_id" in res1
    assert not test_file.exists()
    
    approval_id = res1["approval_id"]
    
    # Retry without human approval -> still pending
    res2 = await executor.execute("filesystem.write", approval_id=approval_id, path=str(test_file), content="data")
    assert res2["status"] == "PENDING"
    assert not test_file.exists()
    
    # Human denies
    engine.deny_approval(approval_id, "human")
    res3 = await executor.execute("filesystem.write", approval_id=approval_id, path=str(test_file), content="data")
    assert res3["status"] == "FAILED"
    assert "denied by human" in res3["error"]
    assert not test_file.exists()
    
    # Audit log check
    assert executor.audit_log[0]["status"] == "PENDING_APPROVAL"
    assert executor.audit_log[1]["status"] == "PENDING"
    assert executor.audit_log[2]["status"] == "DENIED"

@pytest.mark.asyncio
async def test_executor_executes_after_approval(tmp_path):
    registry = ToolRegistry()
    registry.register(FileSystemWriteTool())
    engine = PermissionEngine()
    executor = Executor(tool_registry=registry, permission_engine=engine, allowed_tools=["filesystem.write"])
    
    test_file = tmp_path / "out2.txt"
    
    res1 = await executor.execute("filesystem.write", path=str(test_file), content="data2")
    approval_id = res1["approval_id"]
    
    # Human approves
    engine.grant_approval(approval_id, "human")
    
    # Retry -> executes
    res2 = await executor.execute("filesystem.write", approval_id=approval_id, path=str(test_file), content="data2")
    assert res2["status"] == "SUCCESS"
    assert test_file.read_text() == "data2"
    assert executor.audit_log[-1]["status"] == "SUCCESS"
