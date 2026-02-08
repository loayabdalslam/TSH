from tsh.core.agent import Agent
from tsh.tools.file_tools import (
    FileReadTool, FileWriteTool, ListDirTool, FileSearchTool, FileMoveTool, FileDeleteTool
)
from tsh.tools.web_tools import WebSearchTool, WebFetchTool
from tsh.tools.excel_tools import ExcelReadTool
from tsh.tools.media_tools import ImageAnalyzeTool, VideoAnalyzeTool

from tsh.tools.system_tools import ShellTool, WorkspaceSummaryTool

__version__ = "0.1.0"

def get_default_agent(provider="anthropic", model="claude-3-5-sonnet-20241022"):
    """
    Returns a pre-configured TSH agent with all available tools.
    """
    tools = [
        FileReadTool(),
        FileWriteTool(),
        ListDirTool(),
        FileSearchTool(),
        FileMoveTool(),
        FileDeleteTool(),
        WebSearchTool(),
        WebFetchTool(),
        ExcelReadTool(),
        ImageAnalyzeTool(),
        VideoAnalyzeTool(),
        ShellTool(),
        WorkspaceSummaryTool(),
    ]
    return Agent(provider=provider, model=model, tools=tools)

__all__ = ["Agent", "get_default_agent"]
