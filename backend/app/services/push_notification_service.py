import logging

from app.models.notification import Notification
from app.models.user import User


logger = logging.getLogger(__name__)


async def send_push_notification(
    user: User,
    notification: Notification,
):
    """
    Development-safe push delivery adapter.

    Device-token/FCM infrastructure is not configured yet.
    The mock provider verifies the push delivery pipeline
    without claiming that a real device received a push.
    """

    logger.info(
        "Mock push notification delivery: "
        "user_id=%s notification_id=%s",
        user.id,
        notification.id,
    )

    return {
        "channel": "push",
        "delivered": True,
        "provider": "mock",
        "reason": "mock_delivery",
        "user_id": user.id,
    }
