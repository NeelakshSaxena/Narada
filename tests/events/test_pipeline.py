import pytest
import asyncio
from core.events.models import Event
from core.events.pipeline import EventPipeline
from core.responsibilities.models import Responsibility, ResponsibilityStatus
from core.responsibilities.scheduler import ResponsibilityScheduler
from core.skills.base import SkillRegistry
from core.tools.registry import ToolRegistry

def test_event_pipeline():
    scheduler = ResponsibilityScheduler(SkillRegistry(), ToolRegistry())
    
    resp1 = Responsibility(
        goal="Monitor github pushes",
        trigger_rules=["github.push"]
    )
    resp1.status = ResponsibilityStatus.ACTIVE
    
    resp2 = Responsibility(
        goal="Monitor webhooks",
        trigger_rules=["webhook.received"]
    )
    resp2.status = ResponsibilityStatus.ACTIVE
    
    scheduler.add_responsibility(resp1)
    scheduler.add_responsibility(resp2)
    
    async def mock_llm_callback(prompt: str) -> str:
        if "evaluator" in prompt:
            # The filter stage
            if "github" in prompt.lower():
                return "YES"
            return "NO"
        # The execution stage
        return "Executed on event"
        
    pipeline = EventPipeline(scheduler, mock_llm_callback)
    
    raw_event = {
        "type": "github.push",
        "payload": {"commits": 1},
        "source": "github"
    }
    
    asyncio.run(pipeline.process_raw_event(raw_event))
    
    assert len(pipeline.event_store) == 1
    # Only resp1 should be executed due to the trigger rule + YES evaluator
    assert resp1.memory_state.get("last_result") == "Executed on event"
    assert resp1.memory_state.get("triggering_event") == {"commits": 1}
    assert resp2.memory_state.get("last_result") is None
