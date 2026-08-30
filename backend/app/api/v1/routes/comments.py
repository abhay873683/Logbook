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

from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)

from app.services.comment_service import (
    get_all_comments,
    get_task_comments,
    get_comment_by_id,
    create_comment,
    update_comment,
    delete_comment,
)

from app.services.activity_log_service import (
    log_activity,
)


router = APIRouter()


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
    response_model=list[CommentResponse],
)
def read_comments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_comments(db)


@router.get(
    "/task/{task_id}",
    response_model=list[CommentResponse],
)
def read_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_task_comments(
            task_id,
            db,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
)
def read_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_comment_by_id(
            comment_id,
            db,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.post(
    "/",
    response_model=CommentResponse,
    status_code=201,
)
def create_new_comment(
    comment: CommentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        created = create_comment(
            comment,
            current_user.id,
            db,
        )

        log_activity(
            db=db,
            user_id=current_user.id,
            action="comment_created",
            entity_type="comment",
            entity_id=created.id,
            description=(
                f"Comment created on task "
                f"{created.task_id}"
            ),
            ip_address=get_client_ip(request),
        )

        return created

    except ValueError as e:
        error_message = str(e)

        if error_message == "Task not found":
            status_code = 404
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=error_message,
        )


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
)
def update_existing_comment(
    comment_id: int,
    comment: CommentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated = update_comment(
            comment_id,
            comment,
            db,
        )

        log_activity(
            db=db,
            user_id=current_user.id,
            action="comment_updated",
            entity_type="comment",
            entity_id=updated.id,
            description=(
                f"Comment {updated.id} updated"
            ),
            ip_address=get_client_ip(request),
        )

        return updated

    except ValueError as e:
        error_message = str(e)

        if error_message in {
            "Comment not found",
            "Task not found",
        }:
            status_code = 404
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=error_message,
        )


@router.delete("/{comment_id}")
def delete_existing_comment(
    comment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        existing = get_comment_by_id(
            comment_id,
            db,
        )

        task_id = existing.task_id

        result = delete_comment(
            comment_id,
            db,
        )

        log_activity(
            db=db,
            user_id=current_user.id,
            action="comment_deleted",
            entity_type="comment",
            entity_id=comment_id,
            description=(
                f"Comment deleted from task "
                f"{task_id}"
            ),
            ip_address=get_client_ip(request),
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
