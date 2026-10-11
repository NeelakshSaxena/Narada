import json
import pytest
import httpx

from providers.llm.gemini import GeminiProvider


@pytest.mark.asyncio
async def test_gemini_multiturn_tool_calling_preserves_thought_signatures_and_ids():
    captured_requests = []

    def handler(request: httpx.Request):
        captured_requests.append(json.loads(request.content.decode("utf-8")))
        if len(captured_requests) == 1:
            # Turn 1: model proposes tool call with thoughtSignature and id
            return httpx.Response(200, json={
                "candidates": [{
                    "content": {
                        "parts": [{
                            "functionCall": {
                                "name": "filesystem.write",
                                "args": {"path": "helloworld.txt", "content": "hello world"},
                                "id": "call_12345"
                            },
                            "thoughtSignature": "sig_abc123"
                        }],
                        "role": "model"
                    },
                    "finishReason": "STOP"
                }]
            })
        else:
            # Turn 2: model sees functionResponse and returns final text
            return httpx.Response(200, json={
                "candidates": [{
                    "content": {
                        "parts": [{
                            "text": "File helloworld.txt written successfully."
                        }],
                        "role": "model"
                    },
                    "finishReason": "STOP"
                }]
            })

    transport = httpx.MockTransport(handler)
    provider = GeminiProvider(api_key="test-key", model="gemini-3.1-flash-lite", transport=transport)

    # 1. Turn 1
    resp1 = await provider.generate(
        "Write helloworld.txt",
        tools=[{
            "type": "function",
            "function": {
                "name": "filesystem.write",
                "description": "Write a file",
                "parameters": {"type": "object"}
            }
        }]
    )
    assert len(resp1.metadata["tool_calls"]) == 1
    tool_call = resp1.metadata["tool_calls"][0]
    assert tool_call["id"] == "call_12345"
    assert tool_call["thoughtSignature"] == "sig_abc123"
    assert tool_call["function"]["name"] == "filesystem.write"

    # 2. Turn 2: Feed back conversation history with functionResponse
    messages = [
        {"role": "user", "content": "Write helloworld.txt"},
        {"role": "assistant", "content": resp1.text, "tool_calls": resp1.metadata["tool_calls"]},
        {
            "role": "tool",
            "name": "filesystem.write",
            "tool_call_id": tool_call["id"],
            "content": json.dumps({"status": "SUCCESS", "result": True})
        }
    ]

    resp2 = await provider.generate("", messages=messages)
    assert resp2.text == "File helloworld.txt written successfully."
    assert resp2.metadata["tool_calls"] == []

    # Verify captured request structure for Turn 2
    req2 = captured_requests[1]
    contents = req2["contents"]
    assert len(contents) == 3
    # Check model turn contains preserved thoughtSignature and id
    model_turn = contents[1]
    assert model_turn["role"] == "model"
    assert model_turn["parts"][0]["functionCall"]["id"] == "call_12345"
    assert model_turn["parts"][0]["thoughtSignature"] == "sig_abc123"

    # Check functionResponse turn contains correct response object, name, and id
    func_turn = contents[2]
    assert func_turn["role"] == "user"
    func_resp = func_turn["parts"][0]["functionResponse"]
    assert func_resp["name"] == "filesystem.write"
    assert func_resp["id"] == "call_12345"
    assert func_resp["response"] == {"status": "SUCCESS", "result": True}
