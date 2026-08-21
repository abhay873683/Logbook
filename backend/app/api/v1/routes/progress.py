from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.task_progress import (
    TaskProgressCreate,
    TaskProgressUpdate,
    TaskProgressResponse,
)

from app.services.progress_service import (
    get_all_progress,
    get_progress_by_id,
    create_progress,
    update_progress,
    delete_progress,
)

router = APIRouter()


# ---------------------------------
# Get All Progress
# ---------------------------------
@router.get(
    "/",
    response_model=list[TaskProgressResponse],
)
def read_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_progress(db)


# ---------------------------------
# Get Progress By ID
# ---------------------------------
@router.get(
    "/{progress_id}",
    response_model=TaskProgressResponse,
)
def read_progress_by_id(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_progress_by_id(
            db,
            progress_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ---------------------------------
# Create Progress
# ---------------------------------
@router.post(
    "/",
    response_model=TaskProgressResponse,
    status_code=201,
)
def create_new_progress(
    progress: TaskProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_progress(
        db,
        progress,
        current_user.id,
    )


# ---------------------------------
# Update Progress
# ---------------------------------
@router.put(
    "/{progress_id}",
    response_model=TaskProgressResponse,
)
def update_existing_progress(
    progress_id: int,
    progress: TaskProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_progress(
            db,
            progress_id,
            progress,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ---------------------------------
# Delete Progress
# ---------------------------------
@router.delete("/{progress_id}")
def delete_existing_progress(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_progress(
            db,
            progress_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )