import os
import json
from core.providers.base import LLMProvider
from core.agent.policy import PolicyInjector
from core.agent.executor import Executor

class AgentRuntime:
    """
    AgentRuntime: Manages execution, planning, and state.
    """
    def __init__(self, provider: LLMProvider, user_name: str = "User", executor: Executor = None, workspace: str = None):
        self.is_running = False
        self.provider = provider
        self.user_name = user_name
        self.executor = executor
        self.workspace = os.path.abspath(workspace or os.environ.get("NARADA_WORKSPACE") or os.getcwd())
        self.policy_injector = PolicyInjector(workspace_root=self.workspace)
        
    async def execute_task(self, task: str) -> str:
        # Simple Agent Loop using actual provider
        base_prompt = (
            f"Goal: {task}\n"
            f"Workspace: {self.workspace}\n"
            f"Plan the steps and output the execution result."
        )
        prompt = self.policy_injector.inject(base_prompt)
        response = await self.provider.generate(prompt)
        return response.text

    async def interact(self, messages: list) -> str:
        # Conversational interaction with the agent
        system_prompt = self.policy_injector.inject(
            f"You are NĀRADA, a personal autonomous agent. "
            f"You can engage in conversation, but you are also capable of taking on responsibilities and executing multi-step tasks. "
            f"Your operator's name is {self.user_name}. Always refer to them by their name if appropriate.\n"
            f"Your active workspace path is: {self.workspace}. "
            f"All filesystem read, write, and list operations are strictly confined within this workspace folder. "
            f"When organizing files, use the designated categories:\n"
            f" - documents/ (notes, text, reports, drafts)\n"
            f" - code/ (scripts, snippets, automation programs)\n"
            f" - data/ (datasets, raw JSON, CSV inputs)\n"
            f" - outputs/ (generated deliverables, exports, final summaries)\n"
            f" - temp/ (temporary scratchpad files)\n"
            f"Always resolve any workspace files or actions within this directory."
        )
        
        # Ensure we don't duplicate system prompts, just prepend ours
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Check if the user is confirming or approving a pending action
        if self.executor and getattr(self.executor, "pending_actions", None):
            last_user_msg = next((m.get("content", "").strip() for m in reversed(messages) if m.get("role") == "user"), "")
            if last_user_msg.lower().startswith("/approve") or last_user_msg.lower() in ("yes", "approve", "approved", "proceed", "confirm", "go ahead"):
                app_id = None
                if last_user_msg.lower().startswith("/approve"):
                    parts = last_user_msg.split(" ", 1)
                    if len(parts) > 1 and parts[1].strip():
                        app_id = parts[1].strip()
                
                result = await self.executor.execute_pending(app_id)
                if isinstance(result, dict) and result.get("status") == "SUCCESS":
                    full_messages.append({
                        "role": "system",
                        "content": f"The user approved the pending action. Execution result: {result.get('result')}. Inform the user that the action was approved and successfully completed."
                    })
                    confirmation_response = await self.provider.generate("", messages=full_messages, tools=None)
                    return confirmation_response.text
                elif isinstance(result, dict) and result.get("status") == "FAILED":
                    return f"Approval execution failed: {result.get('error')}"

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
            has_pending_approval = False
            for call in tool_calls:
                call_id = call.get("id")
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
                    
                    if isinstance(result, dict) and result.get("status") == "PENDING_APPROVAL":
                        has_pending_approval = True

                    # Convert result to string if it's not
                    if not isinstance(result, str):
                        result = json.dumps(result, default=str)
                        
                    tool_msg = {
                        "role": "tool",
                        "name": name,
                        "content": result
                    }
                    if call_id:
                        tool_msg["tool_call_id"] = call_id
                    full_messages.append(tool_msg)
                    
            if has_pending_approval:
                # Action requires approval -> Pause and ask the user for confirmation instead of looping
                full_messages.append({
                    "role": "system",
                    "content": (
                        "The tool execution is paused because it requires human approval. "
                        "Do not call any more tools. "
                        "Clearly inform the user about the action you want to take (including relevant details like file path, content summary, or command, and that they can reply 'yes' or type '/approve' to proceed) and ask for their confirmation."
                    )
                })
                explanation_response = await self.provider.generate("", messages=full_messages, tools=None)
                return explanation_response.text
                    
        return "I've reached the maximum number of iterations while thinking."

from core.scheduler.scheduler import LocalScheduler
from core.events.redis_bus import RedisMock
from core.storage.postgres import PostgresConnectionPool, PostgresCanonicalMemoryStore
from core.tools.registry import ToolRegistry
from core.permissions.engine import PermissionEngine
from providers.tools.builtin import builtin_tools
from providers.tools.memory import MemoryReadTool

def init_workspace_structure(workspace_path: str) -> None:
    """Ensure the workspace root and category directories exist."""
    categories = ["documents", "code", "data", "outputs", "temp"]
    os.makedirs(workspace_path, exist_ok=True)
    for cat in categories:
        cat_dir = os.path.join(workspace_path, cat)
        os.makedirs(cat_dir, exist_ok=True)


class NaradaCore:
    def __init__(self, provider: LLMProvider, user_name: str = "User", workspace: str = None, auto_approve_writes: bool = False):
        if workspace:
            self.workspace = os.path.abspath(workspace)
        elif os.environ.get("NARADA_WORKSPACE"):
            self.workspace = os.path.abspath(os.environ["NARADA_WORKSPACE"])
        elif os.path.isdir(os.path.join(os.getcwd(), "workspace")):
            self.workspace = os.path.abspath(os.path.join(os.getcwd(), "workspace"))
        else:
            self.workspace = os.path.abspath(os.getcwd())
            
        init_workspace_structure(self.workspace)
        self.redis = RedisMock()
        self.scheduler = LocalScheduler(self.redis)
        self.pool = PostgresConnectionPool("postgres://fake:5432")
        self.memory = PostgresCanonicalMemoryStore(self.pool)
        
        self.tool_registry = ToolRegistry()
        for t in builtin_tools(workspace_root=self.workspace):
            self.tool_registry.register(t)
        self.tool_registry.register(MemoryReadTool(self.memory))
        
        self.permission_engine = PermissionEngine(auto_approve_writes=auto_approve_writes)
        allowed_tools = list(self.tool_registry._tools.keys())
        self.executor = Executor(self.tool_registry, self.permission_engine, allowed_tools=allowed_tools)
        
        self.agent = AgentRuntime(provider, user_name=user_name, executor=self.executor, workspace=self.workspace)
        self.is_running = False

    async def approve_pending(self, approval_id: str = None):
        """Approve and execute a pending action."""
        if not self.executor:
            return {"status": "FAILED", "error": "No executor configured"}
        return await self.executor.execute_pending(approval_id)
        
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
            "workspace": self.workspace,
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
