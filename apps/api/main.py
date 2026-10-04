from fastapi import FastAPI
import logging

app = FastAPI(title="Narada API", version="0.1.0")
logger = logging.getLogger("narada")

@app.get("/health")
async def health_check():
    """
    Returns a healthy state. 
    Required for container orchestration and Phase 1 verification.
    """
    return {"status": "ok", "service": "narada-core"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
