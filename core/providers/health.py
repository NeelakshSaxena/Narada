import time
from typing import Dict
from dataclasses import dataclass, field

@dataclass
class ServiceHealth:
    provider_id: str
    last_success: float = 0.0
    last_failure: float = 0.0
    failure_count: int = 0
    backoff_until: float = 0.0
    
    def record_success(self):
        self.last_success = time.time()
        self.failure_count = 0
        self.backoff_until = 0.0
        
    def record_failure(self, backoff_seconds: float = 0.0):
        self.last_failure = time.time()
        self.failure_count += 1
        if backoff_seconds > 0:
            self.backoff_until = self.last_failure + backoff_seconds

    def is_available(self) -> bool:
        if self.backoff_until > 0 and time.time() < self.backoff_until:
            return False
        return True

class ProviderHealthTracker:
    def __init__(self):
        self._services: Dict[str, ServiceHealth] = {}
        
    def get_service(self, provider_id: str) -> ServiceHealth:
        if provider_id not in self._services:
            self._services[provider_id] = ServiceHealth(provider_id=provider_id)
        return self._services[provider_id]
        
    def record_success(self, provider_id: str):
        self.get_service(provider_id).record_success()
        
    def record_failure(self, provider_id: str, backoff_seconds: float = 0.0):
        self.get_service(provider_id).record_failure(backoff_seconds)
        
    def is_available(self, provider_id: str) -> bool:
        return self.get_service(provider_id).is_available()
