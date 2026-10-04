from enum import Enum
from dataclasses import dataclass
from typing import Optional

class RiskLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    NOT_REQUIRED = "NOT_REQUIRED"

@dataclass
class PermissionRequest:
    identity: str
    tool: str
    action: str
    scope: str = "global"
    resource: str = "*"
    risk: RiskLevel = RiskLevel.LOW
    
@dataclass
class PermissionDecision:
    request: PermissionRequest
    status: ApprovalStatus
    reason: Optional[str] = None
    requires_approval: bool = False
    approval_id: Optional[str] = None
