from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.revoke_share import (
    RevokeShareRequest,
    RevokeShareResponse,
)

from app.services.revoke_share_service import revoke_share

router = APIRouter()


# ---------------------------------
# Revoke a File Share
# ---------------------------------
@router.post(
    "/revoke",
    response_model=RevokeShareResponse,
)
def revoke_share_api(
    payload: RevokeShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return revoke_share(
            db=db,
            data=payload,
            user_id=current_user.id,
            role=current_user.role,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))