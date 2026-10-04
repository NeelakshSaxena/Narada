from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta

@dataclass
class Responsibility:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    goal: str = ""
    schedule_interval_seconds: int = 3600 # e.g. run every hour
    tools: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    memory_state: Dict[str, Any] = field(default_factory=dict)
    delivery_target: str = "console"
    permissions: List[str] = field(default_factory=list)
    
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None

    def mark_executed(self):
        self.last_run_at = datetime.utcnow()
        self.next_run_at = self.last_run_at + timedelta(seconds=self.schedule_interval_seconds)

    def is_due(self) -> bool:
        if not self.next_run_at:
            return True
        return datetime.utcnow() >= self.next_run_at
