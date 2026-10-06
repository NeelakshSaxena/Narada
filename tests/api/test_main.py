from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "running": True}

from unittest.mock import patch

def test_chat_completions():
    with patch('providers.llm.ollama.OllamaProvider.generate') as mock_gen:
        from core.llm.models import LLMResponse
        mock_gen.return_value = LLMResponse(text="Mocked observation", metadata={"model": "test-model"})
        
        response = client.post(
            "/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}], "model": "test-model"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "chat.completion"
        assert data["choices"][0]["message"]["content"] == "Mocked observation"

def test_get_responsibilities():
    response = client.get("/v1/responsibilities")
    assert response.status_code == 200
    assert response.json() == {"responsibilities": []}
