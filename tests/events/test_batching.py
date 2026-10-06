import pytest
from core.events.models import Event
from core.events.batching import EventBatcher

def test_deduplicate_events():
    e1 = Event(type="github_push", source="github", payload={"repo": "Narada", "commits": 1})
    e2 = Event(type="github_push", source="github", payload={"repo": "Narada", "commits": 1})
    e3 = Event(type="github_push", source="github", payload={"repo": "Narada", "commits": 2})
    
    events = [e1, e2, e3]
    deduped = EventBatcher.deduplicate(events)
    
    # e1 and e2 should be deduplicated, e3 is different
    assert len(deduped) == 2
    assert deduped[0] == e1
    assert deduped[1] == e3

def test_batch_by_source():
    e1 = Event(type="push", source="github", payload={"commits": 1})
    e2 = Event(type="issue", source="github", payload={"id": 123})
    e3 = Event(type="msg", source="telegram", payload={"text": "hello"})
    
    batches = EventBatcher.batch_by_source([e1, e2, e3])
    
    assert "github" in batches
    assert "telegram" in batches
    assert len(batches["github"]) == 2
    assert len(batches["telegram"]) == 1

def test_create_batch_event():
    e1 = Event(type="push", source="github", payload={"commits": 1})
    e2 = Event(type="issue", source="github", payload={"id": 123})
    
    batch_event = EventBatcher.create_batch_event("github", [e1, e2])
    
    assert batch_event.type == "batch"
    assert batch_event.source == "github"
    assert batch_event.payload["count"] == 2
    assert len(batch_event.payload["events"]) == 2
    assert batch_event.payload["events"][0]["type"] == "push"
    assert batch_event.payload["events"][1]["type"] == "issue"
