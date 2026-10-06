import pytest
import asyncio
from providers.messaging.mock import MockMessageProvider

def test_mock_message_provider():
    provider = MockMessageProvider()
    
    async def run_test():
        result = await provider.send_message("user@example.com", "Approval required for shell.execute")
        assert result is True
        assert len(provider.sent_messages) == 1
        assert provider.sent_messages[0]["recipient"] == "user@example.com"
        assert provider.sent_messages[0]["message"] == "Approval required for shell.execute"

    asyncio.run(run_test())
