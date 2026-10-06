import pytest
import time
from core.providers.circuit_breaker import ProviderCircuitBreaker, CircuitState

def test_circuit_breaker_transitions():
    cb = ProviderCircuitBreaker(failure_threshold=3, cooldown_seconds=10.0)
    
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() == True
    
    # 3 failures trip the breaker
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() == False
    
    # Mock time passing (cooldown elapsed)
    cb.last_failure_time = time.time() - 11.0
    
    # First execution after cooldown switches to HALF_OPEN
    assert cb.can_execute() == True
    assert cb.state == CircuitState.HALF_OPEN
    
    # Success resets to CLOSED
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failures == 0

def test_circuit_breaker_half_open_failure():
    cb = ProviderCircuitBreaker(failure_threshold=2, cooldown_seconds=10.0)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    
    cb.last_failure_time = time.time() - 11.0
    assert cb.can_execute() == True
    assert cb.state == CircuitState.HALF_OPEN
    
    # Failing while half-open immediately returns to OPEN
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
