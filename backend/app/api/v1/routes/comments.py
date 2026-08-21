from fastapi import APIRouter, Depends, HTTPException
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
    get_comment_by_id,
    create_comment,
    update_comment,
    delete_comment,
)

router = APIRouter()


# -----------------------------------
# Get All Comments
# -----------------------------------
@router.get(
    "/",
    response_model=list[CommentResponse],
)
def read_comments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_comments(db)


# -----------------------------------
# Get Comment By ID
# -----------------------------------
@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
)
def read_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = get_comment_by_id(comment_id, db)

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    return comment


# -----------------------------------
# Create Comment
# -----------------------------------
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
    return create_comment(
        comment,
        current_user.id,
        db,
    )


# -----------------------------------
# Update Comment
# -----------------------------------
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
    updated_comment = update_comment(
        comment_id,
        comment,
        db,
    )

    if not updated_comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    return updated_comment


# -----------------------------------
# Delete Comment
# -----------------------------------
@router.delete("/{comment_id}")
def delete_existing_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_comment(
        comment_id,
        db,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    return {
        "message": "Comment deleted successfully"
    }