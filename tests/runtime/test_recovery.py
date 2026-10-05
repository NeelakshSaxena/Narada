import pytest
import asyncio
from core.runtime.recovery import RecoveryManager, FailureContext, FailureType

def test_recovery_matrix():
    manager = RecoveryManager()
    
    # Network timeout + idempotent -> RETRY
    assert manager.determine_action(FailureContext(FailureType.NETWORK_TIMEOUT, is_idempotent=True)).value == "retry"
    
    # Network timeout + NOT idempotent + NOT reconciled -> STOP_NOTIFY
    assert manager.determine_action(FailureContext(FailureType.NETWORK_TIMEOUT, is_idempotent=False)).value == "stop_notify"
    
    # Network timeout + NOT idempotent + reconciled -> RETRY
    assert manager.determine_action(FailureContext(FailureType.NETWORK_TIMEOUT, is_idempotent=False, state_reconciled=True)).value == "retry"
    
    # Rate limit -> BACKOFF
    assert manager.determine_action(FailureContext(FailureType.RATE_LIMIT, is_idempotent=True)).value == "backoff"
    
    # Auth failure -> STOP_NOTIFY
    assert manager.determine_action(FailureContext(FailureType.AUTH_FAILURE, is_idempotent=True)).value == "stop_notify"
    
    # Permission denied -> STOP_ENTIRELY
    assert manager.determine_action(FailureContext(FailureType.PERMISSION_DENIED, is_idempotent=True)).value == "stop_entirely"

def test_execute_with_recovery():
    manager = RecoveryManager()
    manager.base_backoff_sec = 0.01  # speed up test
    
    calls = 0
    async def mock_action():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise Exception("Mock failure")
        return "success"
        
    # Test retry logic
    context = FailureContext(FailureType.NETWORK_TIMEOUT, is_idempotent=True)
    result = asyncio.run(manager.execute_with_recovery(mock_action, context))
    assert result == "success"
    assert calls == 3
    
    # Test stop logic
    calls = 0
    context = FailureContext(FailureType.PERMISSION_DENIED, is_idempotent=True)
    with pytest.raises(PermissionError):
        asyncio.run(manager.execute_with_recovery(mock_action, context))
    assert calls == 1
