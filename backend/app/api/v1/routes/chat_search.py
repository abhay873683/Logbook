from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.chat import MessageResponse

from app.services.chat_search_service import (
    search_messages,
)


router = APIRouter()


@router.get(
    "/",
    response_model=list[MessageResponse],
)
def search_chat_messages(
    q: str = Query(
        ...,
        min_length=1,
        max_length=200,
    ),
    chat_type: str | None = Query(
        None
    ),
    chat_id: int | None = Query(
        None,
        ge=1,
    ),
    skip: int = Query(
        0,
        ge=0,
    ),
    limit: int = Query(
        50,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return search_messages(
            db=db,
            user_id=current_user.id,
            query=q,
            chat_type=chat_type,
            chat_id=chat_id,
            skip=skip,
            limit=limit,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )
