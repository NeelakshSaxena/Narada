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

def main():
    parser = argparse.ArgumentParser(description="Narada CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    start_parser = subparsers.add_parser("start", help="Start the Narada FastAPI server")
    start_parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    start_parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    
    chat_parser = subparsers.add_parser("chat", help="Start an interactive chat session")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_server(args.host, args.port)
    elif args.command == "chat":
        asyncio.run(chat_repl())

if __name__ == "__main__":
    main()
