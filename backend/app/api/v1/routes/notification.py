from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
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
    current_user: User,
):
    role = (
        current_user.role or "user"
    ).lower()

    return role in PRIVILEGED_ROLES


def require_owner(
    notification,
    current_user: User,
):
    if (
        notification.user_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )


@router.get(
    "/",
    response_model=list[
        NotificationResponse
    ],
)
def read_notifications(
    is_read: bool | None = None,
    type: str | None = Query(
        default=None,
    ),
    priority: str | None = None,
    category: str | None = None,
    source: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
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
    if (
        type
        and type not in
        ALLOWED_NOTIFICATION_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid notification type",
        )

    if (
        priority
        and priority not in
        ALLOWED_PRIORITIES
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
        notification_type=type,
        priority=priority,
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
def notification_stats(
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
def unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_unread_notification_count(
        db,
        current_user.id,
    )


@router.put(
    "/mark-all-read",
)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return mark_all_notifications_as_read(
        db,
        current_user.id,
    )


@router.put(
    "/mark-all-unread",
)
def mark_all_as_unread(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        mark_all_notifications_as_unread(
            db,
            current_user.id,
        )
    )


@router.post(
    "/priority-preview/",
    response_model=(
        NotificationPriorityPreviewResponse
    ),
)
def priority_preview(
    payload:
        NotificationPriorityPreviewRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    result = prioritize_notification(
        title=payload.title,
        message=payload.message,
        notification_type=payload.type,
        category=payload.category,
        source=payload.source,
    )

    return {
        "priority": result.priority,
        "score": result.score,
        "reasons": result.reasons,
    }


@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=201,
)
def create_new_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    requested_user_id = (
        notification.user_id
    )

    if requested_user_id is None:
        target_user_id = current_user.id

    elif (
        requested_user_id
        == current_user.id
    ):
        target_user_id = current_user.id

    elif is_privileged(current_user):
        target_user_id = requested_user_id

    else:
        raise HTTPException(
            status_code=403,
            detail=(
                "You cannot create "
                "notifications for another user"
            ),
        )

    try:
        return create_notification(
            db=db,
            notification=notification,
            target_user_id=target_user_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


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
    try:
        notification = (
            get_notification_by_id(
                db,
                notification_id,
            )
        )

        require_owner(
            notification,
            current_user,
        )

        return notification

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.put(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def update_existing_notification(
    notification_id: int,
    notification: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        existing = (
            get_notification_by_id(
                db,
                notification_id,
            )
        )

        require_owner(
            existing,
            current_user,
        )

        return update_notification(
            db,
            notification_id,
            notification,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def read_notification_update(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        notification = (
            get_notification_by_id(
                db,
                notification_id,
            )
        )

        require_owner(
            notification,
            current_user,
        )

        return mark_notification_as_read(
            db,
            notification_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.put(
    "/{notification_id}/unread",
    response_model=NotificationResponse,
)
def unread_notification_update(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        notification = (
            get_notification_by_id(
                db,
                notification_id,
            )
        )

        require_owner(
            notification,
            current_user,
        )

        return (
            mark_notification_as_unread(
                db,
                notification_id,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.delete(
    "/{notification_id}",
)
def delete_existing_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        notification = (
            get_notification_by_id(
                db,
                notification_id,
            )
        )

        require_owner(
            notification,
            current_user,
        )

        return delete_notification(
            db,
            notification_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
