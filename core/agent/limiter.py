class CircuitBreakerTripped(Exception):
    """Raised when an agent execution hits a configured resource boundary."""
    pass

class ResourceLimiter:
    def __init__(self, max_steps: int = 15):
        self.max_steps = max_steps
        self.current_step = 0

    def increment(self):
        self.current_step += 1
        if self.current_step > self.max_steps:
            raise CircuitBreakerTripped(f"Execution exceeded max steps: {self.max_steps}")
