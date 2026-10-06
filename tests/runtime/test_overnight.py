import pytest
import asyncio
from core.runtime.overnight import AutonomyEngine, AutonomyState, Decision

class MockStore:
    async def get(self, resp_id):
        class MockResp:
            id = resp_id
            delivery_target = "telegram"
        return MockResp() if resp_id == "r1" else None

class MockValidator:
    async def validate(self, resp):
        return True

class MockAgentCore:
    async def reason(self, resp, event):
        if event.get("trigger") == "important":
            return Decision(True, "fix_bug", True, "I fixed a bug.")
        return Decision(False, None, False, "")
        
    async def act(self, plan):
        return "Action succeeded"

class MockMemory:
    def __init__(self):
        self.stored = []
    async def store(self, resp_id, event, decision, result):
        self.stored.append((resp_id, event, decision, result))

class MockNotifier:
    def __init__(self):
        self.notifications = []
    async def notify(self, target, msg):
        self.notifications.append((target, msg))

def test_overnight_watch_setup():
    engine = AutonomyEngine(MockStore(), MockValidator(), MockAgentCore(), MockMemory(), MockNotifier())
    
    asyncio.run(engine.setup_overnight_watch("r1"))
    
    assert engine.state == AutonomyState.SLEEPING

def test_overnight_wake_and_act():
    memory = MockMemory()
    notifier = MockNotifier()
    engine = AutonomyEngine(MockStore(), MockValidator(), MockAgentCore(), memory, notifier)
    
    asyncio.run(engine.setup_overnight_watch("r1"))
    assert engine.state == AutonomyState.SLEEPING
    
    # Event wakes the agent up
    event = {"trigger": "important"}
    asyncio.run(engine.wake_on_event(event, "r1"))
    
    # Check that it went back to sleep after the cycle
    assert engine.state == AutonomyState.SLEEPING
    
    # Check memory stored the action
    assert len(memory.stored) == 1
    assert memory.stored[0][3] == "Action succeeded"
    
    # Check notification was sent
    assert len(notifier.notifications) == 1
    assert notifier.notifications[0][0] == "telegram"
    assert notifier.notifications[0][1] == "I fixed a bug."

def test_overnight_wake_no_action():
    memory = MockMemory()
    notifier = MockNotifier()
    engine = AutonomyEngine(MockStore(), MockValidator(), MockAgentCore(), memory, notifier)
    
    asyncio.run(engine.setup_overnight_watch("r1"))
    
    # Event wakes the agent up, but reasoning says no action
    event = {"trigger": "mundane"}
    asyncio.run(engine.wake_on_event(event, "r1"))
    
    assert engine.state == AutonomyState.SLEEPING
    
    # Action result should be None
    assert memory.stored[0][3] is None
    # No notification sent
    assert len(notifier.notifications) == 0
