import pytest
from core.permissions.engine import PermissionEngine
from core.permissions.models import RiskLevel, ApprovalStatus
from core.tools.registry import ToolRegistry
from core.agent.executor import Executor
from providers.tools.filesystem import FileSystemWriteTool, FileSystemReadTool
from core.runtime.runtime import AgentRuntime
from providers.llm.fake import FakeLLMProvider
from core.llm.models import LLMResponse


def test_permission_engine_auto_approve_writes():
    # Option B: auto_approve_writes disabled by default
    engine_strict = PermissionEngine(auto_approve_writes=False)
    assert engine_strict.get_baseline_risk("filesystem.write") == RiskLevel.MEDIUM

    # Option B: auto_approve_writes enabled
    engine_auto = PermissionEngine(auto_approve_writes=True)
    assert engine_auto.get_baseline_risk("filesystem.write") == RiskLevel.LOW


@pytest.mark.asyncio
async def test_executor_execute_pending(tmp_path):
    registry = ToolRegistry()
    registry.register(FileSystemWriteTool(workspace_root=str(tmp_path)))
    engine = PermissionEngine(auto_approve_writes=False)
    executor = Executor(tool_registry=registry, permission_engine=engine, allowed_tools=["filesystem.write"])

    # 1. Trigger action -> should be pending
    res = await executor.execute("filesystem.write", path="test.txt", content="hello")
    assert res["status"] == "PENDING_APPROVAL"
    app_id = res["approval_id"]
    assert executor.latest_pending_approval_id == app_id
    assert app_id in executor.pending_actions

    # 2. Execute pending
    exec_res = await executor.execute_pending(app_id)
    assert exec_res["status"] == "SUCCESS"
    assert (tmp_path / "test.txt").read_text(encoding="utf-8") == "hello"
    assert app_id not in executor.pending_actions


@pytest.mark.asyncio
async def test_agent_runtime_pauses_on_pending_approval(tmp_path):
    registry = ToolRegistry()
    registry.register(FileSystemWriteTool(workspace_root=str(tmp_path)))
    engine = PermissionEngine(auto_approve_writes=False)
    executor = Executor(tool_registry=registry, permission_engine=engine, allowed_tools=["filesystem.write"])

    calls = 0
    class ApprovalTestProvider(FakeLLMProvider):
        async def generate(self, prompt: str, **kwargs):
            nonlocal calls
            calls += 1
            tools = kwargs.get("tools")
            if tools:
                # Propose filesystem.write
                return LLMResponse(
                    text="Writing file...",
                    metadata={"tool_calls": [{"function": {"name": "filesystem.write", "arguments": {"path": "test.txt", "content": "hi"}}}]}
                )
            else:
                # Called without tools to explain to user
                return LLMResponse(text="I need your approval to write test.txt. Shall I proceed?", metadata={})

    provider = ApprovalTestProvider()
    rt = AgentRuntime(provider, executor=executor, workspace=str(tmp_path))

    response = await rt.interact([{"role": "user", "content": "Write test.txt"}])

    # Should have called LLM only twice: 1 with tools, and 1 without tools to explain. Not 5 times!
    assert calls == 2
    assert "approval" in response.lower()
    assert executor.latest_pending_approval_id is not None


@pytest.mark.asyncio
async def test_agent_runtime_confirms_approval_in_chat(tmp_path):
    registry = ToolRegistry()
    registry.register(FileSystemWriteTool(workspace_root=str(tmp_path)))
    engine = PermissionEngine(auto_approve_writes=False)
    executor = Executor(tool_registry=registry, permission_engine=engine, allowed_tools=["filesystem.write"])

    class ApprovalTestProvider(FakeLLMProvider):
        async def generate(self, prompt: str, **kwargs):
            tools = kwargs.get("tools")
            if tools:
                return LLMResponse(
                    text="Writing file...",
                    metadata={"tool_calls": [{"function": {"name": "filesystem.write", "arguments": {"path": "test.txt", "content": "hi"}}}]}
                )
            else:
                return LLMResponse(text="Action approved and written.", metadata={})

    provider = ApprovalTestProvider()
    rt = AgentRuntime(provider, executor=executor, workspace=str(tmp_path))

    # Turn 1: trigger pending approval
    await rt.interact([{"role": "user", "content": "Write test.txt"}])
    assert not (tmp_path / "test.txt").exists()

    # Turn 2: user says "yes"
    reply = await rt.interact([
        {"role": "user", "content": "Write test.txt"},
        {"role": "assistant", "content": "Need approval"},
        {"role": "user", "content": "yes"}
    ])

    assert (tmp_path / "test.txt").exists()
    assert (tmp_path / "test.txt").read_text(encoding="utf-8") == "hi"
    assert "Action approved" in reply
