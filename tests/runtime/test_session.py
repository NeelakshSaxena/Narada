import pytest
from core.runtime.session import RunContextBuilder, ContextPriority, Conversation, Session, Run

def test_session_entities():
    conv = Conversation()
    assert conv.id is not None
    assert conv.history == []
    
    sess = Session()
    assert sess.id is not None
    
    run = Run()
    assert run.id is not None

def test_run_context_builder_budget_policy():
    builder = RunContextBuilder()
    
    # Add items out of order
    builder.add_item(ContextPriority.HISTORICAL_CONTEXT, "old chat")
    builder.add_item(ContextPriority.SAFETY_AND_PERMISSIONS, "do not delete db")
    builder.add_item(ContextPriority.CURRENT_TASK, "check logs")
    builder.add_item(ContextPriority.RELEVANT_RESPONSIBILITY, "maintain uptime")
    
    # We want a very small budget to see what gets dropped
    # Let's say budget is 2 items
    run = builder.build_fresh_run(max_items=2)
    
    # Expect only the highest priority items (lowest enum value)
    assert len(run.context_items) == 2
    assert run.context_items[0]["priority"] == ContextPriority.SAFETY_AND_PERMISSIONS
    assert run.context_items[1]["priority"] == ContextPriority.CURRENT_TASK
    
    # The historical context and relevant responsibility should be dropped
    priorities_included = [item["priority"] for item in run.context_items]
    assert ContextPriority.HISTORICAL_CONTEXT not in priorities_included
    assert ContextPriority.RELEVANT_RESPONSIBILITY not in priorities_included
