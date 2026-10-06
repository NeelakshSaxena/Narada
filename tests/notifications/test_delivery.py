import pytest
import datetime
from core.notifications.policy import NotificationPolicy
from core.notifications.delivery import DeliveryManager, UserState, QuietHours, DeliveryDecision

def test_available_delivery():
    manager = DeliveryManager(state=UserState.AVAILABLE)
    assert manager.should_deliver(NotificationPolicy.INFORMATIONAL) == DeliveryDecision.NOTIFY
    assert manager.should_deliver(NotificationPolicy.SILENT) == DeliveryDecision.DISCARD

def test_quiet_hours():
    qh = QuietHours(23, 0, 7, 0)
    manager = DeliveryManager(state=UserState.AVAILABLE, quiet_hours=qh)
    
    # Inside quiet hours
    time_in = datetime.datetime(2023, 1, 1, 1, 0)
    assert manager.should_deliver(NotificationPolicy.INFORMATIONAL, time_in) == DeliveryDecision.QUEUE
    assert manager.should_deliver(NotificationPolicy.URGENT, time_in) == DeliveryDecision.NOTIFY
    
    # Outside quiet hours
    time_out = datetime.datetime(2023, 1, 1, 12, 0)
    assert manager.should_deliver(NotificationPolicy.INFORMATIONAL, time_out) == DeliveryDecision.NOTIFY

def test_away_state():
    manager = DeliveryManager(state=UserState.AWAY)
    assert manager.should_deliver(NotificationPolicy.INFORMATIONAL) == DeliveryDecision.QUEUE
    assert manager.should_deliver(NotificationPolicy.IMPORTANT) == DeliveryDecision.NOTIFY
    assert manager.should_deliver(NotificationPolicy.URGENT) == DeliveryDecision.NOTIFY

def test_dnd_state():
    manager = DeliveryManager(state=UserState.DND)
    assert manager.should_deliver(NotificationPolicy.INFORMATIONAL) == DeliveryDecision.QUEUE
    assert manager.should_deliver(NotificationPolicy.IMPORTANT) == DeliveryDecision.QUEUE
    assert manager.should_deliver(NotificationPolicy.URGENT) == DeliveryDecision.NOTIFY
