"""Built-in tool set shipped with Nārada."""
from typing import List

from core.tools.base import ToolProvider


def builtin_tools() -> List[ToolProvider]:
    """Instantiate every built-in tool that can be loaded in this environment."""
    tools: List[ToolProvider] = []
    try:
        from providers.tools.filesystem import FileSystemReadTool, FileSystemWriteTool
        tools += [FileSystemReadTool(), FileSystemWriteTool()]
    except ImportError:
        pass
    try:
        from providers.tools.web import WebSearchTool, WebOpenTool
        tools += [WebSearchTool(), WebOpenTool()]
    except ImportError:
        pass
    return tools
