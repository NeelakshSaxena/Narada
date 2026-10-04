import pytest
from core.skills.base import Skill, SkillRegistry
from core.agent.executor import Executor
from core.tools.registry import ToolRegistry

def test_skill_serialization_and_loading():
    json_payload = '''
    {
      "name": "project_audit",
      "purpose": "Audit a project for best practices",
      "inputs": {"path": "Target directory"},
      "outputs": {"report": "Audit report"},
      "required_tools": ["filesystem.read"],
      "constraints": ["Do not modify files"],
      "verification_steps": ["Read README", "Check tests"],
      "failure_behavior": "Stop if directory missing"
    }
    '''
    skill = Skill.from_json(json_payload)
    assert skill.name == "project_audit"
    assert "filesystem.read" in skill.required_tools
    
    # Serialize back
    output = skill.to_json()
    assert "project_audit" in output
    
def test_executor_skill_integration():
    registry = SkillRegistry()
    skill = Skill(
        name="email_triage",
        purpose="Triage unread emails",
        inputs={},
        outputs={"summary": "Triage summary"},
        required_tools=["message.send"],
        constraints=["Only reply to high priority"],
        verification_steps=["Check inbox"],
        failure_behavior="Abort on auth failure"
    )
    registry.register(skill)
    
    executor = Executor(tool_registry=ToolRegistry(), skill_registry=registry)
    
    # Verify the executor can load the skill procedural prompt
    prompt = executor.load_skill("email_triage")
    assert "SKILL: email_triage" in prompt
    assert "Only reply to high priority" in prompt
    assert "message.send" in prompt
