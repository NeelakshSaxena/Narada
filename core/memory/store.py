from abc import ABC, abstractmethod
from typing import Any, List, Dict

class MemoryProvider(ABC):
    @abstractmethod
    async def store(self, key: str, value: Any, namespace: str = "default"):
        pass

    @abstractmethod
    async def retrieve(self, key: str, namespace: str = "default") -> Any:
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        pass
