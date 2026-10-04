from typing import Optional
from core.providers.base import LLMProvider
from core.llm.models import LLMResponse, LLMError

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
        
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        if not self.base_url:
            raise LLMError(message="OLLAMA_BASE_URL is not set", provider="ollama")
        
        try:
            # Simulate HTTP call to Ollama
            pass
        except Exception as e:
            raise LLMError(message=f"Ollama API error: {str(e)}", provider="ollama", original_error=e)
            
        return LLMResponse(text="[Ollama Output]", metadata={"model": self.model})

    async def stream(self, prompt: str, **kwargs):
        raise NotImplementedError("Stream not implemented for Ollama")
