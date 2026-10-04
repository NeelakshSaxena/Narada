from abc import ABC, abstractmethod
from typing import Any

class SandboxProvider(ABC):
    @abstractmethod
    async def execute_code(self, code: str, language: str) -> Any:
        pass

    @abstractmethod
    async def run_command(self, command: str) -> Any:
        pass
