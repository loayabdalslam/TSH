from PIL import Image
import os
from typing import Dict, Any
from tsh.tools.base import BaseTool, ToolResult

class ImageAnalyzeTool(BaseTool):
    @property
    def name(self) -> str:
        return "analyze_image"

    @property
    def description(self) -> str:
        return "Analyze an image file (photos) to get metadata like dimensions, format, and color mode."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The path to the image file."}
            },
            "required": ["path"]
        }

    async def execute(self, path: str) -> ToolResult:
        try:
            with Image.open(path) as img:
                info = {
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode,
                }

                # ASCII preview
                preview = ""
                try:
                    thumb = img.copy()
                    thumb.thumbnail((40, 20))
                    thumb = thumb.convert("L")
                    chars = "@%#*+=-:. "
                    pixels = thumb.getdata()
                    preview_lines = []
                    for y in range(thumb.size[1]):
                        line = "".join(chars[int(p * (len(chars) - 1) / 255)] for p in pixels[y * thumb.size[0] : (y + 1) * thumb.size[0]])
                        preview_lines.append(line)
                    preview = "\n[Terminal Preview]\n" + "\n".join(preview_lines)
                except Exception:
                    preview = "\n(Preview unavailable)"

            return ToolResult(content=f"Image Metadata for {os.path.basename(path)}: {str(info)}{preview}")
        except Exception as e:
            return ToolResult(content="", error=str(e))

class VideoAnalyzeTool(BaseTool):
    @property
    def name(self) -> str:
        return "analyze_video"

    @property
    def description(self) -> str:
        return "Analyze a video file for basic metadata (size, existence)."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The path to the video file."}
            },
            "required": ["path"]
        }

    async def execute(self, path: str) -> ToolResult:
        try:
            if not os.path.exists(path):
                return ToolResult(content="", error="Video file not found")

            size_mb = os.path.getsize(path) / (1024 * 1024)
            return ToolResult(content=f"Video file '{os.path.basename(path)}' confirmed. Size: {size_mb:.2f} MB.")
        except Exception as e:
            return ToolResult(content="", error=str(e))
