"""
Notification gateway interface (Port).
Defines the contract for sending notifications to external channels.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class INotificationGateway(ABC):
    """
    Abstract interface for notification delivery.
    Implementations can target Telegram, email, Slack, etc.
    """

    @abstractmethod
    def send_jobs(self, jobs: List[Dict[str, Any]], **kwargs) -> bool:
        """
        Send a batch of job notifications.
        Returns True if delivery was successful.
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the gateway has valid configuration to send messages."""
        pass
