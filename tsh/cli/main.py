import os
import typer
import asyncio
from typing import Optional
from dotenv import load_dotenv
from tsh.core.agent import Agent
from tsh.tools.file_tools import (
    FileReadTool, FileWriteTool, ListDirTool, FileSearchTool, FileMoveTool, FileDeleteTool
)
from tsh.tools.web_tools import WebSearchTool, WebFetchTool
from tsh.tools.excel_tools import ExcelReadTool
from tsh.tools.media_tools import ImageAnalyzeTool, VideoAnalyzeTool
from tsh.tools.system_tools import ShellTool, WorkspaceSummaryTool
from tsh.cli.ui import (
    console, display_welcome, display_user_prompt, display_agent_response,
    display_tool_use, display_tool_result, display_error, set_theme, THEMES,
    get_prompt_text
)

# Load environment variables from .env file
load_dotenv()

app = typer.Typer(help="TSH: The Agentic Personal Assistant CLI")

@app.command()
def main(
    query: Optional[str] = typer.Argument(None, help="The question or task for TSH"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider (anthropic, openai, gemini, ollama, local, glm). Auto-detects from .env if omitted."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name. Auto-selects based on provider if omitted."),
    theme: str = typer.Option("default", "--theme", "-t", help=f"UI Theme ({', '.join(THEMES.keys())})"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Disable interactive mode"),
    export_skill: bool = typer.Option(True, "--export-skill/--no-export-skill", help="Export session to Skill.md on exit")
):
    # Auto-configure provider if not provided
    if provider is None:
        if os.getenv("TSH_PROVIDER"):
            provider = os.getenv("TSH_PROVIDER")
        elif os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            provider = "gemini"
        elif os.getenv("OLLAMA_BASE_URL"):
            provider = "ollama"
        elif os.getenv("DEEPSEEK_API_KEY") or os.getenv("LITELLM_API_KEY"):
             provider = "litellm"
        else:
            provider = "anthropic" # Default fallback

    # Auto-configure model if not provided
    if model is None:
        if os.getenv("TSH_MODEL"):
            model = os.getenv("TSH_MODEL")
        elif provider == "anthropic":
            model = "claude-3-5-sonnet-20241022"
        elif provider == "openai":
            model = "gpt-4o"
        elif provider == "gemini":
            model = "gemini-1.5-pro"
        elif provider == "ollama":
            model = "llama3"
        elif provider == "litellm":
            model = "gpt-3.5-turbo" # Default fallback for litellm
        else:
            model = "claude-3-5-sonnet-20241022"

    try:
        set_theme(theme)
    except Exception as e:
        display_error(str(e))
        return

    display_welcome()

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

    try:
        agent = Agent(provider=provider, model=model, tools=tools)
    except Exception as e:
        display_error(str(e))
        return

    async def run_query(q: str):
        if not q.strip(): return
        display_user_prompt(q)
        try:
            with console.status(f"[bold green]TSH ({agent.provider_name}) is thinking...") as status:
                response = await agent.run(q, on_tool_call=display_tool_use, on_tool_result=display_tool_result)
                display_agent_response(response)
        except Exception as e:
            display_error(str(e))

    if query:
        asyncio.run(run_query(query))
        if export_skill:
            agent.export_session_to_skill()
        if no_interactive:
            return

    # Interactive loop
    while True:
        try:
            user_input = console.input(get_prompt_text())
            if user_input.lower() in ["exit", "quit"]:
                if export_skill:
                    console.print("[dim]Saving session to Skill.md...[/dim]")
                    agent.export_session_to_skill()
                console.print("[yellow]Goodbye![/yellow]")
                break

            # Special command for theme switching in-session
            if user_input.startswith("/theme "):
                new_theme = user_input.split(" ")[1]
                try:
                    set_theme(new_theme)
                    console.print(f"[success]Theme changed to {new_theme}[/success]")
                except Exception as e:
                    display_error(str(e))
                continue

            asyncio.run(run_query(user_input))
        except (KeyboardInterrupt, EOFError):
            if export_skill:
                agent.export_session_to_skill()
            console.print("\n[yellow]Goodbye![/yellow]")
            break

if __name__ == "__main__":
    app()
