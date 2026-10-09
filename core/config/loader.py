"""Load persisted Nārada configuration from the user workspace.

This module lives in ``core/config/`` and is intentionally free of any
provider-specific imports.  It returns plain dicts/dataclasses that a
factory in ``providers/`` can turn into concrete instances.
"""
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import yaml

from core.config.envfile import read_env_file


# Default workspace location
NARADA_HOME = os.path.expanduser("~/.narada")
CONFIG_PATH = os.path.join(NARADA_HOME, "config", "config.yaml")
ENV_PATH = os.path.join(NARADA_HOME, ".env")


@dataclass
class LLMConfig:
    """Plain value object describing the selected LLM."""
    provider: str = ""
    model: str = ""
    mode: str = "cloud"           # cloud | local | hybrid
    base_url: Optional[str] = None

    # Nested configs for hybrid mode
    cloud: Optional[Dict[str, Any]] = None
    local: Optional[Dict[str, Any]] = None


@dataclass
class NaradaConfig:
    """Top-level Nārada configuration (no secrets)."""
    user: str = ""
    llm: LLMConfig = field(default_factory=LLMConfig)
    memory: Dict[str, str] = field(default_factory=lambda: {"type": "sqlite"})
    raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_configured(self) -> bool:
        """True if onboarding has been completed (provider + model are set)."""
        return bool(self.llm.provider and self.llm.model)


def load_config(
    config_path: Optional[str] = None,
    env_path: Optional[str] = None,
) -> NaradaConfig:
    """Read ``config.yaml`` and return a structured config object.

    Does NOT load secrets — call ``load_secrets()`` separately.
    """
    config_path = config_path or CONFIG_PATH

    if not os.path.exists(config_path):
        return NaradaConfig()

    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    llm_raw = raw.get("llm") or {}
    llm = LLMConfig(
        provider=llm_raw.get("provider", ""),
        model=llm_raw.get("model", ""),
        mode=llm_raw.get("mode", "cloud"),
        base_url=llm_raw.get("base_url"),
        cloud=llm_raw.get("cloud"),
        local=llm_raw.get("local"),
    )

    memory_raw = raw.get("memory") or {}

    return NaradaConfig(
        user=raw.get("user", ""),
        llm=llm,
        memory=memory_raw,
        raw=raw,
    )


def load_secrets(env_path: Optional[str] = None) -> Dict[str, str]:
    """Read the secrets env file. Returns a plain dict of KEY=VALUE pairs."""
    env_path = env_path or ENV_PATH
    return read_env_file(env_path)


def config_exists(config_path: Optional[str] = None) -> bool:
    """Check whether onboarding has already been completed."""
    cfg = load_config(config_path)
    return cfg.is_configured
