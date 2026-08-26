from datetime import datetime
from typing import Optional, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
)


ALLOWED_NOTIFICATION_TYPES = {
    "info",
    "success",
    "warning",
    "error",
}


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    type: str = "info"
    data: Optional[dict[str, Any]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError(
                "Notification title cannot be empty"
            )

        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError(
                "Notification message cannot be empty"
            )

        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str):
        value = value.lower().strip()

        if value not in ALLOWED_NOTIFICATION_TYPES:
            raise ValueError(
                "Invalid notification type. "
                "Allowed types: info, success, warning, error"
            )

        return value


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    type: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    is_read: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError(
                "Notification title cannot be empty"
            )

        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError(
                "Notification message cannot be empty"
            )

        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        if value is None:
            return value

        value = value.lower().strip()

        if value not in ALLOWED_NOTIFICATION_TYPES:
            raise ValueError(
                "Invalid notification type. "
                "Allowed types: info, success, warning, error"
            )

        return value


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    data: Optional[dict[str, Any]] = None
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )