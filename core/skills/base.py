from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import json

@dataclass
class Skill:
    name: str
    purpose: str
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    required_tools: List[str]
    constraints: List[str]
    verification_steps: List[str]
    failure_behavior: str
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)
        
    @classmethod
    def from_json(cls, data: str) -> "Skill":
        parsed = json.loads(data)
        return cls(**parsed)

class SkillRegistry:
    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        
    def register(self, skill: Skill):
        self._skills[skill.name] = skill
        
    def get_skill(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)
        
    def list_skills(self) -> List[str]:
        return list(self._skills.keys())
        
    def get_prompt_for_skill(self, name: str) -> str:
        skill = self.get_skill(name)
        if not skill:
            raise ValueError(f"Skill {name} not found")
            
        return f"""
        SKILL: {skill.name}
        PURPOSE: {skill.purpose}
        
        INPUTS: {json.dumps(skill.inputs)}
        OUTPUTS: {json.dumps(skill.outputs)}
        REQUIRED TOOLS: {', '.join(skill.required_tools)}
        
        CONSTRAINTS:
        {chr(10).join(f'- {c}' for c in skill.constraints)}
        
        VERIFICATION STEPS:
        {chr(10).join(f'- {v}' for v in skill.verification_steps)}
        
        FAILURE BEHAVIOR:
        {skill.failure_behavior}
        """
