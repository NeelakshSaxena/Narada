from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SemanticMemoryError(Exception):
    pass

class VectorStore:
    def __init__(self, available: bool = True):
        self.available = available
        self._vectors = {}
        
    def is_available(self) -> bool:
        return self.available

    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        if not self.available:
            raise SemanticMemoryError("Qdrant is unavailable")
        # In a real implementation, this would perform cosine similarity search via Qdrant client
        # Returning dummy data for tests
        if not self._vectors:
            return []
        # Return first N items
        return [{"id": k, "score": 0.9} for k in list(self._vectors.keys())[:limit]]

    def upsert(self, doc_id: str, vector: List[float], payload: Dict[str, Any]):
        if not self.available:
            raise SemanticMemoryError("Qdrant is unavailable")
        self._vectors[doc_id] = {"vector": vector, "payload": payload}


class CanonicalStore:
    def __init__(self):
        self._db = {}
        
    def store_metadata(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        self._db[doc_id] = {"text": text, "metadata": metadata}
        
    def get_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self._db.get(doc_id)
        
    def fts_search(self, query: str) -> List[Dict[str, Any]]:
        # Full Text Search fallback implementation (SQLite FTS mock)
        results = []
        for doc_id, data in self._db.items():
            if query.lower() in data["text"].lower():
                results.append({"id": doc_id, "text": data["text"], "metadata": data["metadata"]})
        return results


class Embedder:
    async def embed(self, text: str) -> List[float]:
        # Dummy embedding
        return [0.1, 0.2, 0.3]


class SemanticMemoryArchitecture:
    """
    Vector Memory Architecture:
    Separates vectors (Qdrant) from canonical metadata (SQLite).
    Provides graceful fallback to FTS if Qdrant is unavailable.
    """
    def __init__(self, vector_store: VectorStore, canonical_store: CanonicalStore, embedder: Embedder):
        self.vector_store = vector_store
        self.canonical = canonical_store
        self.embedder = embedder

    async def store(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        # Canonical is source of truth
        self.canonical.store_metadata(doc_id, text, metadata)
        
        # Best effort to store in Vector store
        try:
            if self.vector_store.is_available():
                vector = await self.embedder.embed(text)
                # Payload in Qdrant should be minimal, just enough to link back to canonical
                self.vector_store.upsert(doc_id, vector, {"doc_id": doc_id})
        except Exception as e:
            logger.warning(f"Failed to store vector in Qdrant: {e}. Canonical metadata was saved.")

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            if not self.vector_store.is_available():
                raise SemanticMemoryError("Qdrant not available, triggering fallback.")
                
            query_vector = await self.embedder.embed(query)
            vector_results = self.vector_store.search(query_vector, limit)
            
            # Rehydrate from canonical
            final_results = []
            for res in vector_results:
                canonical_data = self.canonical.get_metadata(res["id"])
                if canonical_data:
                    final_results.append({
                        "id": res["id"],
                        "score": res["score"],
                        "text": canonical_data["text"],
                        "metadata": canonical_data["metadata"],
                        "source": "semantic_vector"
                    })
            return final_results
            
        except Exception as e:
            logger.info(f"Vector search failed ({e}), falling back to FTS.")
            fts_results = self.canonical.fts_search(query)
            return [{
                "id": r["id"],
                "text": r["text"],
                "metadata": r["metadata"],
                "source": "fts_fallback"
            } for r in fts_results]
