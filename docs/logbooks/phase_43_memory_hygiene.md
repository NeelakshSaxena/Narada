# Phase 43: Long-Term Memory Hygiene Logbook

## Objective
Introduce automated maintenance to ensure `CanonicalMemoryStore` does not grow unbounded with stale or contradictory information. Handle memory contradictions safely without blind overwriting.

## Branch
`phase/43-memory-hygiene`

## Changes Made
- Updated `PostgresCanonicalMemoryStore` with an `upsert_memory` method that checks for potential contradictions.
- If a new text memory fundamentally contradicts an existing memory key, the system logs a `CONTRADICTION` typed memory object with `UNRESOLVED` status instead of overwriting.
- Created `MemoryHygieneJob` in `core/memory/hygiene.py` representing a low-priority scheduled task.
- `MemoryHygieneJob` decays confidence scores of memories based on `last_accessed` timestamps.
- `MemoryHygieneJob` iterates over `UNRESOLVED` contradictions, simulating LLM resolution and updating the target memory, before marking the contradiction as `RESOLVED`.
- Updated mock `execute` function in `PostgresConnectionPool` to handle `DELETE` statements properly.

## Testing & Verification
- Unit tests added in `tests/memory/test_hygiene.py`.
- `test_memory_contradiction`: Verified `upsert_memory` prevents blind overwrites and instead generates a tracking contradiction object.
- `test_hygiene_job_resolution_and_decay`: Verified the batch maintenance job correctly resolves queued contradictions and decays confidence scores on stale records.

## Exit Criteria Checklist
- [x] Contradictions handled without blind overwrites.
- [x] Low-priority maintenance job defined.
- [x] Stale memories are decayed.

## Pre-Merge Status
All requirements for Phase 43 are fulfilled.
