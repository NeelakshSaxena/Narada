from typing import Any
import pytest
import asyncio
from core.runtime.sandbox import SandboxManager, SandboxProvider, SandboxSession

class MockSandbox(SandboxProvider):
    async def execute_code(self, code: str, language: str) -> Any:
        return f"Executed {language}"
        
    async def run_command(self, command: str) -> Any:
        return f"Ran: {command}"

def test_sandbox_manager():
    manager = SandboxManager()
    manager.register_provider("mock", MockSandbox())
    
    session = manager.create_session("mock")
    assert session.is_active is True
    
    result = asyncio.run(session.execute("ls -la"))
    assert result == "Ran: ls -la"
    
    manager.close_session(session.session_id)
    assert session.is_active is False
    
    with pytest.raises(RuntimeError):
        asyncio.run(session.execute("ls"))
