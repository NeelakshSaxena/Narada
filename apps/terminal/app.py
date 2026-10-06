from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Static, RichLog
from textual.reactive import reactive
from rich.text import Text
from rich.table import Table

from apps.terminal.mascot import MascotWidget

import asyncio
import httpx

class StatusPanel(Static):
    """Displays the current status of the agent."""
    status_text = reactive("ONLINE")
    model_text = reactive("Unknown / unknown")

    def render(self) -> Table:
        table = Table.grid(expand=True)
        table.add_column(justify="left")
        table.add_column(justify="right")
        
        status_color = {
            "ONLINE": "#d4af37", # warm gold/positive accent
            "THINKING": "#d4af37",
            "WORKING": "#4a6fa5", # muted blue
            "ERROR": "red"
        }.get(self.status_text, "white")
        
        table.add_row(
            Text("NĀRADA", style="bold white"),
            Text(f"● {self.status_text}", style=f"bold {status_color}")
        )
        table.add_row(
            Text(f"MODEL  {self.model_text}", style="dim white"),
            ""
        )
        return table

class NaradaTerminalUI(App):
    """The main Terminal UI for Narada."""
    
    CSS = """
    Screen {
        background: #0f111a;
        color: #e2e4e9;
    }
    
    StatusPanel {
        dock: top;
        height: 2;
        padding: 0 2;
        background: #0f111a;
        border-bottom: solid #d4af37;
    }
    
    #main-container {
        layout: horizontal;
        height: 1fr;
    }
    
    #mascot-container {
        width: 35;
        height: 1fr;
        align: center middle;
        border-right: solid #4a6fa5;
        color: #d4af37;
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
    }
    
    Input {
        dock: bottom;
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
        yield StatusPanel(id="status-panel")
        
        with Horizontal(id="main-container"):
            with Vertical(id="mascot-container"):
                yield MascotWidget(id="mascot")
            
            with Vertical(id="chat-container"):
                yield RichLog(id="chat-log", highlight=True, markup=True)
                yield Input(placeholder="› ", id="chat-input")

    def on_mount(self) -> None:
        self.title = "Nārada Terminal"
        self.log_widget = self.query_one("#chat-log", RichLog)
        self.mascot = self.query_one("#mascot", MascotWidget)
        self.status_panel = self.query_one("#status-panel", StatusPanel)
        
        greeting = Text()
        greeting.append("\nNārada\n\n", style="bold #d4af37")
        greeting.append("Good evening.\nWhat shall we work on?\n", style="white")
        self.log_widget.write(greeting)
        
        self.query_one(Input).focus()
        
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
                    self.status_panel.model_text = f"{provider} / {model}"
                    if self.status_panel.status_text == "ERROR" and data.get("status") != "ERROR":
                        self.status_panel.status_text = "ONLINE"
                else:
                    self.status_panel.status_text = "ERROR"
        except Exception:
            pass

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()
        if not user_text:
            return
            
        if user_text.lower() in ["exit", "quit"]:
            self.exit()
            return
            
        event.input.value = ""
        
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

        self.run_worker(self.process_chat(user_text), exclusive=True)

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

    async def process_chat(self, user_text: str) -> None:
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
                    
                    t = Text()
                    t.append("Nārada\n\n", style="bold #d4af37")
                    t.append(reply + "\n", style="white")
                    self.log_widget.write(t)
                    
                    await asyncio.sleep(2)
                    self.mascot.set_state("idle")
                    
                else:
                    self.mascot.set_state("error")
                    self.status_panel.status_text = "ERROR"
                    self.log_widget.write(Text(f"System: Error connecting to server ({response.status_code})\n", style="bold red"))
                    await asyncio.sleep(2)
                    self.mascot.set_state("idle")
                    self.status_panel.status_text = "ONLINE"
                    
        except Exception as e:
            self.mascot.set_state("error")
            self.status_panel.status_text = "ERROR"
            self.log_widget.write(Text(f"System: Connection failed: {e}\n", style="bold red"))
            await asyncio.sleep(2)
            self.mascot.set_state("idle")
            self.status_panel.status_text = "ONLINE"

if __name__ == "__main__":
    app = NaradaTerminalUI()
    app.run()
