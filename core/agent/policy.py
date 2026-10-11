import os
from typing import Optional

class PolicyInjector:
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = os.path.abspath(workspace_root or os.environ.get("NARADA_WORKSPACE") or ".")
        self.policy_path = os.path.join(self.workspace_root, ".agents", "AGENTS.md")

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
