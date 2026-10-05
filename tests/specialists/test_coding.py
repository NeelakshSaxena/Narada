import pytest
import asyncio
import json
from core.specialists.coding import CodingSpecialist, CodingVerificationResult
from core.runtime.sandbox import SandboxManager, SandboxProvider, SandboxSession

class MockSandbox(SandboxProvider):
    async def execute_code(self, code: str, language: str) -> str:
        return ""
        
    async def run_command(self, command: str) -> str:
        if command == "git diff":
            return "+ def new_feature(): return True"
        if command == "pytest":
            return "1 passed in 0.01s"
        return ""

def test_coding_specialist():
    manager = SandboxManager()
    manager.register_provider("mock", MockSandbox())
    
    async def mock_llm(prompt: str) -> str:
        # Check if the prompt has the required text
        assert "You are verifying a delegated coding task." in prompt
        
        # Return a mock JSON response
        response_data = {
            "requested_change_satisfied": True,
            "tests_pass": True,
            "unexpected_changes": False,
            "security_concerns": False,
            "deployment_ready": True,
            "explanation": "Looks good."
        }
        return json.dumps(response_data)
        
    specialist = CodingSpecialist(manager, mock_llm)
    
    result = asyncio.run(specialist.delegate_task(
        task_description="Add a new feature",
        sandbox_provider_name="mock",
        test_command="pytest"
    ))
    
    assert result.requested_change_satisfied is True
    assert result.tests_pass is True
    assert result.deployment_ready is True
    assert result.explanation == "Looks good."

def test_coding_specialist_security_concern():
    manager = SandboxManager()
    manager.register_provider("mock", MockSandbox())
    
    async def mock_llm(prompt: str) -> str:
        # Mock a case where tests pass but there is a security concern
        response_data = {
            "requested_change_satisfied": True,
            "tests_pass": True,
            "unexpected_changes": False,
            "security_concerns": True,
            "deployment_ready": True, # the model tries to say it's ready
            "explanation": "Added eval() but tests pass."
        }
        return json.dumps(response_data)
        
    specialist = CodingSpecialist(manager, mock_llm)
    
    result = asyncio.run(specialist.delegate_task(
        task_description="Add a new feature",
        sandbox_provider_name="mock",
        test_command="pytest"
    ))
    
    # We enforce that security_concerns + tests_pass means deployment_ready is forced to False
    assert result.tests_pass is True
    assert result.security_concerns is True
    assert result.deployment_ready is False
