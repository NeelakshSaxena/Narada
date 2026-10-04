# Phase 2: Configuration and Provider Gateway Logbook

## Objective
Establish a clean provider gateway to connect Narada to different LLMs (Sarvam, Ollama) via environment configuration, without modifying core agent code. Ensure absolute isolation of provider SDKs and enforce internal type normalization.

## Branch
`phase/02-configuration-gateway`

## Changes Made
- Created `core/config/settings.py` for configuration loading via `os.getenv`, isolating secrets and endpoints (e.g. `SARVAM_API_KEY`, `OLLAMA_BASE_URL`).
- Introduced normalized internal models `LLMResponse` and `LLMError` in `core/llm/models.py`.
- Updated the `LLMProvider` interface in `core/providers/base.py` to exclusively return `LLMResponse` and explicitly require `stream` method signatures.
- Implemented `FakeLLMProvider` (`providers/llm/fake.py`), `SarvamProvider` (`providers/llm/sarvam.py`), and `OllamaProvider` (`providers/llm/ollama.py`) conforming to the updated interface.
- Added comprehensive asynchronous unit tests in `tests/providers/test_llm_providers.py` covering success paths, missing configuration/auth errors, and fake provider simulation.
- Updated `pyproject.toml` to include `pytest-asyncio` as a dependency.

## Testing & Verification
- Unit tests written to verify the configuration failure paths for Ollama and Sarvam without requiring live API keys.
- Fake provider tested for both success and error normalization.
- Verified that no provider-specific response objects or exceptions leak through the `generate` function.

## Exit Criteria Checklist
- [x] Provider-specific types do not leak into core.
- [x] Provider errors are normalized into `LLMError`.
- [x] Supports synchronous generation (`generate`) and stubs streaming (`stream`).
- [x] Credentials are not hard-coded (loaded from settings).
- [x] Tests use mocks/fakes and do not require live credentials.
- [x] Ollama is not bundled into `narada-core` (accessed via network config).
- [x] No secrets are printed in logs.

## Pre-Merge Status
All requirements for Phase 2 are fulfilled.
