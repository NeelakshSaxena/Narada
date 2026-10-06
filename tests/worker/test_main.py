import pytest
import asyncio
from unittest.mock import patch
from apps.worker.main import TaskWorker
from core.events.redis_bus import RedisMock
from core.storage.postgres import PostgresConnectionPool

def test_worker_loop():
    redis = RedisMock()
    pool = PostgresConnectionPool("mock")
    worker = TaskWorker(redis_client=redis, db_pool=pool)
    
    async def run_test():
        # Pre-populate queue
        await redis.publish("scheduled_tasks", "Test scheduled task")
        
        async def mock_generate(prompt, **kwargs):
            from core.llm.models import LLMResponse
            return LLMResponse(text="Mock result", metadata={})
        
        with patch('providers.llm.ollama.OllamaProvider.generate', side_effect=mock_generate):
            # Run worker briefly
            task = asyncio.create_task(worker.start())
            await asyncio.sleep(0.1)
            worker.stop()
            await task
            
            import json
            # Verify db log
            assert len(pool._db) == 1
            entry = list(pool._db.values())[0]
            assert entry["text"] == "Mock result"
            metadata = json.loads(entry["metadata"])
            assert metadata["task"] == "Test scheduled task"
            assert metadata["worker"] == worker.worker_id

    asyncio.run(run_test())
