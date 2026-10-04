from typing import Any, Dict
from core.tools.base import ToolProvider
import urllib.request
import urllib.error

class WebSearchTool(ToolProvider):
    @property
    def name(self) -> str:
        return "web.search"

    @property
    def description(self) -> str:
        return "Search the web for a query"

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
        return {"type": "object", "properties": {"results": {"type": "array"}}}

    async def execute(self, **kwargs) -> Any:
        query = kwargs.get("query")
        if not query:
            raise ValueError("Query is required")
        # Lightweight mockup of search engine
        return [{"title": f"Result for {query}", "url": f"http://example.com/search?q={query.replace(' ', '+')}"}]

class WebOpenTool(ToolProvider):
    @property
    def name(self) -> str:
        return "web.open"

    @property
    def description(self) -> str:
        return "Open a web page and extract its text content"

    @property
    def risk(self) -> str:
        return "low"

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"url": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"content": {"type": "string"}}}

    async def execute(self, **kwargs) -> Any:
        url = kwargs.get("url")
        if not url:
            raise ValueError("URL is required")
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode('utf-8')
                return html[:1000] # Lightweight extraction
        except Exception as e:
            if "example.com" in url:
                return "Mock extracted content about the topic."
            return f"Error fetching {url}: {str(e)}"
