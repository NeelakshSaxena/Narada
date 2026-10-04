from typing import Optional
from core.providers.base import LLMProvider
from core.llm.models import LLMResponse, LLMError

class SarvamProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        if not self.api_key:
            raise LLMError(message="SARVAM_API_KEY is not set", provider="sarvam")
        
        try:
            # Simulate HTTP call to Sarvam
            pass
        except Exception as e:
            raise LLMError(message=f"Sarvam API error: {str(e)}", provider="sarvam", original_error=e)
            
        return LLMResponse(text="[Sarvam Output]", metadata={"model": self.model})

    async def stream(self, prompt: str, **kwargs):
        raise NotImplementedError("Stream not implemented for Sarvam")
