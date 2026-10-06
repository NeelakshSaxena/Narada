from enum import Enum
from typing import Any, Dict, Protocol

class AutonomyState(Enum):
    CREATED = "created"
    VALIDATED = "validated"
    SLEEPING = "sleeping"
    AWAKE = "awake"
    REASONING = "reasoning"
    ACTING = "acting"
    REMEMBERING = "remembering"
    NOTIFYING = "notifying"

class Decision:
    def __init__(self, requires_action: bool, action_plan: Any, requires_notification: bool, notification_message: str):
        self.requires_action = requires_action
        self.action_plan = action_plan
        self.requires_notification = requires_notification
        self.notification_message = notification_message

class AutonomyEngine:
    def __init__(
        self, 
        responsibility_store: Any, 
        validator: Any, 
        agent_core: Any, 
        memory: Any, 
        notifier: Any
    ):
        self.responsibility_store = responsibility_store
        self.validator = validator
        self.agent_core = agent_core
        self.memory = memory
        self.notifier = notifier
        self.state = AutonomyState.CREATED

    async def setup_overnight_watch(self, responsibility_id: str):
        self.state = AutonomyState.CREATED
        
        resp = await self.responsibility_store.get(responsibility_id)
        if not resp:
            raise ValueError("Responsibility not found")
            
        is_valid = await self.validator.validate(resp)
        if not is_valid:
            raise ValueError("Responsibility validation failed (schedule, tools, permissions, or channel invalid)")
        
        self.state = AutonomyState.VALIDATED
        self._sleep()

    def _sleep(self):
        self.state = AutonomyState.SLEEPING

    async def wake_on_event(self, event: Dict[str, Any], responsibility_id: str):
        if self.state != AutonomyState.SLEEPING:
            raise RuntimeError("Engine must be in SLEEPING state to wake on event")
            
        self.state = AutonomyState.AWAKE
        resp = await self.responsibility_store.get(responsibility_id)
        
        # 1. Reason
        self.state = AutonomyState.REASONING
        decision = await self.agent_core.reason(resp, event)
        
        # 2. Act
        action_result = None
        if decision.requires_action:
            self.state = AutonomyState.ACTING
            action_result = await self.agent_core.act(decision.action_plan)
            
        # 3. Remember
        self.state = AutonomyState.REMEMBERING
        await self.memory.store(responsibility_id, event, decision, action_result)
        
        # 4. Notify if necessary
        if decision.requires_notification:
            self.state = AutonomyState.NOTIFYING
            # Assume resp has a delivery_target attribute
            target = getattr(resp, 'delivery_target', 'default_target')
            await self.notifier.notify(target, decision.notification_message)
            
        # 5. Sleep
        self._sleep()
