from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.file_type import FileTypeResponse

from app.services.file_type_service import get_all_file_types

router = APIRouter()


# ---------------------------------
# Get All File Types
# ---------------------------------
@router.get(
    "/",
    response_model=list[FileTypeResponse],
)
def list_file_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_file_types(db)