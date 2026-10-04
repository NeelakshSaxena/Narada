from abc import ABC, abstractmethod
from typing import Any, Callable

class SchedulerProvider(ABC):
    @abstractmethod
    async def schedule_job(self, job: Callable, trigger: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def cancel_job(self, job_id: str):
        pass
