from typing import Any, Dict
from core.tools.base import ToolProvider

class MemoryReadTool(ToolProvider):
    def __init__(self, memory_store):
        self.memory = memory_store

    @property
    def name(self) -> str:
        return "memory.read"

    @property
    def description(self) -> str:
        return "Reads all stored memories, contextual details, and conversation logs."

    @property
    def risk(self) -> str:
        return "low"

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "memories": {"type": "array", "items": {"type": "string"}}
            }
        }

    async def execute(self, **kwargs) -> Any:
        try:
            records = await self.memory.get_all_metadata()
            return [f"ID: {r['id']} | Content: {r.get('text')} | Meta: {r.get('metadata')}" for r in records]
        except Exception as e:
            return f"Failed to read memory: {e}"
