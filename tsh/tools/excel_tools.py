import pandas as pd
from typing import Dict, Any
from tsh.tools.base import BaseTool, ToolResult

class ExcelReadTool(BaseTool):
    @property
    def name(self) -> str:
        return "read_excel"

    @property
    def description(self) -> str:
        return "Read an Excel file (.xlsx, .xls) and return its content summary."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The path to the Excel file."}
            },
            "required": ["path"]
        }

    async def execute(self, path: str) -> ToolResult:
        try:
            df = pd.read_excel(path)
            summary = {
                "columns": df.columns.tolist(),
                "shape": df.shape,
                "head": df.head(5).to_dict(orient="records")
            }
            return ToolResult(content=f"Excel Data Summary:\n{str(summary)}")
        except Exception as e:
            return ToolResult(content="", error=str(e))
