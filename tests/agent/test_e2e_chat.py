import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from apps.api.main import app

class AsyncMockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP Error")
            
    def json(self):
        return self.json_data

def test_e2e_chat_completions():
    from apps.api.main import core
    core.pool.connected = True
    async def mock_execute(*args, **kwargs): pass
    core.pool.execute = mock_execute
    
    client = TestClient(app)
    
    async def mock_generate(*args, **kwargs):
        from core.llm.models import LLMResponse
        return LLMResponse(text="Step 1: Check logs. Step 2: Fix. Observation: Done.", metadata={})

    with patch.object(core.agent.provider, 'generate', side_effect=mock_generate):
        response = client.post(
            "/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Fix the database"}], "model": "narada"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "chat.completion"
        assert "Observation: Done." in data["choices"][0]["message"]["content"]
