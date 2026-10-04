from abc import ABC, abstractmethod
from typing import Any, Dict

class ToolProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def risk(self) -> str:
        """e.g., 'low', 'medium', 'high'"""
        pass

    @property
    @abstractmethod
    def requires_confirmation(self) -> bool:
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass
