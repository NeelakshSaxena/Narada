from abc import ABC, abstractmethod
from typing import Dict, Any, List

class NotificationProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def send(self, message: str, context: Dict[str, Any] = None) -> bool:
        pass

class DeliveryGateway:
    def __init__(self):
        self._providers: Dict[str, NotificationProvider] = {}

    def register_provider(self, provider: NotificationProvider):
        self._providers[provider.name] = provider

    def get_provider(self, name: str) -> NotificationProvider:
        if name not in self._providers:
            raise ValueError(f"No notification provider registered under '{name}'")
        return self._providers[name]

    async def deliver(self, target: str, message: str, context: Dict[str, Any] = None) -> bool:
        provider = self.get_provider(target)
        return await provider.send(message, context or {})
