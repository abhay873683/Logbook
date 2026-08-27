from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
)


ALLOWED_RECURRENCE = {
    "daily",
    "weekly",
    "monthly",
}


class ReminderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    remind_at: datetime
    is_recurring: bool = False
    recurrence: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Reminder title cannot be empty")

        return value

    @field_validator("recurrence")
    @classmethod
    def validate_recurrence(cls, value):
        if value is None:
            return value

        value = value.lower().strip()

        if value not in ALLOWED_RECURRENCE:
            raise ValueError(
                "Recurrence must be daily, weekly or monthly"
            )

        return value

    @model_validator(mode="after")
    def validate_recurring_settings(self):
        if self.is_recurring and not self.recurrence:
            raise ValueError(
                "recurrence is required when is_recurring is true"
            )

        if not self.is_recurring:
            self.recurrence = None

        return self


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    remind_at: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence: Optional[str] = None
    is_completed: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Reminder title cannot be empty")

        return value

    @field_validator("recurrence")
    @classmethod
    def validate_recurrence(cls, value):
        if value is None:
            return value

        value = value.lower().strip()

        if value not in ALLOWED_RECURRENCE:
            raise ValueError(
                "Recurrence must be daily, weekly or monthly"
            )

        return value


class ReminderResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    remind_at: datetime
    is_recurring: bool
    recurrence: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )