from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class LLMResponse:
    text: str
    metadata: Dict[str, Any]

class LLMError(Exception):
    def __init__(self, message: str, provider: str, original_error: Optional[Exception] = None,
                 status: Optional[int] = None):
        super().__init__(message)
        self.provider = provider
        self.original_error = original_error
        self.status = status
