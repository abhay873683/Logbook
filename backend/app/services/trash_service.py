from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.file import File


def move_to_trash(
    db: Session,
    file_id: int,
    user_id: int,
    role: str,
):
    file = (
        db.query(File)
        .filter(
            File.id == file_id,
            File.is_active == True,
        )
        .first()
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    normalized_role = (role or "").strip().lower()
    allowed_roles = {"admin", "super_admin", "manager"}

    if normalized_role not in allowed_roles and file.uploaded_by != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to move this file to trash",
        )

    file.is_active = False
    file.deleted_at = datetime.now(timezone.utc)
    file.deleted_by = user_id

    try:
        db.commit()
        return {"message": "File moved to trash successfully"}
    except Exception:
        db.rollback()
        raise


def get_trash_files(
    db: Session,
    user_id: int,
    role: str,
):
    query = db.query(File).filter(File.is_active == False)

    normalized_role = (role or "").strip().lower()

    if normalized_role not in {"admin", "super_admin", "manager"}:
        query = query.filter(File.uploaded_by == user_id)

    return query.order_by(File.deleted_at.desc()).all()
