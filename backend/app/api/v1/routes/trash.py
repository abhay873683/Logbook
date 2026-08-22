from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.trash import TrashItem

from app.services.trash_service import (
    move_to_trash,
    get_trash_files,
)

from app.services.activity_log_service import log_activity

router = APIRouter()


# ---------------------------------
# Move File to Trash
# ---------------------------------
@router.delete("/{file_id}")
def move_file_to_trash(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = move_to_trash(
        db=db,
        file_id=file_id,
        user_id=current_user.id,
        role=current_user.role,
    )

    # ---------------------------------
    # Log this activity
    # ---------------------------------
    log_activity(
        db=db,
        user_id=current_user.id,
        action="Moved File to Trash",
        entity_type="File",
        entity_id=file_id,
        description="File moved to trash",
    )

    return result


# ---------------------------------
# List All Trash Files
# ---------------------------------
@router.get(
    "/",
    response_model=list[TrashItem],
)
def list_trash(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    files = get_trash_files(
        db=db,
        user_id=current_user.id,
        role=current_user.role,
    )

    return [
        TrashItem(
            file_id=f.id,
            file_name=f.file_name,
            deleted_at=f.deleted_at,
            deleted_by=f.deleted_by,
            file_type=f.file_type,
            size=f.file_size,
        )
        for f in files
    ]