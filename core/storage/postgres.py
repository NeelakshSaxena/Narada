import json
from typing import Dict, Any, Optional, List

class PostgresConnectionPool:
    """Mock connection pool representing an asyncpg pool."""
    def __init__(self, uri: str):
        self.uri = uri
        self.connected = False
        self._db = {}

    async def connect(self):
        self.connected = True
        
    async def execute(self, query: str, *args):
        if not self.connected:
            raise ConnectionError("Not connected to PostgreSQL")
        # Extremely simplified mock execution
        if "INSERT INTO responsibilities" in query:
            self._db[args[0]] = {"data": args[1]}
        elif "INSERT INTO memory_canonical" in query:
            self._db[args[0]] = {"text": args[1], "metadata": args[2]}

    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        if not self.connected:
            raise ConnectionError("Not connected to PostgreSQL")
        row = self._db.get(args[0])
        return row

    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        if not self.connected:
            raise ConnectionError("Not connected to PostgreSQL")
        return [{"id": k, **v} for k, v in self._db.items()]


class PostgresResponsibilityStore:
    def __init__(self, pool: PostgresConnectionPool):
        self.pool = pool
        
    async def save(self, resp: Any):
        # Assumes resp has an id and can be serialized to JSON
        data = json.dumps(getattr(resp, "__dict__", {}))
        query = "INSERT INTO responsibilities (id, data) VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data"
        await self.pool.execute(query, resp.id, data)
        
    async def get(self, resp_id: str) -> Optional[Any]:
        query = "SELECT data FROM responsibilities WHERE id = $1"
        row = await self.pool.fetchrow(query, resp_id)
        if not row:
            return None
        
        # Domain mapping back to object
        class HydratedResp:
            pass
            
        obj = HydratedResp()
        obj.__dict__ = json.loads(row["data"])
        return obj


class PostgresCanonicalMemoryStore:
    def __init__(self, pool: PostgresConnectionPool):
        self.pool = pool
        
    async def store_metadata(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        meta_json = json.dumps(metadata)
        query = "INSERT INTO memory_canonical (id, text, metadata) VALUES ($1, $2, $3) ON CONFLICT (id) DO UPDATE SET text = EXCLUDED.text, metadata = EXCLUDED.metadata"
        await self.pool.execute(query, doc_id, text, meta_json)

    async def get_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT text, metadata FROM memory_canonical WHERE id = $1"
        row = await self.pool.fetchrow(query, doc_id)
        if not row:
            return None
        return {
            "text": row["text"],
            "metadata": json.loads(row["metadata"])
        }
