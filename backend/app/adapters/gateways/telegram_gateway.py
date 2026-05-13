"""
Telegram notification gateway adapter.
Implements INotificationGateway for Telegram Bot API delivery.
"""
import requests
from typing import List, Dict, Any

from app.domain.interfaces.notification_gateway import INotificationGateway


class TelegramGateway(INotificationGateway):
    """
    Sends job notifications via Telegram Bot API.
    Handles message chunking for large batches.
    """

    MAX_MESSAGE_LENGTH = 4096
    JOBS_PER_MESSAGE = 10

    def __init__(self, bot_token: str, chat_id: str):
        self._bot_token = bot_token
        self._chat_id = chat_id

    def is_configured(self) -> bool:
        """Check if Telegram credentials are available."""
        return bool(self._bot_token and self._chat_id)

    def send_jobs(self, jobs: List[Dict[str, Any]], **kwargs) -> bool:
        """
        Send job notifications to Telegram in chunked messages.
        Returns True if all chunks were sent successfully.
        """
        if not self.is_configured():
            return False

        if not jobs:
            return True

        # Chunk jobs into groups to avoid message length limits
        chunks = [
            jobs[i:i + self.JOBS_PER_MESSAGE]
            for i in range(0, len(jobs), self.JOBS_PER_MESSAGE)
        ]

        all_success = True
        for chunk in chunks:
            message = self._format_jobs_message(chunk)
            if not self._send_message(message):
                all_success = False

        return all_success

    def _format_jobs_message(self, jobs: List[Dict[str, Any]]) -> str:
        """Format a batch of jobs into a Telegram-friendly message."""
        lines = ["🔔 *New Job Listings*\n"]

        for job in jobs:
            title = job.get("title", "Unknown")
            company = job.get("company", "Unknown")
            location = job.get("location", "")
            url = job.get("url", "")
            source = job.get("source", "")

            lines.append(f"💼 *{title}*")
            lines.append(f"🏢 {company}")
            if location:
                lines.append(f"📍 {location}")
            lines.append(f"🔗 [Apply]({url})")
            lines.append(f"📌 Source: {source}")
            lines.append("")

        return "\n".join(lines)

    def _send_message(self, text: str) -> bool:
        """Send a single message via Telegram Bot API."""
        url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False
