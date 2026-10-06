# Phase 27: Qdrant / Semantic Memory Logbook

## Objective
Implement Semantic Memory by integrating a vector store (e.g. Qdrant) while adhering to the "Vector Memory Architecture" rule: vectors are separated from canonical metadata (SQLite), and the system gracefully falls back to Full Text Search (FTS) if the vector store is unavailable.

## Branch
`phase/27-semantic-memory`

## Changes Made
- Created `core/memory/semantic.py` defining the `SemanticMemoryArchitecture`.
- Built `VectorStore` (Qdrant mock) and `CanonicalStore` (SQLite mock) components.
- Enforced the architectural boundary where vector payloads are minimized (storing only `doc_id`) to link back to the Canonical store.
- Implemented `try/except` safeguards to ensure failure in vector storage/retrieval triggers a graceful fallback to `fts_search`.

## Testing & Verification
- Unit test `test_semantic_memory_store_and_search_success` confirms that a healthy vector store returns results hydrated correctly from the canonical store.
- Unit test `test_semantic_memory_fallback_to_fts` explicitly verifies that when `VectorStore.available` is False, the agent gracefully degrades to searching canonical text directly.
- Unit test `test_semantic_memory_fts_no_match` ensures the fallback handles empty results cleanly.

## Exit Criteria Checklist
- [x] Separated Vector and Canonical stores.
- [x] Prevented hard dependency on Vector DB availability.
- [x] Verified FTS fallback behavior with deterministic tests.

## Pre-Merge Status
All requirements for Phase 27 are fulfilled.
