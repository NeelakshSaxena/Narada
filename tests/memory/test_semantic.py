import pytest
import asyncio
from core.memory.semantic import (
    SemanticMemoryArchitecture,
    VectorStore,
    CanonicalStore,
    Embedder
)

def test_semantic_memory_store_and_search_success():
    vector_store = VectorStore(available=True)
    canonical = CanonicalStore()
    embedder = Embedder()
    
    memory = SemanticMemoryArchitecture(vector_store, canonical, embedder)
    
    # Store a document
    asyncio.run(memory.store("doc1", "Narada is an AI agent", {"type": "concept"}))
    
    # Verify canonical has it
    assert canonical.get_metadata("doc1")["text"] == "Narada is an AI agent"
    
    # Search should hit vector store and return semantic_vector source
    results = asyncio.run(memory.search("What is Narada?"))
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
    assert results[0]["source"] == "semantic_vector"

def test_semantic_memory_fallback_to_fts():
    # Simulate unavailable Qdrant
    vector_store = VectorStore(available=False)
    canonical = CanonicalStore()
    embedder = Embedder()
    
    memory = SemanticMemoryArchitecture(vector_store, canonical, embedder)
    
    asyncio.run(memory.store("doc2", "Fallback testing", {"status": "ok"}))
    
    # Canonical should save it, but vector store fails gracefully silently on store
    
    # Search should fallback to FTS
    results = asyncio.run(memory.search("fallback"))
    assert len(results) == 1
    assert results[0]["id"] == "doc2"
    assert results[0]["source"] == "fts_fallback"

def test_semantic_memory_fts_no_match():
    vector_store = VectorStore(available=False)
    canonical = CanonicalStore()
    embedder = Embedder()
    
    memory = SemanticMemoryArchitecture(vector_store, canonical, embedder)
    asyncio.run(memory.store("doc3", "Only specific words", {"foo": "bar"}))
    
    results = asyncio.run(memory.search("unrelated"))
    assert len(results) == 0
