from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, requests blocked
    HALF_OPEN = "half_open" # Testing recovery

class ProviderCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, cooldown_seconds: float = 60.0):
        self.state = CircuitState.CLOSED
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        
        self.failures = 0
        self.last_failure_time = 0.0

    def record_success(self):
        if self.state == CircuitState.HALF_OPEN or self.state == CircuitState.OPEN:
            # Recovered
            self.state = CircuitState.CLOSED
            self.failures = 0

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failed while testing recovery -> go back to OPEN immediately
            self.state = CircuitState.OPEN
        elif self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            # Check if cooldown has elapsed
            if time.time() - self.last_failure_time >= self.cooldown_seconds:
                # Transition to half-open to allow a test request
                self.state = CircuitState.HALF_OPEN
                return True
            return False
            
        if self.state == CircuitState.HALF_OPEN:
            # Already let one request through to test, prevent others until success/fail is recorded
            # For simplicity, we allow one execution to probe the state
            return True
            
        return False
