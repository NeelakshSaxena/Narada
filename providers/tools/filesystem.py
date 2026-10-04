import os
from typing import Any, Dict
from core.tools.base import ToolProvider

class FileSystemReadTool(ToolProvider):
    @property
    def name(self) -> str:
        return "filesystem.read"

    @property
    def description(self) -> str:
        return "Read contents of a file"

    @property
    def risk(self) -> str:
        return "low"

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"path": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"content": {"type": "string"}}}

    async def execute(self, **kwargs) -> Any:
        path = kwargs.get("path")
        if not path:
            raise ValueError("Path is required")
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

class FileSystemWriteTool(ToolProvider):
    @property
    def name(self) -> str:
        return "filesystem.write"

    @property
    def description(self) -> str:
        return "Write contents to a file"

    @property
    def risk(self) -> str:
        return "high"

    @property
    def requires_confirmation(self) -> bool:
        return True

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"success": {"type": "boolean"}}}

    async def execute(self, **kwargs) -> Any:
        path = kwargs.get("path")
        content = kwargs.get("content")
        if not path:
            raise ValueError("Path is required")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content or "")
        return True
