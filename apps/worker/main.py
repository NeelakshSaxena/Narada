import asyncio
import logging
import uuid
from core.events.redis_bus import RedisMock, RedisCoordinator
from core.runtime.runtime import AgentRuntime
from core.storage.postgres import PostgresConnectionPool, PostgresCanonicalMemoryStore

logger = logging.getLogger("narada-worker")

class TaskWorker:
    def __init__(self, redis_client=None, db_pool=None):
        self.redis = redis_client or RedisMock()
        self.coordinator = RedisCoordinator(self.redis)
        self.pool = db_pool or PostgresConnectionPool("postgres://fake:5432")
        self.memory = PostgresCanonicalMemoryStore(self.pool)
        self.agent = AgentRuntime()
        self.worker_id = str(uuid.uuid4())
        self.is_running = False
        
    async def start(self):
        await self.pool.connect()
        subscriber = await self.redis.subscribe("scheduled_tasks")
        logger.info(f"Worker {self.worker_id} started, listening on scheduled_tasks...")
        self.is_running = True
        
        while self.is_running:
            try:
                message = await subscriber.get_message()
                if message and message.get("data"):
                    task_data = message["data"].decode('utf-8')
                    # Acquire lock to prevent duplicate execution
                    if await self.coordinator.acquire_lock(f"task:{task_data}", self.worker_id):
                        logger.info(f"Executing task: {task_data}")
                        result = await self.agent.execute_task(task_data)
                        
                        # Log to memory
                        doc_id = str(uuid.uuid4())
                        await self.memory.store_metadata(
                            doc_id=doc_id,
                            text=result,
                            metadata={"task": task_data, "worker": self.worker_id}
                        )
                        logger.info(f"Task complete. Logged to memory as {doc_id}")
                else:
                    await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(0.1)

    def stop(self):
        self.is_running = False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    worker = TaskWorker()
    asyncio.run(worker.start())
