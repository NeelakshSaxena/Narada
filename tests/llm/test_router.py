import pytest
from core.llm.router import ModelRouter, Provider, ProviderType, TaskContext, RoutingPolicy

def test_model_router_privacy_constraint():
    router = ModelRouter()
    
    # Register local and remote providers
    router.register_provider(Provider("ollama", ProviderType.LOCAL, ["general"], 0.0, 50))
    router.register_provider(Provider("sarvam", ProviderType.REMOTE, ["general", "complex"], 0.1, 500))
    
    # Private task, strict policy
    task = TaskContext(task_type="general", is_private=True, requires_complex_reasoning=True)
    policy = RoutingPolicy(allow_remote_for_private=False)
    
    decision = router.route(task, policy)
    
    # Must choose local despite needing complex reasoning, because privacy strictly forbids remote
    assert decision.provider_name == "ollama"
    assert "privacy constraints" in decision.reason

def test_model_router_complex_reasoning_prefer_remote():
    router = ModelRouter()
    
    router.register_provider(Provider("ollama", ProviderType.LOCAL, ["general"], 0.0, 50))
    router.register_provider(Provider("sarvam", ProviderType.REMOTE, ["general", "complex"], 0.1, 500))
    
    # Not private, needs complex reasoning
    task = TaskContext(task_type="general", is_private=False, requires_complex_reasoning=True)
    policy = RoutingPolicy()
    
    decision = router.route(task, policy)
    
    # Should choose remote for complex reasoning
    assert decision.provider_name == "sarvam"

def test_model_router_no_provider_found():
    router = ModelRouter()
    router.register_provider(Provider("sarvam", ProviderType.REMOTE, ["general"], 0.1, 500))
    
    task = TaskContext(task_type="general", is_private=True, requires_complex_reasoning=False)
    policy = RoutingPolicy(allow_remote_for_private=False)
    
    with pytest.raises(RuntimeError, match="No suitable provider found"):
        router.route(task, policy)
