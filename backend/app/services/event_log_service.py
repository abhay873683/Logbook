from sqlalchemy.orm import Session

from app.models.event_log import EventLog
from app.schemas.event_log import EventLogCreate


def create_event_log(
    db: Session,
    user_id: int | None,
    data: EventLogCreate,
):
    event = EventLog(
        user_id=user_id,
        event_type=data.event_type,
        description=data.description,
        event_metadata=data.metadata,
        ip_address=data.ip_address,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def get_event_logs(
    db: Session,
    limit: int = 50,
):
    return (
        db.query(EventLog)
        .order_by(
            EventLog.created_at.desc()
        )
        .limit(limit)
        .all()
    )