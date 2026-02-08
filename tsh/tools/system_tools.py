import os
import subprocess
from typing import Dict, Any
from tsh.tools.base import BaseTool, ToolResult

class ShellTool(BaseTool):
    @property
    def name(self) -> str:
        return "execute_shell"

    @property
    def description(self) -> str:
        return "Execute a bash/shell command. Use this for git, npm, or other CLI operations."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The command to execute."}
            },
            "required": ["command"]
        }

    async def execute(self, command: str) -> ToolResult:
        try:
            # Note: In a production environment, you should add safety checks here
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout
            if result.stderr:
                output += f"\nErrors:\n{result.stderr}"
            return ToolResult(content=output if output else "Command executed successfully with no output.")
        except Exception as e:
            return ToolResult(content="", error=str(e))

class WorkspaceSummaryTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_workspace_summary"

    @property
    def description(self) -> str:
        return "Get a summary of the current workspace structure and files."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The root path to summarize. Defaults to '.'"}
            }
        }

    async def execute(self, path: str = ".") -> ToolResult:
        try:
            summary = []
            for root, dirs, files in os.walk(path):
                # Ignore hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                level = root.replace(path, '').count(os.sep)
                indent = ' ' * 4 * (level)
                summary.append(f"{indent}[DIR] {os.path.basename(root)}/")
                subindent = ' ' * 4 * (level + 1)
                for f in files:
                    if not f.startswith('.'):
                        summary.append(f"{subindent}{f}")

            return ToolResult(content="\n".join(summary[:100]) + ("\n..." if len(summary) > 100 else ""))
        except Exception as e:
            return ToolResult(content="", error=str(e))
