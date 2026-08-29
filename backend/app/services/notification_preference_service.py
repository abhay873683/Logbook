from sqlalchemy.orm import Session

from app.models.notification_preference import (
    NotificationPreference,
)

from app.schemas.notification_preference import (
    NotificationPreferenceUpdate,
)


DEFAULT_PREFERENCES = {
    "email_notifications": True,
    "push_notifications": True,
    "in_app_notifications": True,
    "task_notifications": True,
    "message_notifications": True,
    "deadline_notifications": True,
    "system_notifications": True,
    "security_notifications": True,
    "approval_notifications": True,
    "general_notifications": True,
}


CATEGORY_FIELD_MAP = {
    "task": "task_notifications",
    "message": "message_notifications",
    "deadline": "deadline_notifications",
    "system": "system_notifications",
    "security": "security_notifications",
    "approval": "approval_notifications",
    "general": "general_notifications",
}


def get_notification_preferences(
    db: Session,
    user_id: int,
):
    preference = (
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.user_id
            == user_id
        )
        .first()
    )

    if preference:
        return preference

    preference = NotificationPreference(
        user_id=user_id,
        **DEFAULT_PREFERENCES,
    )

    db.add(preference)
    db.commit()
    db.refresh(preference)

    return preference


def update_notification_preferences(
    db: Session,
    user_id: int,
    data: NotificationPreferenceUpdate,
):
    preference = get_notification_preferences(
        db,
        user_id,
    )

    update_data = data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    for key, value in update_data.items():
        if key in DEFAULT_PREFERENCES:
            setattr(
                preference,
                key,
                value,
            )

    db.commit()
    db.refresh(preference)

    return preference


def reset_notification_preferences(
    db: Session,
    user_id: int,
):
    preference = get_notification_preferences(
        db,
        user_id,
    )

    for key, value in DEFAULT_PREFERENCES.items():
        setattr(
            preference,
            key,
            value,
        )

    db.commit()
    db.refresh(preference)

    return preference


def is_category_enabled(
    preference: NotificationPreference,
    category: str | None,
):
    normalized_category = (
        category or "general"
    ).strip().lower()

    field_name = CATEGORY_FIELD_MAP.get(
        normalized_category,
        "general_notifications",
    )

    return bool(
        getattr(
            preference,
            field_name,
            True,
        )
    )


def get_effective_preferences(
    db: Session,
    user_id: int,
):
    preference = get_notification_preferences(
        db,
        user_id,
    )

    return {
        "in_app_enabled": (
            preference.in_app_notifications
        ),
        "email_enabled": (
            preference.email_notifications
        ),
        "push_enabled": (
            preference.push_notifications
        ),
        "categories": {
            category: bool(
                getattr(
                    preference,
                    field_name,
                )
            )
            for category, field_name
            in CATEGORY_FIELD_MAP.items()
        },
    }
