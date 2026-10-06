from enum import IntEnum
from dataclasses import dataclass, field
import heapq
import time

class TaskPriority(IntEnum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

@dataclass
class QueuedTask:
    task_id: str
    priority: TaskPriority
    payload: dict
    timestamp: float = field(default_factory=time.time)

    # For heapq to sort properly
    def __lt__(self, other):
        # Sort by priority first (lower number = higher priority), then by timestamp (FIFO for same priority)
        if self.priority == other.priority:
            return self.timestamp < other.timestamp
        return self.priority < other.priority

class PriorityTaskQueue:
    def __init__(self):
        self._queue = []
        self._task_map = {}

    def enqueue(self, task_id: str, payload: dict, priority: TaskPriority = TaskPriority.NORMAL):
        task = QueuedTask(task_id=task_id, priority=priority, payload=payload)
        heapq.heappush(self._queue, task)
        self._task_map[task_id] = task

    def dequeue(self) -> QueuedTask | None:
        if not self._queue:
            return None
        task = heapq.heappop(self._queue)
        if task.task_id in self._task_map:
            del self._task_map[task.task_id]
        return task

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def size(self) -> int:
        return len(self._queue)
