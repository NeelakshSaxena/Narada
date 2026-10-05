import uuid
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Optional

class ApprovalStatus(Enum):
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"

class ApprovalRequest:
    def __init__(
        self,
        task_id: str,
        action_id: str,
        scope: str,
        requester: str,
        expires_in_seconds: int = 3600
    ):
        self.request_id = str(uuid.uuid4())
        self.task_id = task_id
        self.action_id = action_id
        self.scope = scope
        self.requester = requester
        self.status = ApprovalStatus.PENDING
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=expires_in_seconds)

    def is_expired(self) -> bool:
        if self.status == ApprovalStatus.PENDING and datetime.utcnow() > self.expires_at:
            self.status = ApprovalStatus.EXPIRED
            return True
        return self.status == ApprovalStatus.EXPIRED

class ApprovalManager:
    def __init__(self):
        self._requests: Dict[str, ApprovalRequest] = {}

    def request_approval(self, request: ApprovalRequest) -> str:
        self._requests[request.request_id] = request
        return request.request_id

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        req = self._requests.get(request_id)
        if req and req.is_expired():
            # Ensure status is updated if expired
            pass
        return req

    def grant_approval(self, request_id: str) -> bool:
        req = self.get_request(request_id)
        if not req:
            raise ValueError("Approval request not found.")
            
        if req.is_expired():
            raise ValueError("Cannot grant an expired approval.")
            
        if req.status != ApprovalStatus.PENDING:
            return False
            
        req.status = ApprovalStatus.GRANTED
        return True

    def deny_approval(self, request_id: str) -> bool:
        req = self.get_request(request_id)
        if not req:
            raise ValueError("Approval request not found.")
            
        if req.is_expired():
            raise ValueError("Cannot deny an expired approval.")
            
        if req.status != ApprovalStatus.PENDING:
            return False
            
        req.status = ApprovalStatus.DENIED
        return True
