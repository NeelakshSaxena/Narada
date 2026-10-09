from typing import Optional

import httpx

from core.llm.models import LLMError, LLMResponse
from core.providers.base import LLMProvider
from providers.llm.catalog import PROVIDERS
from providers.llm.http_base import HTTPLLMProvider, normalize_messages


class GeminiProvider(HTTPLLMProvider, LLMProvider):
    provider_name = "gemini"
    label = "Gemini"

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None,
                 transport: Optional[httpx.AsyncBaseTransport] = None):
        if not model:
            raise ValueError("A model must be specified.")
        self.api_key = api_key
        self.model = model.removeprefix("models/")
        self.base_url = (base_url or PROVIDERS["gemini"].default_base_url).rstrip("/")
        self.transport = transport

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        if not self.api_key:
            raise LLMError(message="GEMINI_API_KEY is not set", provider=self.provider_name)
        messages = normalize_messages(prompt, kwargs)
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        contents = []
        for m in messages:
            if m["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": m["content"]}]})
            elif m["role"] == "assistant":
                parts = []
                if m.get("content"):
                    parts.append({"text": m["content"]})
                
                tool_calls = m.get("tool_calls", [])
                for call in tool_calls:
                    if call.get("type") == "function":
                        fn = call.get("function", {})
                        parts.append({
                            "functionCall": {
                                "name": fn.get("name"),
                                "args": fn.get("arguments", {})
                            }
                        })
                contents.append({"role": "model", "parts": parts})
            elif m["role"] == "tool":
                # Map to functionResponse
                name = m.get("name", "unknown")
                contents.append({
                    "role": "user", 
                    "parts": [{
                        "functionResponse": {
                            "name": name,
                            "response": {"result": m["content"]}
                        }
                    }]
                })
        body = {"contents": contents}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        if kwargs.get("max_tokens"):
            body["generationConfig"] = {"maxOutputTokens": kwargs["max_tokens"]}
            
        # Add tools support mapping OpenAI format to Gemini format
        tools_list = kwargs.get("tools")
        if tools_list:
            function_declarations = []
            for t in tools_list:
                if t.get("type") == "function":
                    fn = t.get("function", {})
                    # Gemini doesn't support empty parameters gracefully, ensure they are removed or are valid
                    decl = {
                        "name": fn.get("name"),
                        "description": fn.get("description"),
                    }
                    if fn.get("parameters"):
                        decl["parameters"] = fn.get("parameters")
                    function_declarations.append(decl)
                    
            if function_declarations:
                body["tools"] = [{"functionDeclarations": function_declarations}]
                
        # Key goes in a header, never in the URL.
        data = await self._post(f"{self.base_url}/models/{self.model}:generateContent",
                                {"x-goog-api-key": self.api_key}, body)
                                
        text = ""
        tool_calls = []
        try:
            parts = data["candidates"][0]["content"].get("parts", [])
            for p in parts:
                if "text" in p:
                    text += p["text"]
                elif "functionCall" in p:
                    call = p["functionCall"]
                    tool_calls.append({
                        "type": "function",
                        "function": {
                            "name": call.get("name"),
                            "arguments": call.get("args", {})
                        }
                    })
        except (KeyError, IndexError, TypeError):
            pass
            
        return LLMResponse(text=text.strip(),
                           metadata={"provider": self.provider_name,
                                     "model": data.get("modelVersion", self.model),
                                     "tool_calls": tool_calls})

    async def stream(self, prompt: str, **kwargs):
        raise NotImplementedError("Stream not implemented for Gemini")
