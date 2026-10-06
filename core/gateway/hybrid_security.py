import hmac
import hashlib
from typing import List

class SecurityException(Exception):
    pass

class HybridSecurityGateway:
    """
    Local Gateway Security boundary.
    Allows a cloud control plane (like AWS API or EventBridge) to communicate
    with the local Nārada runtime (Ollama/tools) without exposing the local 
    environment directly to the internet unauthenticated.
    """
    def __init__(self, shared_secret: str, allowed_operations: List[str]):
        self.shared_secret = shared_secret.encode('utf-8')
        self.allowed_operations = set(allowed_operations)
        
    def _verify_signature(self, payload: str, signature: str) -> bool:
        expected = hmac.new(self.shared_secret, payload.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
        
    def authorize_request(self, operation: str, payload_str: str, provided_signature: str) -> bool:
        # Check operation scope to prevent dangerous tasks from remote triggers
        if operation not in self.allowed_operations:
            raise SecurityException(f"Operation '{operation}' is not permitted in hybrid mode.")
            
        # Check signature authentication
        if not self._verify_signature(payload_str, provided_signature):
            raise SecurityException("Invalid authentication signature.")
            
        return True
