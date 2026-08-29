from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.core.dependencies import (
    get_current_user,
)

from app.core.reminder_scheduler import (
    start_reminder_scheduler,
    stop_reminder_scheduler,
)

from app.models.user import User

from app.schemas.reminder import (
    ReminderCreate,
    ReminderProcessResult,
    ReminderResponse,
    ReminderSnoozeRequest,
    ReminderStatsResponse,
    ReminderUpdate,
)

from app.services.reminder_service import (
    complete_reminder,
    create_reminder,
    delete_reminder,
    get_due_reminders,
    get_reminder_by_id,
    get_reminder_stats,
    get_reminders,
    get_upcoming_reminders,
    process_due_reminders,
    snooze_reminder,
    update_reminder,
)


router = APIRouter()


@router.on_event("startup")
async def reminder_scheduler_startup():
    start_reminder_scheduler()


@router.on_event("shutdown")
async def reminder_scheduler_shutdown():
    await stop_reminder_scheduler()


@router.get(
    "/",
    response_model=list[ReminderResponse],
)
def read_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_reminders(
        db,
        current_user.id,
    )


@router.get(
    "/upcoming/",
    response_model=list[ReminderResponse],
)
def read_upcoming_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_upcoming_reminders(
        db,
        current_user.id,
    )


@router.get(
    "/due/",
    response_model=list[ReminderResponse],
)
def read_due_reminders(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_due_reminders(
        db,
        user_id=current_user.id,
        limit=limit,
    )


@router.get(
    "/stats/",
    response_model=ReminderStatsResponse,
)
def read_reminder_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_reminder_stats(
        db,
        current_user.id,
    )


@router.post(
    "/process-due/",
    response_model=ReminderProcessResult,
)
async def process_user_due_reminders(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return await process_due_reminders(
        db,
        user_id=current_user.id,
        limit=limit,
    )


@router.post(
    "/",
    response_model=ReminderResponse,
    status_code=201,
)
def add_reminder(
    data: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return create_reminder(
            db,
            current_user.id,
            data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/{reminder_id}",
    response_model=ReminderResponse,
)
def read_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return get_reminder_by_id(
            db,
            reminder_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.put(
    "/{reminder_id}",
    response_model=ReminderResponse,
)
def edit_reminder(
    reminder_id: int,
    data: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return update_reminder(
            db,
            reminder_id,
            current_user.id,
            data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/{reminder_id}/snooze/",
    response_model=ReminderResponse,
)
def snooze_user_reminder(
    reminder_id: int,
    data: ReminderSnoozeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return snooze_reminder(
            db,
            reminder_id,
            current_user.id,
            data.minutes,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/{reminder_id}/complete/",
    response_model=ReminderResponse,
)
def complete_user_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return complete_reminder(
            db,
            reminder_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.delete(
    "/{reminder_id}"
)
def remove_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return delete_reminder(
            db,
            reminder_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
