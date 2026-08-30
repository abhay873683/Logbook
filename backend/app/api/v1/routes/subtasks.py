from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.subtask import (
    SubtaskCreate,
    SubtaskUpdate,
    SubtaskResponse,
)

from app.services.subtask_service import (
    get_all_subtasks,
    get_subtask_by_id,
    create_subtask,
    update_subtask,
    delete_subtask,
)

from app.services.activity_log_service import (
    log_activity,
)


router = APIRouter(
    tags=["Subtasks"]
)


def get_client_ip(
    request: Request,
) -> str | None:
    forwarded = request.headers.get(
        "x-forwarded-for"
    )

    if forwarded:
        return forwarded.split(",")[0].strip()

    if request.client:
        return request.client.host

    return None


@router.get(
    "/",
    response_model=list[SubtaskResponse],
)
def read_subtasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_subtasks(db)


@router.get(
    "/{subtask_id}",
    response_model=SubtaskResponse,
)
def read_subtask(
    subtask_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subtask = get_subtask_by_id(
        subtask_id,
        db,
    )

    if not subtask:
        raise HTTPException(
            status_code=404,
            detail="Subtask not found"
        )

    return subtask


@router.post(
    "/",
    response_model=SubtaskResponse,
    status_code=201,
)
def create_new_subtask(
    subtask: SubtaskCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    created = create_subtask(
        subtask=subtask,
        created_by=current_user.id,
        db=db,
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="subtask_created",
        entity_type="subtask",
        entity_id=created.id,
        description=(
            f"Subtask '{created.title}' created"
        ),
        ip_address=get_client_ip(request),
    )

    return created


@router.put(
    "/{subtask_id}",
    response_model=SubtaskResponse,
)
def update_existing_subtask(
    subtask_id: int,
    subtask: SubtaskUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_subtask = update_subtask(
        subtask_id,
        subtask,
        db,
    )

    if not updated_subtask:
        raise HTTPException(
            status_code=404,
            detail="Subtask not found"
        )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="subtask_updated",
        entity_type="subtask",
        entity_id=updated_subtask.id,
        description=(
            f"Subtask '{updated_subtask.title}' updated"
        ),
        ip_address=get_client_ip(request),
    )

    return updated_subtask


@router.delete("/{subtask_id}")
def delete_existing_subtask(
    subtask_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_subtask_by_id(
        subtask_id,
        db,
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Subtask not found"
        )

    subtask_title = existing.title

    deleted = delete_subtask(
        subtask_id,
        db,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Subtask not found"
        )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="subtask_deleted",
        entity_type="subtask",
        entity_id=subtask_id,
        description=(
            f"Subtask '{subtask_title}' deleted"
        ),
        ip_address=get_client_ip(request),
    )

    return {
        "message": (
            "Subtask deleted successfully"
        )
    }
