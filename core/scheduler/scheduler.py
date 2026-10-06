from abc import ABC, abstractmethod
from typing import Any, Callable
import asyncio
import logging
import uuid

logger = logging.getLogger("narada-scheduler")

class SchedulerProvider(ABC):
    @abstractmethod
    async def schedule_job(self, task_data: str, trigger: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def cancel_job(self, job_id: str):
        pass

class LocalScheduler(SchedulerProvider):
    """
    Local Scheduler abstracting APScheduler functionality.
    Injects scheduled tasks into Redis to wake up Task Workers.
    """
    def __init__(self, redis_client: Any):
        self.redis = redis_client
        self.jobs = {}
        self.is_running = False
        self._task = None
        
    async def schedule_job(self, task_data: str, trigger: str, **kwargs) -> str:
        job_id = str(uuid.uuid4())
        interval = kwargs.get("interval", 1)
        self.jobs[job_id] = {
            "task_data": task_data,
            "trigger": trigger,
            "interval": interval
        }
        logger.info(f"Scheduled job {job_id}: {task_data} (interval {interval}s)")
        return job_id

    async def cancel_job(self, job_id: str):
        if job_id in self.jobs:
            del self.jobs[job_id]
            logger.info(f"Cancelled job {job_id}")

    async def _scheduler_loop(self):
        while self.is_running:
            for job_id, job in self.jobs.items():
                if job["trigger"] == "interval":
                    # Publish to Redis so Task Worker executes it
                    logger.info(f"Triggering {job_id}")
                    await self.redis.publish("scheduled_tasks", job["task_data"])
            await asyncio.sleep(0.01)

    async def start(self):
        self.is_running = True
        logger.info("Scheduler started.")
        self._task = asyncio.create_task(self._scheduler_loop())
        
    async def stop(self):
        self.is_running = False
        if self._task:
            await self._task
        logger.info("Scheduler stopped.")
