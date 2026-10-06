import pytest
import asyncio
from core.storage.postgres import PostgresConnectionPool, PostgresCanonicalMemoryStore
from core.memory.hygiene import MemoryHygieneJob

def test_memory_contradiction():
    pool = PostgresConnectionPool("mock")
    store = PostgresCanonicalMemoryStore(pool)
    
    async def run_test():
        await pool.connect()
        # Original memory
        await store.store_metadata("doc_1", "User likes apples", {"source": "init"})
        
        # Upsert with contradictory memory
        await store.upsert_memory("doc_1", "User hates apples", {"source": "new_chat"})
        
        # Original memory should not be blindly overwritten
        original = await store.get_metadata("doc_1")
        assert original["text"] == "User likes apples"
        
        # But a contradiction should be logged
        all_docs = await store.get_all_metadata()
        contradictions = [d for d in all_docs if d.get("metadata", {}).get("type") == "CONTRADICTION"]
        assert len(contradictions) == 1
        
        c = contradictions[0]
        meta = c["metadata"]
        assert meta["old_memory"] == "User likes apples"
        assert meta["new_memory"] == "User hates apples"
        assert meta["status"] == "UNRESOLVED"
        assert meta["target_doc_id"] == "doc_1"

    asyncio.run(run_test())

def test_hygiene_job_resolution_and_decay():
    pool = PostgresConnectionPool("mock")
    store = PostgresCanonicalMemoryStore(pool)
    job = MemoryHygieneJob(store)
    
    async def run_test():
        await pool.connect()
        # Setup stale memory
        await store.store_metadata("stale_1", "Old thing", {"last_accessed": "2024-01-01", "confidence": 1.0})
        
        # Setup unresolved contradiction
        await store.store_metadata(
            "contradiction_1", 
            "Contradiction", 
            {"type": "CONTRADICTION", "status": "UNRESOLVED", "new_memory": "New truth", "target_doc_id": "target_1", "source": "test"}
        )
        
        await job.run()
        
        # Check decay
        stale = await store.get_metadata("stale_1")
        assert stale["metadata"]["confidence"] == 0.99
        assert stale["metadata"]["decayed"] is True
        
        # Check resolution
        target = await store.get_metadata("target_1")
        assert target["text"] == "Resolved: New truth (Source: test)"
        
        c = await store.get_metadata("contradiction_1")
        assert c["metadata"]["status"] == "RESOLVED"

    asyncio.run(run_test())
