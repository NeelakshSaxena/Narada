import uuid
from core.permissions.models import RiskLevel, ApprovalStatus, PermissionRequest, PermissionDecision

class PermissionEngine:
    def __init__(self):
        # In a real system, this state lives in DB
        self.pending_approvals = {}

    def get_baseline_risk(self, tool_name: str) -> RiskLevel:
        if tool_name in ["filesystem.read", "web.search", "dummy_action"]:
            return RiskLevel.LOW
        elif tool_name in ["filesystem.write"]:
            return RiskLevel.MEDIUM
        elif tool_name in ["shell.execute", "message.send"]:
            return RiskLevel.HIGH
        elif tool_name in ["data.delete", "system.deploy"]:
            return RiskLevel.CRITICAL
        return RiskLevel.HIGH # Unknown tools default to HIGH

    def evaluate(self, request: PermissionRequest) -> PermissionDecision:
        risk = self.get_baseline_risk(request.tool)
        request.risk = risk

        # Low risk -> Not required
        if risk in [RiskLevel.NONE, RiskLevel.LOW]:
            return PermissionDecision(
                request=request, 
                status=ApprovalStatus.NOT_REQUIRED,
                requires_approval=False
            )

        # Higher risk -> Requires explicit approval
        approval_id = str(uuid.uuid4())
        decision = PermissionDecision(
            request=request,
            status=ApprovalStatus.PENDING,
            requires_approval=True,
            approval_id=approval_id,
            reason=f"Action requires approval due to risk level: {risk.value}"
        )
        self.pending_approvals[approval_id] = decision
        return decision
        
    def check_approval_status(self, approval_id: str) -> ApprovalStatus:
        if approval_id not in self.pending_approvals:
            return ApprovalStatus.DENIED
        return self.pending_approvals[approval_id].status

    def grant_approval(self, approval_id: str, identity: str) -> bool:
        # LLM cannot approve its own actions.
        if identity.startswith("agent_") or identity == "llm":
            return False
            
        if approval_id in self.pending_approvals:
            self.pending_approvals[approval_id].status = ApprovalStatus.APPROVED
            return True
        return False
        
    def deny_approval(self, approval_id: str, identity: str) -> bool:
        if approval_id in self.pending_approvals:
            self.pending_approvals[approval_id].status = ApprovalStatus.DENIED
            return True
        return False
