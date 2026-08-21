from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.comment_reply import (
    CommentReplyCreate,
    CommentReplyResponse,
)

from app.services.comment_reply_service import (
    add_comment_reply,
    get_replies,
)

from app.services.activity_log_service import log_activity

router = APIRouter()


# ---------------------------------
# Add Reply to a Comment
# ---------------------------------
@router.post(
    "/reply",
    response_model=CommentReplyResponse,
    status_code=201,
)
def create_comment_reply(
    data: CommentReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = add_comment_reply(db, data, current_user.id)

    # ---------------------------------
    # Log this activity
    # ---------------------------------
    log_activity(
        db=db,
        user_id=current_user.id,
        action="Replied to Comment",
        entity_type="Comment",
        entity_id=data.comment_id,
        description=f"Reply added: {data.reply[:100]}",
    )

    return result


# ---------------------------------
# Get All Replies of a Comment
# ---------------------------------
@router.get(
    "/{comment_id}/replies",
    response_model=list[CommentReplyResponse],
)
def read_comment_replies(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_replies(db, comment_id)