"""Built-in tool set shipped with Nārada."""
from typing import List, Optional

from core.tools.base import ToolProvider


def builtin_tools(workspace_root: Optional[str] = None) -> List[ToolProvider]:
    """Instantiate every built-in tool that can be loaded in this environment."""
    tools: List[ToolProvider] = []
    try:
        from providers.tools.filesystem import FileSystemReadTool, FileSystemWriteTool, FileSystemListTool
        tools += [
            FileSystemReadTool(workspace_root=workspace_root),
            FileSystemWriteTool(workspace_root=workspace_root),
            FileSystemListTool(workspace_root=workspace_root),
        ]
    except ImportError:
        pass
    try:
        from providers.tools.web import WebSearchTool, WebOpenTool
        tools += [WebSearchTool(), WebOpenTool()]
    except ImportError:
        pass
    return tools
