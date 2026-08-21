from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


# ---------------------------------
# Get All Notifications
# ---------------------------------

def get_all_notifications(db: Session):
    return db.query(Notification).all()


# ---------------------------------
# Get Notification By ID
# ---------------------------------

def get_notification_by_id(
    db: Session,
    notification_id: int,
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise ValueError("Notification not found")

    return notification


# ---------------------------------
# Create Notification
# ---------------------------------

def create_notification(
    db: Session,
    notification: NotificationCreate,
):
    new_notification = Notification(
        user_id=notification.user_id,
        title=notification.title,
        message=notification.message,
        type=notification.type,
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification


# ---------------------------------
# Mark Notification As Read
# ---------------------------------

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


# ---------------------------------
# Delete Notification
# ---------------------------------

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
        "message": "Notification deleted successfully"
    }