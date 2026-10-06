# Phase 38: Background Responsibility API Logbook

## Objective
Bind the core scheduler logic directly into a user-facing REST API, allowing client applications to configure long-running agent tasks interactively.

## Branch
`phase/38-background-responsibility`

## Changes Made
- Upgraded `NaradaCore` within `core/runtime/runtime.py` to natively track and spin up `LocalScheduler` and `RedisMock`.
- Hooked the startup lifecycle event in `apps/api/main.py` directly into `NaradaCore.boot()` verifying the daemon initializes gracefully.
- Authored the `POST /v1/responsibilities` endpoint parsing basic scheduling details directly into the `core.scheduler.schedule_job()` function.

## Testing & Verification
- Validated `test_health_check` through explicit FastAPI `TestClient` context managers to assert the engine accurately flags its state as running upon boot.
- Asserts that submitting a `POST` request issues a correct generic task trigger, verifying `job_id` presence via `test_create_responsibility`.

## Exit Criteria Checklist
- [x] Scheduler injected securely into the global runtime instance.
- [x] Boot logic automated inside the main FastAPI entrypoint.
- [x] Active endpoint bound for external task triggers.

## Pre-Merge Status
All requirements for Phase 38 are fulfilled.
