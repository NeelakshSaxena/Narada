import os
from typing import Any, Dict, List, Optional
from core.tools.base import ToolProvider


def resolve_workspace_path(path: str, workspace_root: Optional[str]) -> str:
    """
    Resolve and strictly validate that path is contained within workspace_root.
    Rejects any path traversal or absolute path outside workspace_root.
    """
    clean_path = (path or "").strip()
    if not clean_path:
        if workspace_root:
            return os.path.abspath(workspace_root)
        raise ValueError("Path is required")

    if not workspace_root:
        return os.path.abspath(clean_path)

    workspace_root = os.path.abspath(workspace_root)

    # If relative, resolve against workspace_root
    if not os.path.isabs(clean_path):
        resolved = os.path.abspath(os.path.join(workspace_root, clean_path))
    else:
        resolved = os.path.abspath(clean_path)

    # Strictly check that resolved path is inside workspace_root
    try:
        common = os.path.commonpath([resolved, workspace_root])
    except ValueError:
        # Different drive letters on Windows
        common = ""

    if common != workspace_root:
        raise PermissionError(
            f"Access denied: Path '{path}' is outside the authorized workspace '{workspace_root}'. "
            f"Filesystem operations are strictly confined to the workspace folder."
        )

    return resolved


class FileSystemReadTool(ToolProvider):
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = os.path.abspath(workspace_root) if workspace_root else None

    @property
    def name(self) -> str:
        return "filesystem.read"

    @property
    def description(self) -> str:
        return "Read contents of a file inside the workspace (path must be relative to the workspace or within it)"

    @property
    def risk(self) -> str:
        return "low"

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"content": {"type": "string"}}}

    async def execute(self, **kwargs) -> Any:
        path = kwargs.get("path")
        if not path:
            raise ValueError("Path is required")
        resolved = resolve_workspace_path(path, self.workspace_root)
        if not os.path.exists(resolved):
            raise FileNotFoundError(f"File not found: {resolved}")
        if os.path.isdir(resolved):
            raise IsADirectoryError(f"Target is a directory, not a file: {resolved}")
        with open(resolved, "r", encoding="utf-8") as f:
            return f.read()


class FileSystemWriteTool(ToolProvider):
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = os.path.abspath(workspace_root) if workspace_root else None

    @property
    def name(self) -> str:
        return "filesystem.write"

    @property
    def description(self) -> str:
        return (
            "Write contents to a file inside the workspace. "
            "Categorized subfolders available: documents/, code/, data/, outputs/, temp/."
        )

    @property
    def risk(self) -> str:
        return "high"

    @property
    def requires_confirmation(self) -> bool:
        return True

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative file path within workspace, e.g. documents/note.txt"},
                "content": {"type": "string", "description": "Text content to write"}
            },
            "required": ["path", "content"]
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"success": {"type": "boolean"}}}

    async def execute(self, **kwargs) -> Any:
        path = kwargs.get("path")
        content = kwargs.get("content")
        if not path:
            raise ValueError("Path is required")
        resolved = resolve_workspace_path(path, self.workspace_root)
        parent = os.path.dirname(resolved)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(resolved, "w", encoding="utf-8") as f:
            f.write(content or "")
        return True


class FileSystemListTool(ToolProvider):
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = os.path.abspath(workspace_root) if workspace_root else None

    @property
    def name(self) -> str:
        return "filesystem.list"

    @property
    def description(self) -> str:
        return "List files and category directories within the workspace (path is optional, defaults to workspace root)"

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
            "properties": {
                "path": {"type": "string", "description": "Subdirectory to list (leave empty for workspace root)"}
            }
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"entries": {"type": "array"}}}

    async def execute(self, **kwargs) -> Any:
        rel_path = kwargs.get("path") or ""
        resolved = resolve_workspace_path(rel_path, self.workspace_root)
        if not os.path.exists(resolved):
            raise FileNotFoundError(f"Directory not found: {resolved}")
        if not os.path.isdir(resolved):
            raise NotADirectoryError(f"Target is not a directory: {resolved}")
        entries = []
        for entry in sorted(os.listdir(resolved)):
            full = os.path.join(resolved, entry)
            is_dir = os.path.isdir(full)
            entries.append({
                "name": entry,
                "type": "directory" if is_dir else "file"
            })
        return entries

