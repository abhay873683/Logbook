from sqlalchemy.orm import Session

from app.models.file import File
from app.models.file_share import FileShare
from app.schemas.file_share import FileShareCreate


def share_file(db: Session, data: FileShareCreate, user_id: int, role: str):
    # Only Admin, Manager, Super Admin can share
    if role == "employee":
        raise Exception("Not allowed to share files")

    file = db.query(File).filter(File.id == data.file_id).first()

    if not file:
        raise Exception("File not found")

    share = FileShare(
        file_id=data.file_id,
        shared_by=user_id,
        shared_with=data.shared_with,
        permission=data.permission,
        is_active=True,
    )

    db.add(share)
    db.commit()
    db.refresh(share)

    return share