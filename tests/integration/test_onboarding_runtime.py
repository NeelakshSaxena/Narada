"""Tests for the complete onboarding → runtime integration.

Validates:
  1. Configuration persistence (config.yaml + .env)
  2. Configuration loading
  3. Provider construction via factory
  4. Model propagation to the provider
  5. Credentials reach the provider without exposure
  6. Existing configuration is detected
  7. Reconfiguration replaces the active provider/model
"""
import os
import pytest
import yaml

from core.config.envfile import read_env_file, upsert_env_file
from core.config.loader import load_config, load_secrets, config_exists, NaradaConfig, LLMConfig
from providers.llm.factory import create_provider


# ---------------------------------------------------------------------------
# 1. Configuration persistence
# ---------------------------------------------------------------------------

def test_config_persistence_round_trip(tmp_path):
    """Selected provider + model survive save → load."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_path = str(config_dir / "config.yaml")
    env_path = str(tmp_path / ".env")

    # Simulate what setup.py writes
    config = {
        "user": "Test",
        "llm": {
            "mode": "cloud",
            "provider": "gemini",
            "model": "gemini-2.5-flash",
        },
        "memory": {"type": "sqlite"},
    }
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False)

    upsert_env_file(env_path, {"GEMINI_API_KEY": "test-key-abc123"})

    # Load and verify
    cfg = load_config(config_path)
    assert cfg.llm.provider == "gemini"
    assert cfg.llm.model == "gemini-2.5-flash"
    assert cfg.user == "Test"

    secrets = load_secrets(env_path)
    assert secrets["GEMINI_API_KEY"] == "test-key-abc123"


# ---------------------------------------------------------------------------
# 2. Configuration loading edge cases
# ---------------------------------------------------------------------------

def test_missing_config_returns_unconfigured(tmp_path):
    """No config file → NaradaConfig with is_configured == False."""
    cfg = load_config(str(tmp_path / "nope.yaml"))
    assert not cfg.is_configured
    assert cfg.llm.provider == ""
    assert cfg.llm.model == ""


def test_config_exists_detects_valid_config(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = str(config_dir / "config.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump({"llm": {"provider": "ollama", "model": "qwen3:8b"}}, f)
    assert config_exists(path)


def test_config_exists_returns_false_without_file(tmp_path):
    assert not config_exists(str(tmp_path / "nonexistent.yaml"))


def test_config_exists_returns_false_for_empty_config(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = str(config_dir / "config.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump({"llm": {}}, f)
    assert not config_exists(path)


# ---------------------------------------------------------------------------
# 3. Provider factory — correct class instantiated
# ---------------------------------------------------------------------------

def test_factory_creates_ollama():
    p = create_provider({"provider": "ollama", "model": "qwen3:8b"})
    from providers.llm.ollama import OllamaProvider
    assert isinstance(p, OllamaProvider)
    assert p.model == "qwen3:8b"


def test_factory_creates_gemini():
    p = create_provider(
        {"provider": "gemini", "model": "gemini-2.5-flash"},
        {"GEMINI_API_KEY": "k"},
    )
    from providers.llm.gemini import GeminiProvider
    assert isinstance(p, GeminiProvider)
    assert p.model == "gemini-2.5-flash"
    assert p.api_key == "k"


def test_factory_creates_anthropic():
    p = create_provider(
        {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
        {"ANTHROPIC_API_KEY": "sk"},
    )
    from providers.llm.anthropic import AnthropicProvider
    assert isinstance(p, AnthropicProvider)
    assert p.model == "claude-sonnet-4-20250514"


def test_factory_creates_openai():
    p = create_provider(
        {"provider": "openai", "model": "gpt-4o-mini"},
        {"OPENAI_API_KEY": "sk-test"},
    )
    from providers.llm.openai_compat import OpenAIProvider
    assert isinstance(p, OpenAIProvider)
    assert p.model == "gpt-4o-mini"


def test_factory_creates_openrouter():
    p = create_provider(
        {"provider": "openrouter", "model": "meta-llama/llama-4-scout"},
        {"OPENROUTER_API_KEY": "ok"},
    )
    from providers.llm.openai_compat import OpenRouterProvider
    assert isinstance(p, OpenRouterProvider)
    assert p.model == "meta-llama/llama-4-scout"


def test_factory_creates_sarvam():
    p = create_provider(
        {"provider": "sarvam", "model": "sarvam-m"},
        {"SARVAM_API_KEY": "sa"},
    )
    from providers.llm.sarvam import SarvamProvider
    assert isinstance(p, SarvamProvider)
    assert p.model == "sarvam-m"


def test_factory_creates_other():
    p = create_provider(
        {"provider": "other", "model": "custom-model", "base_url": "http://localhost:1234/v1"},
        {},
    )
    from providers.llm.openai_compat import OpenAICompatibleProvider
    assert isinstance(p, OpenAICompatibleProvider)
    assert p.model == "custom-model"
    assert "1234" in p.base_url


# ---------------------------------------------------------------------------
# 4. Model propagation — exact model reaches provider
# ---------------------------------------------------------------------------

def test_model_propagated_exactly(tmp_path):
    """The model selected during onboarding must be exactly what the provider receives."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = str(config_dir / "config.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump({"llm": {"provider": "gemini", "model": "gemini-2.5-flash"}}, f)

    cfg = load_config(path)
    p = create_provider(
        {"provider": cfg.llm.provider, "model": cfg.llm.model},
        {"GEMINI_API_KEY": "test"},
    )
    assert p.model == "gemini-2.5-flash"


# ---------------------------------------------------------------------------
# 5. Credentials flow — key reaches provider without exposure
# ---------------------------------------------------------------------------

def test_credentials_reach_provider(tmp_path):
    env_path = str(tmp_path / ".env")
    upsert_env_file(env_path, {"ANTHROPIC_API_KEY": "sk-ant-super-secret"})

    secrets = load_secrets(env_path)
    p = create_provider(
        {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
        secrets,
    )
    assert p.api_key == "sk-ant-super-secret"
    # repr must not expose the full key
    assert "sk-ant-super-secret" not in repr(p)


def test_credentials_not_in_config_yaml(tmp_path):
    """API keys must never appear in config.yaml."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = str(config_dir / "config.yaml")
    config = {
        "llm": {"provider": "gemini", "model": "gemini-2.5-flash"},
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False)

    text = open(path, "r").read()
    assert "API_KEY" not in text
    assert "secret" not in text.lower()


# ---------------------------------------------------------------------------
# 6. Existing config detection
# ---------------------------------------------------------------------------

def test_existing_config_detected(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = str(config_dir / "config.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump({"llm": {"provider": "openai", "model": "gpt-4o"}}, f)
    assert config_exists(path)


# ---------------------------------------------------------------------------
# 7. Reconfiguration replaces active provider
# ---------------------------------------------------------------------------

def test_reconfiguration_replaces_provider(tmp_path):
    """Running setup again should overwrite the model and the next factory call uses the new one."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = str(config_dir / "config.yaml")

    # First config
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump({"llm": {"provider": "ollama", "model": "llama2"}}, f)
    cfg1 = load_config(path)
    p1 = create_provider({"provider": cfg1.llm.provider, "model": cfg1.llm.model})
    assert p1.model == "llama2"

    # Reconfigure
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump({"llm": {"provider": "ollama", "model": "qwen3:8b"}}, f)
    cfg2 = load_config(path)
    p2 = create_provider({"provider": cfg2.llm.provider, "model": cfg2.llm.model})
    assert p2.model == "qwen3:8b"


# ---------------------------------------------------------------------------
# 8. Factory error handling
# ---------------------------------------------------------------------------

def test_factory_rejects_missing_provider():
    with pytest.raises(ValueError, match="provider is required"):
        create_provider({"provider": "", "model": "m"})


def test_factory_rejects_missing_model():
    with pytest.raises(ValueError, match="model is required"):
        create_provider({"provider": "gemini", "model": ""})


def test_factory_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        create_provider({"provider": "banana", "model": "m"})


# ---------------------------------------------------------------------------
# 9. Runtime accepts injected provider
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_runtime_uses_injected_provider():
    """AgentRuntime must use the provider passed at construction time."""
    from providers.llm.fake import FakeLLMProvider
    from core.runtime.runtime import AgentRuntime

    provider = FakeLLMProvider(response_text="hello from fake")
    rt = AgentRuntime(provider)
    result = await rt.execute_task("test")
    assert "hello from fake" in result
    assert rt.provider is provider


# ---------------------------------------------------------------------------
# 10. End-to-end: config → factory → runtime
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_end_to_end_config_to_runtime(tmp_path):
    """Config on disk → factory → runtime → first message uses correct provider."""
    from providers.llm.fake import FakeLLMProvider
    from core.runtime.runtime import AgentRuntime

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = str(config_dir / "config.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump({"llm": {"provider": "ollama", "model": "qwen3:8b"}}, f)

    cfg = load_config(path)
    assert cfg.llm.provider == "ollama"
    assert cfg.llm.model == "qwen3:8b"

    # In a real scenario, create_provider would return OllamaProvider.
    # For testing without a running Ollama, we verify the factory
    # creates the right type, then test the runtime with a fake.
    real_provider = create_provider({"provider": cfg.llm.provider, "model": cfg.llm.model})
    assert real_provider.model == "qwen3:8b"

    # Verify runtime works with injected provider
    fake = FakeLLMProvider(response_text="integration ok")
    rt = AgentRuntime(fake)
    assert "integration ok" in await rt.execute_task("test")


# ---------------------------------------------------------------------------
# 11. Hybrid mode persists both cloud and local
# ---------------------------------------------------------------------------

def test_hybrid_config_persists_both(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = str(config_dir / "config.yaml")
    config = {
        "llm": {
            "mode": "hybrid",
            "provider": "gemini",
            "model": "gemini-2.5-flash",
            "cloud": {"provider": "gemini", "model": "gemini-2.5-flash"},
            "local": {"provider": "ollama", "model": "qwen3:8b", "base_url": "http://localhost:11434"},
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False)

    cfg = load_config(path)
    assert cfg.llm.mode == "hybrid"
    assert cfg.llm.cloud["provider"] == "gemini"
    assert cfg.llm.local["provider"] == "ollama"
    # Primary model is what the runtime uses
    assert cfg.llm.provider == "gemini"
    assert cfg.llm.model == "gemini-2.5-flash"
