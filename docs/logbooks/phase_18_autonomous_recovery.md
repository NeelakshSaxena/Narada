# Phase 18: Autonomous Recovery Logbook

## Objective
Enable Nārada to intelligently survive and recover from system and API failures during unattended background runs by implementing a Recovery Matrix.

## Branch
`phase/18-autonomous-recovery`

## Changes Made
- Created the `RecoveryManager` and `FailureContext` abstractions in `core/runtime/recovery.py`.
- Formally modeled the `FailureType` (network timeout, rate limit, auth failure, permission denied).
- Implemented the Recovery Matrix: mapping specific failures to exact behaviors (`RETRY`, `BACKOFF`, `STOP_NOTIFY`, `STOP_ENTIRELY`).
- Codified the safety rule that consequential side effects (non-idempotent operations) can only be retried if their state is proven to be reconciled, blocking blind dangerous retries.

## Testing & Verification
- Unit test `test_recovery_matrix` validates all mappings, explicitly ensuring that non-idempotent timeouts correctly resolve to `STOP_NOTIFY` rather than an unsafe retry.
- Unit test `test_execute_with_recovery` runs simulated exception flows and confirms the system correctly catches, delays, retries, and stops exactly per the matrix definitions.

## Exit Criteria Checklist
- [x] Modeled the Recovery Matrix.
- [x] Defined retry vs. backoff vs. stop behaviors.
- [x] Enforced idempotency checking.
- [x] Guaranteed behavior via deterministic tests.

## Pre-Merge Status
All requirements for Phase 18 are fulfilled.
