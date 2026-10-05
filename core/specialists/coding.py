import json
from typing import Callable, Awaitable, Dict, Any
from core.runtime.sandbox import SandboxManager

class CodingVerificationResult:
    def __init__(
        self,
        requested_change_satisfied: bool,
        tests_pass: bool,
        unexpected_changes: bool,
        security_concerns: bool,
        deployment_ready: bool,
        explanation: str
    ):
        self.requested_change_satisfied = requested_change_satisfied
        self.tests_pass = tests_pass
        self.unexpected_changes = unexpected_changes
        self.security_concerns = security_concerns
        self.deployment_ready = deployment_ready
        self.explanation = explanation

class CodingSpecialist:
    def __init__(self, sandbox_manager: SandboxManager, llm_callback: Callable[[str], Awaitable[str]]):
        self.sandbox_manager = sandbox_manager
        self.llm_callback = llm_callback

    async def delegate_task(self, task_description: str, sandbox_provider_name: str, test_command: str) -> CodingVerificationResult:
        # Spawn a sandbox session for the specialist
        session = self.sandbox_manager.create_session(sandbox_provider_name)
        
        try:
            # Here a real specialist like OpenHands would modify the workspace.
            # We mock the execution of the specialist's task:
            diff = await session.execute("git diff")
            
            # Run tests in the sandbox
            test_results = await session.execute(test_command)
            
            # Verify the output
            return await self.verify_output(task_description, diff, test_results)
        finally:
            self.sandbox_manager.close_session(session.session_id)

    async def verify_output(self, task_description: str, diff: str, test_results: str) -> CodingVerificationResult:
        prompt = f"""
        You are verifying a delegated coding task.
        
        Inspect:
        1. requested change: {task_description}
        2. repository diff: {diff}
        3. tests added/changed: (see diff)
        4. test results: {test_results}
        5. lint/type results: N/A
        6. unexpected modifications: (see diff)
        7. dependency changes: (see diff)
        8. security-sensitive changes: (see diff)
        
        Return a JSON object strictly following this schema:
        {{
            "requested_change_satisfied": bool,
            "tests_pass": bool,
            "unexpected_changes": bool,
            "security_concerns": bool,
            "deployment_ready": bool,
            "explanation": str
        }}
        
        Never mark deployment_ready solely because tests pass.
        """
        
        raw_response = await self.llm_callback(prompt)
        
        try:
            # Simple JSON extraction logic for parsing
            start_idx = raw_response.find('{')
            end_idx = raw_response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                data = json.loads(raw_response[start_idx:end_idx])
            else:
                data = json.loads(raw_response)
                
            # Enforce the logic that tests_pass doesn't auto-mean deployment_ready
            deployment_ready = data.get("deployment_ready", False)
            if data.get("tests_pass") and data.get("security_concerns"):
                deployment_ready = False
                
            return CodingVerificationResult(
                requested_change_satisfied=data.get("requested_change_satisfied", False),
                tests_pass=data.get("tests_pass", False),
                unexpected_changes=data.get("unexpected_changes", False),
                security_concerns=data.get("security_concerns", False),
                deployment_ready=deployment_ready,
                explanation=data.get("explanation", "")
            )
        except json.JSONDecodeError:
            # Fallback for parsing failures
            return CodingVerificationResult(
                requested_change_satisfied=False,
                tests_pass=False,
                unexpected_changes=True,
                security_concerns=True,
                deployment_ready=False,
                explanation="Failed to parse verification response."
            )
