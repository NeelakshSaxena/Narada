import pytest
import hmac
import hashlib
from core.gateway.hybrid_security import HybridSecurityGateway, SecurityException

def generate_sig(secret: str, payload: str) -> str:
    return hmac.new(secret.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()

def test_hybrid_security_valid_request():
    secret = "super-secret-key"
    gateway = HybridSecurityGateway(secret, allowed_operations=["trigger_agent", "status_check"])
    
    payload = '{"task": "summarize"}'
    sig = generate_sig(secret, payload)
    
    # Should pass without exception
    assert gateway.authorize_request("trigger_agent", payload, sig) is True

def test_hybrid_security_invalid_signature():
    secret = "super-secret-key"
    gateway = HybridSecurityGateway(secret, allowed_operations=["trigger_agent"])
    
    payload = '{"task": "summarize"}'
    
    with pytest.raises(SecurityException, match="Invalid authentication signature."):
        gateway.authorize_request("trigger_agent", payload, "bad-signature")

def test_hybrid_security_operation_not_allowed():
    secret = "super-secret-key"
    gateway = HybridSecurityGateway(secret, allowed_operations=["status_check"])
    
    payload = '{"cmd": "rm -rf /"}'
    sig = generate_sig(secret, payload)
    
    # Signature is valid, but operation is not allowed
    with pytest.raises(SecurityException, match="Operation 'execute_shell' is not permitted in hybrid mode."):
        gateway.authorize_request("execute_shell", payload, sig)
