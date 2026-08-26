from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User

from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
)


def validate_notification_user(
    db: Session,
    user_id: int,
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("User is not active")

    return user


def get_all_notifications(
    db: Session,
    user_id: int | None = None,
):
    query = db.query(Notification)

    if user_id is not None:
        query = query.filter(
            Notification.user_id == user_id
        )

    return (
        query
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_notification_by_id(
    db: Session,
    notification_id: int,
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if not notification:
        raise ValueError(
            "Notification not found"
        )

    return notification


def create_notification(
    db: Session,
    notification: NotificationCreate,
):
    validate_notification_user(
        db,
        notification.user_id,
    )

    new_notification = Notification(
        user_id=notification.user_id,
        title=notification.title,
        message=notification.message,
        type=notification.type,
        data=notification.data,
        is_read=False,
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification


def update_notification(
    db: Session,
    notification_id: int,
    notification_data: NotificationUpdate,
):
    notification = get_notification_by_id(
        db,
        notification_id,
    )

    update_data = notification_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            notification,
            key,
            value
        )

    db.commit()
    db.refresh(notification)

    return notification


def mark_notification_as_read(
    db: Session,
    notification_id: int,
):
    notification = get_notification_by_id(
        db,
        notification_id,
    )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification


def mark_all_notifications_as_read(
    db: Session,
    user_id: int,
):
    (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .update(
            {
                Notification.is_read: True
            },
            synchronize_session=False,
        )
    )

    db.commit()

    return {
        "message": (
            "All notifications marked as read"
        )
    }


def delete_notification(
    db: Session,
    notification_id: int,
):
    notification = get_notification_by_id(
        db,
        notification_id,
    )

    db.delete(notification)
    db.commit()

    return {
        "message": (
            "Notification deleted successfully"
        )
    }