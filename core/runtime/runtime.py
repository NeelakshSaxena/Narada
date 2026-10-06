from providers.llm.ollama import OllamaProvider

class AgentRuntime:
    """
    AgentRuntime: Manages execution, planning, and state.
    """
    def __init__(self):
        self.is_running = False
        self.provider = OllamaProvider()
        
    async def execute_task(self, task: str) -> str:
        # Simple Agent Loop using actual provider
        prompt = f"Goal: {task}\nPlan the steps and output the execution result."
        response = await self.provider.generate(prompt)
        return response.text

class NaradaCore:
    def __init__(self):
        self.agent = AgentRuntime()
        self.is_running = True
        
    def get_status(self):
        return {"status": "ok", "running": self.is_running}
