import pytest
import asyncio
from core.gateway.channel import ChannelManager, WebChannel, SMSChannel, Capability

def test_channel_manager_registration():
    manager = ChannelManager()
    manager.register_provider(WebChannel("web"))
    manager.register_provider(SMSChannel("sms"))
    
    assert manager.get_provider("web").name == "web"
    assert manager.get_provider("sms").name == "sms"
    
    with pytest.raises(ValueError, match="not found"):
        manager.get_provider("telegram")

def test_channel_capabilities():
    manager = ChannelManager()
    manager.register_provider(WebChannel("web"))
    manager.register_provider(SMSChannel("sms"))
    
    # Check Web capabilities
    assert manager.can_handle("web", Capability.TEXT_IN) is True
    assert manager.can_handle("web", Capability.INTERACTIVE_APPROVAL) is True
    
    # Check SMS capabilities
    assert manager.can_handle("sms", Capability.TEXT_IN) is True
    assert manager.can_handle("sms", Capability.INTERACTIVE_APPROVAL) is False

def test_channel_methods():
    web = WebChannel("web")
    sms = SMSChannel("sms")
    
    assert asyncio.run(web.send_text("Hello")) is True
    assert asyncio.run(web.request_interactive_approval("Approve?")) is True
    
    assert asyncio.run(sms.send_text("Hello")) is True
    
    with pytest.raises(NotImplementedError):
        asyncio.run(sms.request_interactive_approval("Approve?"))
