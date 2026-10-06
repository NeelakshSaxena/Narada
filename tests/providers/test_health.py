import pytest
import time
from core.providers.health import ProviderHealthTracker

def test_provider_health_success_failure():
    tracker = ProviderHealthTracker()
    
    assert tracker.is_available("github") == True
    
    tracker.record_success("github")
    svc = tracker.get_service("github")
    assert svc.last_success > 0
    assert svc.failure_count == 0
    
    tracker.record_failure("github")
    assert svc.failure_count == 1
    assert svc.last_failure > 0
    assert tracker.is_available("github") == True

def test_provider_backoff():
    tracker = ProviderHealthTracker()
    
    # Backoff for 10 seconds
    tracker.record_failure("aws", backoff_seconds=10.0)
    assert tracker.is_available("aws") == False
    
    # Simulate time passing (mocking backoff_until)
    svc = tracker.get_service("aws")
    svc.backoff_until = time.time() - 1.0 # Backoff expired
    
    assert tracker.is_available("aws") == True
    
    tracker.record_success("aws")
    assert svc.failure_count == 0
    assert svc.backoff_until == 0.0
