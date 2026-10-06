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
        
    async def get_status(self):
        # Check DB
        db_status = "OFFLINE"
        if getattr(self.pool, "connected", False):
            db_status = "READY"
            
        # Check Redis (mock)
        redis_status = "READY" if self.redis else "OFFLINE"
        
        status = "READY" if (db_status == "READY" and redis_status == "READY" and self.is_running) else "DEGRADED"
        if not self.is_running:
            status = "OFFLINE"
            
        return {
            "status": status,
            "running": self.is_running,
            "components": {
                "db": db_status,
                "redis": redis_status,
                "api": "READY" if self.is_running else "OFFLINE"
            },
            "llm": {
                "provider": self.agent.provider.__class__.__name__.replace("Provider", ""),
                "model": getattr(self.agent.provider, "model", "unknown")
            }
        }
