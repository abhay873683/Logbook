import calendar

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.reminder import Reminder

from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
)

from app.services.notification_channel_service import (
    deliver_notification_all_channels,
)


def utc_now():
    return datetime.now(timezone.utc)


def ensure_aware(
    value: datetime,
):
    if value.tzinfo is None:
        raise ValueError(
            "Reminder datetime must include timezone information"
        )

    return value


def get_reminders(
    db: Session,
    user_id: int,
):
    return (
        db.query(Reminder)
        .filter(
            Reminder.user_id == user_id
        )
        .order_by(
            Reminder.remind_at.asc()
        )
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
        raise ValueError(
            "Reminder not found"
        )

    return reminder


def create_reminder(
    db: Session,
    user_id: int,
    data: ReminderCreate,
):
    remind_at = ensure_aware(
        data.remind_at
    )

    if remind_at <= utc_now():
        raise ValueError(
            "Reminder time must be in the future"
        )

    reminder = Reminder(
        user_id=user_id,
        title=data.title,
        description=data.description,
        remind_at=remind_at,
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

    if (
        "remind_at" in update_data
        and update_data["remind_at"] is not None
    ):
        remind_at = ensure_aware(
            update_data["remind_at"]
        )

        if remind_at <= utc_now():
            raise ValueError(
                "Reminder time must be in the future"
            )

        update_data["remind_at"] = remind_at

    for key, value in update_data.items():
        setattr(
            reminder,
            key,
            value,
        )

    if (
        reminder.is_recurring
        and not reminder.recurrence
    ):
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
        "message": (
            "Reminder deleted successfully"
        )
    }


def get_upcoming_reminders(
    db: Session,
    user_id: int,
):
    now = utc_now()

    return (
        db.query(Reminder)
        .filter(
            Reminder.user_id == user_id,
            Reminder.remind_at >= now,
            Reminder.is_completed.is_(False),
        )
        .order_by(
            Reminder.remind_at.asc()
        )
        .all()
    )


def get_due_reminders(
    db: Session,
    user_id: int | None = None,
    limit: int = 100,
):
    query = (
        db.query(Reminder)
        .filter(
            Reminder.remind_at <= utc_now(),
            Reminder.is_completed.is_(False),
        )
    )

    if user_id is not None:
        query = query.filter(
            Reminder.user_id == user_id
        )

    return (
        query
        .order_by(
            Reminder.remind_at.asc()
        )
        .limit(limit)
        .all()
    )


def add_month(
    value: datetime,
):
    if value.month == 12:
        year = value.year + 1
        month = 1
    else:
        year = value.year
        month = value.month + 1

    max_day = calendar.monthrange(
        year,
        month,
    )[1]

    day = min(
        value.day,
        max_day,
    )

    return value.replace(
        year=year,
        month=month,
        day=day,
    )


def calculate_next_reminder_time(
    remind_at: datetime,
    recurrence: str,
):
    recurrence = recurrence.lower()

    if recurrence == "daily":
        next_time = (
            remind_at
            + timedelta(days=1)
        )

    elif recurrence == "weekly":
        next_time = (
            remind_at
            + timedelta(weeks=1)
        )

    elif recurrence == "monthly":
        next_time = add_month(
            remind_at
        )

    else:
        raise ValueError(
            "Unsupported recurrence type"
        )

    now = utc_now()

    while next_time <= now:
        if recurrence == "daily":
            next_time += timedelta(
                days=1
            )

        elif recurrence == "weekly":
            next_time += timedelta(
                weeks=1
            )

        elif recurrence == "monthly":
            next_time = add_month(
                next_time
            )

    return next_time


def create_reminder_notification(
    db: Session,
    reminder: Reminder,
):
    message = (
        reminder.description
        or (
            f"Reminder due: "
            f"{reminder.title}"
        )
    )

    notification = Notification(
        user_id=reminder.user_id,
        title=(
            f"Reminder: "
            f"{reminder.title}"
        ),
        message=message,
        type="info",
        priority="high",
        category="deadline",
        source="reminder",
        data={
            "reminder_id": reminder.id,
            "is_recurring": (
                reminder.is_recurring
            ),
            "recurrence": (
                reminder.recurrence
            ),
        },
        is_read=False,
    )

    db.add(notification)

    return notification


async def process_due_reminders(
    db: Session,
    user_id: int | None = None,
    limit: int = 100,
):
    reminders = get_due_reminders(
        db,
        user_id=user_id,
        limit=limit,
    )

    result = {
        "processed": 0,
        "notifications_created": 0,
        "delivered": 0,
        "recurring_rescheduled": 0,
        "completed": 0,
        "failed": 0,
    }

    for reminder in reminders:
        try:
            notification = (
                create_reminder_notification(
                    db,
                    reminder,
                )
            )

            if (
                reminder.is_recurring
                and reminder.recurrence
            ):
                reminder.remind_at = (
                    calculate_next_reminder_time(
                        reminder.remind_at,
                        reminder.recurrence,
                    )
                )

                result[
                    "recurring_rescheduled"
                ] += 1

            else:
                reminder.is_completed = True
                result["completed"] += 1

            db.commit()
            db.refresh(notification)
            db.refresh(reminder)

            result[
                "notifications_created"
            ] += 1

            delivery = (
                await deliver_notification_all_channels(
                    db,
                    notification,
                )
            )

            if (
                delivery.get(
                    "delivered_channels",
                    0,
                )
                > 0
            ):
                result["delivered"] += 1

            result["processed"] += 1

        except Exception:
            db.rollback()
            result["failed"] += 1

    return result


def snooze_reminder(
    db: Session,
    reminder_id: int,
    user_id: int,
    minutes: int,
):
    reminder = get_reminder_by_id(
        db,
        reminder_id,
        user_id,
    )

    if reminder.is_completed:
        raise ValueError(
            "Completed reminder cannot be snoozed"
        )

    reminder.remind_at = (
        utc_now()
        + timedelta(minutes=minutes)
    )

    db.commit()
    db.refresh(reminder)

    return reminder


def complete_reminder(
    db: Session,
    reminder_id: int,
    user_id: int,
):
    reminder = get_reminder_by_id(
        db,
        reminder_id,
        user_id,
    )

    reminder.is_completed = True

    db.commit()
    db.refresh(reminder)

    return reminder


def get_reminder_stats(
    db: Session,
    user_id: int,
):
    now = utc_now()

    base = db.query(Reminder).filter(
        Reminder.user_id == user_id
    )

    total = base.count()

    completed = (
        base.filter(
            Reminder.is_completed.is_(True)
        )
        .count()
    )

    due = (
        base.filter(
            Reminder.is_completed.is_(False),
            Reminder.remind_at <= now,
        )
        .count()
    )

    scheduled = (
        base.filter(
            Reminder.is_completed.is_(False),
            Reminder.remind_at > now,
        )
        .count()
    )

    recurring = (
        base.filter(
            Reminder.is_recurring.is_(True),
            Reminder.is_completed.is_(False),
        )
        .count()
    )

    return {
        "total": total,
        "scheduled": scheduled,
        "due": due,
        "recurring": recurring,
        "completed": completed,
    }
