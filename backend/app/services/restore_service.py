from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.file import File


def restore_file(db: Session, file_id: int, user_id: int, role: str):
    file = db.query(File).filter(
        File.id == file_id,
        File.is_active == False,
    ).first()

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found in trash",
        )

    # Employee cannot restore any file (per role table)
    if role == "employee":
        raise HTTPException(
            status_code=403,
            detail="Not allowed to restore files",
        )

    file.is_active = True
    file.deleted_at = None
    file.deleted_by = None

    db.commit()
    db.refresh(file)

    return {
        "id": file.id,
        "original_name": file.file_name,
        "restored": True,
        "restored_at": file.created_at,
    }