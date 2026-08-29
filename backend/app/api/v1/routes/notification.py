from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.notification import (
    ALLOWED_NOTIFICATION_TYPES,
    ALLOWED_PRIORITIES,
    NotificationCreate,
    NotificationPriorityPreviewRequest,
    NotificationPriorityPreviewResponse,
    NotificationResponse,
    NotificationStatsResponse,
    NotificationUpdate,
)

from app.services.notification_delivery_service import (
    deliver_notification_in_app,
)

from app.services.notification_priority_service import (
    prioritize_notification,
)

from app.services.notification_service import (
    create_notification,
    delete_notification,
    get_all_notifications,
    get_notification_by_id,
    get_notification_stats,
    get_unread_notification_count,
    mark_all_notifications_as_read,
    mark_all_notifications_as_unread,
    mark_notification_as_read,
    mark_notification_as_unread,
    update_notification,
)


router = APIRouter()


PRIVILEGED_ROLES = {
    "admin",
    "manager",
    "superadmin",
    "super_admin",
}


def is_privileged(
    user: User,
):
    return (
        str(user.role).strip().lower()
        in PRIVILEGED_ROLES
    )


def require_owner(
    db: Session,
    notification_id: int,
    current_user: User,
):
    notification = (
        get_notification_by_id(
            db,
            notification_id,
        )
    )

    if (
        notification is None
        or notification.user_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    return notification


@router.get(
    "/",
    response_model=list[NotificationResponse],
)
def read_notifications(
    is_read: bool | None = Query(
        default=None
    ),
    type: str | None = Query(
        default=None
    ),
    priority: str | None = Query(
        default=None
    ),
    category: str | None = Query(
        default=None
    ),
    source: str | None = Query(
        default=None
    ),
    start_date: datetime | None = Query(
        default=None
    ),
    end_date: datetime | None = Query(
        default=None
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    notification_type = (
        type.strip().lower()
        if type
        else None
    )

    normalized_priority = (
        priority.strip().lower()
        if priority
        else None
    )

    if (
        notification_type
        and notification_type
        not in ALLOWED_NOTIFICATION_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid notification type",
        )

    if (
        normalized_priority
        and normalized_priority
        not in ALLOWED_PRIORITIES
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid notification priority",
        )

    if (
        start_date
        and end_date
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "start_date cannot be "
                "after end_date"
            ),
        )

    return get_all_notifications(
        db=db,
        user_id=current_user.id,
        is_read=is_read,
        notification_type=(
            notification_type
        ),
        priority=normalized_priority,
        category=category,
        source=source,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/stats/",
    response_model=NotificationStatsResponse,
)
def read_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_notification_stats(
        db,
        current_user.id,
    )


@router.get(
    "/unread/count/",
)
def read_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return {
        "unread_count": (
            get_unread_notification_count(
                db,
                current_user.id,
            )
        )
    }


@router.put(
    "/mark-all-read",
)
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    updated_count = (
        mark_all_notifications_as_read(
            db,
            current_user.id,
        )
    )

    return {
        "message": (
            "All notifications marked as read"
        ),
        "updated_count": updated_count,
    }


@router.put(
    "/mark-all-unread",
)
def mark_all_unread(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    updated_count = (
        mark_all_notifications_as_unread(
            db,
            current_user.id,
        )
    )

    return {
        "message": (
            "All notifications marked as unread"
        ),
        "updated_count": updated_count,
    }


@router.post(
    "/priority-preview/",
    response_model=(
        NotificationPriorityPreviewResponse
    ),
)
def preview_priority(
    data: NotificationPriorityPreviewRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    result = prioritize_notification(
        title=data.title,
        message=data.message,
        notification_type=data.type,
        category=data.category,
        source=data.source,
    )

    return {
        "priority": result.priority,
        "score": result.score,
        "reasons": result.reasons,
    }


@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    target_user_id = (
        data.user_id
        if data.user_id is not None
        else current_user.id
    )

    if (
        target_user_id != current_user.id
        and not is_privileged(
            current_user
        )
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "You cannot create a "
                "notification for another user"
            ),
        )

    try:
        notification = create_notification(
            db,
            data,
            target_user_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    await deliver_notification_in_app(
        db,
        notification,
    )

    return notification


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return require_owner(
        db,
        notification_id,
        current_user,
    )


@router.put(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def edit_notification(
    notification_id: int,
    data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    notification = require_owner(
        db,
        notification_id,
        current_user,
    )

    try:
        return update_notification(
            db,
            notification,
            data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    notification = require_owner(
        db,
        notification_id,
        current_user,
    )

    return mark_notification_as_read(
        db,
        notification,
    )


@router.put(
    "/{notification_id}/unread",
    response_model=NotificationResponse,
)
def mark_unread(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    notification = require_owner(
        db,
        notification_id,
        current_user,
    )

    return mark_notification_as_unread(
        db,
        notification,
    )


@router.post(
    "/{notification_id}/deliver/",
)
async def redeliver_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    notification = require_owner(
        db,
        notification_id,
        current_user,
    )

    return await deliver_notification_in_app(
        db,
        notification,
    )


@router.delete(
    "/{notification_id}",
)
def remove_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    notification = require_owner(
        db,
        notification_id,
        current_user,
    )

    delete_notification(
        db,
        notification,
    )

    return {
        "message": (
            "Notification deleted successfully"
        )
    }
