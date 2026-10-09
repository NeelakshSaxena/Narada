"""Static catalogue of supported LLM providers (labels, credential env vars, default endpoints)."""
from dataclasses import dataclass
from typing import Dict, Optional


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
    "other": ProviderSpec("other", "OpenAI-compatible", "NARADA_LLM_API_KEY", needs_key=False),
    "ollama": ProviderSpec("ollama", "Ollama", None, needs_key=False, default_base_url="http://localhost:11434"),
}


def provider_label(key: str) -> str:
    spec = PROVIDERS.get(key)
    return spec.label if spec else key


def mask_secret(secret: str) -> str:
    """Render a secret safely for display, e.g. 'sk-…9f3a'."""
    if not secret:
        return ""
    if len(secret) <= 8:
        return "•" * len(secret)
    return f"{secret[:3]}…{secret[-4:]}"
