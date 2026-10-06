from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class DailyState:
    meaningful_events: List[Dict[str, Any]]
    completed_work: List[Dict[str, Any]]
    failures: List[Dict[str, Any]]
    pending_approvals: List[Dict[str, Any]]
    important_changes: List[Dict[str, Any]]
    blocked_responsibilities: List[Dict[str, Any]]

class DigestGenerator:
    def __init__(self, agent_core):
        self.agent_core = agent_core

    def _build_prompt(self, state: DailyState) -> str:
        prompt = """Generate the user's daily Nārada briefing.

Include only:
1. meaningful events,
2. completed work,
3. failures requiring attention,
4. pending approvals,
5. important changes,
6. blocked responsibilities.

For each item:
- state what happened,
- state why it matters,
- state what Nārada did,
- state what the user must do, if anything.

Do not include routine successful checks.
Do not fabricate activity.
Do not expose internal secrets.

State Data:
"""
        prompt += f"Meaningful Events: {state.meaningful_events}\n"
        prompt += f"Completed Work: {state.completed_work}\n"
        prompt += f"Failures: {state.failures}\n"
        prompt += f"Pending Approvals: {state.pending_approvals}\n"
        prompt += f"Important Changes: {state.important_changes}\n"
        prompt += f"Blocked Responsibilities: {state.blocked_responsibilities}\n"
        
        return prompt

    async def generate_digest(self, state: DailyState) -> str:
        prompt = self._build_prompt(state)
        # We delegate the generation to the LLM agent core
        digest = await self.agent_core.generate(prompt)
        return digest
