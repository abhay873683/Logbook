from datetime import datetime
from typing import Any, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


ALLOWED_NOTIFICATION_TYPES = {
    "info",
    "success",
    "warning",
    "error",
}

ALLOWED_PRIORITIES = {
    "low",
    "normal",
    "high",
    "urgent",
}


class NotificationCreate(BaseModel):
    user_id: Optional[int] = None

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    message: str = Field(
        min_length=1,
        max_length=5000,
    )

    type: str = "info"

    priority: Optional[str] = None

    category: str = Field(
        default="general",
        min_length=1,
        max_length=50,
    )

    source: str = Field(
        default="system",
        min_length=1,
        max_length=100,
    )

    data: Optional[dict[str, Any]] = None

    @field_validator(
        "title",
        "message",
        "category",
        "source",
    )
    @classmethod
    def validate_text(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty"
            )

        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str):
        value = value.lower().strip()

        if value not in ALLOWED_NOTIFICATION_TYPES:
            raise ValueError(
                "Invalid notification type. "
                "Allowed types: "
                "info, success, warning, error"
            )

        return value

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value):
        if value is None:
            return value

        value = value.lower().strip()

        if value not in ALLOWED_PRIORITIES:
            raise ValueError(
                "Invalid priority. "
                "Allowed priorities: "
                "low, normal, high, urgent"
            )

        return value


class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    message: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=5000,
    )

    type: Optional[str] = None

    priority: Optional[str] = None

    category: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    source: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    data: Optional[dict[str, Any]] = None

    is_read: Optional[bool] = None

    @field_validator(
        "title",
        "message",
        "category",
        "source",
    )
    @classmethod
    def validate_optional_text(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty"
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
                "Allowed types: "
                "info, success, warning, error"
            )

        return value

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value):
        if value is None:
            return value

        value = value.lower().strip()

        if value not in ALLOWED_PRIORITIES:
            raise ValueError(
                "Invalid priority. "
                "Allowed priorities: "
                "low, normal, high, urgent"
            )

        return value


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    priority: str
    category: str
    source: str
    data: Optional[dict[str, Any]] = None
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class NotificationStatsResponse(BaseModel):
    total: int
    unread: int
    read: int
    low: int
    normal: int
    high: int
    urgent: int


class NotificationPriorityPreviewRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )

    message: str = Field(
        min_length=1,
        max_length=5000,
    )

    type: str = "info"

    category: str = "general"

    source: str = "system"


class NotificationPriorityPreviewResponse(BaseModel):
    priority: str
    score: int
    reasons: list[str]
