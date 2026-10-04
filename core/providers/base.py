from abc import ABC, abstractmethod
from typing import Any
from core.llm.models import LLMResponse

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        pass

    @abstractmethod
    async def stream(self, prompt: str, **kwargs):
        pass

class STTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        pass

class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        pass

class ChannelProvider(ABC):
    @abstractmethod
    async def send_message(self, recipient_id: str, message: str):
        pass
    
    @abstractmethod
    async def receive_message(self) -> Any:
        pass
