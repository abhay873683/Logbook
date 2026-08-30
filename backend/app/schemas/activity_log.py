from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class ActivityLogCreate(BaseModel):
    user_id: Optional[int] = None

    action: str = Field(
        ...,
        max_length=100,
    )

    module: str = Field(
        ...,
        max_length=100,
    )

    module_id: Optional[int] = None

    description: Optional[str] = None

    ip_address: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    @field_validator(
        "action",
        "module",
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str,
    ):
        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty"
            )

        return value

    @field_validator(
        "description",
        "ip_address",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: Optional[str],
    ):
        if value is None:
            return None

        value = value.strip()

        return value or None


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


class ActivityStatsResponse(BaseModel):
    total_logs: int
    my_logs: int
    unique_actions: int
    unique_modules: int
    recent_24h: int
