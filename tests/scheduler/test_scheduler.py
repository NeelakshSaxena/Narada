import pytest
import asyncio
from unittest.mock import MagicMock
from core.scheduler.scheduler import LocalScheduler
from core.events.redis_bus import RedisMock

def test_scheduler_loop():
    redis = RedisMock()
    scheduler = LocalScheduler(redis)
    
    async def run_test():
        job_id = await scheduler.schedule_job("Check database", "interval", interval=1)
        
        # Start scheduler briefly
        await scheduler.start()
        await asyncio.sleep(0.1)
        await scheduler.stop()
        
        # Ensure it published to redis
        assert "scheduled_tasks" in redis.queues
        assert len(redis.queues["scheduled_tasks"]) > 0
        assert "Check database" in redis.queues["scheduled_tasks"]
        
        # Test cancellation
        await scheduler.cancel_job(job_id)
        assert job_id not in scheduler.jobs

    asyncio.run(run_test())
