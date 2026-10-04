from enum import Enum
from typing import Callable, Awaitable
from core.events.models import Event

class NotificationPolicy(Enum):
    SILENT = "silent"
    INFORMATIONAL = "informational"
    IMPORTANT = "important"
    URGENT = "urgent"
    APPROVAL_REQUIRED = "approval_required"

class PolicyEvaluator:
    def __init__(self, llm_callback: Callable[[str], Awaitable[str]]):
        self.llm_callback = llm_callback

    async def evaluate_policy(self, event: Event, action_result: str) -> NotificationPolicy:
        prompt = f"""
        Determine the notification policy for this execution result.
        EVENT: {event.type}
        RESULT: {action_result}
        
        Policies:
        - silent: Routine check, no meaningful change.
        - informational: Minor change, good for a digest.
        - important: Meaningful change, notify user.
        - urgent: Immediate attention needed.
        - approval_required: Dangerous action requested.
        
        Reply ONLY with the policy name.
        """
        response = await self.llm_callback(prompt)
        response = response.strip().lower()
        try:
            return NotificationPolicy(response)
        except ValueError:
            return NotificationPolicy.INFORMATIONAL # Default fallback
