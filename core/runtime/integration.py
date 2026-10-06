from typing import Any, Dict

class EndToEndFlow:
    def __init__(
        self,
        responsibility_manager: Any,
        skill_registry: Any,
        agent_executor: Any,
        memory_store: Any,
        channel_manager: Any
    ):
        self.responsibilities = responsibility_manager
        self.skills = skill_registry
        self.agent = agent_executor
        self.memory = memory_store
        self.channels = channel_manager

    async def execute_flow(self, user_id: str, responsibility_id: str, event_data: Dict[str, Any]):
        """
        USER -> RESPONSIBILITY -> SKILL -> TASK -> AGENT -> TOOLS -> EVENTS -> MEMORY -> DELIVERY
        """
        # 1. Responsibility
        responsibility = await self.responsibilities.get(responsibility_id)
        if not responsibility:
            raise ValueError(f"Responsibility {responsibility_id} not found.")

        # 2. Skill
        skill = await self.skills.get_skill(responsibility.required_skill)
        if not skill:
            raise ValueError(f"Skill {responsibility.required_skill} not found.")

        # 3. Task (Build context)
        task_context = {
            "responsibility": responsibility.goal,
            "skill_instructions": skill.instructions,
            "event": event_data
        }

        # 4 & 5. Agent & Tools (Execute)
        execution_result = await self.agent.execute(task_context, tools=responsibility.allowed_tools)

        # 6. Events / Memory
        await self.memory.store_execution(
            user_id=user_id,
            responsibility_id=responsibility_id,
            event=event_data,
            result=execution_result
        )

        # 7. Delivery
        if execution_result.requires_delivery:
            provider = self.channels.get_provider(responsibility.delivery_channel)
            await provider.send_text(execution_result.delivery_message)

        return execution_result
