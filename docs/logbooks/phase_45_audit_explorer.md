# Phase 45: Audit Explorer Logbook

## Objective
Build a persistent audit trail mechanism that maps Responsibilities -> Tasks -> Actions -> Tools -> Approvals -> Results. Expose an endpoint/CLI command allowing users to inspect exactly what the agent did in the background.

## Branch
`phase/45-audit-explorer`

## Changes Made
- Added `store_audit_log` method to `PostgresCanonicalMemoryStore` in `core/storage/postgres.py`, which generates an `audit` typed memory log holding metadata about responsibilities, tasks, actions, tools, and approvals.
- Implemented the `GET /v1/audit` endpoint in `apps/api/main.py` which filters canonical memory for `audit` records and sorts them by timestamp.
- Updated the CLI chat interface in `scripts/narada.py` with a `/audit` command to nicely format and print out the audit trail for the user.

## Testing & Verification
- Unit test added for API audit call verifying HTTP 200 response shape and list returned (`test_get_audit_trail`).

## Exit Criteria Checklist
- [x] Persistent audit trail mechanism established in storage.
- [x] Endpoint exposed allowing inspection of background activity.
- [x] CLI command added.

## Pre-Merge Status
All requirements for Phase 45 are fulfilled.
