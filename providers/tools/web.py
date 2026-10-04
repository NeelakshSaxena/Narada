from typing import Any, Dict
from core.tools.base import ToolProvider

class WebSearchTool(ToolProvider):
    @property
    def name(self) -> str:
        return "web.search"

    @property
    def description(self) -> str:
        return "Search the web"

    @property
    def risk(self) -> str:
        return "low"

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"query": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"results": {"type": "string"}}}

    async def execute(self, **kwargs) -> Any:
        query = kwargs.get("query")
        if not query:
            raise ValueError("Query is required")
        # Stubbing the actual web search
        return f"Mock search results for: {query}"
