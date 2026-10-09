import os
import time
from typing import Dict, List, Optional

import yaml
from rich.console import Console
from rich.markup import escape
from rich.prompt import Prompt, Confirm, IntPrompt

from core.config.envfile import read_env_file, upsert_env_file
from providers.llm.discovery import PROVIDERS, DiscoveryError, list_models, test_model

console = Console()

CLOUD_CHOICES = ["openai", "anthropic", "gemini", "openrouter", "sarvam", "other"]
MAX_LISTED_MODELS = 15


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def count_builtin_tools() -> int:
    from core.tools.registry import ToolRegistry
    from providers.tools.builtin import builtin_tools

    registry = ToolRegistry()
    for tool in builtin_tools():
        registry.register(tool)
    return len(registry.list_tools())


def describe_intelligence(llm: Dict) -> str:
    parts = []
    for slot in ("cloud", "local"):
        cfg = llm.get(slot)
        if cfg:
            label = PROVIDERS[cfg["provider"]].label
            parts.append(f"{escape(cfg['model'])} [dim]({label})[/dim]")
    return "  +  ".join(parts) if parts else "[yellow]not configured[/yellow]"


def pick_model(models: List[str]) -> Optional[str]:
    """Numbered picker; for long lists the user can type text to filter or an exact id."""
    view = models
    while True:
        shown = view[:MAX_LISTED_MODELS]
        console.print(f"[bold]Available models[/bold] [dim]({len(view)} of {len(models)})[/dim]\n")
        for i, m in enumerate(shown, 1):
            console.print(f"  {i:>2}. {escape(m)}")
        if len(view) > MAX_LISTED_MODELS:
            console.print(f"\n  [dim]…and {len(view) - MAX_LISTED_MODELS} more. Type part of a name to filter.[/dim]")
        console.print()
        answer = Prompt.ask("›", default="1").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(shown):
            return shown[int(answer) - 1]
        if answer in models:
            return answer
        filtered = [m for m in models if answer.lower() in m.lower()]
        if filtered:
            view = filtered
            clear()
            continue
        console.print(f"[yellow]No models match '{escape(answer)}'.[/yellow]\n")
        view = models


def verify_model(provider: str, model: str, api_key: str, base_url: Optional[str]) -> bool:
    clear()
    with console.status(f"Testing {escape(model)}…", spinner="dots"):
        try:
            reply = test_model(provider, model, api_key=api_key, base_url=base_url)
        except DiscoveryError as e:
            console.print(f"[red]✕ {escape(model)} did not respond.[/red]\n  [dim]{escape(str(e))}[/dim]\n")
            return False
    snippet = f" [dim]“{escape(reply[:40])}”[/dim]" if reply else ""
    console.print(f"[green]✓ {escape(model)} responded successfully.[/green]{snippet}\n")
    return True


def choose_and_verify(provider: str, models: List[str], api_key: str, base_url: Optional[str]) -> Optional[str]:
    while True:
        model = pick_model(models)
        if verify_model(provider, model, api_key, base_url):
            Prompt.ask("[dim]Continue[/dim]", default="", show_default=False)
            return model
        choice = Prompt.ask("Pick another model, keep it anyway, or skip?",
                            choices=["another", "keep", "skip"], default="another")
        if choice == "keep":
            return model
        if choice == "skip":
            return None
        clear()


def configure_cloud(env_path: str, env_updates: Dict[str, str]) -> Optional[Dict]:
    clear()
    console.print("[bold]Choose your AI provider.[/bold]\n")
    for i, key in enumerate(CLOUD_CHOICES, 1):
        console.print(f"  {i}. {PROVIDERS[key].label}")
    console.print()
    idx = IntPrompt.ask("›", choices=[str(i) for i in range(1, len(CLOUD_CHOICES) + 1)], default=5)
    provider = CLOUD_CHOICES[idx - 1]
    spec = PROVIDERS[provider]

    clear()
    console.print(f"[bold]{spec.label}[/bold]\n")
    console.print(f"Nārada will use {spec.label} for reasoning.\n")

    base_url = None
    if provider == "other":
        base_url = Prompt.ask("Base URL [dim](OpenAI-compatible, e.g. http://localhost:1234/v1)[/dim]").strip()

    existing = os.getenv(spec.env_var or "") or read_env_file(env_path).get(spec.env_var or "", "")
    for attempt in range(3):
        if existing and attempt == 0 and Confirm.ask(f"Found an existing {spec.env_var}. Use it?", default=True):
            api_key = existing
        else:
            api_key = Prompt.ask("API key", password=True).strip()
        if not api_key and provider != "other":
            console.print("[yellow]An API key is required.[/yellow]")
            continue

        with console.status(f"Connecting to {spec.label}…", spinner="dots"):
            try:
                models = list_models(provider, api_key=api_key, base_url=base_url)
            except DiscoveryError as e:
                models, error = None, e
        if models is not None:
            break
        console.print(f"[red]✕ {escape(str(error))}[/red]\n")
        if error.kind != "auth" and not Confirm.ask("Try again?", default=True):
            return None
    else:
        console.print("[yellow]Couldn't verify a key. You can re-run `narada setup` later.[/yellow]\n")
        Prompt.ask("[dim]Continue[/dim]", default="", show_default=False)
        return None

    console.print(f"Connecting...                    [green]✓[/green]")
    console.print(f"Fetching available models...     [green]✓[/green] [dim]{len(models)} found[/dim]\n")
    if not models:
        console.print("[yellow]This key has no chat models available.[/yellow]\n")
        Prompt.ask("[dim]Continue[/dim]", default="", show_default=False)
        return None

    model = choose_and_verify(provider, models, api_key, base_url)
    if not model:
        return None

    if spec.env_var and api_key:
        env_updates[spec.env_var] = api_key
    if provider == "sarvam":
        env_updates["SARVAM_MODEL"] = model
    cfg = {"provider": provider, "model": model}
    if base_url:
        cfg["base_url"] = base_url
        env_updates["NARADA_LLM_BASE_URL"] = base_url
    return cfg


def configure_local(env_updates: Dict[str, str]) -> Optional[Dict]:
    base_url = os.getenv("OLLAMA_BASE_URL") or PROVIDERS["ollama"].default_base_url
    while True:
        clear()
        console.print("[bold]Local setup[/bold]\n")
        with console.status(f"Looking for Ollama at {base_url}…", spinner="dots"):
            try:
                models = list_models("ollama", base_url=base_url)
                error = None
            except DiscoveryError as e:
                models, error = None, e
        if models is not None:
            break
        console.print(f"Looking for Ollama...       [red]✕ not found[/red]\n  [dim]{escape(str(error))}[/dim]\n")
        console.print("Install it from [link=https://ollama.com]https://ollama.com[/link] and run `ollama serve`.\n")
        choice = Prompt.ask("Retry, use a different URL, or skip?", choices=["retry", "url", "skip"], default="retry")
        if choice == "skip":
            return None
        if choice == "url":
            base_url = Prompt.ask("Ollama URL", default=base_url).strip()

    console.print("Looking for Ollama...       [green]✓ found[/green]")
    console.print(f"Checking connection...      [green]✓ connected[/green] [dim]{len(models)} models[/dim]\n")
    if not models:
        console.print("[yellow]Ollama has no models installed.[/yellow] Try: [bold]ollama pull qwen3:8b[/bold]\n")
        Prompt.ask("[dim]Continue[/dim]", default="", show_default=False)
        return None

    model = choose_and_verify("ollama", models, "", base_url)
    if not model:
        return None
    env_updates["OLLAMA_BASE_URL"] = base_url
    env_updates["OLLAMA_MODEL"] = model
    return {"provider": "ollama", "model": model, "base_url": base_url}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_logo():
    logo = """[bold #d4af37]       _   _    _    ____    _    ____    _    
      | \\ | |  / \\  |  _ \\  / \\  |  _ \\  / \\   
      |  \\| | / _ \\ | |_) |/ _ \\ | |_) |/ _ \\  
      | |\\  |/ ___ \\|  _ </ ___ \\|  _ </ ___ \\ 
      |_| \\_/_/   \\_\\_| \\_/_/   \\_\\_| \\_/_/   \\_\\
[/bold #d4af37]
                    [bold white]N Ā R A D A[/bold white]

        [dim]Your personal autonomous agent.[/dim]

[dim]────────────────────────────────────────────────────────[/dim]"""
    console.print(logo)

def run_setup():
    clear()
    render_logo()
    
    console.print("\n[white]Let's get you set up.[/white]\n")
    time.sleep(1)
    
    clear()
    console.print("[bold #d4af37]Welcome to Nārada.[/bold #d4af37]\n")
    console.print("Nārada is an agent that can remember things,\nuse tools, and take responsibility for work.\n")
    console.print("Before we begin—\n")
    
    user_name = Prompt.ask("[bold]What should I call you?[/bold]")
    
    clear()
    console.print(f"Nice to meet you, [bold #4a6fa5]{escape(user_name)}[/].\n")
    
    # Mental model
    Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="", show_default=False)
    
    clear()
    console.print("[bold #d4af37]Nārada works differently from a normal chatbot.[/bold #d4af37]\n")
    console.print("You don't just give me questions.\n")
    console.print("You can give me responsibilities.\n")
    console.print("For example:\n")
    console.print("  [dim]\"Keep an eye on my GitHub project.\"[/dim]")
    console.print("  [dim]\"Remind me when my submission changes.\"[/dim]")
    console.print("  [dim]\"Research this every week.\"[/dim]")
    console.print("  [dim]\"Take care of this project.\"[/dim]\n")
    console.print("I'll turn those into goals, tasks and actions.\n")
    
    Prompt.ask("\n[dim]Continue[/dim]", default="", show_default=False)
    
    clear()
    console.print("One more thing.\n")
    console.print("I won't assume that having access to something\nmeans I'm allowed to use it.\n")
    console.print("Actions can require your approval.\n")
    
    Prompt.ask("\n[dim]That's good[/dim]", default="", show_default=False)
    
    clear()
    console.print("[bold]Where should I think?[/bold]\n")
    console.print("  1. [bold]Cloud[/bold]  [dim]Use Sarvam, OpenAI, Gemini, etc.[/dim]")
    console.print("  2. [bold]Local[/bold]  [dim]Use a model running on this machine (Ollama).[/dim]")
    console.print("  3. [bold]Hybrid[/bold] [dim]Local when possible, Cloud when needed.[/dim]\n")
    
    think_loc = IntPrompt.ask("›", choices=["1", "2", "3"], default=1)
    
    narada_home = os.path.expanduser("~/.narada")
    env_path = os.path.join(narada_home, ".env")
    env_updates: dict = {}
    llm_config: dict = {"mode": {1: "cloud", 2: "local", 3: "hybrid"}[think_loc]}
    
    local = cloud = None
    if think_loc in (2, 3):
        local = configure_local(env_updates)
        if local is None and think_loc == 2:
            console.print("\n[yellow]No local model configured. Let's use a cloud provider instead.[/yellow]\n")
            Prompt.ask("[dim]Continue[/dim]", default="", show_default=False)
            llm_config["mode"] = "cloud"
            think_loc = 1
    if think_loc in (1, 3):
        cloud = configure_cloud(env_path, env_updates)
    
    if local:
        llm_config["local"] = local
    if cloud:
        llm_config["cloud"] = cloud
    primary = cloud if llm_config["mode"] == "cloud" else (local or cloud)
    if primary:
        llm_config["provider"] = primary["provider"]
        llm_config["model"] = primary["model"]
        env_updates["NARADA_LLM_PROVIDER"] = primary["provider"]
        env_updates["NARADA_LLM_MODEL"] = primary["model"]
        
    clear()
    console.print("[bold]Where should I keep memory?[/bold]\n")
    console.print("  1. [bold]SQLite[/bold]      [dim]Simple. Private. No server required.[/dim]")
    console.print("  2. [bold]PostgreSQL[/bold]  [dim]Better for larger deployments.[/dim]\n")
    
    mem_choice = IntPrompt.ask("›", choices=["1", "2"], default=1)
    memory_type = "SQLite" if mem_choice == 1 else "PostgreSQL"
    
    clear()
    console.print("[bold]Permissions[/bold]\n")
    console.print("Before I start working, let's decide what I'm allowed to do.\n")
    console.print("  [dim]READ[/dim]")
    console.print("  Files                  [green]✓ allowed[/green]")
    console.print("  Web                    [green]✓ allowed[/green]")
    console.print("  Git repositories       [green]✓ allowed[/green]\n")
    console.print("  [dim]WRITE[/dim]")
    console.print("  Create files           [yellow]? ask first[/yellow]")
    console.print("  Modify files           [yellow]? ask first[/yellow]\n")
    console.print("  [dim]SYSTEM[/dim]")
    console.print("  Run shell commands     [yellow]? ask first[/yellow]")
    console.print("  Delete files           [red]✕ blocked[/red]\n")
    
    Prompt.ask("[dim]Continue[/dim]", default="", show_default=False)
    
    clear()
    console.print("[bold]Where should I keep your Nārada workspace?[/bold]\n")
    console.print(f"  › {narada_home}\n")
    console.print("This is where I'll keep:")
    console.print("  • configuration\n  • local state\n  • memory\n  • logs\n  • credentials metadata\n")
    console.print("[dim]No project files will be touched.[/dim]\n")
    
    if not Confirm.ask("Continue?", default=True):
        console.print("\n[yellow]Setup cancelled. Nothing was saved.[/yellow]")
        return
    
    console.print("\nCreating workspace...")
    for sub in ("config", "memory", "logs", "state"):
        os.makedirs(os.path.join(narada_home, sub), exist_ok=True)
    
    # Non-secret configuration
    config = {
        "user": user_name,
        "llm": llm_config,
        "memory": {"type": memory_type.lower()},
    }
    with open(os.path.join(narada_home, "config", "config.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False)
    
    # Secrets live only in the workspace .env, never in config.yaml or the repo
    if env_updates:
        upsert_env_file(env_path, env_updates)
    
    console.print("                    [green]✓ ready[/green]\n")
    time.sleep(0.6)
    
    tool_count = count_builtin_tools()
    
    clear()
    console.print("[dim]────────────────────────────────────────────────────────[/dim]\n")
    console.print("                    [bold #d4af37]NĀRADA IS READY[/bold #d4af37]\n")
    console.print(f"  Identity          Nārada")
    console.print(f"  Intelligence      {describe_intelligence(llm_config)}")
    console.print(f"  Memory            {memory_type}")
    console.print(f"  Tools             {tool_count} available")
    console.print(f"  Permissions       Approval required for writes")
    console.print(f"  Workspace         {narada_home}\n")
    console.print("[dim]────────────────────────────────────────────────────────[/dim]\n")
    console.print("I can now:\n")
    console.print("  › answer questions")
    console.print("  › use tools")
    console.print("  › remember useful things")
    console.print("  › work on multi-step tasks")
    console.print("  › ask before taking consequential actions\n")
    console.print("But you don't need to configure everything now.\nJust tell me what needs doing.\n")
    console.print("[dim]────────────────────────────────────────────────────────[/dim]\n")
    
    console.print("Starting Nārada…\n")
    time.sleep(0.8)
    
    # Immediately launch chat — no separate command required
    from apps.terminal.app import NaradaTerminalUI
    app = NaradaTerminalUI()
    app.run()

if __name__ == "__main__":
    run_setup()
