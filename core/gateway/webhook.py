import hmac
import hashlib
import time
from typing import Dict, Any, Optional

class WebhookError(Exception):
    pass

class WebhookSecurity:
    def __init__(self, secret: str, max_age_seconds: int = 300):
        self.secret = secret.encode('utf-8')
        self.max_age_seconds = max_age_seconds
        self._seen_events: set[str] = set()

    def verify_signature(self, payload: str, signature: str) -> bool:
        expected = hmac.new(self.secret, payload.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def verify_timestamp(self, timestamp: float) -> bool:
        current_time = time.time()
        return abs(current_time - timestamp) <= self.max_age_seconds

    def check_replay(self, event_id: str) -> bool:
        if event_id in self._seen_events:
            return False
        self._seen_events.add(event_id)
        return True

class WebhookGateway:
    def __init__(self, security: WebhookSecurity, dispatcher):
        self.security = security
        self.dispatcher = dispatcher

    def receive(self, provider: str, event_id: str, timestamp: float, payload: str, signature: str) -> Dict[str, Any]:
        if not self.security.verify_signature(payload, signature):
            raise WebhookError("Invalid signature")
            
        if not self.security.verify_timestamp(timestamp):
            raise WebhookError("Event too old or timestamp invalid")
            
        if not self.security.check_replay(event_id):
            raise WebhookError("Event replay detected")
            
        normalized_event = self._normalize(provider, event_id, payload)
        self.dispatcher.dispatch(normalized_event)
        
        return {"status": "accepted", "event_id": event_id}

    def _normalize(self, provider: str, event_id: str, payload: str) -> Dict[str, Any]:
        return {
            "source": provider,
            "id": event_id,
            "payload": payload,
            "type": "webhook"
        }
