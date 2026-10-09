"""Provider factory: maps a configuration dict to a concrete LLMProvider instance.

This module lives in `providers/` (not `core/`) so that the architectural
boundary — core never imports providers — remains intact.  The entry-point
script or application shell calls `create_provider(config)` and injects the
result into the runtime.
"""
from typing import Any, Dict, Optional

from core.providers.base import LLMProvider
from providers.llm.catalog import PROVIDERS


def create_provider(llm_config: Dict[str, Any], secrets: Optional[Dict[str, str]] = None) -> LLMProvider:
    """Instantiate the correct LLMProvider from a persisted configuration block.

    Parameters
    ----------
    llm_config : dict
        Must contain at least ``provider`` and ``model``.
        May also include ``base_url``.
    secrets : dict, optional
        KEY=VALUE pairs loaded from ``~/.narada/.env``.
        If *None*, the factory falls back to ``os.environ``.

    Returns
    -------
    LLMProvider
        Ready-to-use provider instance.

    Raises
    ------
    ValueError
        If the provider name is unrecognised or configuration is incomplete.
    """
    import os

    provider_name = llm_config.get("provider", "").strip()
    model = llm_config.get("model", "").strip()

    if not provider_name:
        raise ValueError("llm.provider is required in configuration.")
    if not model:
        raise ValueError("llm.model is required in configuration.")

    secrets = secrets or {}

    def _secret(env_var: str) -> str:
        """Look up a secret: explicit secrets dict → process env → empty string."""
        return secrets.get(env_var) or os.getenv(env_var, "")

    spec = PROVIDERS.get(provider_name)
    base_url = llm_config.get("base_url") or (spec.default_base_url if spec else None)

    # --- Ollama (local) ---------------------------------------------------
    if provider_name == "ollama":
        from providers.llm.ollama import OllamaProvider
        return OllamaProvider(
            base_url=base_url or "http://localhost:11434",
            model=model,
        )

    # --- Gemini ------------------------------------------------------------
    if provider_name == "gemini":
        from providers.llm.gemini import GeminiProvider
        return GeminiProvider(
            api_key=_secret("GEMINI_API_KEY"),
            model=model,
            base_url=base_url,
        )

    # --- Anthropic ---------------------------------------------------------
    if provider_name == "anthropic":
        from providers.llm.anthropic import AnthropicProvider
        return AnthropicProvider(
            api_key=_secret("ANTHROPIC_API_KEY"),
            model=model,
            base_url=base_url,
        )

    # --- Sarvam ------------------------------------------------------------
    if provider_name == "sarvam":
        from providers.llm.sarvam import SarvamProvider
        return SarvamProvider(
            api_key=_secret("SARVAM_API_KEY"),
            model=model,
            base_url=base_url,
        )

    # --- OpenAI ------------------------------------------------------------
    if provider_name == "openai":
        from providers.llm.openai_compat import OpenAIProvider
        return OpenAIProvider(
            api_key=_secret("OPENAI_API_KEY"),
            model=model,
            base_url=base_url,
        )

    # --- OpenRouter --------------------------------------------------------
    if provider_name == "openrouter":
        from providers.llm.openai_compat import OpenRouterProvider
        return OpenRouterProvider(
            api_key=_secret("OPENROUTER_API_KEY"),
            model=model,
            base_url=base_url,
        )

    # --- Generic OpenAI-compatible ("other") --------------------------------
    if provider_name == "other":
        from providers.llm.openai_compat import OpenAICompatibleProvider
        return OpenAICompatibleProvider(
            api_key=_secret("NARADA_LLM_API_KEY"),
            model=model,
            base_url=base_url,
        )

    raise ValueError(f"Unknown LLM provider: '{provider_name}'. "
                     f"Supported: {', '.join(PROVIDERS.keys())}")
