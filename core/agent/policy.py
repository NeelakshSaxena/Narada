import os
from typing import Optional

class PolicyInjector:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = workspace_root
        self.policy_path = os.path.join(workspace_root, ".agents", "AGENTS.md")

    def get_policy(self) -> Optional[str]:
        if os.path.exists(self.policy_path):
            with open(self.policy_path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def inject(self, prompt: str) -> str:
        policy = self.get_policy()
        if policy:
            return f"{prompt}\n\n# User Policy\n{policy}"
        return prompt
