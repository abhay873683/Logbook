from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.file import File
from app.models.file_share import FileShare


PRIVILEGED_ROLES = {
    "admin",
    "super_admin",
    "manager",
}


def get_file_report(
    db: Session,
    user_id: int,
    role: str,
):
    normalized_role = (
        role or ""
    ).strip().lower()

    if normalized_role in PRIVILEGED_ROLES:
        files = (
            db.query(File)
            .filter(File.is_active == True)
            .order_by(File.created_at.desc())
            .all()
        )

    else:
        shared_file_ids = [
            share.file_id
            for share in (
                db.query(FileShare)
                .filter(
                    FileShare.shared_with == user_id,
                    FileShare.is_active == True,
                )
                .all()
            )
        ]

        files = (
            db.query(File)
            .filter(
                File.is_active == True,
                or_(
                    File.uploaded_by == user_id,
                    File.id.in_(
                        shared_file_ids
                    ),
                ),
            )
            .order_by(File.created_at.desc())
            .all()
        )

    report = []

    for file in files:
        report.append(
            {
                "file_id": file.id,
                "file_name": file.file_name,
                "file_type": file.file_type,
                "folder_id": file.folder_id,
                "size": file.file_size,
                "uploaded_by": file.uploaded_by,
                "created_at": file.created_at,
            }
        )

    return report
