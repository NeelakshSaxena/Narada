import uuid
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable, Awaitable

class DelegationInput:
    def __init__(self, objective: str, constraints: List[str], allowed_tools: List[str], workspace: str):
        self.task_id = str(uuid.uuid4())
        self.objective = objective
        self.constraints = constraints
        self.allowed_tools = allowed_tools
        self.workspace = workspace

class DelegationOutput:
    def __init__(self, status: str, summary: str, artifacts: List[str], evidence: str):
        self.status = status
        self.summary = summary
        self.artifacts = artifacts
        self.evidence = evidence

class Specialist(ABC):
    def __init__(self, name: str, llm_callback: Callable[[str], Awaitable[str]]):
        self.name = name
        self.llm_callback = llm_callback
    
    def generate_delegation_prompt(self, inputs: DelegationInput) -> str:
        return f"""
        You are a specialist agent working under Nārada.

        You are not the owner of the overall responsibility.

        Your task is:
        {inputs.objective}

        Constraints:
        {inputs.constraints}

        Allowed tools:
        {inputs.allowed_tools}

        Workspace:
        {inputs.workspace}

        Required output:
        Return a JSON object strictly following this schema:
        {{
            "status": "success|failure",
            "summary": "Brief summary of work done",
            "artifacts": ["list", "of", "files"],
            "evidence": "Evidence or reasoning for completion"
        }}

        Rules:
        - Stay within the assigned task.
        - Do not create unrelated work.
        - Do not change permissions.
        - Do not contact the user directly unless explicitly instructed.
        - Report uncertainty.
        - Report failures honestly.
        - Return evidence for important claims.
        - Stop when the task is complete.
        """
    
    async def delegate(self, inputs: DelegationInput) -> DelegationOutput:
        prompt = self.generate_delegation_prompt(inputs)
        raw_response = await self.llm_callback(prompt)
        
        try:
            # Parse the JSON response
            start_idx = raw_response.find('{')
            end_idx = raw_response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                data = json.loads(raw_response[start_idx:end_idx])
            else:
                data = json.loads(raw_response)
                
            return DelegationOutput(
                status=data.get("status", "failure"),
                summary=data.get("summary", ""),
                artifacts=data.get("artifacts", []),
                evidence=data.get("evidence", "")
            )
        except json.JSONDecodeError:
            return DelegationOutput(
                status="failure",
                summary="Failed to parse specialist output.",
                artifacts=[],
                evidence=""
            )

# Example implementation of a generic specialist
class GenericSpecialist(Specialist):
    pass
