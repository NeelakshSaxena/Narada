import pytest
import asyncio
from unittest.mock import patch, MagicMock
from providers.llm.ollama import OllamaProvider
from core.llm.models import LLMError

class AsyncMockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP Error")
            
    def json(self):
        return self.json_data


def test_ollama_provider_success():
    provider = OllamaProvider()
    
    mock_data = {
        "model": "gemma4-2b-uncensored:latest",
        "message": {
            "role": "assistant",
            "content": "Hello World"
        },
        "total_duration": 1234
    }

    async def mock_post(*args, **kwargs):
        return AsyncMockResponse(mock_data)

    with patch('httpx.AsyncClient.post', side_effect=mock_post):
        response = asyncio.run(provider.generate("Say hello"))
        assert response.text == "Hello World"
        assert response.metadata["model"] == "gemma4-2b-uncensored:latest"
        assert response.metadata["tool_calls"] == []


def test_ollama_provider_tool_calls():
    provider = OllamaProvider()
    
    mock_data = {
        "model": "gemma4-2b-uncensored:latest",
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "get_weather",
                        "arguments": {"location": "San Francisco"}
                    }
                }
            ]
        }
    }

    async def mock_post(*args, **kwargs):
        return AsyncMockResponse(mock_data)

    with patch('httpx.AsyncClient.post', side_effect=mock_post):
        response = asyncio.run(provider.generate("weather", tools=[{"type": "function", "function": {"name": "get_weather"}}]))
        assert len(response.metadata["tool_calls"]) == 1
        assert response.metadata["tool_calls"][0]["function"]["name"] == "get_weather"


def test_ollama_provider_error():
    provider = OllamaProvider()

    async def mock_post(*args, **kwargs):
        raise Exception("Connection Refused")

    with patch('httpx.AsyncClient.post', side_effect=mock_post):
        with pytest.raises(LLMError, match="Ollama API error: Connection Refused"):
            asyncio.run(provider.generate("Say hello"))
