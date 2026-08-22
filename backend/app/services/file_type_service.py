from sqlalchemy.orm import Session

from app.models.file_type import FileType


def get_all_file_types(db: Session):
    return db.query(FileType).filter(FileType.is_active == True).all()