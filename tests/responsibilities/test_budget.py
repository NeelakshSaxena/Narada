import pytest
import time
from core.responsibilities.budget import BudgetTracker, BudgetConfig, BudgetExceededError

def test_budget_limits_not_exceeded():
    config = BudgetConfig(max_model_calls=2)
    tracker = BudgetTracker(config)
    tracker.record_model_call(0.1)
    tracker.record_model_call(0.1)
    # Should not raise
    tracker.check_limits()

def test_budget_model_limit():
    config = BudgetConfig(max_model_calls=1)
    tracker = BudgetTracker(config)
    tracker.record_model_call(0.1)
    with pytest.raises(BudgetExceededError, match="Model calls 2 exceeded"):
        tracker.record_model_call(0.1)

def test_budget_tool_limit():
    config = BudgetConfig(max_tool_calls=1)
    tracker = BudgetTracker(config)
    tracker.record_tool_call(0.0)
    with pytest.raises(BudgetExceededError, match="Tool calls 2 exceeded"):
        tracker.record_tool_call(0.0)

def test_budget_cost_limit():
    config = BudgetConfig(max_estimated_cost=0.50)
    tracker = BudgetTracker(config)
    tracker.record_model_call(0.30)
    with pytest.raises(BudgetExceededError, match="Cost"):
        tracker.record_model_call(0.30)

def test_budget_runtime_limit():
    config = BudgetConfig(max_runtime_seconds=0.1)
    tracker = BudgetTracker(config)
    time.sleep(0.2)
    with pytest.raises(BudgetExceededError, match="Runtime"):
        tracker.check_limits()
