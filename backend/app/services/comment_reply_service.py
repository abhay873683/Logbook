from app.models.comment_reply import CommentReply
from app.schemas.comment_reply import CommentReplyCreate
from sqlalchemy.orm import Session

def add_comment_reply(db: Session, data: CommentReplyCreate, user_id: int):
    reply = CommentReply(
        comment_id=data.comment_id,
        reply=data.reply,
        user_id=user_id
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply


def get_replies(db: Session, comment_id: int):
    return db.query(CommentReply).filter(
        CommentReply.comment_id == comment_id
    ).order_by(CommentReply.created_at).all()