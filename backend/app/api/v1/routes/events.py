from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.event import (
    EventCreate,
    EventResponse,
    EventUpdate,
    ParticipantCreate,
    ParticipantResponse,
    RecurrenceCreate,
    RecurrenceResponse,
)

from app.services.event_service import (
    add_participant,
    create_event,
    delete_event,
    get_event,
    get_events,
    get_events_by_range,
    get_participants,
    get_recurrence,
    remove_participant,
    set_recurrence,
    update_event,
)


router = APIRouter()


@router.post(
    "/",
    response_model=EventResponse,
    status_code=201,
)
def add_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_event(
        db,
        current_user.id,
        data,
    )


@router.get(
    "/",
    response_model=list[EventResponse],
)
def read_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_events(
        db,
        current_user.id,
    )


@router.get(
    "/range/",
    response_model=list[EventResponse],
)
def read_events_by_range(
    start: datetime,
    end: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_events_by_range(
        db,
        current_user.id,
        start,
        end,
    )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
)
def read_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_event(
        db,
        current_user.id,
        event_id,
    )


@router.put(
    "/{event_id}",
    response_model=EventResponse,
)
def edit_event(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_event(
        db,
        current_user.id,
        event_id,
        data,
    )


@router.delete("/{event_id}")
def remove_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_event(
        db,
        current_user.id,
        event_id,
    )


@router.post(
    "/{event_id}/participants/",
    response_model=ParticipantResponse,
    status_code=201,
)
def add_event_participant(
    event_id: int,
    data: ParticipantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_participant(
        db,
        current_user.id,
        event_id,
        data,
    )


@router.get(
    "/{event_id}/participants/",
    response_model=list[ParticipantResponse],
)
def read_event_participants(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_participants(
        db,
        current_user.id,
        event_id,
    )


@router.delete(
    "/{event_id}/participants/{participant_user_id}"
)
def delete_event_participant(
    event_id: int,
    participant_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return remove_participant(
        db,
        current_user.id,
        event_id,
        participant_user_id,
    )


@router.post(
    "/{event_id}/recurrence/",
    response_model=RecurrenceResponse,
)
def update_event_recurrence(
    event_id: int,
    data: RecurrenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return set_recurrence(
        db,
        current_user.id,
        event_id,
        data,
    )


@router.get(
    "/{event_id}/recurrence/",
    response_model=RecurrenceResponse,
)
def read_event_recurrence(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_recurrence(
        db,
        current_user.id,
        event_id,
    )