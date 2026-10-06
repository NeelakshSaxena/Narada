# Phase 60: Cost Safety Logbook

## Objective
Enforce bounded spending and execution budgets for autonomous and long-running responsibilities to guarantee unattended safety.

## Branch
`phase/60-cost-safety`

## Changes Made
- Authored `BudgetConfig` outlining thresholds for LLM queries, tool invocations, estimated monetary cost, and total execution time.
- Integrated `BudgetTracker` in `core/responsibilities/budget.py` to maintain operational tally.
- Triggers strict `BudgetExceededError` whenever limits breach across time, compute, or spend.

## Testing & Verification
- Test `test_budget_limits_not_exceeded` verifies safe bounds.
- Dedicated tests for `model_limit`, `tool_limit`, `cost_limit`, and `runtime_limit` assert precise detection of constraint breaches.

## Exit Criteria Checklist
- [x] Tracks model usage constraints.
- [x] Tracks tool usage limits.
- [x] Measures wall-clock runtime limits.
- [x] Errors thrown predictably upon exhaustion.

## Pre-Merge Status
All requirements for Phase 60 are fulfilled.
