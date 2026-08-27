from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.reminder import Reminder
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
)


def get_reminders(
    db: Session,
    user_id: int,
):
    return (
        db.query(Reminder)
        .filter(Reminder.user_id == user_id)
        .order_by(Reminder.remind_at.asc())
        .all()
    )


def get_reminder_by_id(
    db: Session,
    reminder_id: int,
    user_id: int,
):
    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id,
        )
        .first()
    )

    if not reminder:
        raise ValueError("Reminder not found")

    return reminder


def create_reminder(
    db: Session,
    user_id: int,
    data: ReminderCreate,
):
    if data.remind_at <= datetime.now(timezone.utc):
        raise ValueError(
            "Reminder time must be in the future"
        )

    reminder = Reminder(
        user_id=user_id,
        title=data.title,
        description=data.description,
        remind_at=data.remind_at,
        is_recurring=data.is_recurring,
        recurrence=data.recurrence,
        is_completed=False,
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return reminder


def update_reminder(
    db: Session,
    reminder_id: int,
    user_id: int,
    data: ReminderUpdate,
):
    reminder = get_reminder_by_id(
        db,
        reminder_id,
        user_id,
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "remind_at" in update_data:
        if update_data["remind_at"] <= datetime.now(
            timezone.utc
        ):
            raise ValueError(
                "Reminder time must be in the future"
            )

    for key, value in update_data.items():
        setattr(reminder, key, value)

    if reminder.is_recurring and not reminder.recurrence:
        raise ValueError(
            "recurrence is required when is_recurring is true"
        )

    if not reminder.is_recurring:
        reminder.recurrence = None

    db.commit()
    db.refresh(reminder)

    return reminder


def delete_reminder(
    db: Session,
    reminder_id: int,
    user_id: int,
):
    reminder = get_reminder_by_id(
        db,
        reminder_id,
        user_id,
    )

    db.delete(reminder)
    db.commit()

    return {
        "message": "Reminder deleted successfully"
    }


def get_upcoming_reminders(
    db: Session,
    user_id: int,
):
    now = datetime.now(timezone.utc)

    return (
        db.query(Reminder)
        .filter(
            Reminder.user_id == user_id,
            Reminder.remind_at >= now,
            Reminder.is_completed.is_(False),
        )
        .order_by(Reminder.remind_at.asc())
        .all()
    )