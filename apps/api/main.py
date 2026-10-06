from fastapi import FastAPI
from pydantic import BaseModel
import logging
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from core.runtime.runtime import NaradaCore

app = FastAPI(title="Narada API", version="0.1.0")

import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="static")

logger = logging.getLogger("narada")
core = NaradaCore()

@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    if request.url.path != "/health":
        client_ip = request.client.host if request.client else "unknown"
        doc_id = f"telemetry-{uuid.uuid4()}"
        text = f"API Call: {request.method} {request.url.path} returned {response.status_code}"
        metadata = {
            "type": "telemetry",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency": process_time,
            "ip": client_ip,
            "timestamp": start_time
        }
        # In a real app we'd dispatch to a background task, but we log synchronously here
        await core.memory.store_metadata(doc_id=doc_id, text=text, metadata=metadata)
        
    return response

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str = "narada"

@app.get("/health")
async def health_check():
    return await core.get_status()

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

@app.get("/v1/audit")
async def get_audit_trail():
    """
    Endpoint to explicitly fetch the audit trail of the agent.
    """
    all_mem = await core.memory.get_all_metadata()
    audits = [m for m in all_mem if m.get("metadata", {}).get("type") == "audit"]
    # Sort by timestamp if available
    audits.sort(key=lambda x: x.get("metadata", {}).get("timestamp", ""), reverse=True)
    return {"audit": audits}

@app.get("/v1/memory")
async def get_memory():
    """
    Endpoint to retrieve historical task logs from the Canonical Memory Store.
    """
    memories = await core.memory.get_all_metadata()
    return {"memory": memories}

@app.delete("/v1/memory/{doc_id}")
async def delete_memory(doc_id: str):
    """
    Endpoint to explicitly delete a memory from the Canonical Memory Store.
    """
    await core.memory.delete_metadata(doc_id)
    return {"status": "deleted", "doc_id": doc_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
