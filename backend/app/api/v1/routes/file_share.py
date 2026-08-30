from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.file_share import (
    FileShareCreate,
    FileShareResponse,
)

from app.services.file_share_service import share_file

router = APIRouter()


# ---------------------------------
# Share a File
# ---------------------------------
@router.post(
    "/share",
    response_model=FileShareResponse,
)
def share_file_api(
    payload: FileShareCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return share_file(
        db=db,
        data=payload,
        user_id=current_user.id,
        role=current_user.role,
    )