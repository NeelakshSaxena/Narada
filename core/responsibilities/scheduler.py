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
        # Create a fresh executor for isolated session state
        fresh_executor = Executor(
            tool_registry=self.tool_registry, 
            skill_registry=self.skill_registry, 
            allowed_tools=resp.permissions
        )
        
        prompt = self.generate_self_contained_prompt(resp)
        
        # In a full system, this invokes the LLM. Here we simulate the LLM call.
        result = await llm_callback(prompt)
        
        # Update memory state (in reality, parsed from LLM JSON output)
        resp.memory_state["last_result"] = result
        resp.mark_executed()

    async def _loop(self, llm_callback: Callable[[str], Awaitable[str]]):
        while self._running:
            for resp in self.responsibilities:
                if resp.is_due():
                    await self.execute_responsibility(resp, llm_callback)
            await asyncio.sleep(1) # simple poll

    def start(self, llm_callback: Callable[[str], Awaitable[str]]):
        self._running = True
        self._task = asyncio.create_task(self._loop(llm_callback))

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
