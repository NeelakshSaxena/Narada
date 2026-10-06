# Phase 21: Model Routing Logbook

## Objective
Implement dynamic model routing to allow Nārada to safely select between local and remote providers based on task parameters and strict privacy constraints.

## Branch
`phase/21-model-routing`

## Changes Made
- Created `core/llm/router.py` to house the `ModelRouter`, `RoutingPolicy`, and `RoutingDecision` models.
- Implemented a policy-based decision matrix evaluating `privacy`, `cost`, `latency`, and `task type`.
- Enforced a hard constraint that any task flagged with `is_private=True` must not be routed to a remote provider unless explicitly overridden by `allow_remote_for_private=True` in the active policy.

## Testing & Verification
- Unit test `test_model_router_privacy_constraint` ensures the router forcefully downgrades to a local provider (despite needing complex reasoning) if privacy constraints are strict.
- Unit test `test_model_router_no_provider_found` confirms the router safely halts execution if no provider can satisfy the current constraint combination (e.g. private task with no local models).
- Unit test `test_model_router_complex_reasoning_prefer_remote` asserts that complex but non-private tasks correctly escalate to remote models.

## Exit Criteria Checklist
- [x] Implemented dynamic Model Router.
- [x] Evaluated policy constraints (cost, latency, privacy).
- [x] Hard-blocked private tasks from reaching remote providers.
- [x] Verified via deterministic tests.

## Pre-Merge Status
All requirements for Phase 21 are fulfilled.
