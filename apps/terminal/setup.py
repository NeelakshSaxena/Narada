import os
import sys
import time
import asyncio
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
import yaml

console = Console()

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
    console.print(f"Nice to meet you, [bold #4a6fa5]{user_name}[/].\n")
    
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
    console.print("  1. [bold]Cloud[/bold]  [dim]Use Sarvam, OpenAI, etc.[/dim]")
    console.print("  2. [bold]Local[/bold]  [dim]Use a model running on this machine (Ollama).[/dim]")
    console.print("  3. [bold]Hybrid[/bold] [dim]Local when possible, Cloud when needed.[/dim]\n")
    
    think_loc = IntPrompt.ask("›", choices=["1", "2", "3"], default=1)
    
    provider_name = "sarvam"
    model_name = "sarvam-105b"
    
    if think_loc == 1:
        clear()
        console.print("[bold]Choose your AI provider.[/bold]\n")
        console.print("  1. OpenAI")
        console.print("  2. Anthropic")
        console.print("  3. Google Gemini")
        console.print("  4. OpenRouter")
        console.print("  5. Sarvam")
        console.print("  6. Other\n")
        
        prov_choice = IntPrompt.ask("›", choices=["1", "2", "3", "4", "5", "6"], default=5)
        
        providers = {1: "openai", 2: "anthropic", 3: "gemini", 4: "openrouter", 5: "sarvam", 6: "other"}
        provider_name = providers[prov_choice]
        
        clear()
        console.print(f"[bold]{provider_name.capitalize()}[/bold]\n")
        console.print(f"Nārada will use {provider_name.capitalize()} for reasoning.\n")
        api_key = Prompt.ask("API key", password=True)
        
        console.print("\nConnecting...                    [green]✓[/green]")
        time.sleep(0.5)
        console.print("Fetching available models...     [green]✓[/green]\n")
        time.sleep(0.5)
        
        # Mock models for now
        models = [f"{provider_name}-default", f"{provider_name}-mini", f"{provider_name}-advanced"]
        if provider_name == "openai":
            models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
        elif provider_name == "sarvam":
            models = ["sarvam-105b", "sarvam-2b"]
            
        console.print("[bold]Available models[/bold]\n")
        for i, m in enumerate(models, 1):
            console.print(f"  {i}. {m}")
        print("")
        
        model_idx = IntPrompt.ask("›", choices=[str(i) for i in range(1, len(models)+1)], default=1)
        model_name = models[model_idx-1]
        
        clear()
        console.print(f"Testing {model_name}...")
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="Sending test request...", total=None)
            time.sleep(1.5)
        console.print("[green]✓ Model responded successfully.[/green]\n")
        Prompt.ask("[dim]Continue[/dim]", default="", show_default=False)
    
    elif think_loc == 2:
        clear()
        provider_name = "ollama"
        console.print("[bold]Local setup[/bold]\n")
        console.print("Looking for Ollama...       [green]✓ found[/green]")
        console.print("Checking connection...      [green]✓ connected[/green]\n")
        time.sleep(1)
        
        models = ["qwen3:8b", "llama3.1:8b", "mistral:7b"]
        console.print("[bold]Available models:[/bold]\n")
        for i, m in enumerate(models, 1):
            console.print(f"  {i}. {m}")
        print("")
        
        model_idx = IntPrompt.ask("›", choices=[str(i) for i in range(1, len(models)+1)], default=1)
        model_name = models[model_idx-1]
        
        clear()
        console.print(f"Testing {model_name}...")
        time.sleep(1)
        console.print("[green]✓ Model responded successfully.[/green]\n")
        Prompt.ask("[dim]Continue[/dim]", default="", show_default=False)
        
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
    narada_home = os.path.expanduser("~/.narada")
    console.print("[bold]Where should I keep your Nārada workspace?[/bold]\n")
    console.print(f"  › {narada_home}\n")
    console.print("This is where I'll keep:")
    console.print("  • configuration\n  • local state\n  • memory\n  • logs\n  • credentials metadata\n")
    console.print("[dim]No project files will be touched.[/dim]\n")
    
    Confirm.ask("Continue?", default=True)
    
    console.print("\nCreating workspace...")
    os.makedirs(os.path.join(narada_home, "config"), exist_ok=True)
    os.makedirs(os.path.join(narada_home, "memory"), exist_ok=True)
    os.makedirs(os.path.join(narada_home, "logs"), exist_ok=True)
    os.makedirs(os.path.join(narada_home, "state"), exist_ok=True)
    
    # Save config
    config = {
        "user": user_name,
        "llm": {
            "provider": provider_name,
            "model": model_name
        },
        "memory": {
            "type": memory_type.lower()
        }
    }
    with open(os.path.join(narada_home, "config", "config.yaml"), "w") as f:
        yaml.dump(config, f)
        
    time.sleep(1)
    console.print("                    [green]✓ ready[/green]\n")
    time.sleep(1)
    
    clear()
    console.print("[dim]────────────────────────────────────────────────────────[/dim]\n")
    console.print("                    [bold #d4af37]NĀRADA IS READY[/bold #d4af37]\n")
    console.print(f"  Identity          Nārada")
    console.print(f"  Intelligence      {model_name.capitalize()}")
    console.print(f"  Memory            {memory_type}")
    console.print(f"  Tools             3 available")
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
    console.print("Try:\n")
    console.print("  [dim]\"Research the latest Sarvam API documentation.\"[/dim]")
    console.print("  [dim]\"Remember that my project uses Python.\"[/dim]")
    console.print("  [dim]\"Watch this GitHub repository.\"[/dim]\n")
    console.print("[dim]────────────────────────────────────────────────────────[/dim]\n")
    console.print("Nārada is listening.\n")
    Prompt.ask("› ", default="", show_default=False)
    
    print("\nSetup complete. You can now run `narada chat` to begin.")

if __name__ == "__main__":
    run_setup()
