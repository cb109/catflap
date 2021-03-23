import logging

from django.conf import settings

logger = logging.getLogger(__name__)

PushoverClient = None
try:
    from pushover import Client as PushoverClient
except ImportError:
    logger.warning("Pushover not installed, no push notifications")


def send_push_notification(message, title=None):
    if not PushoverClient:
        return
    if not settings.PUSHOVER_USER_KEY or not settings.PUSHOVER_API_TOKEN:
        return
    client = PushoverClient(
        settings.PUSHOVER_USER_KEY, api_token=settings.PUSHOVER_API_TOKEN
    )
    client.send_message(message, title=title)

