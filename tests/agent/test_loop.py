import pytest
import uuid
from typing import Any
from core.agent.state import AgentState, AgentStatus
from core.agent.loop import AgentLoop
from core.agent.executor import Executor
from core.tools.registry import ToolRegistry
from core.tools.base import ToolProvider
from core.providers.base import LLMProvider
from core.llm.models import LLMResponse

class DummyTool(ToolProvider):
    @property
    def name(self) -> str:
        return "dummy_action"

    @property
    def description(self) -> str:
        return "Does nothing"

    @property
    def risk(self) -> str:
        return "low"

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def input_schema(self) -> dict:
        return {}

    @property
    def output_schema(self) -> dict:
        return {}

    async def execute(self, **kwargs) -> Any:
        return "Success"

class ScriptedLLMProvider(LLMProvider):
    def __init__(self):
        self.call_count = 0
        
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        self.call_count += 1
        if "Create plan" in prompt:
            return LLMResponse(text="Step 1: Do something", metadata={})
        elif "Propose action" in prompt:
            return LLMResponse(text="Action proposed", metadata={"action_name": "dummy_action", "action_kwargs": {}})
        elif "Observe" in prompt:
            return LLMResponse(text="Observation noted", metadata={})
        elif "Decide" in prompt:
            return LLMResponse(text="Decided to complete", metadata={"decision": "COMPLETE"})
        return LLMResponse(text="Generic", metadata={})
        
    async def stream(self, prompt: str, **kwargs):
        pass

@pytest.mark.asyncio
async def test_agent_loop_deterministic_completion():
    registry = ToolRegistry()
    registry.register(DummyTool())
    
    executor = Executor(tool_registry=registry, allowed_tools=["dummy_action"])
    llm = ScriptedLLMProvider()
    
    loop = AgentLoop(llm_provider=llm, executor=executor)
    
    state = AgentState(run_id=str(uuid.uuid4()), goal="Test Goal")
    
    assert state.status == AgentStatus.RUNNING
    
    final_state = await loop.run(state)
    
    assert final_state.status == AgentStatus.COMPLETED
    assert len(final_state.plan) > 0
    assert len(final_state.actions) == 1
    assert final_state.actions[0]["name"] == "dummy_action"
    assert final_state.observations[0]["result"] == "Success"
    assert final_state.decision == "COMPLETE"
