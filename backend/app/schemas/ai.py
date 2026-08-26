from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class AISessionCreate(BaseModel):
    title: str = "New AI Chat"


class AISessionUpdate(BaseModel):
    title: str


class AISessionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class AIMessageCreate(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=5000,
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Message cannot be empty"
            )

        return value


class AIMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    tokens: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class AISuggestionCreate(BaseModel):
    suggestion_type: str = "task"
    input_text: str

    @field_validator("input_text")
    @classmethod
    def validate_input(cls, value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Input text cannot be empty"
            )

        return value


class AISuggestionResponse(BaseModel):
    id: int
    user_id: int
    suggestion_type: str
    input_text: str
    output_text: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )