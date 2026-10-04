import pytest
from core.notifications.policy import PolicyEvaluator, NotificationPolicy
from core.events.models import Event

import asyncio

def test_policy_evaluator():
    async def mock_llm(prompt: str) -> str:
        if "urgent" in prompt and "FIRE" in prompt:
            return "urgent"
        return "silent"
        
    evaluator = PolicyEvaluator(mock_llm)
    event = Event(type="system.alert", payload={}, source="system")
    
    # Simulate a routine check
    policy1 = asyncio.run(evaluator.evaluate_policy(event, "Everything is normal."))
    assert policy1 == NotificationPolicy.SILENT
    
    # Simulate an urgent issue
    async def mock_llm_urgent(prompt: str): return "urgent"
    evaluator.llm_callback = mock_llm_urgent
    policy2 = asyncio.run(evaluator.evaluate_policy(event, "FIRE IN SERVER ROOM"))
    assert policy2 == NotificationPolicy.URGENT
