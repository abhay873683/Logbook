from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.event_participant import EventParticipant
from app.models.event_recurrence import EventRecurrence
from app.models.user import User

from app.schemas.event import (
    EventCreate,
    EventUpdate,
    ParticipantCreate,
    RecurrenceCreate,
)


ALLOWED_EVENT_TYPES = {
    "meeting",
    "deadline",
    "reminder",
    "task",
    "project",
    "personal",
}

ALLOWED_FREQUENCIES = {
    "daily",
    "weekly",
    "monthly",
    "yearly",
}


def create_event(
    db: Session,
    user_id: int,
    data: EventCreate,
):
    if data.end_time <= data.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

    if data.event_type not in ALLOWED_EVENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event type",
        )

    event = Event(
        title=data.title,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        location=data.location,
        event_type=data.event_type,
        is_all_day=data.is_all_day,
        created_by=user_id,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def get_events(
    db: Session,
    user_id: int,
):
    return (
        db.query(Event)
        .filter(Event.created_by == user_id)
        .order_by(Event.start_time.asc())
        .all()
    )


def get_event(
    db: Session,
    user_id: int,
    event_id: int,
):
    event = (
        db.query(Event)
        .filter(
            Event.id == event_id,
            Event.created_by == user_id,
        )
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


def update_event(
    db: Session,
    user_id: int,
    event_id: int,
    data: EventUpdate,
):
    event = get_event(
        db,
        user_id,
        event_id,
    )

    values = data.model_dump(exclude_unset=True)

    for key, value in values.items():
        setattr(event, key, value)

    if event.end_time <= event.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

    if event.event_type not in ALLOWED_EVENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event type",
        )

    db.commit()
    db.refresh(event)

    return event


def delete_event(
    db: Session,
    user_id: int,
    event_id: int,
):
    event = get_event(
        db,
        user_id,
        event_id,
    )

    db.query(EventParticipant).filter(
        EventParticipant.event_id == event.id
    ).delete()

    db.query(EventRecurrence).filter(
        EventRecurrence.event_id == event.id
    ).delete()

    db.delete(event)
    db.commit()

    return {
        "message": "Event deleted successfully"
    }


def get_events_by_range(
    db: Session,
    user_id: int,
    start: datetime,
    end: datetime,
):
    if end <= start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Range end must be after range start",
        )

    return (
        db.query(Event)
        .filter(
            Event.created_by == user_id,
            Event.start_time <= end,
            Event.end_time >= start,
        )
        .order_by(Event.start_time.asc())
        .all()
    )


def add_participant(
    db: Session,
    user_id: int,
    event_id: int,
    data: ParticipantCreate,
):
    get_event(db, user_id, event_id)

    participant_user = (
        db.query(User)
        .filter(User.id == data.user_id)
        .first()
    )

    if not participant_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant user not found",
        )

    existing = (
        db.query(EventParticipant)
        .filter(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == data.user_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a participant",
        )

    participant = EventParticipant(
        event_id=event_id,
        user_id=data.user_id,
        role=data.role,
        status="accepted",
    )

    db.add(participant)
    db.commit()
    db.refresh(participant)

    return participant


def get_participants(
    db: Session,
    user_id: int,
    event_id: int,
):
    get_event(db, user_id, event_id)

    return (
        db.query(EventParticipant)
        .filter(EventParticipant.event_id == event_id)
        .all()
    )


def remove_participant(
    db: Session,
    user_id: int,
    event_id: int,
    participant_user_id: int,
):
    get_event(db, user_id, event_id)

    participant = (
        db.query(EventParticipant)
        .filter(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == participant_user_id,
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found",
        )

    db.delete(participant)
    db.commit()

    return {
        "message": "Participant removed successfully"
    }


def set_recurrence(
    db: Session,
    user_id: int,
    event_id: int,
    data: RecurrenceCreate,
):
    event = get_event(
        db,
        user_id,
        event_id,
    )

    if data.frequency not in ALLOWED_FREQUENCIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid recurrence frequency",
        )

    if (
        data.recurrence_end is not None
        and data.recurrence_end <= event.start_time
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurrence end must be after event start time",
        )

    recurrence = (
        db.query(EventRecurrence)
        .filter(EventRecurrence.event_id == event_id)
        .first()
    )

    if recurrence:
        recurrence.frequency = data.frequency
        recurrence.interval = data.interval
        recurrence.days_of_week = data.days_of_week
        recurrence.day_of_month = data.day_of_month
        recurrence.recurrence_end = data.recurrence_end

    else:
        recurrence = EventRecurrence(
            event_id=event_id,
            frequency=data.frequency,
            interval=data.interval,
            days_of_week=data.days_of_week,
            day_of_month=data.day_of_month,
            recurrence_end=data.recurrence_end,
        )

        db.add(recurrence)

    event.is_recurring = True

    db.commit()
    db.refresh(recurrence)

    return recurrence


def get_recurrence(
    db: Session,
    user_id: int,
    event_id: int,
):
    get_event(db, user_id, event_id)

    recurrence = (
        db.query(EventRecurrence)
        .filter(EventRecurrence.event_id == event_id)
        .first()
    )

    if not recurrence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurrence not found",
        )

    return recurrence