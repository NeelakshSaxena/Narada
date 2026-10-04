from core.events.dedup import EventDeduplicator
from core.events.models import Event

def test_event_deduplication():
    dedup = EventDeduplicator()
    event1 = Event(type="github.push", payload={"commits": 1}, source="github")
    event2 = Event(type="github.push", payload={"commits": 1}, source="github")
    event3 = Event(type="github.push", payload={"commits": 2}, source="github")
    
    assert dedup.is_duplicate(event1) is False
    assert dedup.is_duplicate(event2) is True
    assert dedup.is_duplicate(event3) is False
    
    # Test with external ID
    event4 = Event(type="webhook", payload={}, source="stripe")
    assert dedup.is_duplicate(event4, external_event_id="evt_123") is False
    assert dedup.is_duplicate(event4, external_event_id="evt_123") is True
