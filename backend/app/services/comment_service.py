from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
)


# ======================================
# Get All Comments
# ======================================

def get_all_comments(db: Session):
    return db.query(Comment).all()


# ======================================
# Get Comment By ID
# ======================================

def get_comment_by_id(comment_id: int, db: Session):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise ValueError("Comment not found")

    return comment


# ======================================
# Create Comment
# ======================================

def create_comment(
    comment: CommentCreate,
    created_by: int,
    db: Session,
):
    new_comment = Comment(
        task_id=comment.task_id,
        user_id=created_by,
        comment=comment.comment,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


# ======================================
# Update Comment
# ======================================

def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: Session,
):
    db_comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not db_comment:
        raise ValueError("Comment not found")

    update_data = comment.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_comment, key, value)

    db.commit()
    db.refresh(db_comment)

    return db_comment


# ======================================
# Delete Comment
# ======================================

def delete_comment(
    comment_id: int,
    db: Session,
):
    db_comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not db_comment:
        raise ValueError("Comment not found")

    db.delete(db_comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }