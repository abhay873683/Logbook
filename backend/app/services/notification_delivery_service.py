from sqlalchemy.orm import Session

from app.core.websocket.notification_manager import (
    notification_manager,
)

from app.models.notification import Notification

from app.services.notification_preference_service import (
    get_notification_preferences,
    is_category_enabled,
)


def serialize_notification(
    notification: Notification,
):
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type,
        "priority": notification.priority,
        "category": notification.category,
        "source": notification.source,
        "data": notification.data,
        "is_read": notification.is_read,
        "created_at": (
            notification.created_at.isoformat()
            if notification.created_at
            else None
        ),
        "updated_at": (
            notification.updated_at.isoformat()
            if notification.updated_at
            else None
        ),
    }


async def deliver_notification_in_app(
    db: Session,
    notification: Notification,
):
    preference = get_notification_preferences(
        db,
        notification.user_id,
    )

    connections = (
        notification_manager.connection_count(
            notification.user_id
        )
    )

    if not preference.in_app_notifications:
        return {
            "delivered": False,
            "sent_connections": 0,
            "active_connections": connections,
            "reason": (
                "in_app_notifications_disabled"
            ),
        }

    if not is_category_enabled(
        preference,
        notification.category,
    ):
        return {
            "delivered": False,
            "sent_connections": 0,
            "active_connections": connections,
            "reason": (
                "notification_category_disabled"
            ),
        }

    if connections == 0:
        return {
            "delivered": False,
            "sent_connections": 0,
            "active_connections": 0,
            "reason": "no_active_connections",
        }

    event = {
        "type": "notification",
        "notification": (
            serialize_notification(
                notification
            )
        ),
    }

    sent_count = (
        await notification_manager.send_to_user(
            notification.user_id,
            event,
        )
    )

    return {
        "delivered": sent_count > 0,
        "sent_connections": sent_count,
        "active_connections": (
            notification_manager.connection_count(
                notification.user_id
            )
        ),
        "reason": (
            "delivered"
            if sent_count > 0
            else "delivery_failed"
        ),
    }
