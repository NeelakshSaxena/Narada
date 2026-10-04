import pytest
from core.llm.models import LLMResponse, LLMError
from providers.llm.fake import FakeLLMProvider
from providers.llm.sarvam import SarvamProvider
from providers.llm.ollama import OllamaProvider

@pytest.mark.asyncio
async def test_fake_provider_success():
    provider = FakeLLMProvider(response_text="Hello")
    resp = await provider.generate("Hi")
    assert resp.text == "Hello"
    assert "prompt_length" in resp.metadata

@pytest.mark.asyncio
async def test_fake_provider_error():
    provider = FakeLLMProvider(should_fail=True)
    with pytest.raises(LLMError) as exc:
        await provider.generate("Hi")
    assert exc.value.provider == "fake"
    assert "Fake error" in str(exc.value)

@pytest.mark.asyncio
async def test_sarvam_auth_failure():
    provider = SarvamProvider(api_key="", model="sarvam-105b")
    with pytest.raises(LLMError) as exc:
        await provider.generate("Hi")
    assert exc.value.provider == "sarvam"
    assert "SARVAM_API_KEY is not set" in str(exc.value)

@pytest.mark.asyncio
async def test_ollama_base_url_failure():
    provider = OllamaProvider(base_url="", model="llama2")
    with pytest.raises(LLMError) as exc:
        await provider.generate("Hi")
    assert exc.value.provider == "ollama"
    assert "OLLAMA_BASE_URL is not set" in str(exc.value)
