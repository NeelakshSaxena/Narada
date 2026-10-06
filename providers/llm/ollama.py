import httpx
from typing import Optional, List, Dict, Any
from core.providers.base import LLMProvider
from core.llm.models import LLMResponse, LLMError

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gemma4-2b-uncensored:latest"):
        self.base_url = base_url
        self.model = model
        
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        if not self.base_url:
            raise LLMError(message="OLLAMA_BASE_URL is not set", provider="ollama")
            
        # Support either raw prompt or messages array
        messages = kwargs.get("messages")
        if not messages:
            messages = [{"role": "user", "content": prompt}]
            
        tools = kwargs.get("tools")
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        if tools:
            payload["tools"] = tools
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload, timeout=120.0)
                response.raise_for_status()
                data = response.json()
                
                message = data.get("message", {})
                content = message.get("content", "")
                tool_calls = message.get("tool_calls", [])
                
                return LLMResponse(
                    text=content,
                    metadata={
                        "model": data.get("model", self.model),
                        "total_duration": data.get("total_duration"),
                        "tool_calls": tool_calls
                    }
                )
        except Exception as e:
            raise LLMError(message=f"Ollama API error: {str(e)}", provider="ollama", original_error=e)

    async def stream(self, prompt: str, **kwargs):
        raise NotImplementedError("Stream not implemented for Ollama")
