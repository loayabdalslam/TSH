import os
import shutil
import glob
from typing import Dict, Any, List
from tsh.tools.base import BaseTool, ToolResult

class FileReadTool(BaseTool):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file at a given path. Supports text files."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The absolute or relative path to the file."}
            },
            "required": ["path"]
        }

    async def execute(self, path: str) -> ToolResult:
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return ToolResult(content=content)
        except Exception as e:
            return ToolResult(content="", error=str(e))

class FileWriteTool(BaseTool):
    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file at a given path. Creates directories if they don't exist."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The path to the file."},
                "content": {"type": "string", "description": "The content to write."}
            },
            "required": ["path", "content"]
        }

    async def execute(self, path: str, content: str) -> ToolResult:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return ToolResult(content=f"Successfully wrote to {path}")
        except Exception as e:
            return ToolResult(content="", error=str(e))

class ListDirTool(BaseTool):
    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return "List files and directories in a given path."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The path to list. Defaults to '.'"}
            }
        }

    async def execute(self, path: str = ".") -> ToolResult:
        try:
            items = os.listdir(path)
            res = []
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    res.append(f"[DIR] {item}")
                else:
                    res.append(f"[FILE] {item}")
            return ToolResult(content="\n".join(res))
        except Exception as e:
            return ToolResult(content="", error=str(e))

class FileSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "search_files"

    @property
    def description(self) -> str:
        return "Search for files using a glob pattern (e.g., '**/*.py')."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "The glob pattern to search for."},
                "root_dir": {"type": "string", "description": "The directory to start searching from. Defaults to '.'"}
            },
            "required": ["pattern"]
        }

    async def execute(self, pattern: str, root_dir: str = ".") -> ToolResult:
        try:
            matches = glob.glob(os.path.join(root_dir, pattern), recursive=True)
            return ToolResult(content="\n".join(matches) if matches else "No matches found.")
        except Exception as e:
            return ToolResult(content="", error=str(e))

class FileMoveTool(BaseTool):
    @property
    def name(self) -> str:
        return "move_file"

    @property
    def description(self) -> str:
        return "Move or rename a file or directory."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "src": {"type": "string", "description": "Source path."},
                "dst": {"type": "string", "description": "Destination path."}
            },
            "required": ["src", "dst"]
        }

    async def execute(self, src: str, dst: str) -> ToolResult:
        try:
            shutil.move(src, dst)
            return ToolResult(content=f"Moved {src} to {dst}")
        except Exception as e:
            return ToolResult(content="", error=str(e))

class FileDeleteTool(BaseTool):
    @property
    def name(self) -> str:
        return "delete_file"

    @property
    def description(self) -> str:
        return "Delete a file or directory."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The path to the file or directory to delete."}
            },
            "required": ["path"]
        }

    async def execute(self, path: str) -> ToolResult:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return ToolResult(content=f"Deleted {path}")
        except Exception as e:
            return ToolResult(content="", error=str(e))
