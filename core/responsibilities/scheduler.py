import asyncio
from typing import List, Callable, Awaitable
from core.responsibilities.models import Responsibility
from core.skills.base import SkillRegistry
from core.agent.executor import Executor
from core.tools.registry import ToolRegistry

class ResponsibilityScheduler:
    def __init__(self, skill_registry: SkillRegistry, tool_registry: ToolRegistry):
        self.responsibilities: List[Responsibility] = []
        self.skill_registry = skill_registry
        self.tool_registry = tool_registry
        self._running = False
        self._task = None
        self._running_tasks: dict[str, asyncio.Task] = {}

    def add_responsibility(self, resp: Responsibility):
        self.responsibilities.append(resp)

    def generate_self_contained_prompt(self, resp: Responsibility) -> str:
        skills_prompts = []
        for skill_name in resp.skills:
            try:
                skills_prompts.append(self.skill_registry.get_prompt_for_skill(skill_name))
            except ValueError:
                pass

        prompt = f"""
        [RESPONSIBILITY EXECUTION]
        GOAL: {resp.goal}
        
        PREVIOUS STATE:
        {resp.memory_state}
        
        DELIVERY TARGET: {resp.delivery_target}
        
        SKILLS & WORKFLOWS:
        {' '.join(skills_prompts)}
        
        INSTRUCTIONS:
        Execute the goal completely self-contained. Do not wait for user input.
        Compare against the previous state. If there is a meaningful change, 
        summarize and deliver to the target. Otherwise, update state and exit.
        """
        return prompt

    async def execute_responsibility(self, resp: Responsibility, llm_callback: Callable[[str], Awaitable[str]]):
        """
        Creates a fresh execution context and runs the agent loop.
        """
        fresh_executor = Executor(
            tool_registry=self.tool_registry, 
            skill_registry=self.skill_registry, 
            allowed_tools=resp.permissions
        )
        
        prompt = self.generate_self_contained_prompt(resp)
        result = await llm_callback(prompt)
        resp.memory_state["last_result"] = result
        resp.mark_executed()

    def _start_execution(self, resp: Responsibility, llm_callback: Callable[[str], Awaitable[str]]):
        if resp.id in self._running_tasks:
            return
            
        async def run_and_cleanup():
            try:
                await self.execute_responsibility(resp, llm_callback)
            except asyncio.CancelledError:
                resp.memory_state["last_result"] = "Cancelled"
            finally:
                if resp.id in self._running_tasks:
                    del self._running_tasks[resp.id]
                    
        self._running_tasks[resp.id] = asyncio.create_task(run_and_cleanup())

    async def _loop(self, llm_callback: Callable[[str], Awaitable[str]]):
        while self._running:
            for resp in self.responsibilities:
                # Propagate cancellation if task is running and resp is cancelled
                if resp.status.name in ["CANCELLED", "STOPPED", "PAUSED"] and resp.id in self._running_tasks:
                    self._running_tasks[resp.id].cancel()

                if resp.is_due():
                    self._start_execution(resp, llm_callback)
            await asyncio.sleep(0.1)

    def start(self, llm_callback: Callable[[str], Awaitable[str]]):
        self._running = True
        self._task = asyncio.create_task(self._loop(llm_callback))

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
