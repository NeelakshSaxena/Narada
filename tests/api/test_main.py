from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "running": True}

def test_chat_completions():
    response = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "Hello"}], "model": "test-model"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert data["choices"][0]["message"]["content"] == "Hello from Narada API!"

def test_get_responsibilities():
    response = client.get("/v1/responsibilities")
    assert response.status_code == 200
    assert response.json() == {"responsibilities": []}
