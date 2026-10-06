import httpx
import pytest

from core.config.envfile import read_env_file, upsert_env_file
from providers.llm.discovery import DiscoveryError, list_models
from providers.llm.discovery import test_model as probe_model
from providers.tools.builtin import builtin_tools


def _client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_gemini_lists_only_generate_content_models_and_keeps_key_out_of_url():
    seen = {}

    def handler(request: httpx.Request):
        seen["url"] = str(request.url)
        seen["key"] = request.headers.get("x-goog-api-key")
        return httpx.Response(200, json={"models": [
            {"name": "models/gemini-2.5-flash", "supportedGenerationMethods": ["generateContent"]},
            {"name": "models/text-embedding-004", "supportedGenerationMethods": ["embedContent"]},
        ]})

    models = list_models("gemini", api_key="secret", client=_client(handler))
    assert models == ["gemini-2.5-flash"]
    assert seen["key"] == "secret"
    assert "secret" not in seen["url"]


def test_openai_filters_non_chat_models():
    def handler(request):
        return httpx.Response(200, json={"data": [
            {"id": "gpt-4o-mini"}, {"id": "text-embedding-3-small"},
            {"id": "gpt-4o-realtime-preview"}, {"id": "o3-mini"},
        ]})

    assert list_models("openai", api_key="k", client=_client(handler)) == ["gpt-4o-mini", "o3-mini"]


def test_invalid_key_raises_auth_error():
    def handler(request):
        return httpx.Response(401, json={"error": {"message": "bad key"}})

    with pytest.raises(DiscoveryError) as exc:
        list_models("anthropic", api_key="nope", client=_client(handler))
    assert exc.value.kind == "auth"
    assert "bad key" in str(exc.value)


def test_network_failure_raises_network_error():
    def handler(request):
        raise httpx.ConnectError("refused")

    with pytest.raises(DiscoveryError) as exc:
        list_models("ollama", client=_client(handler))
    assert exc.value.kind == "network"


def test_ollama_lists_installed_models_and_tests_model():
    def handler(request):
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "qwen3:8b"}]})
        return httpx.Response(200, json={"response": "OK"})

    client = _client(handler)
    assert list_models("ollama", client=client) == ["qwen3:8b"]
    assert probe_model("ollama", "qwen3:8b", client=client) == "OK"


def test_sarvam_validates_key_via_chat_and_uses_subscription_header():
    seen = {}

    def handler(request):
        seen["header"] = request.headers.get("api-subscription-key")
        return httpx.Response(200, json={"choices": [{"message": {"content": "OK"}}]})

    models = list_models("sarvam", api_key="sk", client=_client(handler))
    assert "sarvam-105b" in models
    assert seen["header"] == "sk"


def test_env_upsert_preserves_other_lines(tmp_path):
    path = tmp_path / ".env"
    path.write_text("# comment\nKEEP=1\nGEMINI_API_KEY=old\n", encoding="utf-8")
    upsert_env_file(str(path), {"GEMINI_API_KEY": "new", "NARADA_LLM_MODEL": "m"})
    text = path.read_text(encoding="utf-8")
    assert "# comment" in text and "KEEP=1" in text
    assert read_env_file(str(path)) == {"KEEP": "1", "GEMINI_API_KEY": "new", "NARADA_LLM_MODEL": "m"}


def test_builtin_tools_are_real():
    names = {t.name for t in builtin_tools()}
    assert {"web.search", "web.open"} <= names
    assert len(names) == 4
