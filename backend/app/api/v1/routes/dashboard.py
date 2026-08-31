from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.services.dashboard_service import (
    get_dashboard_stats,
    get_recent_notifications,
    get_recent_tasks,
)


router = APIRouter()


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_dashboard_stats(
        db,
        current_user.id,
    )


@router.get("/recent-tasks")
def recent_tasks(
    limit: int = Query(
        default=5,
        ge=1,
        le=50,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_recent_tasks(
        db,
        current_user.id,
        limit,
    )


@router.get("/recent-notifications")
def recent_notifications(
    limit: int = Query(
        default=5,
        ge=1,
        le=50,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_recent_notifications(
        db,
        current_user.id,
        limit,
    )