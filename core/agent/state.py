from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class AgentStatus(str, Enum):
    RUNNING = "RUNNING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    OBSERVING = "OBSERVING"
    DECIDING = "DECIDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class AgentState:
    run_id: str
    goal: str
    plan: List[str] = field(default_factory=list)
    current_step: int = 0
    actions: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[Any] = field(default_factory=list)
    decision: Optional[str] = None
    status: AgentStatus = AgentStatus.RUNNING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
