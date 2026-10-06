# Phase 42: Background Worker Tuning & Dead-Letter Queues Logbook

## Objective
Refine the existing Background Worker to support retry policies, dead-lettering, and track execution failures to prevent endlessly looping tasks.

## Branch
`phase/42-background-worker`

## Changes Made
- Added `get` and `set` methods to `RedisMock` in `core/events/redis_bus.py` to enable persistent key-value tracking of task attempts.
- Updated `TaskWorker` in `apps/worker/main.py`:
  - Retries tasks up to 3 times by incrementing an attempt tracker stored in Redis.
  - Automatically re-queues tasks upon exception up to the retry limit.
  - Flags persistently failing tasks as `FAILED_PERMANENT` and archives them as dead-letter documents in `CanonicalMemoryStore`.
  - Ensures distributed locks (`RedisCoordinator`) are safely released in a `finally` block to prevent orphaned lock deadlocks.
- Updated unit tests in `tests/worker/test_main.py` adding `test_worker_retry_dlq` to verify the 3-attempt cycle and final dead-lettering.

## Testing & Verification
- Unit test coverage confirms failures accurately bump attempt counts and re-queue.
- Validated that upon 3 failed attempts, a new document containing `FAILED_PERMANENT` metadata is safely stored and the task is dropped from active polling.

## Exit Criteria Checklist
- [x] Retry policies implemented.
- [x] Dead-lettering (`FAILED_PERMANENT`) correctly stops infinite task loops.
- [x] Failure reasons and attempt counts stored persistently in memory.

## Pre-Merge Status
All requirements for Phase 42 are fulfilled.
