from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.activity_log import ActivityLogResponse

from app.services.activity_log_service import (
    get_activity_logs,
    get_all_activity_logs,
)

router = APIRouter()


# ---------------------------------
# Get My Activity Logs
# ---------------------------------
@router.get(
    "/my",
    response_model=list[ActivityLogResponse],
)
def read_my_activity_logs(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_activity_logs(db, current_user.id, limit)


# ---------------------------------
# Get All Activity Logs (Admin Only)
# ---------------------------------
@router.get(
    "/all",
    response_model=list[ActivityLogResponse],
)
def read_all_activity_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_activity_logs(db, limit)