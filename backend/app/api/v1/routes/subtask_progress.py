from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.subtask_progress import (
    SubtaskProgressCreate,
    SubtaskProgressUpdate,
    SubtaskProgressResponse,
)

from app.services.subtask_progress_service import (
    update_subtask_progress,
    get_my_subtask_progress,
    get_subtask_progress_by_id,
)

from app.services.activity_log_service import log_activity

router = APIRouter()


# ---------------------------------
# Update (or Create) Subtask Progress
# ---------------------------------
@router.put(
    "/progress",
    response_model=SubtaskProgressResponse,
)
def update_progress(
    data: SubtaskProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = update_subtask_progress(db, data, current_user.id)

    # ---------------------------------
    # Log this activity
    # ---------------------------------
    log_activity(
        db=db,
        user_id=current_user.id,
        action="Updated Subtask Progress",
        entity_type="Subtask",
        entity_id=data.subtask_id,
        description=f"Progress updated to {data.progress}% (status: {data.status})",
    )

    return result


# ---------------------------------
# Get My Progress for a Subtask
# ---------------------------------
@router.get(
    "/progress/my",
    response_model=SubtaskProgressResponse,
)
def read_my_progress(
    subtask_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = get_my_subtask_progress(db, subtask_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Progress not found")
    return result


# ---------------------------------
# Get All Progress by Subtask ID
# ---------------------------------
@router.get(
    "/{subtask_id}/progress",
    response_model=list[SubtaskProgressResponse],
)
def read_progress_by_subtask(
    subtask_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_subtask_progress_by_id(db, subtask_id)