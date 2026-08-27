from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
)

from app.services.reminder_service import (
    create_reminder,
    get_reminders,
    get_reminder_by_id,
    update_reminder,
    delete_reminder,
    get_upcoming_reminders,
)


router = APIRouter()


@router.get(
    "/",
    response_model=list[ReminderResponse],
)
def read_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_reminders(
        db,
        current_user.id,
    )


# IMPORTANT:
# Keep /upcoming/ before /{reminder_id}
@router.get(
    "/upcoming/",
    response_model=list[ReminderResponse],
)
def read_upcoming_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_upcoming_reminders(
        db,
        current_user.id,
    )


@router.post(
    "/",
    response_model=ReminderResponse,
    status_code=201,
)
def add_reminder(
    data: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_reminder(
            db,
            current_user.id,
            data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get(
    "/{reminder_id}",
    response_model=ReminderResponse,
)
def read_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_reminder_by_id(
            db,
            reminder_id,
            current_user.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.put(
    "/{reminder_id}",
    response_model=ReminderResponse,
)
def edit_reminder(
    reminder_id: int,
    data: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_reminder(
            db,
            reminder_id,
            current_user.id,
            data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete("/{reminder_id}")
def remove_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_reminder(
            db,
            reminder_id,
            current_user.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )