import argparse
import sys
import uvicorn
import httpx
import asyncio


def start_server(host: str = "0.0.0.0", port: int = 8000):
    print(f"Starting Narada API on {host}:{port}")
    uvicorn.run("apps.api.main:app", host=host, port=port)


async def chat_repl():
    print("Welcome to Narada CLI Chat. Type 'exit' to quit.")
    async with httpx.AsyncClient() as client:
        while True:
            try:
                user_input = input("You> ")
                if user_input.strip().lower() in ["exit", "quit"]:
                    break
                
                if user_input.strip().lower() == "/audit":
                    response = await client.get("http://localhost:8000/v1/audit", timeout=60.0)
                    if response.status_code == 200:
                        data = response.json()
                        print("Narada> Audit Trail:")
                        for log in data.get("audit", []):
                            meta = log.get("metadata", {})
                            print(f" - [Resp:{meta.get('responsibility_id')}|Task:{meta.get('task_id')}] Tool:{meta.get('tool')} Action:{meta.get('action')} | Result: {log.get('text')}")
                    else:
                        print(f"Error fetching audit trail: {response.status_code}")
                    continue

                if user_input.strip().lower() == "/memory":
                    response = await client.get("http://localhost:8000/v1/memory", timeout=60.0)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Narada> Memory Log:")
                        for mem in data.get("memory", []):
                            print(f" - [{mem.get('id')}] {mem.get('metadata', {}).get('task')}: {mem.get('text')}")
                    else:
                        print(f"Error fetching memory: {response.status_code}")
                    continue

                if user_input.strip().lower().startswith("/forget "):
                    doc_id = user_input.strip().split(" ", 1)[1]
                    response = await client.delete(f"http://localhost:8000/v1/memory/{doc_id}", timeout=60.0)
                    if response.status_code == 200:
                        print(f"Narada> Forgotten memory {doc_id}.")
                    else:
                        print(f"Error deleting memory: {response.status_code}")
                    continue
                
                payload = {
                    "messages": [{"role": "user", "content": user_input}],
                    "model": "narada"
                }
                
                response = await client.post("http://localhost:8000/v1/chat/completions", json=payload, timeout=60.0)
                
                if response.status_code == 200:
                    data = response.json()
                    reply = data["choices"][0]["message"]["content"]
                    print(f"Narada> {reply}")
                else:
                    print(f"Error: Server returned {response.status_code} - {response.text}")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error connecting to server: {e}")


async def health_check_cmd():
    print("Checking system health...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "UNKNOWN")
                print(f"Overall Status: {status}")
                print("Components:")
                comps = data.get("components", {})
                for k, v in comps.items():
                    print(f"  - {k.upper()}: {v}")
            else:
                print(f"API returned {response.status_code}")
                print("Overall Status: OFFLINE")
        except Exception as e:
            print("Failed to reach FastAPI service.")
            print("Overall Status: OFFLINE")


def launch_chat():
    """Launch the Textual chat UI with the saved configuration."""
    from apps.terminal.app import NaradaTerminalUI
    app = NaradaTerminalUI()
    app.run()


def main():
    parser = argparse.ArgumentParser(description="Narada CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    start_parser = subparsers.add_parser("start", help="Start the Narada FastAPI server")
    start_parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    start_parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    
    chat_parser = subparsers.add_parser("chat", help="Start an interactive chat session")
    health_parser = subparsers.add_parser("health", help="Check system health")
    setup_parser = subparsers.add_parser("setup", help="Run the Nārada onboarding setup")
    
    args = parser.parse_args()
    
    # No subcommand: auto-detect whether onboarding is needed
    if args.command is None:
        from core.config.loader import config_exists
        if config_exists():
            launch_chat()
        else:
            from apps.terminal.setup import run_setup
            run_setup()
        return
    
    if args.command == "start":
        start_server(args.host, args.port)
    elif args.command == "chat":
        from core.config.loader import config_exists
        if not config_exists():
            from rich.console import Console
            Console().print("[yellow]Nārada has not been configured yet.[/yellow]\n")
            from apps.terminal.setup import run_setup
            run_setup()
        else:
            launch_chat()
    elif args.command == "health":
        asyncio.run(health_check_cmd())
    elif args.command == "setup":
        from apps.terminal.setup import run_setup
        run_setup()


if __name__ == "__main__":
    main()
