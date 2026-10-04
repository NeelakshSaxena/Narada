from datetime import datetime
from typing import Any
from core.agent.state import AgentState, AgentStatus
from core.agent.executor import Executor
from core.providers.base import LLMProvider

class AgentLoop:
    def __init__(self, llm_provider: LLMProvider, executor: Executor):
        self.llm = llm_provider
        self.executor = executor

    async def run(self, state: AgentState) -> AgentState:
        state.status = AgentStatus.RUNNING
        self._update_timestamp(state)

        while state.status != AgentStatus.COMPLETED and state.status != AgentStatus.FAILED:
            if state.status == AgentStatus.RUNNING:
                state.status = AgentStatus.PLANNING

            elif state.status == AgentStatus.PLANNING:
                # LLM proposes plan
                response = await self.llm.generate(f"Create plan for goal: {state.goal}")
                state.plan = [response.text]
                state.status = AgentStatus.EXECUTING

            elif state.status == AgentStatus.EXECUTING:
                if state.current_step >= len(state.plan):
                    state.status = AgentStatus.DECIDING
                    continue

                # LLM proposes action based on plan
                response = await self.llm.generate("Propose action")
                
                action_name = response.metadata.get("action_name", "unknown")
                action_kwargs = response.metadata.get("action_kwargs", {})
                
                state.actions.append({"name": action_name, "kwargs": action_kwargs})
                
                # Execute through strict executor boundary
                result = await self.executor.execute(action_name, **action_kwargs)
                state.observations.append(result)
                state.current_step += 1
                state.status = AgentStatus.OBSERVING

            elif state.status == AgentStatus.OBSERVING:
                # LLM observes result
                await self.llm.generate(f"Observe: {state.observations[-1]}")
                state.status = AgentStatus.DECIDING

            elif state.status == AgentStatus.DECIDING:
                # Decide next steps
                response = await self.llm.generate("Decide next state")
                decision = response.metadata.get("decision", "COMPLETE")
                state.decision = decision

                if decision == "COMPLETE":
                    state.status = AgentStatus.COMPLETED
                else:
                    state.status = AgentStatus.EXECUTING

            self._update_timestamp(state)

        return state

    def _update_timestamp(self, state: AgentState):
        state.updated_at = datetime.utcnow()
