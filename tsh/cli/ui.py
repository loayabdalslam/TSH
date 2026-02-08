import json
import os
from datetime import datetime
try:
    import git
except ImportError:
    git = None

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.theme import Theme
from rich.text import Text
from rich.style import Style

# Define multiple themes
THEMES = {
    "default": Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "brand": "bold magenta",
        "user": "bold magenta",
        "agent": "bold green",
        "tool_call": "bold yellow",
        "tool_result": "bold blue",
    }),
    "ocean": Theme({
        "info": "blue",
        "warning": "bright_yellow",
        "error": "bold bright_red",
        "success": "bold bright_cyan",
        "brand": "bold cyan",
        "user": "bold cyan",
        "agent": "bold blue",
        "tool_call": "bold bright_blue",
        "tool_result": "bold cyan",
    }),
    "forest": Theme({
        "info": "green",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold bright_green",
        "brand": "bold green",
        "user": "bold green",
        "agent": "bold yellow",
        "tool_call": "bold green",
        "tool_result": "bold bright_green",
    }),
    "monochrome": Theme({
        "info": "white",
        "warning": "bright_black",
        "error": "bold white",
        "success": "bold white",
        "brand": "bold white",
        "user": "bold white",
        "agent": "white",
        "tool_call": "bright_black",
        "tool_result": "bright_black",
    })
}

current_theme_name = "default"
console = Console(theme=THEMES[current_theme_name])

def set_theme(theme_name: str):
    global console, current_theme_name
    if theme_name in THEMES:
        current_theme_name = theme_name
        console = Console(theme=THEMES[theme_name])
    else:
        raise ValueError(f"Theme {theme_name} not found. Available: {list(THEMES.keys())}")

def get_git_status():
    if not git:
        return ""
    try:
        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        branch = repo.active_branch.name
        is_dirty = repo.is_dirty()

        dirty_symbol = "*" if is_dirty else ""
        color = "yellow" if is_dirty else "green"

        return f" on [{color}] {branch}{dirty_symbol}[/{color}]"
    except (git.InvalidGitRepositoryError, Exception):
        return ""

def get_prompt_text():
    cwd = os.getcwd()
    folder_name = os.path.basename(cwd) or cwd
    git_info = get_git_status()
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Constructing an "Oh My Posh" / "Powerlevel10k" style prompt
    # Line 1: [Time] [Directory] [Git]
    # Line 2: ❯ Input

    prompt = (
        f"\n[dim]{timestamp}[/dim] "
        f"[bold blue]{folder_name}[/bold blue]"
        f"{git_info}"
        f"\n[bold brand]➜[/bold brand] "
    )
    return prompt

def display_welcome():
    console.print("\n")
    welcome_panel = Panel.fit(
        "  [brand]⚡ TSH: THE AGI CLI ⚡[/brand]  \n"
        "[dim]Evolution of traditional agents[/dim]\n\n"
        "[success]✓[/success] Files  [success]✓[/success] Media  [success]✓[/success] Web  [success]✓[/success] Skills",
        border_style="brand",
        padding=(1, 4),
        title="[bold white]TSH AGENT[/bold white]",
        subtitle=f"[bold brand]v0.1.0 ({current_theme_name})[/bold brand]"
    )
    console.print(welcome_panel, justify="center")
    console.print("[dim italic]Ready to orchestrate your workspace...[/dim italic]\n")

def display_user_prompt(prompt: str):
    # Used when running non-interactively or just logging
    console.print(f"[user]👤 YOU[/user] [dim]❯[/dim] {prompt}")

def display_agent_response(text: str):
    console.print(Panel(
        Markdown(text),
        title="[agent]🤖 TSH[/agent]",
        border_style="agent",
        padding=(1, 2)
    ))

def display_tool_use(tool_name: str, tool_input: dict):
    msg = Text()
    msg.append(" ⚙️  ", style="tool_call")
    msg.append("Invoking Tool: ", style="bold white")
    msg.append(f"{tool_name}", style="info")

    input_str = json.dumps(tool_input, indent=2)

    console.print(Panel(
        input_str,
        title=msg,
        border_style="tool_call",
        expand=False,
        padding=(0, 1)
    ))

def display_tool_result(result: str):
    display_text = str(result) if len(str(result)) < 500 else str(result)[:500] + "..."
    console.print(Panel(
        display_text,
        title="[tool_result]📥 TOOL OUTPUT[/tool_result]",
        border_style="tool_result",
        padding=(0, 1),
        expand=False
    ))

def display_error(error: str):
    console.print(Panel(f"[bold red]✘ Error:[/bold red] {error}", border_style="red"))
