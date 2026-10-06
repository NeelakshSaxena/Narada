from typing import List, Dict, Any
from core.events.models import Event
import hashlib
import json

class EventBatcher:
    @staticmethod
    def _compute_hash(event: Event) -> str:
        # Create a stable hash of the event's type, source, and payload for deduplication.
        # Ignores id and timestamp to deduplicate identical payloads from the same source.
        data = {
            "type": event.type,
            "source": event.source,
            "payload": event.payload
        }
        # stable string representation
        dumped = json.dumps(data, sort_keys=True)
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()

    @staticmethod
    def deduplicate(events: List[Event]) -> List[Event]:
        seen = set()
        deduped = []
        for e in events:
            h = EventBatcher._compute_hash(e)
            if h not in seen:
                seen.add(h)
                deduped.append(e)
        return deduped

    @staticmethod
    def batch_by_source(events: List[Event]) -> Dict[str, List[Event]]:
        batches = {}
        for e in events:
            if e.source not in batches:
                batches[e.source] = []
            batches[e.source].append(e)
        return batches

    @staticmethod
    def create_batch_event(source: str, events: List[Event]) -> Event:
        """
        Roll up a list of events into a single "batch" event for unified LLM analysis.
        """
        payload = {
            "count": len(events),
            "events": [
                {
                    "type": e.type,
                    "payload": e.payload,
                    "id": e.id
                } for e in events
            ]
        }
        return Event(
            type="batch",
            source=source,
            payload=payload
        )
