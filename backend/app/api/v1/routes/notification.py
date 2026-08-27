from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
)

from app.services.notification_service import (
    get_all_notifications,
    get_notification_by_id,
    create_notification,
    update_notification,
    mark_notification_as_read,
    mark_notification_as_unread,
    mark_all_notifications_as_read,
    get_unread_notification_count,
    delete_notification,
)


router = APIRouter()


# =========================================================
# GET CURRENT USER NOTIFICATIONS
# =========================================================

@router.get(
    "/",
    response_model=list[NotificationResponse],
)
def read_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_notifications(
        db,
        current_user.id,
    )


# =========================================================
# MARK ALL AS READ
#
# IMPORTANT:
# Static routes must remain before /{notification_id}
# =========================================================

@router.put("/mark-all-read")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mark_all_notifications_as_read(
        db,
        current_user.id,
    )


# =========================================================
# DAY 44 - GET UNREAD NOTIFICATION COUNT
#
# IMPORTANT:
# Keep before /{notification_id}
# =========================================================

@router.get("/unread/count/")
def unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_unread_notification_count(
        db,
        current_user.id,
    )


# =========================================================
# CREATE NOTIFICATION
# =========================================================

@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=201,
)
def create_new_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_notification(
            db,
            notification,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# =========================================================
# GET NOTIFICATION BY ID
# =========================================================

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        notification = get_notification_by_id(
            db,
            notification_id,
        )

        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail="Notification not found",
            )

        return notification

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# =========================================================
# UPDATE NOTIFICATION
# =========================================================

@router.put(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def update_existing_notification(
    notification_id: int,
    notification: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        existing = get_notification_by_id(
            db,
            notification_id,
        )

        if existing.user_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail="Notification not found",
            )

        return update_notification(
            db,
            notification_id,
            notification,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# =========================================================
# MARK ONE NOTIFICATION AS READ
# =========================================================

@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def read_notification_update(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        notification = get_notification_by_id(
            db,
            notification_id,
        )

        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail="Notification not found",
            )

        return mark_notification_as_read(
            db,
            notification_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# =========================================================
# DAY 44 - MARK ONE NOTIFICATION AS UNREAD
# =========================================================

@router.put(
    "/{notification_id}/unread",
    response_model=NotificationResponse,
)
def unread_notification_update(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        notification = get_notification_by_id(
            db,
            notification_id,
        )

        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail="Notification not found",
            )

        return mark_notification_as_unread(
            db,
            notification_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# =========================================================
# DELETE NOTIFICATION
# =========================================================

@router.delete("/{notification_id}")
def delete_existing_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        notification = get_notification_by_id(
            db,
            notification_id,
        )

        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail="Notification not found",
            )

        return delete_notification(
            db,
            notification_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )