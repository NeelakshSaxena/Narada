from fastapi import FastAPI
from pydantic import BaseModel
import logging
from core.runtime.runtime import NaradaCore

app = FastAPI(title="Narada API", version="0.1.0")
logger = logging.getLogger("narada")
core = NaradaCore()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str = "narada"

@app.get("/health")
async def health_check():
    return core.get_status()

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    """
    OpenAI-compatible chat completions endpoint for Open WebUI.
    """
    last_message = req.messages[-1].content if req.messages else ""
    
    # Process through AgentExecutor (Goal -> Plan -> Execute)
    final_observation = await core.agent.execute_task(last_message)
    
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "model": req.model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": final_observation
            },
            "finish_reason": "stop"
        }]
    }

@app.get("/v1/responsibilities")
async def get_responsibilities():
    """
    Endpoint to fetch active responsibilities.
    """
    return {"responsibilities": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
