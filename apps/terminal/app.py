from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Static, RichLog
from textual.reactive import reactive
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown

from apps.terminal.mascot import MascotWidget

import asyncio
import httpx

from apps.terminal.session import TerminalSessionManager

class StatusPanel(Static):
    """Displays the current status of the agent."""
    status_text = reactive("ONLINE")
    model_text = reactive("unknown")
    provider_text = reactive("Unknown")
    
    THINKING_PHRASES = [
        "Analyzing context...",
        "Consulting memory...",
        "Formulating plan...",
        "Evaluating tools...",
        "Synthesizing...",
        "Gathering information...",
        "Thinking deeply...",
        "Executing tasks...",
    ]

    def on_mount(self):
        self.thinking_idx = 0
        self.set_interval(1.5, self.cycle_thinking_text)
        
    def cycle_thinking_text(self):
        if self.status_text == "WORKING":
            self.thinking_idx = (self.thinking_idx + 1) % len(self.THINKING_PHRASES)
            self.refresh()

    def render(self) -> Text:
        status_color = {
            "ONLINE": "#d4af37",
            "ERROR": "red"
        }.get(self.status_text, "#4a6fa5")
        
        display_text = self.status_text
        if self.status_text == "WORKING":
            display_text = self.THINKING_PHRASES[self.thinking_idx]
            
        t = Text()
        t.append("{ ", style="white")
        t.append(self.model_text, style="bold #ffb828")
        t.append(" | ctx -- | [", style="dim white")
        t.append("░░░░░░░░░░", style="dim white")
        t.append("] -- | ", style="dim white")
        t.append(display_text, style=f"bold {status_color}")
        t.append(" }", style="white")
        return t

class NaradaTerminalUI(App):
    """The main Terminal UI for Narada."""
    
    CSS = """
    Screen {
        background: #0f111a;
        color: #e2e4e9;
    }
    
    StatusPanel {
        height: 1;
        padding: 0 1;
        background: #0f111a;
        color: #e2e4e9;
    }
    
    #main-container {
        layout: horizontal;
        height: 1fr;
    }
    
    #mascot-container {
        width: 50;
        height: 1fr;
        border-right: solid #4a6fa5;
        color: #d4af37;
    }
    
    #mascot {
        height: auto;
        padding-top: 1;
        padding-bottom: 1;
    }

    #sidebar-info {
        padding: 0 2;
        color: #e2e4e9;
        height: auto;
    }
    
    #chat-container {
        width: 1fr;
        height: 1fr;
        padding: 0 1;
    }
    
    RichLog {
        height: 1fr;
        border: none;
        background: #0f111a;
        overflow-x: hidden;
    }
    #command-hints {
        background: #1a1c23;
        color: #e2e4e9;
        padding: 1 2;
        border-top: solid #4a6fa5;
        display: none;
        height: auto;
    }
    
    Input {
        border: none;
        border-top: solid #4a6fa5;
        background: #0f111a;
        padding: 0 1;
    }
    Input:focus {
        border-top: solid #d4af37;
    }
    """

    def compose(self) -> ComposeResult:
        
        with Horizontal(id="main-container"):
            with Vertical(id="mascot-container"):
                yield MascotWidget(id="mascot")
                yield Static(
                    "[dim]Loading details...[/]",
                    id="sidebar-info"
                )
            
            with Vertical(id="chat-container"):
                yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True)
                yield Static(
                    " [bold #d4af37]Available Commands:[/]\n"
                    "  [bold white]/audit[/]   [dim]- View action and tool execution trail[/]\n"
                    "  [bold white]/memory[/]  [dim]- View long-term contextual memories[/]\n"
                    "  [bold white]/forget[/]  [dim]- Forget a specific memory by ID[/]\n"
                    "  [bold white]/session[/] [dim]- Manage chat sessions (list, load, new)[/]",
                    id="command-hints"
                )
                yield Input(placeholder="› ", id="chat-input")
                yield StatusPanel(id="status-panel")

    def on_mount(self) -> None:
        self.title = "Nārada Terminal"
        self.log_widget = self.query_one("#chat-log", RichLog)
        self.mascot = self.query_one("#mascot", MascotWidget)
        self.status_panel = self.query_one("#status-panel", StatusPanel)
        self.chat_history = []
        
        # Show saved provider/model immediately from config
        try:
            from core.config.loader import load_config
            from providers.llm.catalog import provider_label
            import os, uuid
            from datetime import datetime
            
            self.session_manager = TerminalSessionManager()
            
            cfg = load_config()
            sidebar_info = self.query_one("#sidebar-info", Static)
            workspace = os.path.expanduser("~/.narada")
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:6]
            self.session_manager.create_session(self.session_id)
            
            if cfg.is_configured:
                label = provider_label(cfg.llm.provider)
                self.status_panel.provider_text = label
                self.status_panel.model_text = cfg.llm.model
                
                header = (
                    f"[bold #ffb828]{cfg.llm.model}[/] · [white]{label}[/]\n"
                    f"[bold #ffb828]{workspace}[/]\n"
                    f"[dim]Session: {self.session_id}[/]\n\n"
                )
                sidebar_info.update(header + 
                    "[bold #ffb828]Available Tools[/]\n"
                    "[#879854]filesystem:[/] read_file, write_file\n"
                    "[#879854]system:[/] execute_shell, manage_task\n"
                    "[#879854]web:[/] search_web, read_url\n"
                    "[dim](and 5 more tools...)[/]\n"
                    "\n"
                    "[bold #ffb828]Available Skills[/]\n"
                    "[#879854]core:[/] analyze, debug, refactor\n"
                    "[#879854]creative:[/] ascii-art, design\n"
                    "\n"
                    "[bold #ffb828]Profile:[/] [white]Nārada Core[/]\n"
                    "[dim]8 tools · 2 skills · Type / for commands[/]"
                )
        except Exception:
            pass
        
        greeting = Text()
        greeting.append("\nNārada\n\n", style="bold #d4af37")
        model_line = self.status_panel.model_text
        if model_line and model_line != "Unknown / unknown":
            greeting.append(f"{model_line}\n\n", style="dim white")
        greeting.append("Good evening.\nWhat shall we work on?\n", style="white")
        self.log_widget.write(greeting)
        
        self.query_one(Input).focus()
        
        # Mascot init sequence and sleep timer
        self.mascot.set_state("hello")
        self.set_timer(3.0, self.go_idle)
        self.sleep_timer = self.set_timer(60.0, self.go_sleep)
        
        # Start background polling for status/model
        self.set_interval(5.0, self.poll_status)
        self.run_worker(self.poll_status())


    async def poll_status(self) -> None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/health", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    llm_info = data.get("llm", {})
                    provider = llm_info.get("provider", "Unknown").capitalize()
                    model = llm_info.get("model", "unknown")
                    self.status_panel.model_text = model
                    self.status_panel.provider_text = provider
                    if self.status_panel.status_text == "ERROR" and data.get("status") != "ERROR":
                        self.status_panel.status_text = "ONLINE"
                else:
                    self.status_panel.status_text = "ERROR"
        except Exception:
            pass

    def go_idle(self) -> None:
        if self.mascot.current_state in ["hello", "sleeping"]:
            self.mascot.set_state("idle")

    def go_sleep(self) -> None:
        if self.mascot.current_state == "idle":
            self.mascot.set_state("sleeping")

    def reset_sleep_timer(self) -> None:
        if hasattr(self, "sleep_timer"):
            self.sleep_timer.reset()
        if self.mascot.current_state == "sleeping":
            self.mascot.set_state("idle")

    def on_input_changed(self, event: Input.Changed) -> None:
        self.reset_sleep_timer()
        hints = self.query_one("#command-hints", Static)
        if event.value.startswith("/"):
            hints.display = True
        else:
            hints.display = False

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        self.reset_sleep_timer()
        user_text = event.value.strip()
        if not user_text:
            return
            
        if user_text.lower() in ["exit", "quit"]:
            self.exit()
            return
            
        event.input.value = ""
        # Also hide hints when submitted
        self.query_one("#command-hints", Static).display = False
        
        you_text = Text()
        you_text.append("You\n\n", style="bold #4a6fa5")
        you_text.append(user_text + "\n", style="white")
        self.log_widget.write(you_text)
        
        self.mascot.set_state("thinking")
        self.status_panel.status_text = "THINKING"
        
        if user_text.lower() == "/audit":
            self.run_worker(self.process_audit(), exclusive=True)
            return
            
        if user_text.lower() == "/memory":
            self.run_worker(self.process_memory(), exclusive=True)
            return
            
        if user_text.lower().startswith("/forget "):
            doc_id = user_text.strip().split(" ", 1)[1]
            self.run_worker(self.process_forget(doc_id), exclusive=True)
            return
            
        if user_text.lower().startswith("/session "):
            self.run_worker(self.process_session_command(user_text), exclusive=True)
            return

        self.run_worker(self.process_chat(user_text), exclusive=True)

    async def process_session_command(self, user_text: str) -> None:
        parts = user_text.strip().split(" ", 2)
        cmd = parts[1] if len(parts) > 1 else ""
        
        t = Text()
        t.append("System\n\n", style="bold #4a6fa5")
        
        if cmd == "list":
            sessions = self.session_manager.list_sessions(limit=10)
            if not sessions:
                t.append("No saved sessions found.\n", style="white")
            else:
                t.append("Recent Sessions:\n", style="bold white")
                for s in sessions:
                    t.append(f"• {s['id']} ", style="bold #ffb828")
                    t.append(f"({s['updated_at']})\n", style="dim white")
        elif cmd == "new":
            import uuid
            from datetime import datetime
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:6]
            self.session_manager.create_session(self.session_id)
            self.chat_history = []
            
            from core.config.loader import load_config
            from providers.llm.catalog import provider_label
            import os
            
            cfg = load_config()
            sidebar_info = self.query_one("#sidebar-info", Static)
            workspace = os.path.expanduser("~/.narada")
            label = provider_label(cfg.llm.provider) if cfg.is_configured else "Unknown"
            model = cfg.llm.model if cfg.is_configured else "Unknown"
            
            header = (
                f"[bold #ffb828]{model}[/] · [white]{label}[/]\n"
                f"[bold #ffb828]{workspace}[/]\n"
                f"[dim]Session: {self.session_id}[/]\n\n"
            )
            sidebar_info.update(header + 
                "[bold #ffb828]Available Tools[/]\n"
                "[#879854]filesystem:[/] read_file, write_file\n"
                "[#879854]system:[/] execute_shell, manage_task\n"
                "[#879854]web:[/] search_web, read_url\n"
                "[dim](and 5 more tools...)[/]\n"
            )
            
            t.append(f"Started new session: {self.session_id}\n", style="white")
        elif cmd == "load" and len(parts) > 2:
            target_id = parts[2]
            history = self.session_manager.get_messages(target_id)
            if not history:
                t.append(f"Session {target_id} not found or empty.\n", style="red")
            else:
                self.session_id = target_id
                self.chat_history = history
                t.append(f"Loaded session: {self.session_id} ({len(history)} messages)\n", style="green")
                
                # Update sidebar session ID
                from core.config.loader import load_config
                from providers.llm.catalog import provider_label
                import os
                
                cfg = load_config()
                sidebar_info = self.query_one("#sidebar-info", Static)
                workspace = os.path.expanduser("~/.narada")
                label = provider_label(cfg.llm.provider) if cfg.is_configured else "Unknown"
                model = cfg.llm.model if cfg.is_configured else "Unknown"
                
                header = (
                    f"[bold #ffb828]{model}[/] · [white]{label}[/]\n"
                    f"[bold #ffb828]{workspace}[/]\n"
                    f"[dim]Session: {self.session_id}[/]\n\n"
                )
                sidebar_info.update(header + 
                    "[bold #ffb828]Available Tools[/]\n"
                    "[#879854]filesystem:[/] read_file, write_file\n"
                    "[#879854]system:[/] execute_shell, manage_task\n"
                    "[#879854]web:[/] search_web, read_url\n"
                    "[dim](and 5 more tools...)[/]\n"
                )
        else:
            t.append("Usage: /session [list | new | load <id>]\n", style="white")
            
        self.log_widget.write(t)
        self.mascot.set_state("idle")

    async def process_audit(self) -> None:
        self.mascot.set_state("searching")
        self.status_panel.status_text = "WORKING"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/v1/audit", timeout=60.0)
                if response.status_code == 200:
                    data = response.json()
                    t = Text()
                    t.append("Nārada\n\n", style="bold #d4af37")
                    t.append("Audit Trail:\n", style="white")
                    for log in data.get("audit", []):
                        meta = log.get("metadata", {})
                        t.append(f" - [Resp:{meta.get('responsibility_id')}|Task:{meta.get('task_id')}] Tool:{meta.get('tool')} Action:{meta.get('action')} | Result: {log.get('text')}\n", style="dim white")
                    self.log_widget.write(t)
                    self.mascot.set_state("success")
                else:
                    self.mascot.set_state("error")
                    self.log_widget.write(Text(f"System: Error fetching audit ({response.status_code})\n", style="bold red"))
        except Exception as e:
            self.mascot.set_state("error")
            self.log_widget.write(Text(f"System: Connection failed: {e}\n", style="bold red"))
        
        self.status_panel.status_text = "ONLINE"
        await asyncio.sleep(2)
        self.mascot.set_state("idle")
        self.reset_sleep_timer()

    async def process_memory(self) -> None:
        self.mascot.set_state("searching")
        self.status_panel.status_text = "WORKING"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/v1/memory", timeout=60.0)
                if response.status_code == 200:
                    data = response.json()
                    t = Text()
                    t.append("Nārada\n\n", style="bold #d4af37")
                    t.append("Memory Log:\n", style="white")
                    for mem in data.get("memory", []):
                        t.append(f" - [{mem.get('id')}] {mem.get('metadata', {}).get('task')}: {mem.get('text')}\n", style="dim white")
                    self.log_widget.write(t)
                    self.mascot.set_state("success")
                else:
                    self.mascot.set_state("error")
                    self.log_widget.write(Text(f"System: Error fetching memory ({response.status_code})\n", style="bold red"))
        except Exception as e:
            self.mascot.set_state("error")
            self.log_widget.write(Text(f"System: Connection failed: {e}\n", style="bold red"))
            
        self.status_panel.status_text = "ONLINE"
        await asyncio.sleep(2)
        self.mascot.set_state("idle")
        self.reset_sleep_timer()

    async def process_forget(self, doc_id: str) -> None:
        self.mascot.set_state("working")
        self.status_panel.status_text = "WORKING"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(f"http://localhost:8000/v1/memory/{doc_id}", timeout=60.0)
                if response.status_code == 200:
                    t = Text()
                    t.append("Nārada\n\n", style="bold #d4af37")
                    t.append(f"Forgotten memory {doc_id}.\n", style="white")
                    self.log_widget.write(t)
                    self.mascot.set_state("success")
                else:
                    self.mascot.set_state("error")
                    self.log_widget.write(Text(f"System: Error deleting memory ({response.status_code})\n", style="bold red"))
        except Exception as e:
            self.mascot.set_state("error")
            self.log_widget.write(Text(f"System: Connection failed: {e}\n", style="bold red"))
            
        self.status_panel.status_text = "ONLINE"
        await asyncio.sleep(2)
        self.mascot.set_state("idle")
        self.reset_sleep_timer()

    async def process_chat(self, user_text: str) -> None:
        self.mascot.set_state("searching")
        self.status_panel.status_text = "WORKING"
        
        self.chat_history.append({"role": "user", "content": user_text})
        self.session_manager.add_message(self.session_id, "user", user_text)
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "messages": self.chat_history,
                    "model": "narada"
                }
                
                response = await client.post("http://localhost:8000/v1/chat/completions", json=payload, timeout=60.0)
                
                if response.status_code == 200:
                    data = response.json()
                    reply = data["choices"][0]["message"]["content"]
                    
                    self.chat_history.append({"role": "assistant", "content": reply})
                    self.session_manager.add_message(self.session_id, "assistant", reply)
                    
                    # Optional: generate a title if this is the first assistant response
                    if len(self.chat_history) == 2:
                        title_prompt = f"Summarize this input in 3 to 5 words: {user_text}"
                        try:
                            # Not strictly necessary, but nice to have. Let's just set title manually for now
                            title = user_text[:30] + "..." if len(user_text) > 30 else user_text
                            self.session_manager.update_session_title(self.session_id, title)
                        except Exception:
                            pass
                            
                    self.mascot.set_state("success")
                    self.status_panel.status_text = "ONLINE"
                    
                    self.log_widget.write(Text("Nārada\n", style="bold #d4af37"))
                    self.log_widget.write(Markdown(reply))
                    self.log_widget.write(Text("\n"))
                    
                    await asyncio.sleep(2)
                    self.mascot.set_state("idle")
                    self.reset_sleep_timer()
                    
                else:
                    self.mascot.set_state("error")
                    self.status_panel.status_text = "ERROR"
                    
                    error_msg = f"Error connecting to server ({response.status_code})"
                    try:
                        err_data = response.json()
                        if "detail" in err_data:
                            error_msg = str(err_data["detail"])
                    except Exception:
                        if response.text:
                            error_msg = response.text[:100]
                            
                    self.log_widget.write(Text(f"System: {error_msg}\n", style="bold red"))
                    
                    await asyncio.sleep(2)
                    self.mascot.set_state("idle")
                    self.reset_sleep_timer()
                    self.status_panel.status_text = "ONLINE"
                    
        except Exception as e:
            self.mascot.set_state("error")
            self.status_panel.status_text = "ERROR"
            self.log_widget.write(Text(f"System: Connection failed: {e}\n", style="bold red"))
            await asyncio.sleep(2)
            self.mascot.set_state("idle")
            self.reset_sleep_timer()
            self.status_panel.status_text = "ONLINE"

if __name__ == "__main__":
    app = NaradaTerminalUI()
    app.run()
