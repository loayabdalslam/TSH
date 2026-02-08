import json
import os
import uuid
from typing import List, Dict, Any, Optional, Callable
from tsh.tools.base import BaseTool, ToolResult
from tsh.core.providers import get_provider, BaseProvider
from tsh.core.memory import Memory

class Agent:
    def __init__(
        self,
        provider: str = "anthropic",
        model: str = "claude-3-5-sonnet-20241022",
        tools: List[BaseTool] = None,
        system_prompt: str = None,
        session_id: str = None,
        memory_db: str = "tsh_memory.sql",
        skill_file: str = "Skill.md"
    ):
        self.provider_name = provider
        self.provider: BaseProvider = get_provider(provider)
        self.model = model
        self.tools = tools or []
        self.memory = Memory(db_path=memory_db)
        self.session_id = session_id or str(uuid.uuid4())
        self.memory.create_session(self.session_id)
        self.skill_file = skill_file

        # Load acquired skills from Skill.md if it exists
        acquired_skills = ""
        if os.path.exists(self.skill_file):
            try:
                with open(self.skill_file, "r", encoding="utf-8") as f:
                    acquired_skills = f.read()
            except Exception:
                pass

        self.system_prompt = system_prompt or (
            "You are TSH, an AGI-style agentic personal assistant. You are capable of handling files, "
            "media, web searches, and data analysis. Use your tools effectively to solve user requests. "
            "When using tools, explain what you are doing. Be concise but helpful. "
            "You have access to the whole workspace and can read/write any file types including images and videos.\n\n"
            f"### ACQUIRED SKILLS & KNOWLEDGE (from {self.skill_file}):\n"
            f"{acquired_skills if acquired_skills else 'No skills acquired yet.'}"
        )

    def _get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_dict() for tool in self.tools]

    def _get_history(self) -> List[Dict[str, Any]]:
        return self.memory.get_history(self.session_id)

    async def run(self, prompt: str, on_tool_call: Optional[Callable] = None, on_tool_result: Optional[Callable] = None):
        # Store user message
        self.memory.add_message(self.session_id, "user", prompt)

        while True:
            history = self._get_history()

            response = await self.provider.generate(
                model=self.model,
                messages=history,
                system_prompt=self.system_prompt,
                tools=self._get_tool_schemas()
            )

            # Store assistant response (text + tool calls)
            assistant_content = []
            if response.content:
                assistant_content.append({"type": "text", "text": response.content})

            for tc in response.tool_calls:
                assistant_content.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["input"]
                })

            self.memory.add_message(self.session_id, "assistant", assistant_content)

            if not response.tool_calls:
                return response.content

            # Process tool calls
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["input"]
                tool_id = tool_call["id"]

                if on_tool_call:
                    on_tool_call(tool_name, tool_input)

                # Find the tool
                tool = next((t for t in self.tools if t.name == tool_name), None)
                if not tool:
                    result = ToolResult(content="", error=f"Tool {tool_name} not found")
                else:
                    try:
                        result = await tool.execute(**tool_input)
                    except Exception as e:
                        result = ToolResult(content="", error=str(e))

                if on_tool_result:
                    on_tool_result(result.content if not result.error else f"Error: {result.error}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": result.content if not result.error else f"Error: {result.error}"
                })

            # Store tool results
            self.memory.add_message(self.session_id, "user", tool_results)

    def export_session_to_skill(self, file_path: str = "Skill.md"):
        """Implements 'Session Recording to Skill.md' feature."""
        from datetime import datetime
        history = self._get_history()

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n# Session Record: {self.session_id}\n")
            f.write(f"**Context:** {os.path.basename(os.getcwd())}\n")
            f.write(f"**Date:** {timestamp}\n\n")

            for msg in history:
                role = msg["role"].upper()
                content = msg["content"]

                if role == "USER":
                    # Check if this is a tool result or actual user input
                    is_tool_result = isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict) and content[0].get("type") == "tool_result"

                    if is_tool_result:
                        f.write(f"### 📥 System (Tool Output)\n")
                        for item in content:
                            if item.get("type") == "tool_result":
                                f.write(f"**Tool:** `{item.get('tool_use_id')}`\n")
                                f.write(f"```\n{item['content']}\n```\n\n")
                    else:
                        f.write(f"### 👤 User\n")
                        if isinstance(content, str):
                            f.write(f"{content}\n\n")
                        elif isinstance(content, list):
                             for item in content:
                                f.write(f"{item}\n\n")

                elif role == "ASSISTANT":
                    f.write(f"### 🤖 Agent\n")
                    if isinstance(content, str):
                         f.write(f"{content}\n\n")
                    elif isinstance(content, list):
                        for item in content:
                            if item["type"] == "text":
                                f.write(f"{item['text']}\n\n")
                            elif item["type"] == "tool_use":
                                f.write(f"**⚙️ Tool Call:** `{item['name']}`\n")
                                f.write(f"```json\n{json.dumps(item['input'], indent=2)}\n```\n\n")

            f.write("---\n")
