from core.providers.base import LLMProvider
from core.agent.policy import PolicyInjector
from core.agent.executor import Executor
import json

class AgentRuntime:
    """
    AgentRuntime: Manages execution, planning, and state.
    """
    def __init__(self, provider: LLMProvider, user_name: str = "User", executor: Executor = None):
        self.is_running = False
        self.provider = provider
        self.user_name = user_name
        self.executor = executor
        self.policy_injector = PolicyInjector()
        
    async def execute_task(self, task: str) -> str:
        # Simple Agent Loop using actual provider
        base_prompt = f"Goal: {task}\nPlan the steps and output the execution result."
        prompt = self.policy_injector.inject(base_prompt)
        response = await self.provider.generate(prompt)
        return response.text

    async def interact(self, messages: list) -> str:
        # Conversational interaction with the agent
        system_prompt = self.policy_injector.inject(
            f"You are NĀRADA, a personal autonomous agent. "
            f"You can engage in conversation, but you are also capable of taking on responsibilities and executing multi-step tasks. "
            f"Your operator's name is {self.user_name}. Always refer to them by their name if appropriate."
        )
        
        # Ensure we don't duplicate system prompts, just prepend ours
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Prepare tools array for OpenAI-compatible schema
        tools = []
        if self.executor and getattr(self.executor, 'tool_registry', None):
            for name, tool in self.executor.tool_registry._tools.items():
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema
                    }
                })
        
        max_iterations = 5
        for i in range(max_iterations):
            response = await self.provider.generate("", messages=full_messages, tools=tools if tools else None)
            
            tool_calls = response.metadata.get("tool_calls", [])
            if not tool_calls:
                return response.text
                
            # Append assistant message with both text and tool_calls
            if response.text or tool_calls:
                full_messages.append({
                    "role": "assistant", 
                    "content": response.text,
                    "tool_calls": tool_calls
                })
            
            # Execute tools
            for call in tool_calls:
                fn = call.get("function", {})
                name = fn.get("name")
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except:
                        args = {}
                        
                if name:
                    if self.executor:
                        result = await self.executor.execute(name, **args)
                    else:
                        result = f"Error: Tool {name} cannot be executed because no executor is configured."
                    
                    # Convert result to string if it's not
                    if not isinstance(result, str):
                        result = json.dumps(result, default=str)
                        
                    full_messages.append({
                        "role": "tool",
                        "name": name,
                        "content": result
                    })
                    
        return "I've reached the maximum number of iterations while thinking."

from core.scheduler.scheduler import LocalScheduler
from core.events.redis_bus import RedisMock
from core.storage.postgres import PostgresConnectionPool, PostgresCanonicalMemoryStore
from core.tools.registry import ToolRegistry
from core.permissions.engine import PermissionEngine
from providers.tools.builtin import builtin_tools
from providers.tools.memory import MemoryReadTool

class NaradaCore:
    def __init__(self, provider: LLMProvider, user_name: str = "User"):
        self.redis = RedisMock()
        self.scheduler = LocalScheduler(self.redis)
        self.pool = PostgresConnectionPool("postgres://fake:5432")
        self.memory = PostgresCanonicalMemoryStore(self.pool)
        
        self.tool_registry = ToolRegistry()
        for t in builtin_tools():
            self.tool_registry.register(t)
        self.tool_registry.register(MemoryReadTool(self.memory))
        
        self.permission_engine = PermissionEngine()
        allowed_tools = list(self.tool_registry._tools.keys())
        self.executor = Executor(self.tool_registry, self.permission_engine, allowed_tools=allowed_tools)
        
        self.agent = AgentRuntime(provider, user_name=user_name, executor=self.executor)
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
