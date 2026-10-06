from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Dict

class Capability(Enum):
    TEXT_IN = "text_in"
    TEXT_OUT = "text_out"
    FILES = "files"
    VOICE = "voice"
    INTERACTIVE_APPROVAL = "interactive_approval"
    STREAMING = "streaming"

@dataclass
class ChannelCapabilities:
    supported: set[Capability]
    
    def has(self, capability: Capability) -> bool:
        return capability in self.supported

class ChannelProvider(ABC):
    def __init__(self, name: str):
        self.name = name
        self.capabilities = self._define_capabilities()

    @abstractmethod
    def _define_capabilities(self) -> ChannelCapabilities:
        pass

    @abstractmethod
    async def send_text(self, text: str) -> Any:
        pass

    @abstractmethod
    async def request_interactive_approval(self, prompt: str) -> Any:
        pass

class ChannelManager:
    def __init__(self):
        self._providers: Dict[str, ChannelProvider] = {}

    def register_provider(self, provider: ChannelProvider):
        self._providers[provider.name] = provider

    def get_provider(self, name: str) -> ChannelProvider:
        if name not in self._providers:
            raise ValueError(f"Channel provider '{name}' not found")
        return self._providers[name]

    def can_handle(self, channel_name: str, capability: Capability) -> bool:
        provider = self.get_provider(channel_name)
        return provider.capabilities.has(capability)

# Example providers reflecting the Channel Capability Matrix from the design
class WebChannel(ChannelProvider):
    def _define_capabilities(self) -> ChannelCapabilities:
        return ChannelCapabilities(supported={
            Capability.TEXT_IN,
            Capability.TEXT_OUT,
            Capability.FILES,
            Capability.INTERACTIVE_APPROVAL,
            Capability.STREAMING
        })
        
    async def send_text(self, text: str) -> Any:
        return True

    async def request_interactive_approval(self, prompt: str) -> Any:
        return True

class SMSChannel(ChannelProvider):
    def _define_capabilities(self) -> ChannelCapabilities:
        return ChannelCapabilities(supported={
            Capability.TEXT_IN,
            Capability.TEXT_OUT
        })
        
    async def send_text(self, text: str) -> Any:
        return True

    async def request_interactive_approval(self, prompt: str) -> Any:
        raise NotImplementedError("SMS does not natively support rich interactive approval.")
