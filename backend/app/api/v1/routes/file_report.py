from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.services.file_report_service import get_file_report

router = APIRouter()


# ---------------------------------
# Get File Report
# ---------------------------------
@router.get("/report")
def file_report_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_file_report(
        db=db,
        user_id=current_user.id,
        role=current_user.role,
    )