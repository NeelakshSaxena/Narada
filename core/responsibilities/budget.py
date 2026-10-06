import time
from dataclasses import dataclass
from enum import Enum

class BudgetExceededError(Exception):
    pass

@dataclass
class BudgetConfig:
    max_runtime_seconds: float = 300.0
    max_model_calls: int = 5
    max_tool_calls: int = 15
    max_estimated_cost: float = 0.25

class BudgetTracker:
    def __init__(self, config: BudgetConfig):
        self.config = config
        self.start_time = time.time()
        
        self.model_calls = 0
        self.tool_calls = 0
        self.estimated_cost = 0.0

    def check_limits(self):
        runtime = time.time() - self.start_time
        if runtime > self.config.max_runtime_seconds:
            raise BudgetExceededError(f"Runtime {runtime:.2f}s exceeded limit of {self.config.max_runtime_seconds}s")
            
        if self.model_calls > self.config.max_model_calls:
            raise BudgetExceededError(f"Model calls {self.model_calls} exceeded limit of {self.config.max_model_calls}")
            
        if self.tool_calls > self.config.max_tool_calls:
            raise BudgetExceededError(f"Tool calls {self.tool_calls} exceeded limit of {self.config.max_tool_calls}")
            
        if self.estimated_cost > self.config.max_estimated_cost:
            raise BudgetExceededError(f"Cost ${self.estimated_cost:.4f} exceeded limit of ${self.config.max_estimated_cost}")

    def record_model_call(self, cost: float = 0.0):
        self.model_calls += 1
        self.estimated_cost += cost
        self.check_limits()
        
    def record_tool_call(self, cost: float = 0.0):
        self.tool_calls += 1
        self.estimated_cost += cost
        self.check_limits()
