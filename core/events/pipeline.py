from typing import List, Callable, Awaitable
from core.events.models import Event
from core.responsibilities.models import Responsibility
from core.responsibilities.scheduler import ResponsibilityScheduler
from core.events.dedup import EventDeduplicator

class EventPipeline:
    def __init__(self, scheduler: ResponsibilityScheduler, llm_callback: Callable[[str], Awaitable[str]]):
        self.scheduler = scheduler
        self.llm_callback = llm_callback
        self.event_store = [] # Simple persistence
        self.deduplicator = EventDeduplicator()
        
    def normalize(self, raw_event: dict) -> Event:
        # Converts a raw external payload into our internal Event schema
        return Event(
            type=raw_event.get("type", "unknown"),
            payload=raw_event.get("payload", {}),
            source=raw_event.get("source", "system")
        )
        
    def persist(self, event: Event):
        self.event_store.append(event)
        
    def match_responsibilities(self, event: Event) -> List[Responsibility]:
        matched = []
        for resp in self.scheduler.responsibilities:
            # Match by trigger rules
            if event.type in resp.trigger_rules:
                matched.append(resp)
        return matched
        
    async def filter_irrelevant(self, event: Event, responsibilities: List[Responsibility]) -> List[Responsibility]:
        relevant = []
        for resp in responsibilities:
            prompt = f"""
            You are the Narada event relevance evaluator.
            
            EVENT: {event.type}
            PAYLOAD: {event.payload}
            
            RESPONSIBILITY GOAL: {resp.goal}
            
            Does this event materially affect or trigger the responsibility goal?
            Reply only YES or NO.
            """
            decision = await self.llm_callback(prompt)
            if "YES" in decision.upper():
                relevant.append(resp)
        return relevant
        
    async def process_raw_event(self, raw_event: dict):
        event = self.normalize(raw_event)
        
        ext_id = raw_event.get("external_event_id")
        if self.deduplicator.is_duplicate(event, ext_id):
            return # Skip duplicate
            
        self.persist(event)
        matched = self.match_responsibilities(event)
        relevant = await self.filter_irrelevant(event, matched)
        
        for resp in relevant:
            # Wake relevant responsibility -> execute
            # We inject the event into memory_state before execution
            resp.memory_state["triggering_event"] = event.payload
            await self.scheduler.execute_responsibility(resp, self.llm_callback)
