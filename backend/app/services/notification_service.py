from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User

from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
)

from app.services.notification_priority_service import (
    prioritize_notification,
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
        raise ValueError(
            "User not found"
        )

    if not user.is_active:
        raise ValueError(
            "User is not active"
        )

    return user


def get_all_notifications(
    db: Session,
    user_id: int | None = None,
    is_read: bool | None = None,
    notification_type: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    source: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    skip: int = 0,
    limit: int = 50,
):
    query = db.query(Notification)

    if user_id is not None:
        query = query.filter(
            Notification.user_id == user_id
        )

    if is_read is not None:
        query = query.filter(
            Notification.is_read == is_read
        )

    if notification_type:
        query = query.filter(
            Notification.type
            == notification_type
        )

    if priority:
        query = query.filter(
            Notification.priority
            == priority
        )

    if category:
        query = query.filter(
            Notification.category
            == category
        )

    if source:
        query = query.filter(
            Notification.source
            == source
        )

    if start_date:
        query = query.filter(
            Notification.created_at
            >= start_date
        )

    if end_date:
        query = query.filter(
            Notification.created_at
            <= end_date
        )

    return (
        query
        .order_by(
            Notification.created_at.desc(),
            Notification.id.desc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_notification_by_id(
    db: Session,
    notification_id: int,
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id
            == notification_id
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
    target_user_id: int,
):
    validate_notification_user(
        db,
        target_user_id,
    )

    if notification.priority:
        priority = notification.priority

    else:
        result = prioritize_notification(
            title=notification.title,
            message=notification.message,
            notification_type=notification.type,
            category=notification.category,
            source=notification.source,
        )

        priority = result.priority

    new_notification = Notification(
        user_id=target_user_id,
        title=notification.title,
        message=notification.message,
        type=notification.type,
        priority=priority,
        category=notification.category,
        source=notification.source,
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

    update_data = (
        notification_data.model_dump(
            exclude_unset=True
        )
    )

    for key, value in update_data.items():
        setattr(
            notification,
            key,
            value,
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


def mark_notification_as_unread(
    db: Session,
    notification_id: int,
):
    notification = get_notification_by_id(
        db,
        notification_id,
    )

    notification.is_read = False

    db.commit()
    db.refresh(notification)

    return notification


def mark_all_notifications_as_read(
    db: Session,
    user_id: int,
):
    updated_count = (
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
        "message":
            "All notifications marked as read",
        "updated_count": updated_count,
    }


def mark_all_notifications_as_unread(
    db: Session,
    user_id: int,
):
    updated_count = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(True),
        )
        .update(
            {
                Notification.is_read: False
            },
            synchronize_session=False,
        )
    )

    db.commit()

    return {
        "message":
            "All notifications marked as unread",
        "updated_count": updated_count,
    }


def get_unread_notification_count(
    db: Session,
    user_id: int,
):
    count = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .count()
    )

    return {
        "unread_count": count
    }


def get_notification_stats(
    db: Session,
    user_id: int,
):
    query = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id
        )
    )

    total = query.count()

    unread = (
        query.filter(
            Notification.is_read.is_(False)
        )
        .count()
    )

    read = total - unread

    return {
        "total": total,
        "unread": unread,
        "read": read,
        "low": query.filter(
            Notification.priority == "low"
        ).count(),
        "normal": query.filter(
            Notification.priority == "normal"
        ).count(),
        "high": query.filter(
            Notification.priority == "high"
        ).count(),
        "urgent": query.filter(
            Notification.priority == "urgent"
        ).count(),
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
        "message":
            "Notification deleted successfully"
    }
