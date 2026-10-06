import logging
from core.notifications.base import MessageProvider

logger = logging.getLogger("narada-messaging")

class MockMessageProvider(MessageProvider):
    def __init__(self):
        self.sent_messages = []

    async def send_message(self, recipient: str, message: str) -> bool:
        logger.info(f"MOCK MESSAGE to {recipient}: {message}")
        self.sent_messages.append({"recipient": recipient, "message": message})
        return True
