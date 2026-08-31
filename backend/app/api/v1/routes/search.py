from datetime import datetime

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
    project_id: int | None = Query(
        None,
        ge=1,
    ),
    project_status: str | None = Query(
        None,
    ),
    task_status: str | None = Query(
        None,
    ),
    priority: str | None = Query(
        None,
    ),
    file_type: str | None = Query(
        None,
    ),
    created_from: datetime | None = Query(
        None,
    ),
    created_to: datetime | None = Query(
        None,
    ),
    min_relevance: float = Query(
        0.0,
        ge=0,
        le=1,
    ),
    sort_by: str = Query(
        "relevance",
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
            project_id=project_id,
            project_status=project_status,
            task_status=task_status,
            priority=priority,
            file_type=file_type,
            created_from=created_from,
            created_to=created_to,
            min_relevance=min_relevance,
            sort_by=sort_by,
            skip=skip,
            limit=limit,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
