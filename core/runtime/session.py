import uuid
from enum import Enum
from typing import List, Dict, Any

class ContextPriority(Enum):
    SAFETY_AND_PERMISSIONS = 1
    CURRENT_TASK = 2
    CURRENT_GOAL = 3
    RELEVANT_RESPONSIBILITY = 4
    RECENT_OBSERVATIONS = 5
    RELEVANT_MEMORY = 6
    HISTORICAL_CONTEXT = 7

class Conversation:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.history: List[Dict[str, str]] = []

class Session:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.active_conversations: List[str] = []

class Run:
    def __init__(self, run_id: str = None):
        self.id = run_id or str(uuid.uuid4())
        self.context_items: List[Dict[str, Any]] = []

class RunContextBuilder:
    def __init__(self):
        self._items: List[Dict[str, Any]] = []

    def add_item(self, priority: ContextPriority, data: str):
        self._items.append({"priority": priority, "data": data})

    def build_fresh_run(self, max_items: int = 10) -> Run:
        # Sort items by priority (1 is highest priority)
        sorted_items = sorted(self._items, key=lambda x: x["priority"].value)
        
        # Budget policy: take highest priority items up to max_items
        selected_items = sorted_items[:max_items]
        
        run = Run()
        run.context_items = selected_items
        return run
