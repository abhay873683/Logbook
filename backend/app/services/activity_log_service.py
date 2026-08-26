from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.user import User

from app.schemas.activity_log import ActivityLogCreate


def validate_activity_user(
    db: Session,
    user_id: int | None,
):
    if user_id is None:
        return None

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    return user


def create_activity_log(
    db: Session,
    activity: ActivityLogCreate,
):
    validate_activity_user(
        db,
        activity.user_id,
    )

    new_log = ActivityLog(
        user_id=activity.user_id,
        action=activity.action,
        module=activity.module,
        module_id=activity.module_id,
        description=activity.description,
        ip_address=activity.ip_address,
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log


def log_activity(
    db: Session,
    user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int | None,
    description: str | None = None,
    ip_address: str | None = None,
):
    activity = ActivityLogCreate(
        user_id=user_id,
        action=action,
        module=entity_type,
        module_id=entity_id,
        description=description,
        ip_address=ip_address,
    )

    return create_activity_log(
        db,
        activity,
    )


def get_activity_log_by_id(
    db: Session,
    activity_id: int,
):
    activity = (
        db.query(ActivityLog)
        .filter(ActivityLog.id == activity_id)
        .first()
    )

    if not activity:
        raise ValueError(
            "Activity log not found"
        )

    return activity


def get_activity_logs(
    db: Session,
    user_id: int,
    limit: int = 20,
):
    return (
        db.query(ActivityLog)
        .filter(
            ActivityLog.user_id == user_id
        )
        .order_by(
            ActivityLog.created_at.desc()
        )
        .limit(limit)
        .all()
    )


def get_all_activity_logs(
    db: Session,
    limit: int = 50,
):
    return (
        db.query(ActivityLog)
        .order_by(
            ActivityLog.created_at.desc()
        )
        .limit(limit)
        .all()
    )


def delete_activity_log(
    db: Session,
    activity_id: int,
):
    activity = get_activity_log_by_id(
        db,
        activity_id,
    )

    db.delete(activity)
    db.commit()

    return {
        "message": "Activity log deleted successfully"
    }