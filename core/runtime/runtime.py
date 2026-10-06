from providers.llm.ollama import OllamaProvider
from core.agent.policy import PolicyInjector

class AgentRuntime:
    """
    AgentRuntime: Manages execution, planning, and state.
    """
    def __init__(self):
        self.is_running = False
        self.provider = OllamaProvider()
        self.policy_injector = PolicyInjector()
        
    async def execute_task(self, task: str) -> str:
        # Simple Agent Loop using actual provider
        base_prompt = f"Goal: {task}\nPlan the steps and output the execution result."
        prompt = self.policy_injector.inject(base_prompt)
        response = await self.provider.generate(prompt)
        return response.text

from core.scheduler.scheduler import LocalScheduler
from core.events.redis_bus import RedisMock
from core.storage.postgres import PostgresConnectionPool, PostgresCanonicalMemoryStore

class NaradaCore:
    def __init__(self):
        self.agent = AgentRuntime()
        self.redis = RedisMock()
        self.scheduler = LocalScheduler(self.redis)
        self.pool = PostgresConnectionPool("postgres://fake:5432")
        self.memory = PostgresCanonicalMemoryStore(self.pool)
        self.is_running = False
        
    async def boot(self):
        self.is_running = True
        await self.pool.connect()
        await self.scheduler.start()
        
    def get_status(self):
        return {"status": "ok", "running": self.is_running}
