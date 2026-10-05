import pytest
import asyncio
import json
from core.specialists.base import GenericSpecialist, DelegationInput, DelegationOutput

def test_specialist_delegation_contract():
    async def mock_llm(prompt: str) -> str:
        assert "You are a specialist agent working under Nārada." in prompt
        assert "Read the documentation" in prompt
        assert "read_file" in prompt
        
        response_data = {
            "status": "success",
            "summary": "Read the documentation successfully.",
            "artifacts": ["docs.md"],
            "evidence": "File contents showed instructions."
        }
        return json.dumps(response_data)
        
    specialist = GenericSpecialist(name="researcher", llm_callback=mock_llm)
    
    inputs = DelegationInput(
        objective="Read the documentation",
        constraints=["Only read files"],
        allowed_tools=["read_file"],
        workspace="/tmp/workspace"
    )
    
    output = asyncio.run(specialist.delegate(inputs))
    
    assert output.status == "success"
    assert output.summary == "Read the documentation successfully."
    assert "docs.md" in output.artifacts
    assert "File contents showed instructions." in output.evidence

def test_specialist_parse_failure():
    async def mock_llm_fail(prompt: str) -> str:
        return "I am unable to output JSON."
        
    specialist = GenericSpecialist(name="coder", llm_callback=mock_llm_fail)
    inputs = DelegationInput(
        objective="Code something",
        constraints=[],
        allowed_tools=[],
        workspace="/tmp/workspace"
    )
    
    output = asyncio.run(specialist.delegate(inputs))
    
    assert output.status == "failure"
    assert "Failed to parse" in output.summary
