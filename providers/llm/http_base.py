"""Shared HTTP plumbing for remote LLM providers."""
from typing import Any, Dict, List, Optional

import httpx

from core.llm.models import LLMError
from providers.llm.catalog import mask_secret


def normalize_messages(prompt: str, kwargs: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return an OpenAI-style message list from either `messages=` or a raw prompt."""
    messages = kwargs.get("messages")
    if not messages:
        messages = [{"role": "user", "content": prompt}]
    return [{"role": m["role"], "content": m["content"]} for m in messages]


def _error_detail(resp: httpx.Response) -> str:
    try:
        data = resp.json()
    except ValueError:
        return resp.text[:200]
    err = data.get("error") if isinstance(data, dict) else None
    if isinstance(err, dict):
        return str(err.get("message", ""))[:200]
    if isinstance(err, str):
        return err[:200]
    return ""


class HTTPLLMProvider:
    """Mixin providing an authenticated JSON POST with consistent LLMError mapping."""

    provider_name: str = "remote"
    label: str = "Remote"
    api_key: str = ""
    model: str = ""
    timeout: float = 120.0
    transport: Optional[httpx.AsyncBaseTransport] = None

    async def _post(self, url: str, headers: Dict[str, str], body: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
                resp = await client.post(url, headers=headers, json=body)
        except httpx.HTTPError as e:
            raise LLMError(message=f"{self.label} API error: could not connect ({type(e).__name__})",
                           provider=self.provider_name, original_error=e)
        if resp.status_code >= 400:
            detail = _error_detail(resp)
            if resp.status_code in (401, 403):
                msg = f"{self.label} rejected the API key."
            else:
                msg = f"{self.label} API error: HTTP {resp.status_code}."
            raise LLMError(message=f"{msg} {detail}".strip(), provider=self.provider_name, status=resp.status_code)
        try:
            return resp.json()
        except ValueError as e:
            raise LLMError(message=f"{self.label} returned a non-JSON response.",
                           provider=self.provider_name, original_error=e)

    def __repr__(self) -> str:  # never expose the full key
        return f"{type(self).__name__}(model={self.model!r}, api_key={mask_secret(self.api_key)!r})"
