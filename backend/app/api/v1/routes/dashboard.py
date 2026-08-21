from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.services.dashboard_service import (
    get_dashboard_stats,
    get_recent_tasks,
    get_recent_notifications,
)

router = APIRouter()


# ---------------------------------
# Dashboard Statistics
# ---------------------------------

@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_dashboard_stats(db)


# ---------------------------------
# Recent Tasks
# ---------------------------------

@router.get("/recent-tasks")
def recent_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_recent_tasks(db)


# ---------------------------------
# Recent Notifications
# ---------------------------------

@router.get("/recent-notifications")
def recent_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_recent_notifications(db)