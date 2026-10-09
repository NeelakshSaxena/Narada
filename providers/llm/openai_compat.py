"""OpenAI-compatible chat providers: OpenAI, OpenRouter and any compatible server."""
from typing import Dict, Optional

import httpx

from core.llm.models import LLMError, LLMResponse
from core.providers.base import LLMProvider
from providers.llm.catalog import PROVIDERS
from providers.llm.http_base import HTTPLLMProvider, normalize_messages


class OpenAICompatibleProvider(HTTPLLMProvider, LLMProvider):
    provider_name = "other"
    label = "OpenAI-compatible"

    def __init__(self, model: str, api_key: str = "", base_url: Optional[str] = None,
                 transport: Optional[httpx.AsyncBaseTransport] = None):
        if not model:
            raise ValueError("A model must be specified.")
        self.model = model
        self.api_key = api_key
        self.base_url = (base_url or PROVIDERS[self.provider_name].default_base_url or "").rstrip("/")
        self.transport = transport

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def _check_ready(self) -> None:
        if PROVIDERS[self.provider_name].needs_key and not self.api_key:
            env_var = PROVIDERS[self.provider_name].env_var
            raise LLMError(message=f"{env_var} is not set", provider=self.provider_name)
        if not self.base_url:
            raise LLMError(message="Base URL is not set", provider=self.provider_name)

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        self._check_ready()
        body = {"model": self.model, "messages": normalize_messages(prompt, kwargs)}
        if kwargs.get("max_tokens"):
            body["max_tokens"] = kwargs["max_tokens"]
        if kwargs.get("tools"):
            body["tools"] = kwargs["tools"]
        data = await self._post(f"{self.base_url}/chat/completions", self._headers(), body)
        try:
            message = data["choices"][0]["message"]
        except (KeyError, IndexError, TypeError):
            raise LLMError(message=f"{self.label} returned an unexpected response.", provider=self.provider_name)
        return LLMResponse(
            text=(message.get("content") or "").strip(),
            metadata={"provider": self.provider_name, "model": data.get("model", self.model),
                      "tool_calls": message.get("tool_calls", [])},
        )

    async def stream(self, prompt: str, **kwargs):
        raise NotImplementedError(f"Stream not implemented for {self.label}")


class OpenAIProvider(OpenAICompatibleProvider):
    provider_name = "openai"
    label = "OpenAI"


class OpenRouterProvider(OpenAICompatibleProvider):
    provider_name = "openrouter"
    label = "OpenRouter"
