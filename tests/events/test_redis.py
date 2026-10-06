import pytest
import asyncio
from core.events.redis_bus import RedisMock, RedisEventBus, RedisCoordinator

def test_redis_event_bus():
    redis = RedisMock()
    bus = RedisEventBus(redis)
    
    received_payloads = []
    
    async def handle_task(payload):
        received_payloads.append(payload)
        
    bus.on("task.created", handle_task)
    
    # Emit event
    asyncio.run(bus.emit("task.created", {"task_id": "123"}))
    
    # Process event
    asyncio.run(bus.process_events())
    
    assert len(received_payloads) == 1
    assert received_payloads[0]["task_id"] == "123"

def test_redis_coordinator_locking():
    redis = RedisMock()
    coord = RedisCoordinator(redis)
    
    # Worker 1 acquires lock
    acquired = asyncio.run(coord.acquire_lock("job_456", "worker_1"))
    assert acquired is True
    
    # Worker 2 fails to acquire same lock
    acquired_2 = asyncio.run(coord.acquire_lock("job_456", "worker_2"))
    assert acquired_2 is False
    
    # Worker 1 releases lock
    asyncio.run(coord.release_lock("job_456"))
    
    # Worker 2 can now acquire
    acquired_3 = asyncio.run(coord.acquire_lock("job_456", "worker_2"))
    assert acquired_3 is True
