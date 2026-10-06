from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ProviderType(Enum):
    LOCAL = "local"
    REMOTE = "remote"

@dataclass
class Provider:
    name: str
    provider_type: ProviderType
    supported_tasks: list[str]
    cost_per_1k: float
    avg_latency_ms: int

@dataclass
class TaskContext:
    task_type: str
    is_private: bool
    requires_complex_reasoning: bool

@dataclass
class RoutingPolicy:
    allow_remote_for_private: bool = False
    max_cost_per_1k: float = 1.0
    max_latency_ms: int = 5000

@dataclass
class RoutingDecision:
    provider_name: str
    model_name: str
    reason: str
    policy_basis: str

class ModelRouter:
    def __init__(self):
        self.providers = []

    def register_provider(self, provider: Provider):
        self.providers.append(provider)

    def route(self, task: TaskContext, policy: RoutingPolicy) -> RoutingDecision:
        # Hard constraint: Never route private=true tasks to remote provider unless explicitly allowed by policy
        
        valid_providers = []
        for p in self.providers:
            # Check privacy constraint
            if task.is_private and p.provider_type == ProviderType.REMOTE and not policy.allow_remote_for_private:
                continue
                
            # Check cost constraint
            if p.cost_per_1k > policy.max_cost_per_1k:
                continue
                
            # Check latency constraint
            if p.avg_latency_ms > policy.max_latency_ms:
                continue
                
            # Check task support
            if task.task_type not in p.supported_tasks and "general" not in p.supported_tasks:
                continue
                
            valid_providers.append(p)
            
        if not valid_providers:
            raise RuntimeError("No suitable provider found for task given the current policy constraints.")
            
        # Select best provider based on reasoning needs or cost
        # Simple heuristic: if complex reasoning, prefer remote if available, otherwise lowest cost
        best_provider = None
        if task.requires_complex_reasoning:
            remotes = [p for p in valid_providers if p.provider_type == ProviderType.REMOTE]
            if remotes:
                best_provider = min(remotes, key=lambda x: x.cost_per_1k)
        
        if not best_provider:
            best_provider = min(valid_providers, key=lambda x: x.cost_per_1k)
            
        reason = "Selected based on cost and capability."
        if task.is_private and best_provider.provider_type == ProviderType.LOCAL:
            reason = "Selected local provider to satisfy privacy constraints."
            
        return RoutingDecision(
            provider_name=best_provider.name,
            model_name="default", # In a full system, models would be chosen here
            reason=reason,
            policy_basis=f"private={task.is_private}, allow_remote={policy.allow_remote_for_private}"
        )
