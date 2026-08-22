from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.file import File
from app.models.file_share import FileShare


def get_file_report(db: Session, user_id: int, role: str):
    if role == "employee":
        # Own files + files shared with them
        shared_file_ids = [
            fs.file_id for fs in db.query(FileShare).filter(
                FileShare.shared_with == user_id,
                FileShare.is_active == True,
            ).all()
        ]

        files = db.query(File).filter(
            or_(
                File.uploaded_by == user_id,
                File.id.in_(shared_file_ids),
            )
        ).all()
    else:
        # Admin / Manager see all files
        files = db.query(File).all()

    report = []
    for f in files:
        report.append({
            "file_id": f.id,
            "file_name": f.file_name,
            "file_type": f.file_type,
            "size": f.file_size,
            "uploaded_by": f.uploaded_by,
            "created_at": f.created_at,
        })

    return report