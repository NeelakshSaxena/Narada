from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta
from enum import Enum

class ResponsibilityStatus(Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    RECOVERY = "RECOVERY"
    CANCELLED = "CANCELLED"
    STOPPED = "STOPPED"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"

@dataclass
class Responsibility:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    goal: str = ""
    status: ResponsibilityStatus = ResponsibilityStatus.DRAFT
    priority: int = 1
    schedule_interval_seconds: int = 3600 # e.g. run every hour
    trigger_rules: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    memory_namespace: str = "default"
    memory_state: Dict[str, Any] = field(default_factory=dict)
    delivery_target: str = "console"
    permissions: List[str] = field(default_factory=list)
    
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None

    def transition_to(self, new_status: ResponsibilityStatus):
        # State machine bounds
        if self.status in [ResponsibilityStatus.COMPLETED, ResponsibilityStatus.CANCELLED, ResponsibilityStatus.STOPPED, ResponsibilityStatus.ARCHIVED]:
            raise ValueError(f"Cannot transition out of {self.status.name} state.")
        if new_status == ResponsibilityStatus.RECOVERY and self.status != ResponsibilityStatus.ERROR:
            raise ValueError("Can only enter RECOVERY from ERROR state.")
        self.status = new_status

    def pause(self):
        self.transition_to(ResponsibilityStatus.PAUSED)
        
    def cancel(self):
        self.transition_to(ResponsibilityStatus.CANCELLED)

    def stop(self):
        self.transition_to(ResponsibilityStatus.STOPPED)

    def disable(self):
        self.transition_to(ResponsibilityStatus.DISABLED)

    def archive(self):
        self.transition_to(ResponsibilityStatus.ARCHIVED)

    def mark_executed(self, success: bool = True):
        now = datetime.utcnow()
        self.last_run_at = now
        self.next_run_at = now + timedelta(seconds=self.schedule_interval_seconds)
        if success:
            self.last_success = now
            if self.status in [ResponsibilityStatus.ERROR, ResponsibilityStatus.RECOVERY]:
                self.transition_to(ResponsibilityStatus.ACTIVE)
        else:
            self.last_failure = now
            self.transition_to(ResponsibilityStatus.ERROR)

    def is_due(self) -> bool:
        if self.status not in [ResponsibilityStatus.ACTIVE, ResponsibilityStatus.RECOVERY]:
            return False
        if not self.next_run_at:
            return True
        return datetime.utcnow() >= self.next_run_at
