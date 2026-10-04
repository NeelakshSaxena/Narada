from abc import ABC, abstractmethod
from typing import Any, Callable

class EventBus(ABC):
    @abstractmethod
    async def publish(self, topic: str, event: Any):
        pass

    @abstractmethod
    async def subscribe(self, topic: str, handler: Callable):
        pass
