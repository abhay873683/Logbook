from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
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


router = APIRouter()


# =========================================================
# GET ALL COMMENTS
# =========================================================
@router.get(
    "/",
    response_model=list[CommentResponse],
)
def read_comments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_comments(db)


# =========================================================
# GET COMMENTS FOR TASK
# IMPORTANT: Keep before /{comment_id}
# =========================================================
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


# =========================================================
# GET COMMENT BY ID
# =========================================================
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


# =========================================================
# CREATE COMMENT
# =========================================================
@router.post(
    "/",
    response_model=CommentResponse,
    status_code=201,
)
def create_new_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_comment(
            comment,
            current_user.id,
            db,
        )

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


# =========================================================
# UPDATE COMMENT
# =========================================================
@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
)
def update_existing_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_comment(
            comment_id,
            comment,
            db,
        )

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


# =========================================================
# DELETE COMMENT
# =========================================================
@router.delete("/{comment_id}")
def delete_existing_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_comment(
            comment_id,
            db,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )