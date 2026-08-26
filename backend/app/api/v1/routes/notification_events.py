from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.notification_preference import (
    NotificationPreferenceUpdate,
    NotificationPreferenceResponse,
)

from app.schemas.event_log import (
    EventLogCreate,
    EventLogResponse,
)

from app.services.notification_preference_service import (
    get_notification_preferences,
    update_notification_preferences,
)

from app.services.event_log_service import (
    create_event_log,
    get_event_logs,
)


router = APIRouter()


# =========================================================
# NOTIFICATION PREFERENCES
# =========================================================

@router.get(
    "/notification/preferences/",
    response_model=NotificationPreferenceResponse,
)
def read_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_notification_preferences(
        db,
        current_user.id,
    )


@router.put(
    "/notification/preferences/",
    response_model=NotificationPreferenceResponse,
)
def edit_preferences(
    data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_notification_preferences(
        db,
        current_user.id,
        data,
    )


# =========================================================
# EVENT LOGS
# =========================================================

@router.post(
    "/events/log",
    response_model=EventLogResponse,
    status_code=201,
)
def log_event(
    data: EventLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_event_log(
        db,
        current_user.id,
        data,
    )


@router.get(
    "/events/",
    response_model=list[EventLogResponse],
)
def read_event_logs(
    limit: int = Query(
        50,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_event_logs(
        db,
        limit,
    )