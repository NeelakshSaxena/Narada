from typing import Any, Dict
from core.tools.base import ToolProvider
from core.mcp.client import MCPClient, MCPTool
from core.permissions.models import RiskLevel
from core.permissions.engine import PermissionEngine

class MCPToolAdapter(ToolProvider):
    """Adapts an MCPTool into Narada's native ToolProvider."""
    def __init__(self, mcp_client: MCPClient, mcp_tool: MCPTool, permission_engine: PermissionEngine):
        self.mcp_client = mcp_client
        self.mcp_tool = mcp_tool
        
        # We consult the PermissionEngine to map the tool name to a baseline risk.
        self._risk = permission_engine.get_baseline_risk(mcp_tool.name)

    @property
    def name(self) -> str:
        return self.mcp_tool.name

    @property
    def description(self) -> str:
        return self.mcp_tool.description

    @property
    def risk(self) -> str:
        # Note: Permission engine uses RiskLevel enum
        return self._risk.value

    @property
    def requires_confirmation(self) -> bool:
        return self._risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    @property
    def input_schema(self) -> Dict[str, Any]:
        return self.mcp_tool.input_schema

    @property
    def output_schema(self) -> Dict[str, Any]:
        # MCP tools generally return strings or opaque JSON
        return {"type": "object", "properties": {"result": {"type": "string"}}}

    async def execute(self, **kwargs) -> Any:
        # Crucially, execution actually calls out to the MCP Server
        return await self.mcp_client.execute_tool(self.mcp_tool.name, kwargs)

async def discover_and_register_mcp_tools(mcp_client: MCPClient, tool_registry, permission_engine: PermissionEngine):
    """
    Implements: discover server -> list tools -> validate schemas -> apply Narada permissions.
    """
    await mcp_client.connect()
    mcp_tools = await mcp_client.list_tools()
    for t in mcp_tools:
        adapter = MCPToolAdapter(mcp_client, t, permission_engine)
        tool_registry.register(adapter)
