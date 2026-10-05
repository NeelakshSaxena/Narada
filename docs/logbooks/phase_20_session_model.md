# Phase 20: Session Model Logbook

## Objective
Decouple standard chatbot conversation history from autonomous execution runs by creating distinct `Conversation`, `Session`, `Run`, and `Responsibility` entities, and implement a Context Budget Policy.

## Branch
`phase/20-session-model`

## Changes Made
- Created precise domain models (`Conversation`, `Session`, `Run`) in `core/runtime/session.py`.
- Implemented `RunContextBuilder`, resolving the fundamental problem of infinite context growth by dynamically constructing isolated `Run` scopes for background execution.
- Enforced the Context Budget Policy using a `ContextPriority` Enum, ensuring that `SAFETY_AND_PERMISSIONS` and `CURRENT_TASK` are aggressively prioritized over `HISTORICAL_CONTEXT`.

## Testing & Verification
- Unit test `test_session_entities` validates the existence and default isolated states of the new models.
- Unit test `test_run_context_builder_budget_policy` injects a mix of safe/unsafe, high/low priority context, constrains the budget, and ensures the builder intentionally truncates low-priority historical data to preserve critical safety instructions.

## Exit Criteria Checklist
- [x] Separated Conversation from Run.
- [x] Built the `RunContextBuilder`.
- [x] Enforced Context Budget prioritization.
- [x] Protected safety limits under constrained budgets.

## Pre-Merge Status
All requirements for Phase 20 are fulfilled.
