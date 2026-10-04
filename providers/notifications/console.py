from core.notifications.gateway import NotificationProvider
from typing import Dict, Any

class ConsoleProvider(NotificationProvider):
    def __init__(self, name: str = "console"):
        self._name = name
        self.sent_messages = []

    @property
    def name(self) -> str:
        return self._name

    async def send(self, message: str, context: Dict[str, Any] = None) -> bool:
        print(f"[NĀRADA NOTIFICATION] {message}")
        if context:
            print(f"[CONTEXT] {context}")
        self.sent_messages.append({"message": message, "context": context})
        return True
