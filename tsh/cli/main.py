import typer
import asyncio
from typing import Optional
from tsh.core.agent import Agent
from tsh.tools.file_tools import FileReadTool, FileWriteTool, ListDirTool
from tsh.tools.web_tools import WebSearchTool, WebFetchTool
from tsh.tools.excel_tools import ExcelReadTool
from tsh.tools.media_tools import ImageAnalyzeTool, VideoAnalyzeTool
from tsh.tools.system_tools import ShellTool, WorkspaceSummaryTool
from tsh.cli.ui import (
    console, display_welcome, display_user_prompt, display_agent_response,
    display_tool_use, display_tool_result, display_error, set_theme, THEMES,
    get_prompt_text
)

app = typer.Typer(help="TSH: The Agentic Personal Assistant CLI")

@app.command()
def main(
    query: Optional[str] = typer.Argument(None, help="The question or task for TSH"),
    provider: str = typer.Option("anthropic", "--provider", "-p", help="AI provider (anthropic, openai, gemini, ollama, local, glm)"),
    model: str = typer.Option("claude-3-5-sonnet-20241022", "--model", "-m", help="Model name"),
    theme: str = typer.Option("default", "--theme", "-t", help=f"UI Theme ({', '.join(THEMES.keys())})"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Disable interactive mode"),
    export_skill: bool = typer.Option(True, "--export-skill/--no-export-skill", help="Export session to Skill.md on exit")
):
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
