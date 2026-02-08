import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import anthropic
import openai
import google.generativeai as genai
from google.generativeai.types import content_types
from collections.abc import Iterable
from pydantic import BaseModel

try:
    import litellm
except ImportError:
    litellm = None

class ProviderResponse(BaseModel):
    content: str
    tool_calls: List[Dict[str, Any]] = []
    raw_response: Any = None

class BaseProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        tools: List[Dict[str, Any]]
    ) -> ProviderResponse:
        pass

class LiteLLMProvider(BaseProvider):
    def __init__(self):
        if not litellm:
            raise ImportError("litellm is not installed. Please install it with `pip install litellm`.")

    async def generate(self, model: str, messages: List[Dict[str, Any]], system_prompt: str, tools: List[Dict[str, Any]]) -> ProviderResponse:
        # Prepare tools in OpenAI format
        openai_tools = []
        for t in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"]
                }
            })

        # Inject system prompt
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        response = await litellm.acompletion(
            model=model,
            messages=full_messages,
            tools=openai_tools if openai_tools else None,
            tool_choice="auto" if openai_tools else None
        )

        message = response.choices[0].message
        text_content = message.content or ""
        tool_calls = []

        if message.tool_calls:
            for tc in message.tool_calls:
                import json
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {} # Handle parsing error or empty args

                tool_calls.append({
                    "id": tc.id or f"call_{tc.function.name}",
                    "name": tc.function.name,
                    "input": args
                })

        return ProviderResponse(
            content=text_content,
            tool_calls=tool_calls,
            raw_response=response
        )

class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    async def generate(self, model: str, messages: List[Dict[str, Any]], system_prompt: str, tools: List[Dict[str, Any]]) -> ProviderResponse:
        # Anthropic uses a specific format for system prompt and messages
        response = self.client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

        text_content = ""
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                text_content += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })

        return ProviderResponse(
            content=text_content,
            tool_calls=tool_calls,
            raw_response=response
        )

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

        # Fallback for local providers that might not need a key, but the client requires one
        if not self.api_key and self.base_url:
            self.api_key = "dummy-key"

        if not self.api_key:
            raise ValueError("API Key not found (OPENAI_API_KEY)")

        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    async def generate(self, model: str, messages: List[Dict[str, Any]], system_prompt: str, tools: List[Dict[str, Any]]) -> ProviderResponse:
        # OpenAI style tools
        openai_tools = []
        for t in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"]
                }
            })

        full_messages = [{"role": "system", "content": system_prompt}] + messages

        response = self.client.chat.completions.create(
            model=model,
            messages=full_messages,
            tools=openai_tools if openai_tools else None,
            tool_choice="auto" if openai_tools else None
        )

        message = response.choices[0].message
        text_content = message.content or ""
        tool_calls = []

        if message.tool_calls:
            for tc in message.tool_calls:
                import json
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "input": json.loads(tc.function.arguments)
                })

        return ProviderResponse(
            content=text_content,
            tool_calls=tool_calls,
            raw_response=response
        )

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        genai.configure(api_key=self.api_key)

    async def generate(self, model: str, messages: List[Dict[str, Any]], system_prompt: str, tools: List[Dict[str, Any]]) -> ProviderResponse:
        # Convert tools to Gemini format
        # Gemini expects a specific tool declaration format
        gemini_tools = []
        # Note: Gemini python SDK handles tool declarations via 'tools' argument in GenerativeModel
        # We need to convert our JSON schema to what Gemini expects or pass as functions if possible.
        # However, the SDK also accepts a list of tool definitions.
        # For simplicity in this implementation, we'll try to map the schema or just use the OpenAI provider for Gemini
        # via their OpenAI-compatible endpoint if available, but here we are using the native SDK.

        # Native SDK tool mapping is complex. Let's simplify by using the tool definitions as function declarations.
        function_declarations = []
        for t in tools:
            function_declarations.append({
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"]
            })

        gemini_tools = [{"function_declarations": function_declarations}] if function_declarations else None

        # Create the model
        generative_model = genai.GenerativeModel(
            model_name=model,
            tools=gemini_tools,
            system_instruction=system_prompt
        )

        # Convert messages to Gemini format
        # Gemini uses 'user' and 'model' roles
        gemini_history = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            parts = []

            if isinstance(msg["content"], str):
                parts.append(msg["content"])
            elif isinstance(msg["content"], list):
                for item in msg["content"]:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            parts.append(item["text"])
                        elif item.get("type") == "tool_use":
                            # Reconstruct tool use for history?
                            # Gemini history management is tricky with manual tool calls.
                            # We might need to handle this carefully.
                            # For now, let's append a text representation if it's complex
                            pass
                        elif item.get("type") == "tool_result":
                             parts.append(f"Tool Result ({item.get('tool_use_id')}): {item['content']}")

            if parts:
                gemini_history.append({"role": role, "parts": parts})

        # Generate content
        # For the last message, we don't put it in history, we send it
        last_message = gemini_history.pop() if gemini_history else None

        chat = generative_model.start_chat(history=gemini_history)

        if last_message:
            response = chat.send_message(last_message["parts"])
        else:
             # Fallback if no messages?
             return ProviderResponse(content="Error: No messages to send.")

        # Parse response
        text_content = ""
        tool_calls = []

        for part in response.parts:
            if part.text:
                text_content += part.text
            if part.function_call:
                tool_calls.append({
                    "id": "gemini_tool_" + part.function_call.name, # Gemini doesn't give IDs easily
                    "name": part.function_call.name,
                    "input": dict(part.function_call.args)
                })

        return ProviderResponse(
            content=text_content,
            tool_calls=tool_calls,
            raw_response=response
        )

def get_provider(provider_name: str) -> BaseProvider:
    provider_name = provider_name.lower()

    if provider_name == "litellm":
        return LiteLLMProvider()

    elif provider_name == "anthropic":
        return AnthropicProvider()

    elif provider_name == "openai":
        return OpenAIProvider()

    elif provider_name == "gemini" or provider_name == "google":
        return GeminiProvider()

    elif provider_name == "ollama":
        return OpenAIProvider(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key="ollama"
        )

    elif provider_name in ["local", "lm_studio", "lmstudio"]:
        return OpenAIProvider(
            base_url=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
            api_key="lm-studio"
        )

    elif provider_name in ["glm", "zhipu", "zhipuai"]:
        return OpenAIProvider(
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            api_key=os.getenv("ZHIPUAI_API_KEY")
        )

    else:
        # Fallback to LiteLLM for unknown providers, as it supports many
        try:
            return LiteLLMProvider()
        except ImportError:
            # Check if user provided env vars for generic OpenAI compatible
            if os.getenv("OPENAI_BASE_URL"):
                return OpenAIProvider()

            raise ValueError(f"Unsupported provider: {provider_name} and litellm not installed.")
