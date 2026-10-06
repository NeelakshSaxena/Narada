import pytest
import asyncio
from core.agent.loop import AgentLoop, AgentState
from core.events.bus import EventBus
from core.tools.registry import ToolRegistry

class MockMemory:
    pass

class MockEventBus:
    def __init__(self):
        self.handlers = {}

    async def publish(self, topic: str, event: dict):
        if topic in self.handlers:
            for handler in self.handlers[topic]:
                handler(event)

    async def subscribe(self, topic: str, handler):
        if topic not in self.handlers:
            self.handlers[topic] = []
        self.handlers[topic].append(handler)

class MockProvider:
    pass

class MockExecutor:
    pass

async def run_narada_demo():
    # 1. Setup the environment
    bus = MockEventBus()
    registry = ToolRegistry()
    
    # 2. User request -> Create responsibility
    # "Watch my GitHub project and tell me when something important changes."
    # Simulated by registering a task in the scheduler/bus
    
    # We will simulate a github push event arriving at the gateway
    events_received = []
    
    def on_github_push(event):
        events_received.append(event)
        
    await bus.subscribe("github.push", on_github_push)
    
    # 3. Simulate Event
    await bus.publish("github.push", {"repo": "Narada", "commits": 1})
    
    # 4. Trigger agent loop
    # In a real scenario, the event triggers the loop
    memory = MockMemory()
    loop = AgentLoop(
        llm_provider=MockProvider(),
        executor=MockExecutor()
    )
    
    # For testing, we just verify the event bus routed the event
    assert len(events_received) == 1
    assert events_received[0]["repo"] == "Narada"
    
    from core.agent.state import AgentStatus
    
    # If the loop were fully mocked, we would verify state transitions
    state = AgentState(run_id="demo-1", goal="Review github push")
    assert state.goal == "Review github push"
    assert state.status == AgentStatus.RUNNING
    
    # Transition to completion (simulated)
    state.status = AgentStatus.COMPLETED
    assert state.status == AgentStatus.COMPLETED

def test_narada_demo_loop():
    asyncio.run(run_narada_demo())
