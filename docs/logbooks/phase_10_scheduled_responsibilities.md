# Phase 10: Scheduled Responsibilities Logbook

## Objective
Allow Nārada to execute autonomous, long-running background tasks without the user being present by strictly enforcing the "self-contained" execution model and fresh session contexts.

## Branch
`phase/10-scheduled-responsibilities`

## Changes Made
- Established the `Responsibility` schema in `core/responsibilities/models.py`. It tracks the critical dimensions of an autonomous background job: explicit `goal`, `schedule_interval_seconds`, `memory_state`, `delivery_target`, and bounded `permissions`.
- Implemented an in-process `ResponsibilityScheduler` inside `core/responsibilities/scheduler.py` based on an asyncio event loop, deliberately avoiding the introduction of heavy external schedulers (e.g., celery/redis/docker) as requested by the blueprint constraints.
- Engineered the core execution model: When a responsibility is due, the system forces a brand-new, isolated `Executor` context.
- Implemented the "Self-Contained Rule": Rather than relying on conversation history, the system dynamically generates a strict prompt containing the raw goal, the previous `memory_state`, the required procedural `Skills` (from Phase 9), and explicit formatting rules dictating how to deliver the result.
- Wrote robust tests (`tests/responsibilities/test_scheduler.py`) modeling timing limits, execution contexts, and the self-contained prompt generation.

## Testing & Verification
- Test `test_responsibility_model_scheduling` mathematically validates the due-time execution limits.
- Test `test_scheduler_execution_context` mocks an LLM callback to definitively prove the self-contained generation template accurately builds out the context blocks required by the blueprint.

## Exit Criteria Checklist
- [x] Defined `Responsibility` abstraction in `models.py`.
- [x] Built in-process scheduler inside `narada-core` (no new Docker containers).
- [x] Created fresh execution session model.
- [x] Enforced self-contained prompts to prevent conversational drift.
- [x] Wrote deterministic, mocked unit tests.

## Pre-Merge Status
All requirements for Phase 10 are fulfilled.
