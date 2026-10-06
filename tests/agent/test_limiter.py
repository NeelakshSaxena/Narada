import pytest
import asyncio
import uuid
from core.agent.state import AgentState, AgentStatus
from core.agent.loop import AgentLoop
from core.agent.executor import Executor
from core.tools.registry import ToolRegistry
from core.providers.base import LLMProvider
from core.llm.models import LLMResponse

class InfiniteLLMProvider(LLMProvider):
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        if "Create plan" in prompt:
            return LLMResponse(text="Step 1: Loop forever", metadata={})
        elif "Propose action" in prompt:
            return LLMResponse(text="Action proposed", metadata={"action_name": "unknown", "action_kwargs": {}})
        elif "Observe" in prompt:
            return LLMResponse(text="Observation noted", metadata={})
        elif "Decide" in prompt:
            return LLMResponse(text="Decided to continue", metadata={"decision": "CONTINUE"})
        return LLMResponse(text="Generic", metadata={})
        
    async def stream(self, prompt: str, **kwargs):
        pass

def test_circuit_breaker_tripped():
    async def run_test():
        registry = ToolRegistry()
        executor = Executor(tool_registry=registry, allowed_tools=[])
        llm = InfiniteLLMProvider()
        
        # Max 5 steps
        loop = AgentLoop(llm_provider=llm, executor=executor, max_steps=5)
        
        state = AgentState(run_id=str(uuid.uuid4()), goal="Loop forever")
        
        final_state = await loop.run(state)
        
        assert final_state.status == AgentStatus.FAILED
        
        # Audit log should have circuit_breaker
        actions = [log["action"] for log in executor.audit_log]
        assert "circuit_breaker" in actions
    asyncio.run(run_test())
