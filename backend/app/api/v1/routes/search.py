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
from app.schemas.search import SearchResponse
from app.services.search_service import search_all


router = APIRouter()


@router.get(
    "/",
    response_model=SearchResponse,
)
def advanced_search(
    q: str = Query(
        ...,
        min_length=1,
        max_length=200,
    ),
    resource_type: str = Query(
        "all",
    ),
    skip: int = Query(
        0,
        ge=0,
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return search_all(
            db=db,
            user_id=current_user.id,
            role=current_user.role,
            query=q,
            resource_type=resource_type,
            skip=skip,
            limit=limit,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
