import json
from typing import Callable, Awaitable, Dict, Any, List

class RedisMock:
    """Mock representing aioredis/redis-py client."""
    def __init__(self):
        self.queues = {}
        self.locks = {}
        
    async def publish(self, channel: str, message: str):
        if channel not in self.queues:
            self.queues[channel] = []
        self.queues[channel].append(message)
        
    async def subscribe(self, channel: str) -> 'RedisSubscriberMock':
        return RedisSubscriberMock(self, channel)
        
    async def setnx(self, key: str, value: str) -> bool:
        if key in self.locks:
            return False
        self.locks[key] = value
        return True
        
    async def delete(self, key: str):
        self.locks.pop(key, None)

    async def get(self, key: str) -> str:
        return self.locks.get(key)
        
    async def set(self, key: str, value: str):
        self.locks[key] = value


class RedisSubscriberMock:
    def __init__(self, client: RedisMock, channel: str):
        self.client = client
        self.channel = channel
        
    async def get_message(self):
        if self.channel in self.client.queues and self.client.queues[self.channel]:
            return {"data": self.client.queues[self.channel].pop(0).encode('utf-8')}
        return None


class RedisEventBus:
    """
    Redis-backed Event Bus transitioning the app to a multi-worker model.
    Durable event semantics via PUB/SUB or Streams.
    """
    def __init__(self, redis_client: RedisMock):
        self.redis = redis_client
        self.handlers: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}
        
    async def emit(self, event_type: str, payload: Dict[str, Any]):
        message = json.dumps({"type": event_type, "payload": payload})
        await self.redis.publish("narada_events", message)
        
    def on(self, event_type: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        
    async def process_events(self):
        subscriber = await self.redis.subscribe("narada_events")
        message = await subscriber.get_message()
        if message and message.get("data"):
            data = json.loads(message["data"].decode('utf-8'))
            event_type = data.get("type")
            payload = data.get("payload")
            
            if event_type in self.handlers:
                for handler in self.handlers[event_type]:
                    await handler(payload)


class RedisCoordinator:
    """
    Provides distributed locking allowing multiple workers to safely
    pick up scheduled jobs without duplicating work.
    """
    def __init__(self, redis_client: RedisMock):
        self.redis = redis_client
        
    async def acquire_lock(self, lock_key: str, worker_id: str) -> bool:
        return await self.redis.setnx(f"lock:{lock_key}", worker_id)
        
    async def release_lock(self, lock_key: str):
        await self.redis.delete(f"lock:{lock_key}")
