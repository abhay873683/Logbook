from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User

from app.services.email_notification_service import (
    send_notification_email,
)

from app.services.notification_delivery_service import (
    deliver_notification_in_app,
)

from app.services.notification_preference_service import (
    get_notification_preferences,
    is_category_enabled,
)

from app.services.push_notification_service import (
    send_push_notification,
)


def skipped_result(
    channel: str,
    reason: str,
):
    return {
        "channel": channel,
        "delivered": False,
        "reason": reason,
    }


async def deliver_notification_all_channels(
    db: Session,
    notification: Notification,
):
    preference = get_notification_preferences(
        db,
        notification.user_id,
    )

    category_enabled = is_category_enabled(
        preference,
        notification.category,
    )

    user = (
        db.query(User)
        .filter(
            User.id == notification.user_id
        )
        .first()
    )

    if user is None:
        return {
            "notification_id": notification.id,
            "user_id": notification.user_id,
            "delivered_channels": 0,
            "channels": {
                "in_app": skipped_result(
                    "in_app",
                    "user_not_found",
                ),
                "email": skipped_result(
                    "email",
                    "user_not_found",
                ),
                "push": skipped_result(
                    "push",
                    "user_not_found",
                ),
            },
        }

    if category_enabled:
        in_app_result = (
            await deliver_notification_in_app(
                db,
                notification,
            )
        )
        in_app_result["channel"] = "in_app"

    else:
        in_app_result = skipped_result(
            "in_app",
            "notification_category_disabled",
        )

    if not category_enabled:
        email_result = skipped_result(
            "email",
            "notification_category_disabled",
        )

    elif not preference.email_notifications:
        email_result = skipped_result(
            "email",
            "email_notifications_disabled",
        )

    else:
        email_result = (
            await send_notification_email(
                user,
                notification,
            )
        )

    if not category_enabled:
        push_result = skipped_result(
            "push",
            "notification_category_disabled",
        )

    elif not preference.push_notifications:
        push_result = skipped_result(
            "push",
            "push_notifications_disabled",
        )

    else:
        push_result = (
            await send_push_notification(
                user,
                notification,
            )
        )

    channels = {
        "in_app": in_app_result,
        "email": email_result,
        "push": push_result,
    }

    delivered_channels = sum(
        1
        for result in channels.values()
        if result.get("delivered")
    )

    return {
        "notification_id": notification.id,
        "user_id": notification.user_id,
        "delivered_channels": delivered_channels,
        "channels": channels,
    }
