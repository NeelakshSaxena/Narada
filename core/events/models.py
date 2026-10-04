from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

@dataclass
class Event:
    type: str
    payload: Dict[str, Any]
    source: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
