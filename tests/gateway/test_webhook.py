import pytest
import time
import hmac
import hashlib
from core.gateway.webhook import WebhookSecurity, WebhookGateway, WebhookError

class MockDispatcher:
    def __init__(self):
        self.dispatched = []
        
    def dispatch(self, event):
        self.dispatched.append(event)

def generate_signature(secret: str, payload: str) -> str:
    return hmac.new(secret.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()

def test_webhook_security_success():
    secret = "my_secret"
    security = WebhookSecurity(secret=secret)
    dispatcher = MockDispatcher()
    gateway = WebhookGateway(security, dispatcher)
    
    payload = '{"action": "push"}'
    signature = generate_signature(secret, payload)
    timestamp = time.time()
    event_id = "evt_123"
    
    res = gateway.receive("github", event_id, timestamp, payload, signature)
    assert res["status"] == "accepted"
    assert len(dispatcher.dispatched) == 1

def test_webhook_security_invalid_signature():
    security = WebhookSecurity(secret="my_secret")
    gateway = WebhookGateway(security, MockDispatcher())
    
    with pytest.raises(WebhookError, match="Invalid signature"):
        gateway.receive("github", "evt_1", time.time(), "payload", "bad_sig")

def test_webhook_security_replay():
    secret = "my_secret"
    security = WebhookSecurity(secret=secret)
    gateway = WebhookGateway(security, MockDispatcher())
    
    payload = "data"
    signature = generate_signature(secret, payload)
    
    # First time works
    gateway.receive("github", "evt_dup", time.time(), payload, signature)
    
    # Second time fails
    with pytest.raises(WebhookError, match="replay detected"):
        gateway.receive("github", "evt_dup", time.time(), payload, signature)

def test_webhook_security_timestamp():
    secret = "my_secret"
    security = WebhookSecurity(secret=secret, max_age_seconds=10)
    gateway = WebhookGateway(security, MockDispatcher())
    
    payload = "data"
    signature = generate_signature(secret, payload)
    
    old_timestamp = time.time() - 20 # older than max_age
    
    with pytest.raises(WebhookError, match="too old"):
        gateway.receive("github", "evt_old", old_timestamp, payload, signature)
