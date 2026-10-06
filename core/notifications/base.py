from abc import ABC, abstractmethod

class MessageProvider(ABC):
    @abstractmethod
    async def send_message(self, recipient: str, message: str) -> bool:
        """
        Sends a message to a user.
        Returns True if successful, False otherwise.
        """
        pass
