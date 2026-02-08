# TSH: The Agentic Personal Assistant ⚡

TSH is a powerful, multi-provider Agentic AI CLI and Python library designed to look like "Oh My Open Code" with extensive customization, persistent SQL-based memory, and full workspace access.

## 🚀 Features

- **Universal Multi-Provider AI**: Powered by **LiteLLM**, TSH supports 100+ LLMs including Anthropic, OpenAI, Gemini, Ollama, DeepSeek, Azure, and more.
- **Persistent Memory**: Unlimited history and "skills" stored in a `.sql` database (SQLite).
- **Smart Session Recording**: Automatically records structured session logs into a `Skill.md` file, capturing tool inputs/outputs and context to help the agent learn.
- **Universal File Access**: Works with text, images (ASCII previews), videos, and Excel. Full workspace search and manipulation.
- **"Oh My Open Code" UI**: A beautiful, interactive terminal interface with Powerline-style prompts (Git status, timestamps) and customizable themes (Default, Ocean, Forest, Monochrome).
- **Developer Ready**: Use it as a CLI tool or import it as a Python package.
- **Benchmark Driven**: Built-in evaluation framework for GAIA and other agentic tasks.

## 🛠 Setup

1. **Install the package**:
   ```bash
   pip install -e .
   ```
   *Note: This installs `litellm` and `gitpython` for enhanced capabilities.*

2. **Configure Environment**:
   Create a `.env` file in your root directory:
   ```env
   # Core
   ANTHROPIC_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here

   # Any LiteLLM supported provider
   GEMINI_API_KEY=...
   DEEPSEEK_API_KEY=...

   # Local
   OLLAMA_BASE_URL=http://localhost:11434
   ```

## 💻 Usage

### CLI Interface
Launch the interactive terminal:
```bash
tsh
```

**Options:**
- `--provider / -p`: Choose provider (`anthropic`, `openai`, `gemini`, `ollama`, `litellm`, `local`)
- `--model / -m`: Specify any model name supported by the provider (e.g., `gpt-4o`, `claude-3-5-sonnet`, `llama3`)
- `--theme / -t`: Choose theme (`default`, `ocean`, `forest`, `monochrome`)
- `--no-export-skill`: Disable automatic recording to `Skill.md`

**Examples:**
```bash
# Use Claude 3.5 Sonnet (Default)
tsh

# Use GPT-4o
tsh -p openai -m gpt-4o

# Use Local Ollama
tsh -p ollama -m llama3

# Use DeepSeek (via LiteLLM)
tsh -p litellm -m deepseek/deepseek-chat
```

### Python Library
Integrate TSH into your own applications:
```python
from tsh import get_default_agent
import asyncio

async def main():
    # Initialize with default settings or customize
    agent = get_default_agent(provider="litellm", model="gpt-4o")

    # Run a task
    response = await agent.run("Analyze the project structure and suggest improvements.")
    print(response)

    # Export current session knowledge
    agent.export_session_to_skill("my_knowledge.md")

asyncio.run(main())
```

## 🧪 Testing & Evaluation

Run tests:
```bash
pytest tests/
```

Run GAIA-style benchmarks:
```bash
python -m tsh.core.evaluation
```

## 🎨 Themes
Switch themes in the CLI using the `/theme <name>` command, or pass the `-t` flag at startup.

---
🤖 Generated with [TSH Agent Template]
