from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.task import Task

from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
)


# =========================================================
# Validate Task
# =========================================================
def validate_comment_task(
    task_id: int,
    db: Session,
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise ValueError("Task not found")

    return task


# =========================================================
# Validate Comment Content
# =========================================================
def validate_comment_content(
    content: str | None,
):
    if content is None:
        raise ValueError(
            "Comment content cannot be empty"
        )

    if not content.strip():
        raise ValueError(
            "Comment content cannot be empty"
        )

    return content.strip()


# =========================================================
# Get All Comments
# =========================================================
def get_all_comments(db: Session):
    return db.query(Comment).all()


# =========================================================
# Get Comments For Task
# =========================================================
def get_task_comments(
    task_id: int,
    db: Session,
):
    validate_comment_task(
        task_id,
        db,
    )

    return (
        db.query(Comment)
        .filter(Comment.task_id == task_id)
        .all()
    )


# =========================================================
# Get Comment By ID
# =========================================================
def get_comment_by_id(
    comment_id: int,
    db: Session,
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise ValueError("Comment not found")

    return comment


# =========================================================
# Create Comment
# =========================================================
def create_comment(
    comment: CommentCreate,
    created_by: int,
    db: Session,
):
    # Validate Task
    validate_comment_task(
        comment.task_id,
        db,
    )

    # Validate Comment Content
    clean_comment = validate_comment_content(
        comment.comment
    )

    new_comment = Comment(
        task_id=comment.task_id,
        user_id=created_by,
        comment=clean_comment,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


# =========================================================
# Update Comment
# =========================================================
def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: Session,
):
    db_comment = get_comment_by_id(
        comment_id,
        db,
    )

    update_data = comment.model_dump(
        exclude_unset=True
    )

    # If Task ID is being changed
    if "task_id" in update_data:
        validate_comment_task(
            update_data["task_id"],
            db,
        )

    # Validate changed comment text
    if "comment" in update_data:
        update_data["comment"] = (
            validate_comment_content(
                update_data["comment"]
            )
        )

    for key, value in update_data.items():
        setattr(
            db_comment,
            key,
            value,
        )

    db.commit()
    db.refresh(db_comment)

    return db_comment


# =========================================================
# Delete Comment
# =========================================================
def delete_comment(
    comment_id: int,
    db: Session,
):
    db_comment = get_comment_by_id(
        comment_id,
        db,
    )

    db.delete(db_comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }