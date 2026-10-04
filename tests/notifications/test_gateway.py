import pytest
import asyncio
from core.notifications.gateway import DeliveryGateway
from providers.notifications.console import ConsoleProvider

def test_delivery_gateway():
    gateway = DeliveryGateway()
    provider = ConsoleProvider(name="mock_console")
    gateway.register_provider(provider)
    
    success = asyncio.run(gateway.deliver("mock_console", "Test message", {"level": "info"}))
    
    assert success is True
    assert len(provider.sent_messages) == 1
    assert provider.sent_messages[0]["message"] == "Test message"
    assert provider.sent_messages[0]["context"] == {"level": "info"}

def test_unregistered_provider():
    gateway = DeliveryGateway()
    with pytest.raises(ValueError):
        gateway.get_provider("missing")
