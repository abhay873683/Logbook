from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationPreferenceUpdate(BaseModel):
    email_notifications: bool | None = None
    push_notifications: bool | None = None
    in_app_notifications: bool | None = None

    task_notifications: bool | None = None
    message_notifications: bool | None = None
    deadline_notifications: bool | None = None
    system_notifications: bool | None = None
    security_notifications: bool | None = None
    approval_notifications: bool | None = None
    general_notifications: bool | None = None


class NotificationPreferenceResponse(BaseModel):
    id: int
    user_id: int

    email_notifications: bool
    push_notifications: bool
    in_app_notifications: bool

    task_notifications: bool
    message_notifications: bool
    deadline_notifications: bool
    system_notifications: bool
    security_notifications: bool
    approval_notifications: bool
    general_notifications: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class NotificationPreferenceEffectiveResponse(BaseModel):
    in_app_enabled: bool
    email_enabled: bool
    push_enabled: bool

    categories: dict[str, bool]


class NotificationConnectionResponse(BaseModel):
    user_id: int
    active_connections: int
    connected: bool
