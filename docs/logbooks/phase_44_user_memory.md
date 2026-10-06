# Phase 44: User-Controlled Memory Logbook

## Objective
Provide the user with granular control over canonical memory storage, explicitly allowing true persistence deletion.

## Branch
`phase/44-user-memory`

## Changes Made
- Expanded the `Narada API` (`apps/api/main.py`) with a `DELETE /v1/memory/{doc_id}` endpoint that drops metadata items directly from the backend.
- Expanded the CLI interactive shell (`scripts/narada.py`) with a `/forget <doc_id>` command that invokes the API endpoint.
- Handled PostgreSQL DELETE requests accurately inside the memory mock implementations.

## Testing & Verification
- Unit test added for API delete calls verifying HTTP 200 response shapes (`test_delete_memory`).
- Manual inspection of mock DB semantics.

## Exit Criteria Checklist
- [x] API endpoint implemented for deletion.
- [x] CLI exposes /forget command.
- [x] Deletion removes data from persistent storage interface, not just hiding it.

## Pre-Merge Status
All requirements for Phase 44 are fulfilled.
