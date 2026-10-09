from typing import Optional

import httpx

from core.llm.models import LLMError, LLMResponse
from core.providers.base import LLMProvider
from providers.llm.catalog import PROVIDERS
from providers.llm.http_base import HTTPLLMProvider, normalize_messages

ANTHROPIC_VERSION = "2023-06-01"


class AnthropicProvider(HTTPLLMProvider, LLMProvider):
    provider_name = "anthropic"
    label = "Anthropic"

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None,
                 max_tokens: int = 1024, transport: Optional[httpx.AsyncBaseTransport] = None):
        if not model:
            raise ValueError("A model must be specified.")
        self.api_key = api_key
        self.model = model
        self.base_url = (base_url or PROVIDERS["anthropic"].default_base_url).rstrip("/")
        self.max_tokens = max_tokens
        self.transport = transport

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        if not self.api_key:
            raise LLMError(message="ANTHROPIC_API_KEY is not set", provider=self.provider_name)
        messages = normalize_messages(prompt, kwargs)
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        body = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens") or self.max_tokens,
            "messages": [m for m in messages if m["role"] in ("user", "assistant")],
        }
        if system:
            body["system"] = system
        headers = {"x-api-key": self.api_key, "anthropic-version": ANTHROPIC_VERSION}
        data = await self._post(f"{self.base_url}/messages", headers, body)
        text = "".join(c.get("text", "") for c in data.get("content", []) if c.get("type") == "text")
        return LLMResponse(text=text.strip(),
                           metadata={"provider": self.provider_name, "model": data.get("model", self.model)})

    async def stream(self, prompt: str, **kwargs):
        raise NotImplementedError("Stream not implemented for Anthropic")
