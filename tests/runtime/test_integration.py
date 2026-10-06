import pytest
import asyncio
from core.runtime.integration import EndToEndFlow

class MockResponsibility:
    def __init__(self, id, goal, required_skill, allowed_tools, delivery_channel):
        self.id = id
        self.goal = goal
        self.required_skill = required_skill
        self.allowed_tools = allowed_tools
        self.delivery_channel = delivery_channel

class MockResponsibilityManager:
    async def get(self, req_id):
        if req_id == "resp_1":
            return MockResponsibility("resp_1", "Monitor Github", "github_monitor_skill", ["web_search"], "telegram")
        return None

class MockSkill:
    def __init__(self, name, instructions):
        self.name = name
        self.instructions = instructions

class MockSkillRegistry:
    async def get_skill(self, name):
        if name == "github_monitor_skill":
            return MockSkill(name, "Check recent commits")
        return None

class MockExecutionResult:
    def __init__(self, requires_delivery, delivery_message):
        self.requires_delivery = requires_delivery
        self.delivery_message = delivery_message

class MockAgentExecutor:
    async def execute(self, task_context, tools):
        assert "event" in task_context
        if task_context["event"].get("action") == "found_bug":
            return MockExecutionResult(True, "Bug found!")
        return MockExecutionResult(False, "")

class MockMemoryStore:
    def __init__(self):
        self.history = []
    async def store_execution(self, user_id, responsibility_id, event, result):
        self.history.append((user_id, responsibility_id, event, result))

class MockChannelProvider:
    def __init__(self):
        self.messages = []
    async def send_text(self, text):
        self.messages.append(text)

class MockChannelManager:
    def __init__(self):
        self.provider = MockChannelProvider()
    def get_provider(self, name):
        return self.provider

def test_end_to_end_flow_with_delivery():
    rm = MockResponsibilityManager()
    sr = MockSkillRegistry()
    ae = MockAgentExecutor()
    ms = MockMemoryStore()
    cm = MockChannelManager()
    
    flow = EndToEndFlow(rm, sr, ae, ms, cm)
    
    event = {"action": "found_bug"}
    result = asyncio.run(flow.execute_flow("user_123", "resp_1", event))
    
    # Verify execution result
    assert result.requires_delivery is True
    
    # Verify memory
    assert len(ms.history) == 1
    assert ms.history[0][1] == "resp_1"
    
    # Verify delivery
    provider = cm.get_provider("telegram")
    assert len(provider.messages) == 1
    assert provider.messages[0] == "Bug found!"

def test_end_to_end_flow_missing_responsibility():
    flow = EndToEndFlow(MockResponsibilityManager(), MockSkillRegistry(), MockAgentExecutor(), MockMemoryStore(), MockChannelManager())
    
    with pytest.raises(ValueError, match="not found"):
        asyncio.run(flow.execute_flow("user_1", "invalid", {}))
