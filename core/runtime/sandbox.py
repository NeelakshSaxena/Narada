from abc import ABC, abstractmethod
from typing import Any, Dict
import uuid

class SandboxProvider(ABC):
    @abstractmethod
    async def execute_code(self, code: str, language: str) -> Any:
        pass

    @abstractmethod
    async def run_command(self, command: str) -> Any:
        pass

class SandboxSession:
    def __init__(self, provider: SandboxProvider):
        self.session_id = str(uuid.uuid4())
        self.provider = provider
        self.is_active = True

    async def execute(self, command: str) -> Any:
        if not self.is_active:
            raise RuntimeError("Cannot execute command in closed sandbox session.")
        return await self.provider.run_command(command)

    def close(self):
        self.is_active = False

class SandboxManager:
    def __init__(self):
        self._providers: Dict[str, SandboxProvider] = {}
        self._active_sessions: Dict[str, SandboxSession] = {}

    def register_provider(self, name: str, provider: SandboxProvider):
        self._providers[name] = provider

    def create_session(self, provider_name: str) -> SandboxSession:
        if provider_name not in self._providers:
            raise ValueError(f"Unknown sandbox provider '{provider_name}'")
        session = SandboxSession(self._providers[provider_name])
        self._active_sessions[session.session_id] = session
        return session

    def close_session(self, session_id: str):
        if session_id in self._active_sessions:
            self._active_sessions[session_id].close()
            del self._active_sessions[session_id]
