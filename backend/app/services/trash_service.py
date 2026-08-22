from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.file import File


# ----------------------------------------
# Move File to Trash (soft delete)
# ----------------------------------------
def move_to_trash(db: Session, file_id: int, user_id: int, role: str):
    file = db.query(File).filter(
        File.id == file_id,
        File.is_active == True,
    ).first()

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    if role == "employee":
        raise HTTPException(
            status_code=403,
            detail="Not allowed to move files to trash",
        )

    file.is_active = False
    file.deleted_at = datetime.utcnow()
    file.deleted_by = user_id

    db.commit()

    return {
        "message": "File moved to trash successfully"
    }


# ----------------------------------------
# List Trash Files (role based)
# ----------------------------------------
def get_trash_files(db: Session, user_id: int, role: str):
    query = db.query(File).filter(File.is_active == False)

    # Employee has no access to trash at all
    if role == "employee":
        raise HTTPException(
            status_code=403,
            detail="Not allowed to access trash",
        )

    return query.order_by(File.deleted_at.desc()).all()