from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy import distinct
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.user import User

from app.schemas.activity_log import (
    ActivityLogCreate,
)


def is_admin(user: User) -> bool:
    return (
        str(user.role or "")
        .strip()
        .lower()
        == "admin"
    )


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
        raise ValueError(
            "User not found"
        )

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
        .filter(
            ActivityLog.id == activity_id
        )
        .first()
    )

    if not activity:
        raise ValueError(
            "Activity log not found"
        )

    return activity


def get_activity_log_for_user(
    db: Session,
    activity_id: int,
    current_user: User,
):
    activity = get_activity_log_by_id(
        db,
        activity_id,
    )

    if (
        activity.user_id
        != current_user.id
        and not is_admin(current_user)
    ):
        raise PermissionError(
            "You do not have permission "
            "to view this activity log"
        )

    return activity


def build_activity_query(
    db: Session,
    user_id: int | None = None,
    action: str | None = None,
    module: str | None = None,
    module_id: int | None = None,
):
    query = db.query(ActivityLog)

    if user_id is not None:
        query = query.filter(
            ActivityLog.user_id
            == user_id
        )

    if action:
        query = query.filter(
            ActivityLog.action.ilike(
                f"%{action.strip()}%"
            )
        )

    if module:
        query = query.filter(
            ActivityLog.module.ilike(
                f"%{module.strip()}%"
            )
        )

    if module_id is not None:
        query = query.filter(
            ActivityLog.module_id
            == module_id
        )

    return query


def get_activity_logs(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    action: str | None = None,
    module: str | None = None,
    module_id: int | None = None,
):
    return (
        build_activity_query(
            db=db,
            user_id=user_id,
            action=action,
            module=module,
            module_id=module_id,
        )
        .order_by(
            ActivityLog.created_at.desc(),
            ActivityLog.id.desc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_activity_logs(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    user_id: int | None = None,
    action: str | None = None,
    module: str | None = None,
    module_id: int | None = None,
):
    return (
        build_activity_query(
            db=db,
            user_id=user_id,
            action=action,
            module=module,
            module_id=module_id,
        )
        .order_by(
            ActivityLog.created_at.desc(),
            ActivityLog.id.desc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_activity_stats(
    db: Session,
    current_user: User,
):
    admin = is_admin(
        current_user
    )

    if admin:
        base_query = db.query(
            ActivityLog
        )
    else:
        base_query = (
            db.query(ActivityLog)
            .filter(
                ActivityLog.user_id
                == current_user.id
            )
        )

    total_logs = (
        base_query.count()
    )

    my_logs = (
        db.query(ActivityLog)
        .filter(
            ActivityLog.user_id
            == current_user.id
        )
        .count()
    )

    action_query = db.query(
        distinct(
            ActivityLog.action
        )
    )

    module_query = db.query(
        distinct(
            ActivityLog.module
        )
    )

    if not admin:
        action_query = (
            action_query.filter(
                ActivityLog.user_id
                == current_user.id
            )
        )

        module_query = (
            module_query.filter(
                ActivityLog.user_id
                == current_user.id
            )
        )

    unique_actions = (
        action_query.count()
    )

    unique_modules = (
        module_query.count()
    )

    since = (
        datetime.now(
            timezone.utc
        )
        - timedelta(hours=24)
    )

    recent_query = (
        db.query(ActivityLog)
        .filter(
            ActivityLog.created_at
            >= since
        )
    )

    if not admin:
        recent_query = (
            recent_query.filter(
                ActivityLog.user_id
                == current_user.id
            )
        )

    recent_24h = (
        recent_query.count()
    )

    return {
        "total_logs": total_logs,
        "my_logs": my_logs,
        "unique_actions": (
            unique_actions
        ),
        "unique_modules": (
            unique_modules
        ),
        "recent_24h": recent_24h,
    }
