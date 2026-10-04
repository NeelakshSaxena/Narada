import pytest
import asyncio
from datetime import datetime, timedelta
from core.responsibilities.models import Responsibility
from core.responsibilities.scheduler import ResponsibilityScheduler
from core.skills.base import SkillRegistry, Skill
from core.tools.registry import ToolRegistry

@pytest.mark.asyncio
async def test_responsibility_model_scheduling():
    resp = Responsibility(schedule_interval_seconds=60)
    assert resp.is_due() is True
    
    resp.mark_executed()
    assert resp.is_due() is False
    
    # Fast forward time
    resp.next_run_at = datetime.utcnow() - timedelta(seconds=1)
    assert resp.is_due() is True

@pytest.mark.asyncio
async def test_scheduler_execution_context():
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
    scheduler.add_responsibility(resp)
    
    async def mock_llm_call(prompt: str) -> str:
        # Verify self-contained prompt constraints
        assert "GOAL: Check github" in prompt
        assert "last_commit" in prompt
        assert "constraint1" in prompt
        assert "console" in prompt
        return "New commit xyz found."

    # Manually trigger execution instead of running the endless loop
    await scheduler.execute_responsibility(resp, mock_llm_call)
    
    # State should be updated
    assert resp.memory_state["last_result"] == "New commit xyz found."
    assert resp.is_due() is False
