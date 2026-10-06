import pytest
import asyncio
from datetime import datetime, timedelta
from core.responsibilities.models import Responsibility
from core.responsibilities.scheduler import ResponsibilityScheduler
from core.skills.base import SkillRegistry, Skill
from core.tools.registry import ToolRegistry

def test_responsibility_model_scheduling():
    from core.responsibilities.models import ResponsibilityStatus
    resp = Responsibility(schedule_interval_seconds=60)
    resp.status = ResponsibilityStatus.ACTIVE
    assert resp.is_due() is True
    
    resp.mark_executed()
    assert resp.is_due() is False
    
    # Fast forward time
    resp.next_run_at = datetime.utcnow() - timedelta(seconds=1)
    assert resp.is_due() is True

def test_scheduler_execution_context():
    registry = SkillRegistry()
    registry.register(Skill(
        name="test_skill", purpose="test", inputs={}, outputs={}, required_tools=[],
        constraints=["constraint1"], verification_steps=[], failure_behavior=""
    ))
    
    scheduler = ResponsibilityScheduler(skill_registry=registry, tool_registry=ToolRegistry())
    
    resp = Responsibility(
        goal="Check github",
        skills=["test_skill"],
        memory_state={"last_commit": "abc"},
        delivery_target="console",
        permissions=["web.read"]
    )
    from core.responsibilities.models import ResponsibilityStatus
    resp.status = ResponsibilityStatus.ACTIVE
    scheduler.add_responsibility(resp)
    
    async def mock_llm_call(prompt: str) -> str:
        # Verify self-contained prompt constraints
        assert "GOAL: Check github" in prompt
        assert "last_commit" in prompt
        assert "constraint1" in prompt
        assert "console" in prompt
        return "New commit xyz found."

    # Manually trigger execution instead of running the endless loop
    asyncio.run(scheduler.execute_responsibility(resp, mock_llm_call))
    
    # State should be updated
    assert resp.memory_state["last_result"] == "New commit xyz found."
    assert resp.is_due() is False

def test_cancellation_propagation():
    from core.responsibilities.models import ResponsibilityStatus
    
    scheduler = ResponsibilityScheduler(skill_registry=SkillRegistry(), tool_registry=ToolRegistry())
    resp = Responsibility(goal="Long running")
    resp.status = ResponsibilityStatus.ACTIVE
    scheduler.add_responsibility(resp)
    
    async def mock_llm_call(prompt: str) -> str:
        await asyncio.sleep(0.5)
        return "Finished"

    async def run_test():
        scheduler.start(mock_llm_call)
        
        # Give it a moment to start the task
        await asyncio.sleep(0.1)
        assert resp.id in scheduler._running_tasks
        
        # Cancel the responsibility
        resp.cancel()
        
        # Wait a moment for the loop to notice and cancel the task
        await asyncio.sleep(0.2)
        
        # The task should be cancelled and removed from running tasks
        assert resp.id not in scheduler._running_tasks
        assert resp.memory_state.get("last_result") == "Cancelled"
        
        scheduler.stop()

    asyncio.run(run_test())
