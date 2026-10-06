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

@app.on_event("startup")
async def startup_event():
    await core.boot()

class ResponsibilityRequest(BaseModel):
    task: str
    interval: int = 1

@app.get("/v1/responsibilities")
async def get_responsibilities():
    """
    Endpoint to fetch active responsibilities.
    """
    return {"responsibilities": []}

@app.post("/v1/responsibilities")
async def create_responsibility(req: ResponsibilityRequest):
    job_id = await core.scheduler.schedule_job(req.task, "interval", interval=req.interval)
    return {"status": "created", "job_id": job_id}

@app.get("/v1/memory")
async def get_memory():
    """
    Endpoint to retrieve historical task logs from the Canonical Memory Store.
    """
    memories = await core.memory.get_all_metadata()
    return {"memory": memories}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
