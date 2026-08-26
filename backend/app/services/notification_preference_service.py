from sqlalchemy.orm import Session

from app.models.notification_preference import (
    NotificationPreference,
)

from app.schemas.notification_preference import (
    NotificationPreferenceUpdate,
)


def get_notification_preferences(
    db: Session,
    user_id: int,
):
    preference = (
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.user_id == user_id
        )
        .first()
    )

    if preference:
        return preference

    preference = NotificationPreference(
        user_id=user_id
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

    update_data = data.model_dump()

    for key, value in update_data.items():
        setattr(
            preference,
            key,
            value,
        )

    db.commit()
    db.refresh(preference)

    return preference