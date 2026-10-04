from core.providers.base import LLMProvider
from core.llm.models import LLMResponse, LLMError

class FakeLLMProvider(LLMProvider):
    def __init__(self, response_text: str = "Fake response", should_fail: bool = False):
        self.response_text = response_text
        self.should_fail = should_fail
        
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        if self.should_fail:
            raise LLMError(message="Fake error", provider="fake")
        return LLMResponse(text=self.response_text, metadata={"prompt_length": len(prompt)})

    async def stream(self, prompt: str, **kwargs):
        raise NotImplementedError("Stream not implemented for FakeLLMProvider yet.")
