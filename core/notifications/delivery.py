import datetime
from dataclasses import dataclass
from typing import Optional
from enum import Enum
from core.notifications.policy import NotificationPolicy

class UserState(Enum):
    AVAILABLE = "available"
    AWAY = "away"
    DND = "do_not_disturb"

@dataclass
class QuietHours:
    start_hour: int
    start_minute: int
    end_hour: int
    end_minute: int

class DeliveryDecision(Enum):
    NOTIFY = "notify"
    QUEUE = "queue"
    DISCARD = "discard"

class DeliveryManager:
    def __init__(self, state: UserState = UserState.AVAILABLE, quiet_hours: Optional[QuietHours] = None):
        self.state = state
        self.quiet_hours = quiet_hours

    def is_quiet_hours(self, current_time: datetime.datetime) -> bool:
        if not self.quiet_hours:
            return False
            
        current_minutes = current_time.hour * 60 + current_time.minute
        start_minutes = self.quiet_hours.start_hour * 60 + self.quiet_hours.start_minute
        end_minutes = self.quiet_hours.end_hour * 60 + self.quiet_hours.end_minute
        
        if start_minutes < end_minutes:
            return start_minutes <= current_minutes <= end_minutes
        else: # Over midnight
            return current_minutes >= start_minutes or current_minutes <= end_minutes

    def should_deliver(self, policy: NotificationPolicy, current_time: Optional[datetime.datetime] = None) -> DeliveryDecision:
        if current_time is None:
            current_time = datetime.datetime.now()

        if policy == NotificationPolicy.SILENT:
            return DeliveryDecision.DISCARD
            
        if self.state == UserState.DND:
            if policy == NotificationPolicy.URGENT:
                return DeliveryDecision.NOTIFY
            return DeliveryDecision.QUEUE
            
        if self.is_quiet_hours(current_time):
            if policy == NotificationPolicy.URGENT:
                return DeliveryDecision.NOTIFY
            return DeliveryDecision.QUEUE
            
        if self.state == UserState.AWAY:
            if policy in [NotificationPolicy.URGENT, NotificationPolicy.IMPORTANT, NotificationPolicy.APPROVAL_REQUIRED]:
                return DeliveryDecision.NOTIFY
            return DeliveryDecision.QUEUE
            
        # Available
        return DeliveryDecision.NOTIFY
