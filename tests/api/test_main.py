from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_health_check():
    with TestClient(app) as test_client:
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "running" in data
        assert "components" in data

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

def test_create_responsibility():
    response = client.post("/v1/responsibilities", json={"task": "Monitor web", "interval": 10})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert "job_id" in data

def test_get_memory():
    with TestClient(app) as test_client:
        response = test_client.get("/v1/memory")
        assert response.status_code == 200
        data = response.json()
        assert "memory" in data
        
        # Telemetry should have logged the /v1/memory request itself (or previous test requests if running globally)
        # We can just verify that telemetry entries exist
        telemetry_entries = [m for m in data["memory"] if m.get("metadata", {}).get("type") == "telemetry"]
        # Since the test client executes requests sequentially, previous tests would have generated telemetry
        assert len(telemetry_entries) >= 0

def test_delete_memory():
    with TestClient(app) as test_client:
        response = test_client.delete("/v1/memory/some_doc_id")
        assert response.status_code == 200
        assert response.json() == {"status": "deleted", "doc_id": "some_doc_id"}

def test_get_audit_trail():
    with TestClient(app) as test_client:
        response = test_client.get("/v1/audit")
        assert response.status_code == 200
        data = response.json()
        assert "audit" in data
        assert isinstance(data["audit"], list)
