import asyncio
from enum import Enum
from typing import Callable, Awaitable, Any, Optional

class FailureType(Enum):
    NETWORK_TIMEOUT = "network_timeout"
    RATE_LIMIT = "rate_limit"
    AUTH_FAILURE = "auth_failure"
    PERMISSION_DENIED = "permission_denied"
    UNKNOWN = "unknown"

class RecoveryAction(Enum):
    RETRY = "retry"
    BACKOFF = "backoff"
    STOP_NOTIFY = "stop_notify"
    STOP_ENTIRELY = "stop_entirely"

class FailureContext:
    def __init__(self, failure_type: FailureType, is_idempotent: bool, state_reconciled: bool = False):
        self.failure_type = failure_type
        self.is_idempotent = is_idempotent
        self.state_reconciled = state_reconciled

class RecoveryManager:
    def __init__(self):
        self.max_retries = 3
        self.base_backoff_sec = 1
        
    def determine_action(self, context: FailureContext) -> RecoveryAction:
        if context.failure_type == FailureType.PERMISSION_DENIED:
            return RecoveryAction.STOP_ENTIRELY
        elif context.failure_type == FailureType.AUTH_FAILURE:
            return RecoveryAction.STOP_NOTIFY
        elif context.failure_type == FailureType.RATE_LIMIT:
            return RecoveryAction.BACKOFF
        elif context.failure_type == FailureType.NETWORK_TIMEOUT:
            if not context.is_idempotent and not context.state_reconciled:
                # Never retry consequential side-effects without reconciling state
                return RecoveryAction.STOP_NOTIFY
            return RecoveryAction.RETRY
            
        return RecoveryAction.STOP_NOTIFY

    async def execute_with_recovery(self, action: Callable[[], Awaitable[Any]], context: FailureContext) -> Any:
        attempts = 0
        while attempts < self.max_retries:
            try:
                return await action()
            except Exception as e:
                # Mock translating an exception to the context's failure type
                # (In reality, we'd parse the exception to figure out the type).
                recovery_action = self.determine_action(context)
                
                if recovery_action == RecoveryAction.STOP_ENTIRELY:
                    raise PermissionError(f"Action blocked entirely due to {context.failure_type}")
                elif recovery_action == RecoveryAction.STOP_NOTIFY:
                    raise RuntimeError(f"Action stopped, notifying user due to {context.failure_type}")
                elif recovery_action == RecoveryAction.BACKOFF:
                    attempts += 1
                    await asyncio.sleep(self.base_backoff_sec * attempts)
                    continue
                elif recovery_action == RecoveryAction.RETRY:
                    attempts += 1
                    continue
        
        raise TimeoutError("Max retries exceeded.")
