from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
)


class ActivityLogCreate(BaseModel):
    user_id: Optional[int] = None
    action: str
    module: str
    module_id: Optional[int] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None

    @field_validator("action")
    @classmethod
    def validate_action(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError(
                "Activity action cannot be empty"
            )

        return value

    @field_validator("module")
    @classmethod
    def validate_module(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError(
                "Activity module cannot be empty"
            )

        return value


class ActivityLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    module: str
    module_id: Optional[int] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )