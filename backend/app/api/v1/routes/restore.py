from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.file_restore import (
    FileRestore,
    FileRestoreResponse,
)

from app.services.restore_service import restore_file

from app.services.activity_log_service import log_activity

router = APIRouter()


# ---------------------------------
# Restore File From Trash
# ---------------------------------
@router.post(
    "/",
    response_model=FileRestoreResponse,
)
def restore_file_route(
    data: FileRestore,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = restore_file(
        db=db,
        file_id=data.file_id,
        user_id=current_user.id,
        role=current_user.role,
    )

    # ---------------------------------
    # Log this activity
    # ---------------------------------
    log_activity(
        db=db,
        user_id=current_user.id,
        action="Restored File",
        entity_type="File",
        entity_id=data.file_id,
        description=f"Restored file: {result['original_name']}",
    )

    return result