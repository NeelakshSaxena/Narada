import pytest
from core.scheduler.queue import PriorityTaskQueue, TaskPriority

def test_priority_queue():
    q = PriorityTaskQueue()
    
    # Enqueue tasks in random order
    q.enqueue("task_low", {"msg": "low"}, priority=TaskPriority.LOW)
    q.enqueue("task_high", {"msg": "high"}, priority=TaskPriority.HIGH)
    q.enqueue("task_normal", {"msg": "normal"}, priority=TaskPriority.NORMAL)
    q.enqueue("task_critical", {"msg": "crit"}, priority=TaskPriority.CRITICAL)
    q.enqueue("task_bg", {"msg": "bg"}, priority=TaskPriority.BACKGROUND)
    
    assert q.size() == 5
    
    # Should pop in priority order
    t1 = q.dequeue()
    assert t1.task_id == "task_critical"
    
    t2 = q.dequeue()
    assert t2.task_id == "task_high"
    
    t3 = q.dequeue()
    assert t3.task_id == "task_normal"
    
    t4 = q.dequeue()
    assert t4.task_id == "task_low"
    
    t5 = q.dequeue()
    assert t5.task_id == "task_bg"
    
    assert q.is_empty()

def test_priority_queue_fifo_for_same_priority():
    q = PriorityTaskQueue()
    
    q.enqueue("task1", {}, priority=TaskPriority.NORMAL)
    q.enqueue("task2", {}, priority=TaskPriority.NORMAL)
    
    t1 = q.dequeue()
    t2 = q.dequeue()
    
    assert t1.task_id == "task1"
    assert t2.task_id == "task2"
