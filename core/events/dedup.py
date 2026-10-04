import hashlib
from typing import Set
from core.events.models import Event

class EventDeduplicator:
    def __init__(self):
        self.seen_signatures: Set[str] = set()

    def generate_signature(self, event: Event, external_event_id: str = None) -> str:
        if external_event_id:
            return f"{event.source}:{event.type}:{external_event_id}"
        
        # Hash payload if no external ID is available
        payload_str = str(sorted(event.payload.items()))
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        return f"{event.source}:{event.type}:{payload_hash}"

    def is_duplicate(self, event: Event, external_event_id: str = None) -> bool:
        sig = self.generate_signature(event, external_event_id)
        if sig in self.seen_signatures:
            return True
        self.seen_signatures.add(sig)
        return False
