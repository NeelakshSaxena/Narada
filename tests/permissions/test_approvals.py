import pytest
from datetime import datetime, timedelta
from core.permissions.approvals import ApprovalManager, ApprovalRequest, ApprovalStatus

def test_approval_lifecycle():
    manager = ApprovalManager()
    
    req = ApprovalRequest(
        task_id="task-1",
        action_id="deploy-prod",
        scope="production",
        requester="system"
    )
    
    req_id = manager.request_approval(req)
    assert manager.get_request(req_id).status == ApprovalStatus.PENDING
    
    # Grant approval
    assert manager.grant_approval(req_id) is True
    assert manager.get_request(req_id).status == ApprovalStatus.GRANTED

def test_approval_expiration():
    manager = ApprovalManager()
    
    req = ApprovalRequest(
        task_id="task-2",
        action_id="delete-db",
        scope="production",
        requester="system",
        expires_in_seconds=-1 # instantly expires
    )
    
    req_id = manager.request_approval(req)
    
    # Should be seen as expired
    assert manager.get_request(req_id).is_expired() is True
    assert manager.get_request(req_id).status == ApprovalStatus.EXPIRED
    
    with pytest.raises(ValueError, match="Cannot grant an expired approval"):
        manager.grant_approval(req_id)

def test_approval_denial():
    manager = ApprovalManager()
    
    req = ApprovalRequest(
        task_id="task-3",
        action_id="email-all",
        scope="public",
        requester="system"
    )
    
    req_id = manager.request_approval(req)
    manager.deny_approval(req_id)
    assert manager.get_request(req_id).status == ApprovalStatus.DENIED
