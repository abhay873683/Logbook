from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
)

from app.services.notification_service import (
    get_all_notifications,
    get_notification_by_id,
    create_notification,
    mark_notification_as_read,
    delete_notification,
)

router = APIRouter()


# ---------------------------------
# Get All Notifications
# ---------------------------------

@router.get(
    "/",
    response_model=list[NotificationResponse],
)
def read_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_notifications(db)


# ---------------------------------
# Get Notification By ID
# ---------------------------------

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
        return get_notification_by_id(
            db,
            notification_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ---------------------------------
# Create Notification
# ---------------------------------

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
    return create_notification(
        db,
        notification,
    )


# ---------------------------------
# Mark Notification As Read
# ---------------------------------

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
        return mark_notification_as_read(
            db,
            notification_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ---------------------------------
# Delete Notification
# ---------------------------------

@router.delete("/{notification_id}")
def delete_existing_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_notification(
            db,
            notification_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )