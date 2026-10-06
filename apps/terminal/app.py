from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll, Vertical
from textual.widgets import Header, Footer, Input, Static, Log
from textual.reactive import reactive
from textual.message import Message

from apps.terminal.mascot import MascotWidget

import asyncio
import httpx

class StatusPanel(Static):
    """Displays the current status of the agent."""
    status_text = reactive("ONLINE")

    def render(self) -> str:
        return f"NĀRADA ● {self.status_text}"

class NaradaTerminalUI(App):
    """The main Terminal UI for Narada."""
    
    CSS = """
    Screen {
        background: $surface;
        color: $text;
    }
    
    StatusPanel {
        dock: top;
        height: 1;
        content-align: center middle;
        background: $primary;
        color: $text;
        text-style: bold;
    }
    
    #main-container {
        layout: horizontal;
        height: 1fr;
    }
    
    #mascot-container {
        width: 30;
        height: 1fr;
        align: center middle;
        border-right: solid $primary;
    }
    
    #chat-container {
        width: 1fr;
        height: 1fr;
    }
    
    Log {
        height: 1fr;
        border: none;
    }
    
    Input {
        dock: bottom;
        border: none;
        border-top: solid $primary;
    }
    """

    def compose(self) -> ComposeResult:
        yield StatusPanel(id="status-panel")
        
        with Horizontal(id="main-container"):
            with Vertical(id="mascot-container"):
                yield MascotWidget(id="mascot")
            
            with Vertical(id="chat-container"):
                yield Log(id="chat-log", highlight=True)
                yield Input(placeholder="› _", id="chat-input")

    def on_mount(self) -> None:
        self.title = "Nārada Terminal"
        self.log_widget = self.query_one("#chat-log", Log)
        self.mascot = self.query_one("#mascot", MascotWidget)
        self.status_panel = self.query_one("#status-panel", StatusPanel)
        
        self.log_widget.write_line("[bold color(214)]Nārada:[/bold color(214)] Good evening. What shall we work on?")
        self.query_one(Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()
        if not user_text:
            return
            
        if user_text.lower() in ["exit", "quit"]:
            self.exit()
            return
            
        event.input.value = ""
        self.log_widget.write_line(f"[bold cyan]You:[/bold cyan] {user_text}")
        
        # Simulate transition to working/thinking
        self.mascot.set_state("thinking")
        self.status_panel.status_text = "THINKING"
        
        # Check for special commands
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

        # We process this as a background task so UI doesn't freeze
        self.run_worker(self.process_chat(user_text), exclusive=True)

    async def process_audit(self) -> None:
        self.mascot.set_state("searching")
        self.status_panel.status_text = "WORKING"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/v1/audit", timeout=60.0)
                if response.status_code == 200:
                    data = response.json()
                    self.log_widget.write_line("[bold color(214)]Nārada:[/bold color(214)] Audit Trail:")
                    for log in data.get("audit", []):
                        meta = log.get("metadata", {})
                        self.log_widget.write_line(f" - [Resp:{meta.get('responsibility_id')}|Task:{meta.get('task_id')}] Tool:{meta.get('tool')} Action:{meta.get('action')} | Result: {log.get('text')}")
                    self.mascot.set_state("success")
                else:
                    self.mascot.set_state("error")
                    self.log_widget.write_line(f"[bold red]System:[/bold red] Error fetching audit: {response.status_code}")
        except Exception as e:
            self.mascot.set_state("error")
            self.log_widget.write_line(f"[bold red]System:[/bold red] Connection failed: {e}")
        
        self.status_panel.status_text = "ONLINE"
        await asyncio.sleep(2)
        self.mascot.set_state("idle")

    async def process_memory(self) -> None:
        self.mascot.set_state("searching")
        self.status_panel.status_text = "WORKING"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/v1/memory", timeout=60.0)
                if response.status_code == 200:
                    data = response.json()
                    self.log_widget.write_line("[bold color(214)]Nārada:[/bold color(214)] Memory Log:")
                    for mem in data.get("memory", []):
                        self.log_widget.write_line(f" - [{mem.get('id')}] {mem.get('metadata', {}).get('task')}: {mem.get('text')}")
                    self.mascot.set_state("success")
                else:
                    self.mascot.set_state("error")
                    self.log_widget.write_line(f"[bold red]System:[/bold red] Error fetching memory: {response.status_code}")
        except Exception as e:
            self.mascot.set_state("error")
            self.log_widget.write_line(f"[bold red]System:[/bold red] Connection failed: {e}")
            
        self.status_panel.status_text = "ONLINE"
        await asyncio.sleep(2)
        self.mascot.set_state("idle")

    async def process_forget(self, doc_id: str) -> None:
        self.mascot.set_state("working")
        self.status_panel.status_text = "WORKING"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(f"http://localhost:8000/v1/memory/{doc_id}", timeout=60.0)
                if response.status_code == 200:
                    self.log_widget.write_line(f"[bold color(214)]Nārada:[/bold color(214)] Forgotten memory {doc_id}.")
                    self.mascot.set_state("success")
                else:
                    self.mascot.set_state("error")
                    self.log_widget.write_line(f"[bold red]System:[/bold red] Error deleting memory: {response.status_code}")
        except Exception as e:
            self.mascot.set_state("error")
            self.log_widget.write_line(f"[bold red]System:[/bold red] Connection failed: {e}")
            
        self.status_panel.status_text = "ONLINE"
        await asyncio.sleep(2)
        self.mascot.set_state("idle")

    async def process_chat(self, user_text: str) -> None:
        """Call the local API and handle state changes."""
        
        self.mascot.set_state("searching")
        self.status_panel.status_text = "WORKING"
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "messages": [{"role": "user", "content": user_text}],
                    "model": "narada"
                }
                
                response = await client.post("http://localhost:8000/v1/chat/completions", json=payload, timeout=60.0)
                
                if response.status_code == 200:
                    data = response.json()
                    reply = data["choices"][0]["message"]["content"]
                    
                    self.mascot.set_state("success")
                    self.status_panel.status_text = "ONLINE"
                    
                    self.log_widget.write_line(f"[bold color(214)]Nārada:[/bold color(214)] {reply}")
                    
                    # Return to idle after a short moment
                    await asyncio.sleep(2)
                    self.mascot.set_state("idle")
                    
                else:
                    self.mascot.set_state("error")
                    self.status_panel.status_text = "ERROR"
                    self.log_widget.write_line(f"[bold red]System:[/bold red] Error connecting to server ({response.status_code})")
                    await asyncio.sleep(2)
                    self.mascot.set_state("idle")
                    self.status_panel.status_text = "ONLINE"
                    
        except Exception as e:
            self.mascot.set_state("error")
            self.status_panel.status_text = "ERROR"
            self.log_widget.write_line(f"[bold red]System:[/bold red] Connection failed: {e}")
            await asyncio.sleep(2)
            self.mascot.set_state("idle")
            self.status_panel.status_text = "ONLINE"

if __name__ == "__main__":
    app = NaradaTerminalUI()
    app.run()
