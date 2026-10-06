import os
import pytest
from core.agent.policy import PolicyInjector

def test_policy_injector(tmpdir):
    # Setup mock workspace
    workspace = tmpdir.mkdir("workspace")
    agents_dir = workspace.mkdir(".agents")
    policy_file = agents_dir.join("AGENTS.md")
    policy_file.write("Do not send emails on Sunday.")
    
    injector = PolicyInjector(workspace_root=str(workspace))
    
    prompt = "Task: send email"
    injected = injector.inject(prompt)
    
    assert "Task: send email" in injected
    assert "# User Policy" in injected
    assert "Do not send emails on Sunday." in injected

def test_policy_injector_no_policy(tmpdir):
    workspace = tmpdir.mkdir("workspace_empty")
    
    injector = PolicyInjector(workspace_root=str(workspace))
    
    prompt = "Task: run"
    injected = injector.inject(prompt)
    
    assert injected == "Task: run"
