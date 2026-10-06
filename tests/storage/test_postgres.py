import pytest
import asyncio
from core.storage.postgres import PostgresConnectionPool, PostgresResponsibilityStore, PostgresCanonicalMemoryStore

class DummyResponsibility:
    def __init__(self, id, goal):
        self.id = id
        self.goal = goal

def test_postgres_responsibility_store():
    pool = PostgresConnectionPool("postgresql://user:pass@localhost:5432/narada")
    asyncio.run(pool.connect())
    
    store = PostgresResponsibilityStore(pool)
    resp = DummyResponsibility("resp_123", "Migrate to PG")
    
    # Save
    asyncio.run(store.save(resp))
    
    # Retrieve
    loaded = asyncio.run(store.get("resp_123"))
    assert loaded is not None
    assert loaded.id == "resp_123"
    assert loaded.goal == "Migrate to PG"

def test_postgres_canonical_memory():
    pool = PostgresConnectionPool("postgresql://user:pass@localhost:5432/narada")
    asyncio.run(pool.connect())
    
    store = PostgresCanonicalMemoryStore(pool)
    
    asyncio.run(store.store_metadata("doc_abc", "Important memory", {"confidence": 0.99}))
    
    data = asyncio.run(store.get_metadata("doc_abc"))
    assert data is not None
    assert data["text"] == "Important memory"
    assert data["metadata"]["confidence"] == 0.99

def test_postgres_not_connected():
    pool = PostgresConnectionPool("postgresql://user:pass@localhost:5432/narada")
    store = PostgresResponsibilityStore(pool)
    
    resp = DummyResponsibility("resp_1", "Will Fail")
    with pytest.raises(ConnectionError, match="Not connected to PostgreSQL"):
        asyncio.run(store.save(resp))
