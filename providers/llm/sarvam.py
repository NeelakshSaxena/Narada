from typing import Optional

import httpx

from core.llm.models import LLMError, LLMResponse
from providers.llm.openai_compat import OpenAICompatibleProvider


class SarvamProvider(OpenAICompatibleProvider):
    """Sarvam chat completions (OpenAI-shaped API, `api-subscription-key` auth)."""
    provider_name = "sarvam"
    label = "Sarvam"

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None,
                 transport: Optional[httpx.AsyncBaseTransport] = None):
        super().__init__(model=model, api_key=api_key, base_url=base_url, transport=transport)

    def _headers(self):
        return {"api-subscription-key": self.api_key}

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        if not self.api_key:
            raise LLMError(message="SARVAM_API_KEY is not set", provider="sarvam")
        return await super().generate(prompt, **kwargs)
