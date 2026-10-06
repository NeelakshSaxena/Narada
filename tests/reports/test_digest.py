import pytest
import asyncio
from core.reports.digest import DailyState, DigestGenerator

class MockAgentCore:
    async def generate(self, prompt: str) -> str:
        # Simple mock to verify prompt construction
        if "Pending Approvals: [{'id': 'app_123'}]" in prompt:
            return "Digest Generated Correctly"
        return "Failed to parse state"

def test_daily_digest_prompt_construction():
    state = DailyState(
        meaningful_events=[],
        completed_work=[],
        failures=[],
        pending_approvals=[{"id": "app_123"}],
        important_changes=[],
        blocked_responsibilities=[]
    )
    
    agent = MockAgentCore()
    generator = DigestGenerator(agent)
    
    # Check that the private method builds the prompt with the exact strings mandated
    prompt = generator._build_prompt(state)
    assert "Generate the user's daily Nārada briefing." in prompt
    assert "Do not fabricate activity." in prompt
    assert "Pending Approvals: [{'id': 'app_123'}]" in prompt

def test_daily_digest_generation():
    state = DailyState(
        meaningful_events=[],
        completed_work=[],
        failures=[],
        pending_approvals=[{"id": "app_123"}],
        important_changes=[],
        blocked_responsibilities=[]
    )
    
    agent = MockAgentCore()
    generator = DigestGenerator(agent)
    
    digest = asyncio.run(generator.generate_digest(state))
    assert digest == "Digest Generated Correctly"
