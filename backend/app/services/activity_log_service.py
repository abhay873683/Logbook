from app.models.activity_log import ActivityLog
from sqlalchemy.orm import Session
from datetime import datetime

def log_activity(db: Session, user_id: int, action: str, entity_type: str, entity_id: int, description: str = None):
    log = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        created_at=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_activity_logs(db: Session, user_id: int, limit: int = 20):
    return db.query(ActivityLog).filter(
        ActivityLog.user_id == user_id
    ).order_by(ActivityLog.created_at.desc()).limit(limit).all()


def get_all_activity_logs(db: Session, limit: int = 50):
    return db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit).all()