import logging

from app.models.notification import Notification
from app.models.user import User


logger = logging.getLogger(__name__)


async def send_notification_email(
    user: User,
    notification: Notification,
):
    """
    Development-safe email delivery adapter.

    No SMTP credentials are configured yet, so this adapter
    performs a mock delivery instead of pretending that a
    real external email was sent.

    A real SMTP/provider implementation can later replace
    this adapter without changing notification orchestration.
    """

    if not user.email:
        return {
            "channel": "email",
            "delivered": False,
            "provider": "mock",
            "reason": "user_email_missing",
        }

    logger.info(
        "Mock email notification delivery: "
        "user_id=%s notification_id=%s",
        user.id,
        notification.id,
    )

    return {
        "channel": "email",
        "delivered": True,
        "provider": "mock",
        "reason": "mock_delivery",
        "recipient": user.email,
    }
