from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.activity_log import (
    ActivityLogCreate,
    ActivityLogResponse,
)

from app.services.activity_log_service import (
    create_activity_log,
    get_activity_log_by_id,
    get_activity_logs,
    get_all_activity_logs,
    delete_activity_log,
)


router = APIRouter()


@router.post(
    "/",
    response_model=ActivityLogResponse,
    status_code=201,
)
def create_new_activity_log(
    activity: ActivityLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if activity.user_id is None:
            activity.user_id = current_user.id

        return create_activity_log(
            db,
            activity,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get(
    "/my",
    response_model=list[ActivityLogResponse],
)
def read_my_activity_logs(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_activity_logs(
        db,
        current_user.id,
        limit,
    )


@router.get(
    "/all",
    response_model=list[ActivityLogResponse],
)
def read_all_activity_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_activity_logs(
        db,
        limit,
    )


@router.get(
    "/{activity_id}",
    response_model=ActivityLogResponse,
)
def read_activity_log(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_activity_log_by_id(
            db,
            activity_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.delete("/{activity_id}")
def delete_existing_activity_log(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_activity_log(
            db,
            activity_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )