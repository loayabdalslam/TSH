import os
import httpx
from typing import Dict, Any
from tsh.tools.base import BaseTool, ToolResult

class WebSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for information using DuckDuckGo."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."}
            },
            "required": ["query"]
        }

    async def execute(self, query: str) -> ToolResult:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))

            if not results:
                return ToolResult(content="No results found.")

            formatted_results = []
            for r in results:
                formatted_results.append(f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}\n")

            return ToolResult(content="\n---\n".join(formatted_results))
        except Exception as e:
            return ToolResult(content="", error=str(e))

class WebFetchTool(BaseTool):
    @property
    def name(self) -> str:
        return "fetch_web_page"

    @property
    def description(self) -> str:
        return "Fetch the content of a web page given its URL."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL of the page to fetch."}
            },
            "required": ["url"]
        }

    async def execute(self, url: str) -> ToolResult:
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                content = response.text[:15000]
                return ToolResult(content=f"Content from {url}:\n\n{content}")
        except Exception as e:
            return ToolResult(content="", error=str(e))
