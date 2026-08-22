from sqlalchemy.orm import Session

from app.models.file_share import FileShare
from app.schemas.revoke_share import RevokeShareRequest


def revoke_share(db: Session, data: RevokeShareRequest, user_id: int, role: str):
    if role == "employee":
        raise Exception("Not allowed to revoke shares")

    share = db.query(FileShare).filter(
        FileShare.id == data.share_id,
        FileShare.is_active == True,
    ).first()

    if not share:
        raise Exception("Share not found or already revoked")

    share.is_active = False
    db.commit()

    return {
        "message": "Share revoked successfully",
        "is_active": share.is_active,
    }