"""
Model discovery and connectivity checks for LLM providers.

Used by onboarding (`narada setup`) to:
  * validate an API key,
  * fetch the models actually available to that key,
  * send a minimal test request to the chosen model.

All vendor-specific HTTP details live here so callers stay provider-agnostic.
Secrets are only ever sent in headers (never in URLs) so they don't leak into logs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import httpx

DEFAULT_TIMEOUT = 20.0
TEST_PROMPT = "Reply with the single word: OK"


class DiscoveryError(Exception):
    """Raised when a provider cannot be reached or rejects the request."""

    def __init__(self, message: str, kind: str = "unknown", status: Optional[int] = None):
        super().__init__(message)
        self.kind = kind  # "auth" | "network" | "not_found" | "unknown"
        self.status = status


@dataclass(frozen=True)
class ProviderSpec:
    key: str
    label: str
    env_var: Optional[str]          # env var the API key is stored under
    needs_key: bool = True
    default_base_url: Optional[str] = None


PROVIDERS: Dict[str, ProviderSpec] = {
    "openai": ProviderSpec("openai", "OpenAI", "OPENAI_API_KEY", default_base_url="https://api.openai.com/v1"),
    "anthropic": ProviderSpec("anthropic", "Anthropic", "ANTHROPIC_API_KEY", default_base_url="https://api.anthropic.com/v1"),
    "gemini": ProviderSpec("gemini", "Google Gemini", "GEMINI_API_KEY", default_base_url="https://generativelanguage.googleapis.com/v1beta"),
    "openrouter": ProviderSpec("openrouter", "OpenRouter", "OPENROUTER_API_KEY", default_base_url="https://openrouter.ai/api/v1"),
    "sarvam": ProviderSpec("sarvam", "Sarvam", "SARVAM_API_KEY", default_base_url="https://api.sarvam.ai/v1"),
    "other": ProviderSpec("other", "OpenAI-compatible", "NARADA_LLM_API_KEY"),
    "ollama": ProviderSpec("ollama", "Ollama", None, needs_key=False, default_base_url="http://localhost:11434"),
}

# Sarvam has no public model-listing endpoint; these are the documented chat models.
SARVAM_CHAT_MODELS = ["sarvam-105b", "sarvam-105b-conversations"]

_OPENAI_CHAT_PREFIXES = ("gpt-", "o1", "o3", "o4", "chatgpt-")
_OPENAI_EXCLUDE = ("audio", "realtime", "transcribe", "tts", "image", "search", "embedding")


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _raise_for_status(resp: httpx.Response, label: str) -> None:
    if resp.status_code < 400:
        return
    detail = _error_detail(resp)
    if resp.status_code in (401, 403):
        raise DiscoveryError(f"{label} rejected the API key. {detail}".strip(), kind="auth", status=resp.status_code)
    if resp.status_code == 404:
        raise DiscoveryError(f"{label} returned 404 (not found). {detail}".strip(), kind="not_found", status=404)
    raise DiscoveryError(f"{label} returned HTTP {resp.status_code}. {detail}".strip(), status=resp.status_code)


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


def _request(client: httpx.Client, method: str, url: str, label: str, **kwargs) -> httpx.Response:
    try:
        resp = client.request(method, url, **kwargs)
    except httpx.TimeoutException as e:
        raise DiscoveryError(f"Timed out reaching {label}.", kind="network") from e
    except httpx.HTTPError as e:
        raise DiscoveryError(f"Could not reach {label}: {e}", kind="network") from e
    _raise_for_status(resp, label)
    return resp


def _base(provider: str, base_url: Optional[str]) -> str:
    url = base_url or PROVIDERS[provider].default_base_url
    if not url:
        raise DiscoveryError("A base URL is required for this provider.", kind="not_found")
    return url.rstrip("/")


# ---------------------------------------------------------------------------
# Model listing
# ---------------------------------------------------------------------------

def list_models(
    provider: str,
    api_key: str = "",
    base_url: Optional[str] = None,
    client: Optional[httpx.Client] = None,
) -> List[str]:
    """Return model ids available to this key. Raises DiscoveryError on failure."""
    if provider not in PROVIDERS:
        raise DiscoveryError(f"Unknown provider '{provider}'.")
    owns_client = client is None
    client = client or httpx.Client(timeout=DEFAULT_TIMEOUT)
    try:
        return _LISTERS[provider](client, api_key, _base(provider, base_url))
    finally:
        if owns_client:
            client.close()


def _list_openai(client, key, base):
    data = _request(client, "GET", f"{base}/models", "OpenAI", headers={"Authorization": f"Bearer {key}"}).json()
    ids = [m["id"] for m in data.get("data", [])]
    chat = [i for i in ids if i.startswith(_OPENAI_CHAT_PREFIXES) and not any(x in i for x in _OPENAI_EXCLUDE)]
    return sorted(chat or ids)


def _list_compatible(client, key, base):
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    data = _request(client, "GET", f"{base}/models", "Provider", headers=headers).json()
    return sorted(m["id"] for m in data.get("data", []))


def _list_anthropic(client, key, base):
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
    data = _request(client, "GET", f"{base}/models", "Anthropic", headers=headers, params={"limit": 100}).json()
    return [m["id"] for m in data.get("data", [])]


def _list_gemini(client, key, base):
    data = _request(client, "GET", f"{base}/models", "Gemini",
                    headers={"x-goog-api-key": key}, params={"pageSize": 1000}).json()
    models = []
    for m in data.get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []) and "tts" not in m["name"]:
            models.append(m["name"].removeprefix("models/"))
    return models


def _list_openrouter(client, key, base):
    # The model catalogue is public, so validate the key explicitly first.
    _request(client, "GET", f"{base}/key", "OpenRouter", headers={"Authorization": f"Bearer {key}"})
    data = _request(client, "GET", f"{base}/models", "OpenRouter").json()
    return sorted(m["id"] for m in data.get("data", []))


def _list_sarvam(client, key, base):
    # No listing endpoint: validate the key with a minimal request instead.
    _test_sarvam(client, key, base, SARVAM_CHAT_MODELS[0])
    return list(SARVAM_CHAT_MODELS)


def _list_ollama(client, key, base):
    data = _request(client, "GET", f"{base}/api/tags", "Ollama").json()
    return [m["name"] for m in data.get("models", [])]


_LISTERS: Dict[str, Callable] = {
    "openai": _list_openai,
    "anthropic": _list_anthropic,
    "gemini": _list_gemini,
    "openrouter": _list_openrouter,
    "sarvam": _list_sarvam,
    "other": _list_compatible,
    "ollama": _list_ollama,
}


# ---------------------------------------------------------------------------
# Model test
# ---------------------------------------------------------------------------

def test_model(
    provider: str,
    model: str,
    api_key: str = "",
    base_url: Optional[str] = None,
    client: Optional[httpx.Client] = None,
) -> str:
    """Send a minimal prompt to the model. Returns the reply text; raises DiscoveryError."""
    if provider not in PROVIDERS:
        raise DiscoveryError(f"Unknown provider '{provider}'.")
    owns_client = client is None
    client = client or httpx.Client(timeout=60.0)
    try:
        return _TESTERS[provider](client, api_key, _base(provider, base_url), model)
    finally:
        if owns_client:
            client.close()


def _chat_body(model):
    return {"model": model, "messages": [{"role": "user", "content": TEST_PROMPT}]}


def _openai_reply(data) -> str:
    try:
        return (data["choices"][0]["message"].get("content") or "").strip()
    except (KeyError, IndexError, TypeError):
        return ""


def _test_openai_like(label):
    def _t(client, key, base, model):
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        data = _request(client, "POST", f"{base}/chat/completions", label, headers=headers, json=_chat_body(model)).json()
        return _openai_reply(data)
    return _t


def _test_sarvam(client, key, base, model):
    data = _request(client, "POST", f"{base}/chat/completions", "Sarvam",
                    headers={"api-subscription-key": key}, json=_chat_body(model)).json()
    return _openai_reply(data)


def _test_anthropic(client, key, base, model):
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
    body = {"model": model, "max_tokens": 16, "messages": [{"role": "user", "content": TEST_PROMPT}]}
    data = _request(client, "POST", f"{base}/messages", "Anthropic", headers=headers, json=body).json()
    parts = [c.get("text", "") for c in data.get("content", []) if c.get("type") == "text"]
    return "".join(parts).strip()


def _test_gemini(client, key, base, model):
    body = {"contents": [{"parts": [{"text": TEST_PROMPT}]}]}
    data = _request(client, "POST", f"{base}/models/{model}:generateContent", "Gemini",
                    headers={"x-goog-api-key": key}, json=body).json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts).strip()
    except (KeyError, IndexError, TypeError):
        return ""


def _test_ollama(client, key, base, model):
    body = {"model": model, "prompt": TEST_PROMPT, "stream": False}
    data = _request(client, "POST", f"{base}/api/generate", "Ollama", json=body).json()
    return str(data.get("response", "")).strip()


_TESTERS: Dict[str, Callable] = {
    "openai": _test_openai_like("OpenAI"),
    "openrouter": _test_openai_like("OpenRouter"),
    "other": _test_openai_like("Provider"),
    "anthropic": _test_anthropic,
    "gemini": _test_gemini,
    "sarvam": _test_sarvam,
    "ollama": _test_ollama,
}
