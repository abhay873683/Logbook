from app.models.subtask_progress import SubtaskProgress
from app.schemas.subtask_progress import SubtaskProgressCreate
from sqlalchemy.orm import Session

def update_subtask_progress(db: Session, data: SubtaskProgressCreate, user_id: int):
    existing = db.query(SubtaskProgress).filter(
        SubtaskProgress.subtask_id == data.subtask_id,
        SubtaskProgress.user_id == user_id
    ).first()

    if existing:
        existing.progress = data.progress
        existing.status = data.status
        existing.note = data.note
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_progress = SubtaskProgress(**data.dict(), user_id=user_id)
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        return new_progress


def get_my_subtask_progress(db: Session, subtask_id: int, user_id: int):
    return db.query(SubtaskProgress).filter(
        SubtaskProgress.subtask_id == subtask_id,
        SubtaskProgress.user_id == user_id
    ).first()


def get_subtask_progress_by_id(db: Session, subtask_id: int):
    return db.query(SubtaskProgress).filter(
        SubtaskProgress.subtask_id == subtask_id
    ).order_by(SubtaskProgress.updated_at.desc()).all()