from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationPreferenceUpdate(BaseModel):
    email_notifications: bool = True
    in_app_notifications: bool = True
    task_notifications: bool = True
    message_notifications: bool = True
    deadline_notifications: bool = True
    system_notifications: bool = True


class NotificationPreferenceResponse(BaseModel):
    id: int
    user_id: int

    email_notifications: bool
    in_app_notifications: bool
    task_notifications: bool
    message_notifications: bool
    deadline_notifications: bool
    system_notifications: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )